#!/usr/bin/env python3
"""Join locked blind results with metadata only after analysis."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).parent


def main() -> None:
    results = json.loads((ROOT / "blind20-results-blinded.json").read_text())
    manifest = json.loads((ROOT / "blind20-manifest.json").read_text())
    title_map = json.loads((ROOT / "blind20-title-map.json").read_text())
    sources = {row["blind_id"]: row for row in manifest["selected"]}
    metadata = {row["blind_id"]: row for row in title_map["tracks"]}
    if set(sources) != set(metadata):
        raise ValueError("manifest and metadata blind IDs differ")

    decoded = []
    for row in results["tracks"]:
        blind_id = row["blind_id"]
        decoded.append({**row, "source": sources[blind_id], "metadata": metadata[blind_id]})

    title_counts = Counter(row["metadata"]["title"] for row in decoded)
    output = {
        "protocol": results["protocol"],
        "decode_boundary": title_map["decode_timing"],
        "population_assets": len(decoded),
        "unique_title_strings": len(title_counts),
        "duplicate_title_strings": {name: count for name, count in title_counts.items() if count > 1},
        "category_counts": results["category_counts"],
        "tracks": decoded,
    }
    (ROOT / "blind20-results-decoded.json").write_text(
        json.dumps(output, ensure_ascii=False, indent=2) + "\n"
    )
    print(json.dumps({
        "category_counts": output["category_counts"],
        "unique_title_strings": output["unique_title_strings"],
        "duplicate_title_strings": output["duplicate_title_strings"],
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
