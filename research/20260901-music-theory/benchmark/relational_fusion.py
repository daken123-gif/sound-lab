#!/usr/bin/env python3
"""Fuse periodic evidence without collapsing it to one tempo label."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from baseline_analyzer import analyze as analyze_scipy
from librosa_analyzer import analyze as analyze_librosa


ENGINE_METHODS = {
    "scipy_baseline": "energy_autocorrelation",
    "librosa_1.0": "onset_tempogram",
}


def close_period(left: float, right: float) -> bool:
    return abs(left - right) <= max(0.04, min(left, right) * 0.04)


def integer_ratio(larger: float, smaller: float) -> int | None:
    if smaller <= 0 or larger <= smaller:
        return None
    ratio = larger / smaller
    nearest = round(ratio)
    if nearest >= 2 and abs(ratio - nearest) <= 0.06:
        return nearest
    return None


def observations(engine: str, result: dict) -> list[dict]:
    rows = []
    method = ENGINE_METHODS[engine]
    for rank, candidate in enumerate(result["period_hypotheses"]):
        score = float(candidate["score"])
        if score <= 0.0:
            continue
        rows.append(
            {
                "engine": engine,
                "method": method,
                "scope": "mix",
                "rank": rank,
                "period": float(candidate["period"]),
                "score": score,
            }
        )
    for channel in result["channel_analysis"]:
        for rank, candidate in enumerate(channel["period_hypotheses"][:6]):
            score = float(candidate["score"])
            if score <= 0.0:
                continue
            rows.append(
                {
                    "engine": engine,
                    "method": method,
                    "scope": f"channel:{channel['channel']}",
                    "rank": rank,
                    "period": float(candidate["period"]),
                    "score": score,
                }
            )
    if len(result["onsets"]) >= 2:
        iois = np.diff(np.asarray(result["onsets"], dtype=float))
        rows.append(
            {
                "engine": engine,
                "method": "median_inter_onset_interval",
                "scope": "mix",
                "rank": 0,
                "period": float(np.median(iois)),
                "score": None,
            }
        )
    return rows


def cluster_observations(rows: list[dict]) -> list[dict]:
    clusters: list[list[dict]] = []
    for row in sorted(rows, key=lambda item: item["period"]):
        match = next(
            (
                cluster
                for cluster in clusters
                if close_period(
                    row["period"],
                    sum(item["period"] for item in cluster) / len(cluster),
                )
            ),
            None,
        )
        if match is None:
            clusters.append([row])
        else:
            match.append(row)

    nodes = []
    for index, cluster in enumerate(clusters, start=1):
        period = float(np.median([item["period"] for item in cluster]))
        mix_engines = sorted(
            {
                item["engine"]
                for item in cluster
                if item["scope"] == "mix"
                and item["method"] != "median_inter_onset_interval"
            }
        )
        channel_top = sorted(
            {
                f"{item['engine']}:{item['scope']}"
                for item in cluster
                if item["scope"].startswith("channel:") and item["rank"] == 0
            }
        )
        nodes.append(
            {
                "id": f"period-{index:02d}",
                "period": round(period, 6),
                "roles": [],
                "mix_engine_support": mix_engines,
                "channel_top_support": channel_top,
                "evidence": cluster,
                "conflicts": [],
            }
        )
    return nodes


def find_node(nodes: list[dict], period: float) -> dict | None:
    return next((node for node in nodes if close_period(node["period"], period)), None)


def mix_rank(node: dict, engine: str) -> int | None:
    ranks = [
        row["rank"]
        for row in node["evidence"]
        if row["engine"] == engine
        and row["scope"] == "mix"
        and row["method"] != "median_inter_onset_interval"
    ]
    return min(ranks) if ranks else None


def add_role(node: dict, role: str) -> None:
    if role not in node["roles"]:
        node["roles"].append(role)


def build_graph(path: Path) -> dict:
    results = {
        "scipy_baseline": analyze_scipy(path),
        "librosa_1.0": analyze_librosa(path),
    }
    rows = [
        row
        for engine, result in results.items()
        for row in observations(engine, result)
    ]
    nodes = cluster_observations(rows)

    ioi_periods = [
        row["period"]
        for row in rows
        if row["method"] == "median_inter_onset_interval"
    ]
    pulse_period = float(np.median(ioi_periods)) if ioi_periods else None
    pulse_node = find_node(nodes, pulse_period) if pulse_period else None
    if pulse_node:
        add_role(pulse_node, "pulse_candidate")

    edges = []
    for smaller in nodes:
        for larger in nodes:
            ratio = integer_ratio(larger["period"], smaller["period"])
            if ratio is None:
                continue
            edges.append(
                {
                    "from": smaller["id"],
                    "to": larger["id"],
                    "relation": "integer_multiple",
                    "ratio": ratio,
                }
            )

    if pulse_node:
        pulse_rank = mix_rank(pulse_node, "scipy_baseline")
        for node in nodes:
            ratio = integer_ratio(node["period"], pulse_node["period"])
            if ratio is None:
                continue
            if len(node["mix_engine_support"]) >= 2:
                add_role(node, "recurrence_cycle_candidate")
            node_rank = mix_rank(node, "scipy_baseline")
            if node_rank is not None and pulse_rank is not None and node_rank < pulse_rank:
                add_role(node, "accent_cycle_candidate")

    for node in nodes:
        scipy_rank = mix_rank(node, "scipy_baseline")
        librosa_rank = mix_rank(node, "librosa_1.0")
        if (
            scipy_rank is not None
            and librosa_rank is not None
            and abs(scipy_rank - librosa_rank) >= 3
        ):
            node["conflicts"].append(
                {
                    "type": "rank_disagreement",
                    "ranks": {
                        "scipy_baseline": scipy_rank,
                        "librosa_1.0": librosa_rank,
                    },
                }
            )

    dominant_channels = {}
    for engine, result in results.items():
        periods = [
            float(channel["period_hypotheses"][0]["period"])
            for channel in result["channel_analysis"]
            if channel["period_hypotheses"]
        ]
        if len(periods) >= 2 and not close_period(periods[0], periods[1]):
            dominant_channels[engine] = periods
            for period in periods:
                node = find_node(nodes, period)
                if node:
                    add_role(node, "layer_period_candidate")

    for engine, periods in dominant_channels.items():
        for node in sorted(nodes, key=lambda item: item["period"], reverse=True):
            ratios = [integer_ratio(node["period"], period) for period in periods]
            if all(ratio is not None for ratio in ratios):
                add_role(node, "joint_recurrence_candidate")
                node["evidence"].append(
                    {
                        "engine": engine,
                        "method": "channel_common_multiple",
                        "scope": "cross_channel",
                        "rank": 0,
                        "period": node["period"],
                        "score": None,
                        "source_periods": periods,
                    }
                )
                break

    curves = {
        engine: result["low_band_tempo_curve"]
        for engine, result in results.items()
        if result["low_band_tempo_curve"] is not None
    }
    varying_engines = [
        engine
        for engine, curve in curves.items()
        if abs(curve["period_end"] - curve["period_start"])
        / curve["period_start"]
        >= 0.05
    ]
    tempo_state = {
        "time_varying": bool(varying_engines),
        "supporting_engines": varying_engines,
        "curves": curves,
    }
    if varying_engines and pulse_node:
        add_role(pulse_node, "time_varying_pulse_candidate")
        for node in nodes:
            node["conflicts"].append(
                {
                    "type": "global_period_summarizes_time_varying_evidence",
                    "supporting_engines": varying_engines,
                }
            )

    for node in nodes:
        node["roles"].sort()

    return {
        "graph": "relational-period-hypotheses-v0.1",
        "audio": path.name,
        "nodes": nodes,
        "edges": edges,
        "tempo_state": tempo_state,
        "non_comparable_fields": [
            "score across different engines",
            "rank across different temporal representations",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("audio", type=Path, nargs="+")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    graphs = [build_graph(path) for path in args.audio]
    payload = graphs[0] if len(graphs) == 1 else graphs
    text = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.write_text(text, encoding="utf-8")
        print(args.output)
    else:
        print(text, end="")


if __name__ == "__main__":
    main()
