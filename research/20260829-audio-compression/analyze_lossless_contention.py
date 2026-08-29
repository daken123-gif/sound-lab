#!/usr/bin/env python3
import csv
import statistics
import sys
from collections import defaultdict
from pathlib import Path


def median(values: list[float]) -> float:
    return statistics.median(values)


input_path = Path(sys.argv[1] if len(sys.argv) > 1 else "lossless-contention-benchmark/results.csv")
summary_path = Path(sys.argv[2] if len(sys.argv) > 2 else "lossless-contention-benchmark/summary.csv")
overhead_path = Path(sys.argv[3] if len(sys.argv) > 3 else "lossless-contention-benchmark/overhead.csv")

groups: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
with input_path.open(newline="") as source:
    for row in csv.DictReader(source):
        groups[(row["format"], row["mode"])].append(row)

summary: dict[tuple[str, str], dict[str, float | int | str]] = {}
for key, rows in groups.items():
    summary[key] = {
        "format": key[0],
        "mode": key[1],
        "runs": len(rows),
        "median_cpu_seconds": median([
            float(row["user_cpu_seconds"]) + float(row["system_cpu_seconds"])
            for row in rows
        ]),
        "median_wall_seconds": median([float(row["wall_seconds"]) for row in rows]),
        "median_max_rss_kb": median([float(row["max_rss_kb"]) for row in rows]),
    }

with summary_path.open("w", newline="") as target:
    fieldnames = [
        "format",
        "mode",
        "runs",
        "median_cpu_seconds",
        "median_wall_seconds",
        "median_max_rss_kb",
    ]
    writer = csv.DictWriter(target, fieldnames=fieldnames)
    writer.writeheader()
    for key in sorted(summary):
        row = summary[key]
        writer.writerow({
            **row,
            "median_cpu_seconds": f'{row["median_cpu_seconds"]:.3f}',
            "median_wall_seconds": f'{row["median_wall_seconds"]:.3f}',
            "median_max_rss_kb": f'{row["median_max_rss_kb"]:.0f}',
        })

with overhead_path.open("w", newline="") as target:
    fieldnames = [
        "format",
        "cpu_increase_percent",
        "wall_increase_percent",
        "max_rss_increase_percent",
    ]
    writer = csv.DictWriter(target, fieldnames=fieldnames)
    writer.writeheader()
    for format_name in sorted({key[0] for key in summary}):
        baseline = summary[(format_name, "four_decode")]
        combined = summary[(format_name, "four_decode_plus_encode_codec_only")]

        def increase(field: str) -> float:
            before = float(baseline[field])
            after = float(combined[field])
            return 100 * (after / before - 1)

        writer.writerow({
            "format": format_name,
            "cpu_increase_percent": f'{increase("median_cpu_seconds"):.1f}',
            "wall_increase_percent": f'{increase("median_wall_seconds"):.1f}',
            "max_rss_increase_percent": f'{increase("median_max_rss_kb"):.1f}',
        })
