#!/usr/bin/env python3
"""Download the locked Apple previews and require the original SHA-256 bytes."""

from __future__ import annotations

import argparse
import hashlib
import json
import urllib.parse
import urllib.request
from pathlib import Path


ROOT = Path(__file__).parent
USER_AGENT = "sound-lab-blind20-audit/1.0"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def get_json(url: str) -> dict:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def download(url: str, target: Path) -> None:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    partial = target.with_suffix(target.suffix + ".part")
    partial.unlink(missing_ok=True)
    with urllib.request.urlopen(request, timeout=60) as response, partial.open("wb") as handle:
        while block := response.read(1024 * 1024):
            handle.write(block)
    partial.replace(target)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--ids", nargs="+", help="optional blind-ID subset")
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)

    manifest = json.loads((ROOT / "blind20-manifest.json").read_text())
    title_map = json.loads((ROOT / "blind20-title-map.json").read_text())
    expected = {row["blind_id"]: row for row in manifest["selected"]}
    metadata = {row["blind_id"]: row for row in title_map["tracks"]}
    if set(expected) != set(metadata):
        raise SystemExit("manifest and title map blind IDs differ")

    selected_ids = sorted(args.ids or expected)
    unknown = sorted(set(selected_ids) - set(expected))
    if unknown:
        raise SystemExit(f"unknown blind IDs: {', '.join(unknown)}")

    verified = []
    for blind_id in selected_ids:
        row = expected[blind_id]
        meta = metadata[blind_id]
        country = "GB" if "/gb/" in meta["url"] else "US"
        query = urllib.parse.urlencode({"id": meta["track_id"], "country": country})
        lookup = get_json(f"https://itunes.apple.com/lookup?{query}")
        matches = [item for item in lookup.get("results", []) if item.get("trackId") == meta["track_id"]]
        if len(matches) != 1 or not matches[0].get("previewUrl"):
            raise SystemExit(f"preview lookup failed: {blind_id} track_id={meta['track_id']}")

        target = args.output / f"{blind_id}.m4a"
        if not target.exists() or sha256(target) != row["sha256"]:
            download(matches[0]["previewUrl"], target)
        actual = sha256(target)
        if actual != row["sha256"]:
            target.unlink(missing_ok=True)
            raise SystemExit(
                f"SHA-256 mismatch: {blind_id} expected={row['sha256']} actual={actual}"
            )
        verified.append({"blind_id": blind_id, "track_id": meta["track_id"], "sha256": actual})
        print(f"verified {blind_id} {meta['title']}")

    (args.output / "verified.json").write_text(
        json.dumps({"protocol": manifest["protocol"], "tracks": verified}, indent=2) + "\n"
    )
    print(f"verified {len(verified)} locked previews")


if __name__ == "__main__":
    main()
