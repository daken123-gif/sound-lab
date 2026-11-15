"""Fail before numeric classification; do not invent an invalid-result category."""
import math


def validate_phase_inputs(full: dict, windows: list[dict], *, full_bpm: bool) -> None:
    """Check consumed numeric fields only; preserve the caller's output contract.

    Numeric strings remain accepted, as with the classifiers' existing float()
    conversions. Unused window entropy and Demucs full BPM are not required.
    This does not change BPM folding, score thresholds, or window-count policy.
    """
    shared = ("beat_confidence", "triplet_spacing_score", "binary_spacing_score")
    full_fields = shared + ("phase_entropy_0_concentrated_1_diffuse",)
    if full_bpm:
        full_fields += ("bpm_candidate",)
    rows = [("full", full, full_fields)]
    rows.extend((f"window[{i}]", row, shared + ("bpm_candidate",))
                for i, row in enumerate(windows))
    for location, row, fields in rows:
        for field in fields:
            try:
                raw = row[field]
                if isinstance(raw, bool):
                    raise ValueError("boolean is not a feature value")
                value = float(raw)
            except (KeyError, TypeError, ValueError, OverflowError) as exc:
                raise ValueError(f"{location}.{field}: expected a finite number") from exc
            if not math.isfinite(value):
                raise ValueError(f"{location}.{field}: expected a finite number")
            if field == "bpm_candidate" and value <= 0:
                raise ValueError(f"{location}.{field}: BPM must be positive")
