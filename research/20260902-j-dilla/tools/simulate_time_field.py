#!/usr/bin/env python3
"""Deterministic event-domain tests for the J Dilla time-field hypothesis.

This module does not model or imitate any copyrighted recording.  It creates
synthetic event times so competing timing rules can be compared without
claiming that their values are measurements of J Dilla's music.
"""

from __future__ import annotations

import argparse
import json
import math
from copy import deepcopy
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "sound-lab.j-dilla.synthetic-time-field/v1"


def floor_time(step: int, subdivision_seconds: float) -> float:
    return step * subdivision_seconds


def global_swing_offset(step: int, amount_seconds: float) -> float:
    """Delay every odd subdivision by one shared amount."""
    return amount_seconds if step % 2 else 0.0


def structured_offset(voice: str, step: int) -> float:
    """Return a voice- and position-relative synthetic timing shape."""
    shapes = {
        "kick": (0.000, -0.012, 0.006, -0.004),
        "snare": (0.000, 0.018, 0.004, 0.011),
        "hat": (-0.006, 0.009, -0.003, 0.014),
    }
    if voice not in shapes:
        raise ValueError(f"unknown voice: {voice}")
    return shapes[voice][step % len(shapes[voice])]


def event_time(
    step: int,
    voice: str,
    subdivision_seconds: float,
    *,
    mode: str,
    swing_seconds: float = 0.0,
    coupling_seconds: float = 0.0,
    gesture_seconds: float = 0.0,
    recovery_seconds: float = 0.0,
) -> float:
    if mode == "global_swing":
        voice_shape = global_swing_offset(step, swing_seconds)
    elif mode == "structured_relation":
        voice_shape = structured_offset(voice, step)
    else:
        raise ValueError(f"unknown mode: {mode}")
    return (
        floor_time(step, subdivision_seconds)
        + voice_shape
        + coupling_seconds
        + gesture_seconds
        + recovery_seconds
    )


def recover_from_current_state(now: float, target_phase: float, period: float) -> float:
    """Find the first target phase at or after now, never rewinding."""
    if period <= 0:
        raise ValueError("period must be positive")
    cycles = math.ceil((now - target_phase) / period)
    return target_phase + max(0, cycles) * period


def release_to_floor(state: dict[str, Any], voice: str) -> dict[str, Any]:
    """Release one intervention while leaving all other voices untouched."""
    result = deepcopy(state)
    interventions = result.setdefault("active_interventions", {})
    if voice not in interventions:
        raise KeyError(voice)
    interventions[voice] = 0.0
    return result


def build_fixture() -> dict[str, Any]:
    subdivision_seconds = 0.125
    voices = ("kick", "snare", "hat")
    steps = range(8)
    global_events = {
        voice: [
            round(event_time(step, voice, subdivision_seconds, mode="global_swing", swing_seconds=0.02), 6)
            for step in steps
        ]
        for voice in voices
    }
    structured_events = {
        voice: [
            round(event_time(step, voice, subdivision_seconds, mode="structured_relation"), 6)
            for step in steps
        ]
        for voice in voices
    }
    initial = {"active_interventions": {"kick": -0.02, "snare": 0.015, "hat": 0.008}}
    released = release_to_floor(initial, "snare")
    now = 1.37
    target_phase = 0.10
    period = 0.50
    recovery = recover_from_current_state(now, target_phase, period)
    return {
        "schema_version": SCHEMA_VERSION,
        "scope": "synthetic event-domain counterexample; not an audio measurement or style preset",
        "parameters": {
            "subdivision_seconds": subdivision_seconds,
            "global_swing_seconds": 0.02,
        },
        "global_swing": global_events,
        "structured_relation": structured_events,
        "release_to_floor": {"before": initial, "released_voice": "snare", "after": released},
        "recover_from_current_state": {
            "now": now,
            "target_phase": target_phase,
            "period": period,
            "next_target": round(recovery, 6),
        },
        "claims_supported": [
            "one global swing amount cannot encode voice-specific offsets at the same subdivision",
            "release_to_floor can be defined as a local intervention release rather than a global reset",
            "recovery can advance from the current state without rewinding to a loop origin",
        ],
        "claims_not_supported": [
            "the synthetic offsets reproduce J Dilla",
            "the synthetic offsets are measured from a recording",
            "the operations are usable in a product interface",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    rendered = json.dumps(build_fixture(), ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
