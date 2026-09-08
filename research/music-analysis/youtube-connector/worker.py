"""Isolated YouTube worker. Standard public playback only; private bytes stay here."""
import hashlib
import json
import math
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import yt_dlp

VIDEO = re.compile(r"[A-Za-z0-9_-]{11}\Z")
CHANNEL = re.compile(r"UC[A-Za-z0-9_-]{22}\Z")


def canonical(video_id):
    if not VIDEO.fullmatch(video_id):
        raise ValueError("invalid_video_id")
    return "https://www.youtube.com/watch?v=" + video_id


def clean_error(error):
    message = str(error)
    if message in {"duration_unverified", "incomplete_or_different_duration", "invalid_video_id", "invalid_query"}:
        return message
    if isinstance(error, subprocess.CalledProcessError):
        return "decode_or_analysis_failed"
    lower = message.lower()
    if "timed out" in lower or "timeout" in lower:
        return "network_timeout"
    if "certificate" in lower:
        return "tls_verification_failed"
    if any(x in lower for x in ["sign in", "login", "private video", "403", "po token", "not a bot"]):
        return "access_requirement_or_denial"
    if "unavailable" in lower:
        return "source_unavailable"
    # Never return signed CDN URLs, cookies, IPs or arbitrary external log text.
    return "worker_failure"


class QuietLogger:
    def debug(self, message):
        pass

    warning = debug
    error = debug


def options():
    return {
        "quiet": True, "no_warnings": True, "logger": QuietLogger(),
        "cachedir": False, "noplaylist": True, "socket_timeout": 15,
        "retries": 0, "extractor_retries": 0,
        "js_runtimes": {"node": {}},
        "compat_opts": {"no-certifi"} if os.environ.get("YOUTUBE_SYSTEM_CA", "1") == "1" else set(),
    }


def metadata(info):
    video_id = info["id"]
    return {
        "id": video_id, "title": info.get("title", video_id),
        "url": canonical(video_id), "channel": info.get("channel"),
        "channel_id": info.get("channel_id"), "duration_s": info.get("duration"),
        "description": (info.get("description") or "")[:8000],
        "state": "metadata_observed", "audio_retrieved": False,
    }


def progress(root, stage, **details):
    target = root / "progress.json"
    temporary = root / "progress.tmp"
    temporary.write_text(json.dumps({"stage": stage, **details}, ensure_ascii=False))
    temporary.replace(target)


def verify_audio(path, info):
    probe = json.loads(subprocess.check_output([
        "ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(path)
    ], timeout=30, stderr=subprocess.PIPE))
    audio = next(s for s in probe["streams"] if s["codec_type"] == "audio")
    pcm = path.parent / "verification.pcm"
    try:
        subprocess.run([
            "ffmpeg", "-v", "error", "-xerror", "-i", str(path), "-map", "0:a:0",
            "-ac", "1", "-ar", "16000", "-f", "s16le", "-y", str(pcm)
        ], check=True, timeout=120, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        duration = pcm.stat().st_size / 32000
    finally:
        pcm.unlink(missing_ok=True)
    expected = info.get("duration")
    if not expected or not math.isfinite(float(expected)) or duration <= 0:
        raise ValueError("duration_unverified")
    if abs(duration - float(expected)) > 2:
        raise ValueError("incomplete_or_different_duration")
    with path.open("rb") as handle:
        digest = hashlib.file_digest(handle, "sha256").hexdigest()
    return {
        "provider": "youtube", "source_page": canonical(info["id"]),
        "video_id": info["id"], "channel_id": info.get("channel_id"),
        "title": info.get("title"), "sha256": digest,
        "audio_bytes": path.stat().st_size,
        "codec": audio["codec_name"], "sample_rate": int(audio["sample_rate"]),
        "channels": audio["channels"], "page_duration_s": expected,
        "decoded_duration_s": duration, "state": "full-source-decoded",
        "retrieved_at": datetime.now(timezone.utc).isoformat(),
        "master_identity_vs_preview": "unverified",
    }


def execute(request):
    action = request["action"]
    root = Path(request["job_dir"]) if "job_dir" in request else None
    if action == "analyze":
        script = Path(__file__).resolve().parent.parent / "analyze_source_windows.py"
        output = root / "analysis.json"
        progress(root, "analyzing")
        subprocess.run([
            sys.executable, str(script), request["audio_path"],
            "--manifest", request["manifest_path"], "--output", str(output)
        ], check=True, timeout=120, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        return {"stage": "analyzed", "analysis": json.loads(output.read_text())}
    opts = options()
    if action == "search":
        query = request["query"].strip()
        if not 1 <= len(query) <= 200:
            raise ValueError("invalid_query")
        opts["extract_flat"] = "in_playlist"
        with yt_dlp.YoutubeDL(opts) as ydl:
            result = ydl.extract_info("ytsearch5:" + query, download=False)
        return {"results": [
            {"id": e["id"], "title": e.get("title", e["id"]), "url": canonical(e["id"])}
            for e in result.get("entries", []) if e and VIDEO.fullmatch(e.get("id", ""))
        ]}
    url = canonical(request["video_id"])
    if action == "acquire":
        progress(root, "resolving")
        opts.update({"format": "bestaudio", "outtmpl": str(root / "audio.%(ext)s"),
                     "max_filesize": 256 * 1024 * 1024})
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=False)
        meta = metadata(info)
        if action == "fetch":
            return {"id": meta["id"], "title": meta["title"], "url": meta["url"],
                    "text": meta["description"], "metadata": {k: v for k, v in meta.items() if k != "description"}}
        if info.get("id") != request["video_id"]:
            return {"stage": "metadata_observed", "error": "video_mismatch", "metadata": meta}
        if info.get("channel_id") != request["expected_channel_id"]:
            return {"stage": "metadata_observed", "error": "channel_mismatch", "metadata": meta}
        if info.get("is_live") or not info.get("duration") or float(info["duration"]) > 3600:
            return {"stage": "metadata_observed", "error": "unsupported_live_or_duration", "metadata": meta}
        progress(root, "stream_url_resolved", metadata=meta)

        def hook(event):
            if event["status"] == "finished":
                progress(root, "audio_downloaded", metadata=meta)

        ydl.add_progress_hook(hook)
        # URLs are resolved afresh for this job and are never exposed by an MCP tool.
        ydl.process_info(info)
        path = Path(ydl.prepare_filename(info))
    if not path.is_file() or path.stat().st_size == 0:
        return {"stage": "stream_url_resolved", "error": "no_audio_file"}
    progress(root, "decoding", metadata=meta)
    manifest = verify_audio(path, info)
    (root / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2))
    return {"stage": "decoded", "manifest": manifest, "audio_filename": path.name}


if __name__ == "__main__":
    try:
        answer = execute(json.load(sys.stdin))
    except Exception as exc:
        answer = {"error": clean_error(exc)}
    print(json.dumps(answer, ensure_ascii=False))
