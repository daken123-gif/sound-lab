"""Offline regression tests for the live-check gate, not YouTube acquisition evidence."""
import asyncio
from contextlib import asynccontextmanager, contextmanager
from copy import deepcopy
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

import smoke_mcp as smoke

ACQUIRE_ID = "a" * 32
ANALYSIS_ID = "b" * 32
DIGEST = "c" * 64


def acquired():
    return {"job_id": ACQUIRE_ID, "status": "succeeded", "stage": "decoded", "manifest": {
        "state": "full-source-decoded", "video_id": smoke.VIDEO, "channel_id": smoke.CHANNEL,
        "sha256": DIGEST, "decoded_duration_s": 600, "audio_bytes": 1024,
    }}


def analyzed():
    return {"job_id": ANALYSIS_ID, "status": "succeeded", "stage": "analyzed", "analysis": {
        "source_sha256": DIGEST, "duration_s": 600,
        "windows": [{"start_s": start, "end_s": start + 30} for start in range(0, 600, 30)],
    }}


class FakeSession:
    def __init__(self, acquisition=None, analysis=None, acquisition_tool_error=False):
        self.acquisition = deepcopy(acquisition if acquisition is not None else acquired())
        self.analysis = deepcopy(analysis if analysis is not None else analyzed())
        self.acquisition_tool_error = acquisition_tool_error
        self.calls = []

    async def __aenter__(self):
        return self

    async def __aexit__(self, *_):
        return False

    async def initialize(self):
        pass

    async def list_tools(self):
        return SimpleNamespace(tools=[SimpleNamespace(name=name, annotations=SimpleNamespace(
            readOnlyHint=name in {"search", "fetch", "job_status"})) for name in smoke.TOOLS])

    async def call_tool(self, name, arguments):
        self.calls.append((name, arguments))
        if name == "fetch" or name == "acquire_audio" and self.acquisition_tool_error:
            return SimpleNamespace(isError=True, structuredContent=None,
                                   content="Cookie=PRIVATE; https://cdn.example/audio?sig=SIGNED_SECRET")
        if name == "acquire_audio":
            job = self.acquisition
        elif name == "analyze_audio":
            assert arguments["source_job_id"] == ACQUIRE_ID
            job = self.analysis
        else:
            raise AssertionError("Unexpected tool call")
        return SimpleNamespace(isError=False, structuredContent=deepcopy(job))


@pytest.fixture
def attach(monkeypatch):
    def use(session):
        @asynccontextmanager
        async def transport(url, **kwargs):
            yield None, None, None

        monkeypatch.setattr(smoke, "streamablehttp_client", transport)
        monkeypatch.setattr(smoke, "ClientSession", lambda *_: session)
        return session
    return use


@pytest.mark.parametrize("state", ["failed", "interrupted"])
def test_failed_acquisition_exits_nonzero_and_does_not_start_analysis(tmp_path, attach, state):
    session = attach(FakeSession(acquisition={"job_id": ACQUIRE_ID, "status": state,
                                             "stage": "stream_url_resolved", "error": "network_timeout"}))
    path = tmp_path / "report.json"
    assert smoke.cli(["--live", "--report", str(path)]) == 1
    report = json.loads(path.read_text())
    assert report["status"] == "failed"
    assert report["phase"] == "acquisition"
    assert report["acquisition"]["status"] == state
    assert report["acquisition"]["error"] == "network_timeout"
    assert report["analysis"]["status"] == "not_requested"
    assert [name for name, _ in session.calls].count("acquire_audio") == 1
    assert not any(name == "analyze_audio" for name, _ in session.calls)


def test_live_success_requires_analysis_of_the_same_complete_audio(tmp_path, attach):
    session = attach(FakeSession())
    path = tmp_path / "report.json"
    assert smoke.cli(["--live", "--report", str(path)]) == 0
    report = json.loads(path.read_text())
    assert report["status"] == "passed"
    assert report["acquisition"]["verified"] is True
    assert report["analysis"]["verified"] is True
    assert report["acquisition"]["sha256"] == report["analysis"]["source_sha256"] == DIGEST
    assert report["analysis"]["window_count"] == 20
    assert [name for name, _ in session.calls] == ["fetch", "acquire_audio", "analyze_audio"]


def test_other_audio_hash_is_failure_after_analysis_not_analysis_unreached(tmp_path, attach):
    job = analyzed()
    job["analysis"]["source_sha256"] = "d" * 64
    attach(FakeSession(analysis=job))
    path = tmp_path / "report.json"
    assert smoke.cli(["--live", "--report", str(path)]) == 1
    report = json.loads(path.read_text())
    assert report["phase"] == "analysis"
    assert report["acquisition"]["verified"] is True
    assert report["analysis"]["job_id"] == ANALYSIS_ID
    assert report["analysis"]["status"] == "succeeded"
    assert report["error"] == "analysis_source_hash_mismatch"
    assert not report["analysis"].get("verified", False)


@pytest.mark.parametrize("damage,expected", [
    ("gap", "analysis_coverage_missing"),
    ("missing_tail", "analysis_coverage_missing"),
    ("wrong_duration", "analysis_duration_mismatch"),
])
def test_incomplete_analysis_does_not_pass(tmp_path, attach, damage, expected):
    job = analyzed()
    if damage == "gap":
        job["analysis"]["windows"][1]["start_s"] += 1
    elif damage == "missing_tail":
        job["analysis"]["windows"].pop()
    else:
        job["analysis"]["duration_s"] -= 10
    attach(FakeSession(analysis=job))
    path = tmp_path / "report.json"
    assert smoke.cli(["--live", "--report", str(path)]) == 1
    assert json.loads(path.read_text())["error"] == expected


def test_remote_error_text_never_reaches_stdout_or_report(tmp_path, attach, capsys):
    attach(FakeSession(acquisition_tool_error=True))
    path = tmp_path / "report.json"
    assert smoke.cli(["--live", "--report", str(path)]) == 1
    output = capsys.readouterr().out + path.read_text()
    assert "PRIVATE" not in output and "SIGNED_SECRET" not in output and "cdn.example" not in output
    assert json.loads(path.read_text())["error"] == "mcp_tool_failed"


def test_unknown_worker_error_is_redacted(tmp_path, attach, capsys):
    attach(FakeSession(acquisition={"job_id": ACQUIRE_ID, "status": "failed",
                                   "error": "Cookie=PRIVATE; https://cdn.example/?sig=SECRET"}))
    path = tmp_path / "report.json"
    assert smoke.cli(["--live", "--report", str(path)]) == 1
    output = capsys.readouterr().out + path.read_text()
    assert "PRIVATE" not in output and "SECRET" not in output
    assert json.loads(path.read_text())["acquisition"]["error"] == "worker_error_redacted"


def test_transport_only_mode_never_requests_audio(tmp_path, attach):
    session = attach(FakeSession())
    path = tmp_path / "report.json"
    assert smoke.cli(["--report", str(path)]) == 0
    report = json.loads(path.read_text())
    assert report["live_requested"] is False
    assert report["acquisition"]["status"] == report["analysis"]["status"] == "not_requested"
    assert [name for name, _ in session.calls] == ["fetch"]


@pytest.mark.parametrize("retain", [False, True])
def test_spawn_retains_only_explicit_data_directory(tmp_path, attach, monkeypatch, retain):
    attach(FakeSession())
    used = []

    @contextmanager
    def server(data):
        data = Path(data)
        data.mkdir(parents=True, exist_ok=True)
        (data / "job-fixture").write_text("offline test job")
        used.append(data)
        yield "http://127.0.0.1:54321/mcp"

    monkeypatch.setattr(smoke, "spawned_server", server)
    path = tmp_path / "report.json"
    arguments = ["--spawn", "--report", str(path)]
    if retain:
        arguments += ["--data-dir", str(tmp_path / "retained-jobs")]
    assert smoke.cli(arguments) == 0
    assert used[0].exists() is retain
    if retain:
        assert (used[0] / "job-fixture").is_file()
    assert json.loads(path.read_text())["artifact_retention"] == ("retained" if retain else "temporary")


def test_data_directory_cannot_claim_to_control_an_existing_server(tmp_path):
    with pytest.raises(SystemExit) as error:
        smoke.cli(["--data-dir", str(tmp_path)])
    assert error.value.code == 2


def test_poll_wait_timeout_is_failure_with_the_running_job_preserved():
    report = {}
    with pytest.raises(smoke.SmokeFailure, match="job_wait_deadline_exceeded"):
        asyncio.run(smoke.wait_job(None, {"job_id": ACQUIRE_ID, "status": "running"},
                                  report, lambda: None, wait_seconds=0))
    assert report == {"job_id": ACQUIRE_ID, "status": "running"}


def test_spawn_uses_the_allocated_port_for_both_server_and_client(monkeypatch, tmp_path):
    calls = []

    class Socket:
        def __enter__(self):
            return self

        def __exit__(self, *_):
            pass

        def bind(self, address):
            assert address == ("127.0.0.1", 0)

        def getsockname(self):
            return ("127.0.0.1", 54321)

    class Process:
        pid = 12345

        def poll(self):
            return None

        def wait(self, timeout):
            return 0

    def start(arguments, **kwargs):
        calls.append(arguments)
        assert kwargs["stdout"] == kwargs["stderr"] == smoke.subprocess.DEVNULL
        return Process()

    def connect(address, timeout):
        assert address == ("127.0.0.1", 54321)
        return Socket()

    monkeypatch.setattr(smoke.socket, "socket", Socket)
    monkeypatch.setattr(smoke.socket, "create_connection", connect)
    monkeypatch.setattr(smoke.subprocess, "Popen", start)
    monkeypatch.setattr(smoke.os, "killpg", lambda *_: None)
    with smoke.spawned_server(tmp_path) as url:
        assert url == "http://127.0.0.1:54321/mcp"
    arguments = calls[0]
    assert arguments[arguments.index("--port") + 1] == "54321"


def test_exception_group_keeps_the_specific_failure_without_remote_message():
    error = ExceptionGroup("PRIVATE", [smoke.SmokeFailure("analysis_source_hash_mismatch")])
    assert smoke.failure_code(error) == "analysis_source_hash_mismatch"
