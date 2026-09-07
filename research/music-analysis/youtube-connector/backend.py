"""Bounded, persistent jobs. Failed transfers never become acquired audio."""
import hashlib
import fcntl
import json
import os
import re
import signal
import sqlite3
import subprocess
import sys
import threading
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from worker import CHANNEL, canonical


def run_worker(payload, timeout):
    proc = subprocess.Popen(
        [sys.executable, str(Path(__file__).with_name("worker.py"))],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        text=True, start_new_session=True,
    )
    try:
        stdout, _ = proc.communicate(json.dumps(payload), timeout=timeout)
    except subprocess.TimeoutExpired:
        os.killpg(proc.pid, signal.SIGKILL)
        proc.communicate()
        return {"error": "worker_deadline_exceeded"}
    if proc.returncode:
        return {"error": "worker_process_failed"}
    try:
        return json.loads(stdout)
    except (ValueError, TypeError):
        return {"error": "invalid_worker_response"}


class Backend:
    def __init__(self, root, runner=run_worker, deadline=180):
        self.root = Path(root).resolve()
        self.root.mkdir(parents=True, exist_ok=True)
        self.process_lock = (self.root / "server.lock").open("a")
        try:
            fcntl.flock(self.process_lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            self.process_lock.close()
            raise RuntimeError("data_directory_already_in_use")
        self.lock = threading.RLock()
        self.runner, self.deadline = runner, deadline
        self.pool = ThreadPoolExecutor(max_workers=2, thread_name_prefix="youtube")
        self.db = sqlite3.connect(self.root / "jobs.sqlite", check_same_thread=False)
        self.db.execute("CREATE TABLE IF NOT EXISTS jobs (id TEXT PRIMARY KEY, key TEXT UNIQUE, payload TEXT, status TEXT, result TEXT, created REAL)")
        self.db.execute("UPDATE jobs SET status='interrupted', result=? WHERE status IN ('queued','running')",
                        (json.dumps({"error": "server_restarted"}),))
        self.db.commit()

    def direct(self, action, **kwargs):
        return self.runner({"action": action, **kwargs}, min(self.deadline, 75))

    def submit(self, action, request_key, **kwargs):
        if not re.fullmatch(r"[A-Za-z0-9_-]{1,80}", request_key):
            raise ValueError("invalid_request_key")
        if action == "acquire":
            canonical(kwargs["video_id"])
            if not CHANNEL.fullmatch(kwargs["expected_channel_id"]):
                raise ValueError("invalid_channel_id")
        elif action == "analyze":
            source = self.status(kwargs["source_job_id"])
            if source["status"] != "succeeded" or source.get("stage") != "decoded":
                raise ValueError("source_not_decoded")
        else:
            raise ValueError("unsupported_action")
        payload = {"action": action, **kwargs}
        encoded = json.dumps(payload, sort_keys=True)
        with self.lock:
            existing = self.db.execute("SELECT id,payload FROM jobs WHERE key=?", (request_key,)).fetchone()
            if existing:
                if existing[1] != encoded:
                    raise ValueError("request_key_conflict")
                return self.status(existing[0])
            active = self.db.execute("SELECT count(*) FROM jobs WHERE status IN ('queued','running')").fetchone()[0]
            if active >= 8:
                raise ValueError("queue_full")
            job_id = uuid.uuid4().hex
            self.db.execute("INSERT INTO jobs VALUES (?,?,?,'queued','{}',?)", (job_id, request_key, encoded, time.time()))
            self.db.commit()
            self.pool.submit(self._run, job_id, payload)
        return self.status(job_id)

    def _run(self, job_id, payload):
        root = self.root / job_id
        root.mkdir()
        with self.lock:
            self.db.execute("UPDATE jobs SET status='running' WHERE id=?", (job_id,))
            self.db.commit()
        try:
            request = {**payload, "job_dir": str(root)}
            if payload["action"] == "analyze":
                source_id = payload["source_job_id"]
                source = self.status(source_id)
                filename = source["audio_filename"]
                if Path(filename).name != filename:
                    raise ValueError("invalid_audio_filename")
                request.update(audio_path=str(self.root / source_id / filename),
                               manifest_path=str(self.root / source_id / "manifest.json"))
            result = self.runner(request, self.deadline)
            expected = "decoded" if payload["action"] == "acquire" else "analyzed"
            if result.get("stage") != expected and not result.get("error"):
                result["error"] = "completion_evidence_missing"
            if payload["action"] == "acquire" and not result.get("error"):
                manifest = result.get("manifest") or {}
                filename = result.get("audio_filename", "")
                audio = root / filename
                if not filename or Path(filename).name != filename or not audio.is_file():
                    result["error"] = "audio_evidence_missing"
                elif hashlib.sha256(audio.read_bytes()).hexdigest() != manifest.get("sha256"):
                    result["error"] = "audio_hash_mismatch"
                elif (not (root / "manifest.json").is_file()
                      or json.loads((root / "manifest.json").read_text()) != manifest
                      or manifest.get("state") != "full-source-decoded"
                      or manifest.get("video_id") != payload["video_id"]
                      or manifest.get("channel_id") != payload["expected_channel_id"]
                      or not manifest.get("decoded_duration_s", 0) > 0):
                    result["error"] = "decode_evidence_missing"
            if payload["action"] == "analyze" and not result.get("error"):
                report = root / "analysis.json"
                if (not report.is_file() or json.loads(report.read_text()) != result.get("analysis")
                        or result["analysis"].get("source_sha256") != source["manifest"]["sha256"]):
                    result["error"] = "analysis_evidence_missing"
            status = "failed" if result.get("error") else "succeeded"
        except Exception:
            status, result = "failed", {"error": "job_internal_error"}
        with self.lock:
            self.db.execute("UPDATE jobs SET status=?, result=? WHERE id=?", (status, json.dumps(result), job_id))
            self.db.commit()

    def status(self, job_id):
        if not re.fullmatch(r"[a-f0-9]{32}", job_id):
            raise ValueError("invalid_job_id")
        with self.lock:
            row = self.db.execute("SELECT status,result FROM jobs WHERE id=?", (job_id,)).fetchone()
        if not row:
            raise ValueError("unknown_job")
        progress = self.root / job_id / "progress.json"
        details = json.loads(progress.read_text()) if progress.exists() else {}
        return {"job_id": job_id, **details, **json.loads(row[1]), "status": row[0]}

    def close(self):
        self.pool.shutdown(wait=True)
        self.db.close()
        self.process_lock.close()
