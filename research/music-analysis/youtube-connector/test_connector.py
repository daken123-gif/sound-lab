import json
import subprocess
import time
from pathlib import Path

import pytest
import numpy as np
from scipy.io import wavfile

from backend import Backend
from worker import canonical, clean_error, verify_audio, execute

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

    monkeypatch.setattr("worker.yt_dlp.YoutubeDL", FakePlayer)
    result = execute({"action": "acquire", "job_dir": str(tmp_path), "video_id": VIDEO,
                      "expected_channel_id": CHANNEL})
    assert result["error"] == error
