"""Verify local MCP; --live must acquire, decode and analyze the chosen audio."""
import argparse
import asyncio
from contextlib import contextmanager, nullcontext, suppress
from datetime import datetime, timezone
import json
import math
import os
from pathlib import Path
import re
import signal
import socket
import subprocess
import sys
import tempfile
import time
from urllib.parse import urlsplit
import uuid

import httpx
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

VIDEO = "mdhtm6qjmhU"
CHANNEL = "UCBUAlfIrcw1f0c4qGrYn3xA"
TOOLS = {"search", "fetch", "acquire_audio", "job_status", "analyze_audio"}
STATES = {"queued", "running", "succeeded", "failed", "interrupted"}
STAGES = {"resolving", "metadata_observed", "stream_url_resolved", "downloading",
          "audio_downloaded", "decoding", "decoded", "analyzing", "analyzed"}
SAFE_WORKER_ERRORS = {
    "network_timeout", "tls_verification_failed", "access_requirement_or_denial",
    "source_unavailable", "worker_failure", "worker_deadline_exceeded",
    "worker_process_failed", "invalid_worker_response", "server_restarted",
    "decode_or_analysis_failed", "decode_timeout", "analysis_timeout", "probe_timeout",
    "login_required", "bot_verification_required", "http_forbidden",
    "po_token_required", "no_audio_file", "duration_unverified",
    "incomplete_or_different_duration", "video_mismatch", "channel_mismatch",
    "unsupported_live_or_duration", "completion_evidence_missing",
    "audio_evidence_missing", "audio_hash_mismatch", "decode_evidence_missing",
    "analysis_evidence_missing", "job_internal_error", "audio_size_limit_exceeded",
    "guest_playback_denied", "authentication_required", "account_required_content",
    "playback_token_required", "drm_protected", "account_authentication_disabled",
    "rate_limited", "decode_or_analysis_timeout", "source_audio_changed",
    "job_storage_failed",
}


class SmokeFailure(Exception):
    """Only locally assigned error codes, never remote log text."""


def new_report(live, retention="server_managed"):
    return {"schema_version": 1, "started_at": datetime.now(timezone.utc).isoformat(),
            "live_requested": live, "status": "running", "phase": "mcp",
            "artifact_retention": retention, "checks": {},
            "acquisition": {"status": "not_requested"},
            "analysis": {"status": "not_requested"}}


def write_report(report, path):
    if path is None:
        return
    path = Path(path)
    temporary = path.with_name(path.name + ".tmp")
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
        temporary.replace(path)
    except OSError:
        raise SmokeFailure("report_write_failed") from None


def failure_code(exc):
    # MCP transports may wrap the original failure in an ExceptionGroup.
    if isinstance(exc, SmokeFailure):
        return exc.args[0]
    for child in getattr(exc, "exceptions", ()):
        code = failure_code(child)
        if code != "mcp_transport_failed":
            return code
    return "mcp_transport_failed"


def validate_url(url):
    parsed = urlsplit(url)
    if (parsed.scheme not in {"http", "https"}
            or parsed.hostname not in {"127.0.0.1", "localhost", "::1"}
            or parsed.username is not None or parsed.password is not None
            or parsed.query or parsed.fragment):
        raise SmokeFailure("invalid_local_endpoint")


async def call_job_tool(session, name, arguments):
    response = await session.call_tool(name, arguments)
    if response.isError:
        raise SmokeFailure("mcp_tool_failed")
    if not isinstance(response.structuredContent, dict):
        raise SmokeFailure("invalid_job_response")
    return response.structuredContent


def record_job(target, job):
    job_id, status = job.get("job_id"), job.get("status")
    if (not isinstance(job_id, str) or not re.fullmatch(r"[a-f0-9]{32}", job_id)
            or not isinstance(status, str) or status not in STATES
            or target.get("job_id", job_id) != job_id):
        raise SmokeFailure("invalid_job_response")
    target.update(job_id=job_id, status=status)
    if "stage" in job:
        stage = job["stage"]
        target["stage"] = stage if isinstance(stage, str) and stage in STAGES else "unrecognized"
    if job.get("error"):
        error = job["error"]
        target["error"] = error if isinstance(error, str) and error in SAFE_WORKER_ERRORS else "worker_error_redacted"


async def wait_job(session, job, target, checkpoint, wait_seconds=210, poll_seconds=2):
    deadline = time.monotonic() + wait_seconds
    while True:
        previous = dict(target)
        record_job(target, job)
        if target != previous:
            checkpoint()
        if job["status"] not in {"queued", "running"}:
            return job
        if time.monotonic() >= deadline:
            raise SmokeFailure("job_wait_deadline_exceeded")
        await asyncio.sleep(poll_seconds)
        job = await call_job_tool(session, "job_status", {"job_id": target["job_id"]})


def positive_number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value) and value > 0


def verify_acquisition(job, target):
    if job["status"] != "succeeded" or job.get("error"):
        raise SmokeFailure("acquisition_failed")
    manifest = job.get("manifest")
    if (job.get("stage") != "decoded" or not isinstance(manifest, dict)
            or manifest.get("state") != "full-source-decoded"
            or manifest.get("video_id") != VIDEO or manifest.get("channel_id") != CHANNEL
            or not isinstance(manifest.get("sha256"), str)
            or not re.fullmatch(r"[a-f0-9]{64}", manifest["sha256"])
            or not positive_number(manifest.get("decoded_duration_s"))
            or type(manifest.get("audio_bytes")) is not int or manifest["audio_bytes"] <= 0):
        raise SmokeFailure("acquisition_evidence_missing")
    target.update(verified=True, sha256=manifest["sha256"], audio_bytes=manifest["audio_bytes"],
                  decoded_duration_s=manifest["decoded_duration_s"], video_id=VIDEO, channel_id=CHANNEL)
    return manifest


def verify_analysis(job, manifest, target):
    if job["status"] != "succeeded" or job.get("error"):
        raise SmokeFailure("analysis_failed")
    analysis = job.get("analysis")
    if job.get("stage") != "analyzed" or not isinstance(analysis, dict):
        raise SmokeFailure("analysis_evidence_missing")
    if analysis.get("source_sha256") != manifest["sha256"]:
        raise SmokeFailure("analysis_source_hash_mismatch")
    duration = analysis.get("duration_s")
    if not positive_number(duration) or abs(duration - manifest["decoded_duration_s"]) > 0.1:
        raise SmokeFailure("analysis_duration_mismatch")
    windows = analysis.get("windows")
    if not isinstance(windows, list) or not windows:
        raise SmokeFailure("analysis_coverage_missing")
    end = 0.0
    for window in windows:
        if not isinstance(window, dict):
            raise SmokeFailure("analysis_coverage_missing")
        start, stop = window.get("start_s"), window.get("end_s")
        if (not isinstance(start, (int, float)) or isinstance(start, bool) or not math.isfinite(start)
                or not positive_number(stop) or abs(start - end) > 1e-6 or stop <= start):
            raise SmokeFailure("analysis_coverage_missing")
        end = stop
    if abs(end - duration) > 1e-6:
        raise SmokeFailure("analysis_coverage_missing")
    target.update(verified=True, source_sha256=analysis["source_sha256"],
                  duration_s=duration, window_count=len(windows))


async def verify_session(session, report, checkpoint):
    await session.initialize()
    listing = await session.list_tools()
    tools = {tool.name: tool for tool in listing.tools}
    if (not TOOLS.issubset(tools) or not tools["search"].annotations.readOnlyHint
            or not tools["fetch"].annotations.readOnlyHint
            or tools["acquire_audio"].annotations.readOnlyHint):
        raise SmokeFailure("mcp_tool_contract_failed")
    report["checks"]["mcp_initialize"] = "passed"
    invalid = await session.call_tool("fetch", {"id": "../etc/passwd"})
    if not invalid.isError:
        raise SmokeFailure("invalid_id_was_accepted")
    report["checks"]["invalid_id_rejected"] = True
    checkpoint()
    if not report["live_requested"]:
        return

    report["phase"] = "acquisition"
    report["acquisition"]["status"] = "requesting"
    checkpoint()
    job = await call_job_tool(session, "acquire_audio", {
        "video_id": VIDEO, "expected_channel_id": CHANNEL,
        "request_key": "smoke-acquire-" + uuid.uuid4().hex,
    })
    job = await wait_job(session, job, report["acquisition"], checkpoint)
    manifest = verify_acquisition(job, report["acquisition"])
    checkpoint()

    report["phase"] = "analysis"
    report["analysis"]["status"] = "requesting"
    checkpoint()
    analysis_job = await call_job_tool(session, "analyze_audio", {
        "source_job_id": job["job_id"], "request_key": "smoke-analyze-" + uuid.uuid4().hex,
    })
    analysis_job = await wait_job(session, analysis_job, report["analysis"], checkpoint)
    verify_analysis(analysis_job, manifest, report["analysis"])


async def main(url, live, report_path=None, retention="server_managed"):
    report = new_report(live, retention)

    def checkpoint():
        write_report(report, report_path)
        print(json.dumps(report, ensure_ascii=False), flush=True)

    def local_client(**kwargs):
        return httpx.AsyncClient(**kwargs, trust_env=False)

    try:
        validate_url(url)
        async with streamablehttp_client(url, httpx_client_factory=local_client) as (read, write, _):
            async with ClientSession(read, write) as session:
                await verify_session(session, report, checkpoint)
        report.update(status="passed", phase="complete")
    except Exception as exc:
        report.update(status="failed", error=failure_code(exc))
    report["finished_at"] = datetime.now(timezone.utc).isoformat()
    try:
        checkpoint()
    except SmokeFailure:
        report.update(status="failed", error="report_write_failed")
        print(json.dumps(report, ensure_ascii=False), flush=True)
    return report


@contextmanager
def spawned_server(data):
    # Ask the OS for an unused port instead of connecting to an unrelated :8841 server.
    with socket.socket() as reservation:
        reservation.bind(("127.0.0.1", 0))
        port = reservation.getsockname()[1]
    proc = subprocess.Popen([
        sys.executable, str(Path(__file__).with_name("server.py")), "--transport",
        "streamable-http", "--port", str(port), "--data-dir", str(data),
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
    try:
        deadline = time.monotonic() + 15
        while True:
            if proc.poll() is not None:
                raise SmokeFailure("server_start_failed")
            try:
                with socket.create_connection(("127.0.0.1", port), timeout=0.1):
                    break
            except OSError:
                if time.monotonic() >= deadline:
                    raise SmokeFailure("server_start_deadline_exceeded")
                time.sleep(0.05)
        yield f"http://127.0.0.1:{port}/mcp"
    finally:
        if proc.poll() is None:
            with suppress(ProcessLookupError):
                os.killpg(proc.pid, signal.SIGTERM)
            # The backend reaps its worker's separate process group at its 180 s deadline.
            # Keep the parent alive for that cleanup if the MCP connection ended early.
            cleanup_deadline = time.monotonic() + 195
            while True:
                try:
                    proc.wait(timeout=1)
                    break
                except subprocess.TimeoutExpired:
                    if time.monotonic() >= cleanup_deadline:
                        with suppress(ProcessLookupError):
                            os.killpg(proc.pid, signal.SIGKILL)
                        proc.wait(timeout=5)
                        break


def cli(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default="http://127.0.0.1:8841/mcp")
    parser.add_argument("--live", action="store_true", help="Require full acquisition and analysis success")
    parser.add_argument("--spawn", action="store_true", help="Run a local server on an unused port")
    parser.add_argument("--data-dir", type=Path, help="With --spawn, retain job files here after exit")
    parser.add_argument("--report", type=Path, help="Write a redacted JSON verification report, including failures")
    args = parser.parse_args(argv)
    if args.data_dir is not None and not args.spawn:
        parser.error("--data-dir requires --spawn; an existing server owns its data directory")
    retention = "retained" if args.data_dir is not None else "temporary" if args.spawn else "server_managed"
    try:
        if args.spawn:
            data_context = nullcontext(args.data_dir.resolve()) if args.data_dir is not None else tempfile.TemporaryDirectory(
                prefix="smoke-", dir=Path(__file__).parent)
            with data_context as data:
                with spawned_server(data) as url:
                    report = asyncio.run(main(url, args.live, args.report, retention))
        else:
            report = asyncio.run(main(args.url, args.live, args.report, retention))
    except Exception as exc:
        report = new_report(args.live, retention)
        report.update(status="failed", phase="startup", error=failure_code(exc))
        report["finished_at"] = datetime.now(timezone.utc).isoformat()
        try:
            write_report(report, args.report)
        except SmokeFailure:
            report["error"] = "report_write_failed"
        print(json.dumps(report, ensure_ascii=False), flush=True)
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    sys.exit(cli())
