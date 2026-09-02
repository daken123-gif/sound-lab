#!/usr/bin/env python3
"""Verify the locked sample and expose it under blind IDs for separation."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path


ROOT = Path(__file__).parent
WORKSPACE = ROOT.parent


def main() -> None:
    manifest = json.loads((ROOT / "blind20-manifest.json").read_text())
    output = ROOT / "blind20-input"
    output.mkdir(exist_ok=True)
    for row in manifest["selected"]:
        source = WORKSPACE / row["source"]
        digest = hashlib.sha256(source.read_bytes()).hexdigest()
        if digest != row["sha256"]:
            raise SystemExit(f"hash mismatch: {row['blind_id']} {source}")
        target = output / f"{row['blind_id']}.m4a"
        if target.exists() or target.is_symlink():
            target.unlink()
        os.link(source, target)
    print(f"verified and linked {len(manifest['selected'])} inputs")


if __name__ == "__main__":
    main()
