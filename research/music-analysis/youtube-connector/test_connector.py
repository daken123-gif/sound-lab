import json
import subprocess
import time
import threading
from http.cookiejar import Cookie
from pathlib import Path

import pytest
import numpy as np
from scipy.io import wavfile

from backend import Backend
from worker import canonical, clean_error, verify_audio, execute, GuestYoutubeDL, options

VIDEO = "mdhtm6qjmhU"
CHANNEL = "UCBUAlfIrcw1f0c4qGrYn3xA"


def wait(backend, job):
    for _ in range(200):
        state = backend.status(job["job_id"])
        if state["status"] not in ("queued", "running"):
            return state
        time.sleep(0.01)
    raise AssertionError("job did not terminate")


@pytest.mark.parametrize("value", ["../manifest", "https://example.com/file", "mdhtm6qjmhU\n", "-" * 200])
def test_no_arbitrary_url_or_path(value):
    with pytest.raises(ValueError):
        canonical(value)


def test_error_does_not_expose_signed_url():
    error = Exception("HTTPSConnectionPool https://cdn.example/a?sig=SECRET&ip=127.0.0.1 Read timed out")
    assert clean_error(error) == "network_timeout"


def test_failed_acquisition_is_not_analyzable_and_retry_is_idempotent(tmp_path):
    calls = []

    def fail(payload, timeout):
        calls.append(payload)
        return {"error": "network_timeout"}

    b = Backend(tmp_path, runner=fail)
    try:
        job = b.submit("acquire", "same-request", video_id=VIDEO, expected_channel_id=CHANNEL)
        result = wait(b, job)
        assert result["status"] == "failed"
        assert b.submit("acquire", "same-request", video_id=VIDEO, expected_channel_id=CHANNEL)["job_id"] == job["job_id"]
        assert len(calls) == 1
        with pytest.raises(ValueError, match="source_not_decoded"):
            b.submit("analyze", "analysis", source_job_id=job["job_id"])
        with pytest.raises(ValueError, match="request_key_conflict"):
            b.submit("acquire", "same-request", video_id="abcdefghijk", expected_channel_id=CHANNEL)
    finally:
        b.close()
    b = Backend(tmp_path, runner=fail)
    try:
        assert b.status(job["job_id"])["status"] == "failed"
    finally:
        b.close()


def test_completion_word_without_bytes_is_rejected(tmp_path):
    b = Backend(tmp_path, runner=lambda *_: {"stage": "decoded", "manifest": {"sha256": "fake"}})
    try:
        job = b.submit("acquire", "bad-evidence", video_id=VIDEO, expected_channel_id=CHANNEL)
        result = wait(b, job)
        assert result["status"] == "failed"
        assert result["error"] == "audio_evidence_missing"
    finally:
        b.close()


def test_real_decoder_and_truncation_detection(tmp_path):
    audio = tmp_path / "fixture.wav"
    subprocess.run(["ffmpeg", "-v", "error", "-f", "lavfi", "-i", "sine=frequency=440:duration=2",
                    "-ac", "2", str(audio)], check=True)
    info = {"id": VIDEO, "channel_id": CHANNEL, "title": "synthetic test fixture", "duration": 2}
    result = verify_audio(audio, info)
    assert result["state"] == "full-source-decoded"
    assert result["decoded_duration_s"] == 2
    with pytest.raises(ValueError, match="incomplete_or_different_duration"):
        verify_audio(audio, {**info, "duration": 600})
    audio.write_bytes(b"not audio")
    with pytest.raises(subprocess.CalledProcessError):
        verify_audio(audio, info)


def test_single_server_per_data_directory(tmp_path):
    b = Backend(tmp_path)
    try:
        with pytest.raises(RuntimeError, match="data_directory_already_in_use"):
            Backend(tmp_path)
    finally:
        b.close()


def test_restart_marks_unfinished_job_interrupted(tmp_path):
    b = Backend(tmp_path)
    job_id = "a" * 32
    b.db.execute("INSERT INTO jobs VALUES (?,?,?,'running','{}',?)", (job_id, "old", "{}", time.time()))
    b.db.commit()
    b.close()
    b = Backend(tmp_path)
    try:
        assert b.status(job_id)["status"] == "interrupted"
        assert b.status(job_id)["error"] == "server_restarted"
    finally:
        b.close()


def test_fixture_acquisition_to_real_analysis_pipeline(tmp_path):
    def fixture_runner(payload, timeout):
        if payload["action"] == "analyze":
            return execute(payload)
        root = Path(payload["job_dir"])
        audio = root / "fixture.wav"
        samples = (0.5 * np.sin(2 * np.pi * 440 * np.arange(88200) / 44100)).astype(np.float32)
        wavfile.write(audio, 44100, np.column_stack([samples, samples]))
        manifest = verify_audio(audio, {"id": VIDEO, "channel_id": CHANNEL,
                                       "title": "synthetic fixture, not YouTube audio", "duration": 2})
        (root / "manifest.json").write_text(json.dumps(manifest))
        return {"stage": "decoded", "manifest": manifest, "audio_filename": audio.name}

    b = Backend(tmp_path, runner=fixture_runner)
    try:
        job = b.submit("acquire", "fixture", video_id=VIDEO, expected_channel_id=CHANNEL)
        assert wait(b, job)["status"] == "succeeded"
        analysis = b.submit("analyze", "measure-fixture", source_job_id=job["job_id"])
        result = wait(b, analysis)
        assert result["status"] == "succeeded"
        assert result["analysis"]["duration_s"] == 2
        assert len(result["analysis"]["windows"]) == 1
        assert abs(result["analysis"]["windows"][0]["spectral_centroid_hz"] - 440) < 2
    finally:
        b.close()


@pytest.mark.parametrize("changed,error", [({"channel_id": "UC" + "x" * 22}, "channel_mismatch"),
                                          ({"id": "abcdefghijk"}, "video_mismatch")])
def test_source_mismatch_stops_before_download(tmp_path, monkeypatch, changed, error):
    class FakePlayer:
        def __init__(self, options):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

        def extract_info(self, url, download):
            assert download is False
            return {"id": VIDEO, "title": "test metadata", "channel_id": CHANNEL, "duration": 600, **changed}

        def process_info(self, info):
            raise AssertionError("must not download the wrong source")

    monkeypatch.setattr("worker.GuestYoutubeDL", FakePlayer)
    result = execute({"action": "acquire", "job_dir": str(tmp_path), "video_id": VIDEO,
                      "expected_channel_id": CHANNEL})
    assert result["error"] == error


def test_local_decode_timeout_is_not_network_timeout():
    assert clean_error(subprocess.TimeoutExpired(["ffmpeg"], 120)) == "decode_or_analysis_timeout"
    assert clean_error(Exception("Sign in to confirm you’re not a bot")) == "guest_playback_denied"
    assert clean_error(Exception("HTTP Error 403: Forbidden")) == "http_forbidden"
    assert clean_error(Exception("HTTP Error 429: Too Many Requests")) == "rate_limited"


def test_guest_worker_rejects_account_inputs_before_request(monkeypatch):
    for setting in ({"cookiefile": "never-read.txt"}, {"cookiesfrombrowser": ("chrome",)},
                    {"usenetrc": True}, {"username": "fixture"},
                    {"http_headers": {"Authorization": "fixture"}},
                    {"http_headers": {"Cookie": "SID=fixture"}}):
        with pytest.raises(ValueError, match="account_authentication_disabled"):
            GuestYoutubeDL({**options(), **setting})

    # Exercise the real cookie jar; replace transport only, so no request leaves.
    from yt_dlp.networking import Request
    calls = []
    monkeypatch.setattr("yt_dlp.YoutubeDL.urlopen", lambda self, req: calls.append(req))
    with GuestYoutubeDL(options()) as ydl:
        ydl.params["http_headers"]["Authorization"] = "fixture"
        with pytest.raises(ValueError, match="account_authentication_disabled"):
            ydl.urlopen(Request("https://www.youtube.com/"))
        del ydl.params["http_headers"]["Authorization"]
        with pytest.raises(ValueError, match="account_authentication_disabled"):
            ydl.urlopen(Request("https://www.youtube.com/", headers={"Authorization": "fixture"}))
        ydl.cookiejar.set_cookie(Cookie(0, "SID", "fixture", None, False, ".youtube.com", True, True,
                                       "/", True, True, None, True, None, None, {}))
        with pytest.raises(ValueError, match="account_authentication_disabled"):
            ydl.urlopen(Request("https://www.youtube.com/"))
    assert calls == []


def test_ambient_plugins_are_disabled():
    from yt_dlp.globals import plugin_dirs
    import os
    assert plugin_dirs.value == []
    assert os.environ["YTDLP_NO_PLUGINS"] == "1"


def test_login_demand_ends_guest_attempt_without_download(tmp_path, monkeypatch):
    calls = []

    class Denied:
        def __init__(self, settings):
            assert settings["cookiefile"] is None
            assert settings["cookiesfrombrowser"] is None
            assert settings["retries"] == 0
        def __enter__(self):
            return self
        def __exit__(self, *args):
            pass
        def extract_info(self, *args, **kwargs):
            calls.append("resolve")
            raise RuntimeError("Sign in to confirm you’re not a bot")
        def process_info(self, info):
            raise AssertionError("download must not start")

    monkeypatch.setattr("worker.GuestYoutubeDL", Denied)
    result = execute({"action": "acquire", "job_dir": str(tmp_path), "video_id": VIDEO,
                      "expected_channel_id": CHANNEL})
    assert result["error"] == "guest_playback_denied"
    assert result["audio_retrieved"] is False
    assert calls == ["resolve"]


def test_unknown_length_download_stops_at_byte_limit(tmp_path, monkeypatch):
    import functools
    from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

    # No Content-Length: yt-dlp's declared filesize guard cannot help here.
    source_dir = tmp_path / "http"
    source_dir.mkdir()
    (source_dir / "large.bin").write_bytes(b"x" * 65536)
    class Handler(SimpleHTTPRequestHandler):
        def send_header(self, name, value):
            if name.lower() != "content-length":
                super().send_header(name, value)
        def log_message(self, *args):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(Handler, directory=str(source_dir)))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    root = tmp_path / "job"
    root.mkdir()
    original = GuestYoutubeDL
    class FixtureTransfer(original):
        def extract_info(self, *args, **kwargs):
            return {"id": VIDEO, "title": "HTTP fixture", "channel_id": CHANNEL,
                    "duration": 2, "url": f"http://127.0.0.1:{server.server_port}/large.bin",
                    "format_id": "fixture", "ext": "bin", "protocol": "http"}

    monkeypatch.setattr("worker.GuestYoutubeDL", FixtureTransfer)
    monkeypatch.setattr("worker.MAX_AUDIO_BYTES", 1024)
    try:
        result = execute({"action": "acquire", "job_dir": str(root), "video_id": VIDEO,
                          "expected_channel_id": CHANNEL})
        assert result["error"] == "audio_size_limit_exceeded"
        assert result["audio_retrieved"] is False
        assert not (root / "manifest.json").exists()
    finally:
        server.shutdown()
        server.server_close()
        thread.join()


def test_analysis_rechecks_source_before_running(tmp_path):
    calls = []
    def runner(payload, timeout):
        calls.append(payload["action"])
        root = Path(payload["job_dir"])
        audio = root / "fixture.wav"
        wavfile.write(audio, 16000, np.zeros(32000, dtype=np.int16))
        manifest = verify_audio(audio, {"id": VIDEO, "channel_id": CHANNEL, "duration": 2})
        (root / "manifest.json").write_text(json.dumps(manifest))
        return {"stage": "decoded", "manifest": manifest, "audio_filename": audio.name}

    b = Backend(tmp_path, runner=runner)
    try:
        source = wait(b, b.submit("acquire", "first", video_id=VIDEO, expected_channel_id=CHANNEL))
        assert source["status"] == "succeeded"
        (tmp_path / source["job_id"] / source["audio_filename"]).write_bytes(b"changed")
        result = wait(b, b.submit("analyze", "changed", source_job_id=source["job_id"]))
        assert result["error"] == "source_audio_changed"
        assert calls == ["acquire"]
    finally:
        b.close()


def test_direct_requests_share_worker_limit(tmp_path):
    b = Backend(tmp_path, runner=lambda *_: {"unexpected": True})
    try:
        assert b.execution_slots.acquire(blocking=False)
        assert b.execution_slots.acquire(blocking=False)
        assert b.direct("fetch", video_id=VIDEO) == {"error": "worker_busy"}
        b.execution_slots.release()
        b.execution_slots.release()
    finally:
        b.close()


def test_storage_failure_terminates_job(tmp_path, monkeypatch):
    b = Backend(tmp_path, runner=lambda *_: {"unexpected": True})
    original_mkdir = Path.mkdir
    def full_disk(path, *args, **kwargs):
        if path.parent == tmp_path:
            raise OSError("synthetic storage failure")
        return original_mkdir(path, *args, **kwargs)
    monkeypatch.setattr(Path, "mkdir", full_disk)
    try:
        result = wait(b, b.submit("acquire", "storage", video_id=VIDEO, expected_channel_id=CHANNEL))
        assert result["status"] == "failed"
        assert result["error"] == "job_storage_failed"
    finally:
        b.close()
