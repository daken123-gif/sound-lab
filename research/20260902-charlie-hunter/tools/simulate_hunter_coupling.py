#!/usr/bin/env python3
"""Deterministic contrast model for Charlie Hunter coupling research.

The coefficients are synthetic. They distinguish three causal topologies and
do not encode measured Charlie Hunter timing or an artist-style preset.
"""

from __future__ import annotations

import json
from copy import deepcopy


VOICES = ("bass", "chord", "melody")
GESTURES = (
    {"id": "g1", "time": 1.0, "action": "bass_shorten", "amount": 0.20},
    {"id": "g2", "time": 2.0, "action": "melody_delay", "amount": 0.12},
    {"id": "g3", "time": 3.0, "action": "chord_mute", "amount": 1.00},
)
CONDITIONS = ("independent_voice", "fixed_macro", "hunter_coupling")


def baseline(time: float) -> dict[str, dict[str, float | bool]]:
    return {
        voice: {"onset": time, "duration": 0.75, "active": True}
        for voice in VOICES
    }


def apply_independent(state: dict, gesture: dict) -> None:
    action = gesture["action"]
    amount = gesture["amount"]
    if action == "bass_shorten":
        state["bass"]["duration"] -= amount
    elif action == "melody_delay":
        state["melody"]["onset"] += amount
    elif action == "chord_mute":
        state["chord"]["active"] = False


def apply_fixed_macro(state: dict, gesture: dict) -> None:
    action = gesture["action"]
    amount = gesture["amount"]
    for voice in VOICES:
        if action == "bass_shorten":
            state[voice]["duration"] -= amount
        elif action == "melody_delay":
            state[voice]["onset"] += amount
        elif action == "chord_mute":
            state[voice]["active"] = False


def apply_hunter_coupling(state: dict, gesture: dict) -> None:
    """Apply a synthetic differentiated coupling matrix."""
    action = gesture["action"]
    amount = gesture["amount"]
    if action == "bass_shorten":
        state["bass"]["duration"] -= amount
        state["chord"]["onset"] -= 0.06
        state["melody"]["duration"] += 0.05
    elif action == "melody_delay":
        state["melody"]["onset"] += amount
        state["chord"]["duration"] -= 0.06
        state["bass"]["onset"] -= 0.03
    elif action == "chord_mute":
        state["chord"]["active"] = False
        state["bass"]["duration"] -= 0.08
        state["melody"]["onset"] += 0.04


APPLIERS = {
    "independent_voice": apply_independent,
    "fixed_macro": apply_fixed_macro,
    "hunter_coupling": apply_hunter_coupling,
}


def rounded(value: float) -> float:
    return round(value, 6)


def change(before: dict, after: dict) -> dict:
    return {
        "onset_delta": rounded(after["onset"] - before["onset"]),
        "duration_delta": rounded(after["duration"] - before["duration"]),
        "active_changed": after["active"] != before["active"],
    }


def changed(delta: dict) -> bool:
    return (
        delta["onset_delta"] != 0.0
        or delta["duration_delta"] != 0.0
        or delta["active_changed"]
    )


def simulate_condition(condition: str) -> dict:
    slots = []
    signatures = []
    for gesture in GESTURES:
        before = baseline(gesture["time"])
        after = deepcopy(before)
        APPLIERS[condition](after, gesture)
        targets = []
        for voice in VOICES:
            delta = change(before[voice], after[voice])
            slots.append(
                {
                    "gesture_id": gesture["id"],
                    "voice": voice,
                    "onset": rounded(after[voice]["onset"]),
                    "duration": rounded(after[voice]["duration"]),
                    "active": after[voice]["active"],
                }
            )
            if changed(delta):
                targets.append({"voice": voice, **delta})
        signatures.append(
            {
                "gesture_id": gesture["id"],
                "action": gesture["action"],
                "targets": targets,
            }
        )
    return {"slots": slots, "causal_signatures": signatures}


def pattern_count(signature: dict) -> int:
    patterns = {
        (
            target["onset_delta"],
            target["duration_delta"],
            target["active_changed"],
        )
        for target in signature["targets"]
    }
    return len(patterns)


def build_report() -> dict:
    conditions = {
        condition: simulate_condition(condition) for condition in CONDITIONS
    }
    return {
        "schema_version": "sound-lab.synthetic-hunter-coupling/v1",
        "evidence_boundary": (
            "Synthetic topology contrast only; no Charlie Hunter audio, MIDI, "
            "onset measurement, or artist-style preset is included."
        ),
        "input": {"voices": list(VOICES), "gestures": list(GESTURES)},
        "conditions": conditions,
        "summary": {
            "event_slots": {
                name: len(result["slots"]) for name, result in conditions.items()
            },
            "affected_voice_counts": {
                name: [
                    len(signature["targets"])
                    for signature in result["causal_signatures"]
                ]
                for name, result in conditions.items()
            },
            "distinct_target_patterns": {
                name: [
                    pattern_count(signature)
                    for signature in result["causal_signatures"]
                ]
                for name, result in conditions.items()
            },
            "automatic_events_added": {name: 0 for name in CONDITIONS},
        },
    }


if __name__ == "__main__":
    print(json.dumps(build_report(), ensure_ascii=False, indent=2, sort_keys=True))
