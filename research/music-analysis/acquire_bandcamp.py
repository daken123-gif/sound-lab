#!/usr/bin/env python3
"""Fetch one public Bandcamp stream and verify its complete decode; no audio in Git."""
import argparse
import hashlib
import html
import json
import re
import subprocess
import tempfile
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


def fetch(url, limit):
    request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(request, timeout=45) as response:
        data = response.read(limit + 1)
        if len(data) > limit:
            raise ValueError("Response exceeds the configured byte limit")
        return data, response.headers.get("Content-Type", "")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("url", help="Official artist/label Bandcamp album or track page")
    parser.add_argument("--track", required=True, help="Exact displayed track title")
    parser.add_argument("--artist", required=True, help="Expected displayed artist")
    parser.add_argument("--out-dir", type=Path, default=Path(__file__).parent / ".source-work")
    args = parser.parse_args()
    parsed = urllib.parse.urlsplit(args.url)
    if parsed.scheme != "https" or not (parsed.hostname or "").endswith(".bandcamp.com"):
        raise ValueError("An HTTPS Bandcamp artist/label page is required")
    page, _ = fetch(args.url, 8 * 1024 * 1024)
    match = re.search(r'data-tralbum="([^"]+)"', page.decode("utf-8"))
    if not match:
        raise ValueError("Public track metadata was not found")
    album = json.loads(html.unescape(match.group(1)))
    if album.get("artist", "").casefold() != args.artist.casefold():
        raise ValueError(f"Artist mismatch: {album.get('artist')!r}")
    tracks = [t for t in album["trackinfo"] if t["title"] == args.track]
    if len(tracks) != 1:
        raise ValueError(f"Expected one exact track title, found {len(tracks)}")
    track = tracks[0]
    stream = (track.get("file") or {}).get("mp3-128")
    if not stream:
        raise ValueError("This track has no publicly supplied mp3-128 stream")
    if stream.startswith("//"):
        stream = "https:" + stream
    stream_parts = urllib.parse.urlsplit(stream)
    if stream_parts.scheme != "https" or not (stream_parts.hostname or "").endswith(".bcbits.com"):
        raise ValueError("Unexpected stream origin; inspect before acquiring")
    data, content_type = fetch(stream, 256 * 1024 * 1024)
    if not data or not content_type.startswith("audio/"):
        raise ValueError(f"Not an audio response: {content_type}")
    digest = hashlib.sha256(data).hexdigest()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="bandcamp-", dir=args.out_dir) as temporary:
        source = Path(temporary) / "source.mp3"
        pcm = Path(temporary) / "decoded.pcm"
        source.write_bytes(data)
        probe = json.loads(subprocess.check_output([
            "ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(source)
        ]))
        subprocess.run([
            "ffmpeg", "-v", "error", "-xerror", "-i", str(source),
            "-map", "0:a:0", "-ac", "1", "-ar", "16000", "-f", "s16le", str(pcm)
        ], check=True, timeout=180)
        decoded_seconds = pcm.stat().st_size / 32000
        expected = float(track["duration"])
        if decoded_seconds <= 0 or abs(decoded_seconds - expected) > 1:
            raise ValueError(f"Duration mismatch: decoded={decoded_seconds}, page={expected}")
        destination = args.out_dir / f"{digest}.mp3"
        if destination.exists() and hashlib.sha256(destination.read_bytes()).hexdigest() != digest:
            raise ValueError("Existing content-addressed asset is inconsistent")
        if not destination.exists():
            source.rename(destination)
    audio = next(s for s in probe["streams"] if s["codec_type"] == "audio")
    report = {
        "schema_version": 1,
        "provider": "bandcamp",
        "source_page": args.url,
        "artist": album["artist"],
        "release": album.get("current", {}).get("title"),
        "title": track["title"],
        "track_id": track.get("track_id", track.get("id")),
        "retrieved_at": datetime.now(timezone.utc).isoformat(),
        "representation": "public mp3-128 stream; not purchased lossless",
        "audio_file": destination.name,
        "audio_bytes": len(data),
        "sha256": digest,
        "page_duration_s": expected,
        "decoded_duration_s": decoded_seconds,
        "codec": audio["codec_name"],
        "sample_rate": int(audio["sample_rate"]),
        "channels": audio["channels"],
        "stream_host": stream_parts.hostname,
        "stream_url_sha256": hashlib.sha256(stream.encode()).hexdigest(),
        "decode": "ffmpeg -xerror, mono s16le 16000 Hz, complete stream",
        "ffmpeg_version": subprocess.check_output(["ffmpeg", "-version"], text=True).splitlines()[0],
        "state": "full-source-decoded",
        "master_identity_vs_preview": "unverified",
        "musical_analysis": "not_performed_by_this_acquirer",
    }
    manifest = args.out_dir / f"{digest}.manifest.json"
    manifest.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
