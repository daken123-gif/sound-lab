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
from yt_dlp.globals import plugin_dirs

# This worker uses bundled extractors only. Do not import an ambient plugin that
# can read browser profiles, attach authentication, or call another service.
os.environ["YTDLP_NO_PLUGINS"] = "1"
plugin_dirs.value = []

VIDEO = re.compile(r"[A-Za-z0-9_-]{11}\Z")
CHANNEL = re.compile(r"UC[A-Za-z0-9_-]{22}\Z")
MAX_AUDIO_BYTES = 256 * 1024 * 1024
AUTH_COOKIES = {"SID", "HSID", "SSID", "APISID", "SAPISID", "LOGIN_INFO",
                "SIDCC", "__Secure-1PSID", "__Secure-3PSID", "__Secure-1PAPISID",
                "__Secure-3PAPISID", "__Secure-1PSIDTS", "__Secure-3PSIDTS",
                "__Secure-1PSIDCC", "__Secure-3PSIDCC"}


def require_guest_headers(headers):
    if any(k.lower() in {"authorization", "x-youtube-identity-token"} for k in headers):
        raise ValueError("account_authentication_disabled")
    raw_cookie = next((v for k, v in headers.items() if k.lower() == "cookie"), "")
    if any(item.split("=", 1)[0].strip() in AUTH_COOKIES for item in raw_cookie.split(";")):
        raise ValueError("account_authentication_disabled")


class GuestYoutubeDL(yt_dlp.YoutubeDL):
    """Guest requests only; no browser/profile import or account headers."""
    def __init__(self, params):
        if any(params.get(k) for k in ("cookiefile", "cookiesfrombrowser", "usenetrc",
                                     "netrc_cmd", "username", "password", "videopassword")):
            raise ValueError("account_authentication_disabled")
        require_guest_headers(params.get("http_headers") or {})
        super().__init__(params)

    def urlopen(self, request):
        # Guest cookies received during playback may remain in memory. Known
        # account cookies and account authorization must never leave this worker.
        if any(c.name in AUTH_COOKIES for c in self.cookiejar):
            raise ValueError("account_authentication_disabled")
        require_guest_headers(self.params.get("http_headers") or {})
        require_guest_headers(getattr(request, "headers", {}))
        return super().urlopen(request)


def canonical(video_id):
    if not VIDEO.fullmatch(video_id):
        raise ValueError("invalid_video_id")
    return "https://www.youtube.com/watch?v=" + video_id


def clean_error(error):
    message = str(error)
    if message in {"duration_unverified", "incomplete_or_different_duration", "invalid_video_id", "invalid_query",
                   "account_authentication_disabled", "audio_size_limit_exceeded", "invalid_action"}:
        return message
    if isinstance(error, subprocess.TimeoutExpired):
        return "decode_or_analysis_timeout"
    if isinstance(error, subprocess.CalledProcessError):
        return "decode_or_analysis_failed"
    lower = message.lower()
    if "timed out" in lower or "timeout" in lower:
        return "network_timeout"
    if "certificate" in lower:
        return "tls_verification_failed"
    if "not a bot" in lower:
        return "guest_playback_denied"
    if "429" in lower or "too many requests" in lower:
        return "rate_limited"
    if "private video" in lower or "members-only" in lower:
        return "account_required_content"
    if "sign in" in lower or "login" in lower:
        return "authentication_required"
    if "403" in lower:
        return "http_forbidden"
    if "po token" in lower:
        return "playback_token_required"
    if "drm" in lower:
        return "drm_protected"
    if "unavailable" in lower:
        return "source_unavailable"
    # Never return signed CDN URLs, cookies, IPs or arbitrary external log text.
    return "worker_failure"


class QuietLogger:
    def __init__(self):
        self.events = []

    def debug(self, message):
        return None

    def warning(self, message):
        code = clean_error(Exception(message))
        if code != "worker_failure" and code not in self.events:
            self.events.append(code)

    error = warning


def options(logger=None):
    return {
        "quiet": True, "no_warnings": False, "logger": logger or QuietLogger(),
        "cachedir": False, "noplaylist": True, "socket_timeout": 15,
        "retries": 0, "extractor_retries": 0,
        "fragment_retries": 0, "file_access_retries": 0,
        "skip_unavailable_fragments": False, "concurrent_fragment_downloads": 1,
        "cookiefile": None, "cookiesfrombrowser": None, "usenetrc": False,
        "username": None, "password": None,
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
    temporary.write_text(json.dumps({"stage": stage, "authentication_mode": "guest",
                                     "audio_retrieved": False, **details}, ensure_ascii=False))
    temporary.replace(target)


def verify_audio(path, info):
    if path.stat().st_size > MAX_AUDIO_BYTES:
        raise ValueError("audio_size_limit_exceeded")
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
        "authentication_mode": "guest",
    }


def execute(request):
    action = request["action"]
    if action not in {"search", "fetch", "acquire", "analyze"}:
        raise ValueError("invalid_action")
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
    logger = QuietLogger()
    opts = options(logger)
    if action == "search":
        query = request["query"].strip()
        if not 1 <= len(query) <= 200:
            raise ValueError("invalid_query")
        opts["extract_flat"] = "in_playlist"
        with GuestYoutubeDL(opts) as ydl:
            result = ydl.extract_info("ytsearch5:" + query, download=False)
        return {"results": [
            {"id": e["id"], "title": e.get("title", e["id"]), "url": canonical(e["id"])}
            for e in result.get("entries", []) if e and VIDEO.fullmatch(e.get("id", ""))
        ]}
    url = canonical(request["video_id"])
    if action == "acquire":
        progress(root, "resolving")
        opts.update({"format": "bestaudio", "outtmpl": str(root / "audio.%(ext)s"),
                     "max_filesize": MAX_AUDIO_BYTES})
    with GuestYoutubeDL(opts) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
        except Exception as exc:
            return {"stage": "resolving", "error": clean_error(exc),
                    "diagnostics": logger.events, "authentication_mode": "guest", "audio_retrieved": False}
        meta = metadata(info)
        if action == "fetch":
            return {"id": meta["id"], "title": meta["title"], "url": meta["url"],
                    "text": meta["description"], "metadata": {k: v for k, v in meta.items() if k != "description"}}
        if info.get("id") != request["video_id"]:
            return {"stage": "metadata_observed", "error": "video_mismatch", "metadata": meta}
        if info.get("channel_id") != request["expected_channel_id"]:
            return {"stage": "metadata_observed", "error": "channel_mismatch", "metadata": meta}
        if (info.get("is_live") or not info.get("duration")
                or not math.isfinite(float(info["duration"])) or not 0 < float(info["duration"]) <= 3600):
            return {"stage": "metadata_observed", "error": "unsupported_live_or_duration", "metadata": meta}
        if info.get("has_drm"):
            return {"stage": "metadata_observed", "error": "drm_protected", "metadata": meta}
        selected = {k: info[k] for k in ("format_id", "ext", "acodec", "protocol", "filesize", "filesize_approx")
                    if k in info}
        progress(root, "stream_url_resolved", metadata=meta, selected_format=selected)
        transfer = {"received_bytes": 0}

        def hook(event):
            received = int(event.get("downloaded_bytes") or 0)
            transfer["received_bytes"] = max(transfer["received_bytes"], received)
            if transfer["received_bytes"] > MAX_AUDIO_BYTES:
                raise ValueError("audio_size_limit_exceeded")
            if event["status"] == "downloading":
                progress(root, "downloading", metadata=meta, selected_format=selected, **transfer)
            if event["status"] == "finished":
                progress(root, "audio_downloaded", metadata=meta, selected_format=selected, **transfer)

        ydl.add_progress_hook(hook)
        # URLs are resolved afresh for this job and are never exposed by an MCP tool.
        try:
            ydl.process_info(info)
        except Exception as exc:
            return {"stage": "downloading" if transfer["received_bytes"] else "stream_url_resolved",
                    "error": clean_error(exc), "metadata": meta, "selected_format": selected,
                    "diagnostics": logger.events, "authentication_mode": "guest", "audio_retrieved": False,
                    **transfer}
        path = Path(ydl.prepare_filename(info))
    if not path.is_file() or path.stat().st_size == 0:
        return {"stage": "stream_url_resolved", "error": "no_audio_file"}
    progress(root, "decoding", metadata=meta)
    manifest = verify_audio(path, info)
    (root / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2))
    return {"stage": "decoded", "manifest": manifest, "audio_filename": path.name,
            "audio_retrieved": True, "authentication_mode": "guest", "selected_format": selected,
            "diagnostics": logger.events}


if __name__ == "__main__":
    try:
        answer = execute(json.load(sys.stdin))
    except Exception as exc:
        answer = {"error": clean_error(exc)}
    print(json.dumps(answer, ensure_ascii=False))
