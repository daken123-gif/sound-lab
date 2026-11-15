"""Validate accessed numeric features without changing classifier short circuits.

Unused fields are deliberately not inspected, even if missing or nonfinite.
These internal views neither cache nor pre-consume window iterables. The public
callers supply lists; a one-shot iterator retains its historical consumption.
"""
import math
import numpy as np


class _NumericRow:
    def __init__(self, row, location):
        self.row = row
        self.location = location

    def __getitem__(self, field):
        try:
            raw = self.row[field]
            if isinstance(raw, (bool, np.bool_)):
                raise ValueError("boolean is not a feature value")
            value = float(raw)
        except (KeyError, TypeError, ValueError, OverflowError) as exc:
            raise ValueError(f"{self.location}.{field}: expected a finite number") from exc
        if not math.isfinite(value):
            raise ValueError(f"{self.location}.{field}: expected a finite number")
        if field == "bpm_candidate" and value <= 0:
            raise ValueError(f"{self.location}.{field}: BPM must be positive")
        return value


class _NumericWindows:
    def __init__(self, rows, location):
        self.rows = rows
        self.location = location

    def __iter__(self):
        return (_NumericRow(row, f"{self.location}[{i}]")
                for i, row in enumerate(self.rows))


def phase_input_views(full, windows, *, model=""):
    """Return lazy private views; validation occurs only at numeric access.

    Missing/nonconvertible accessed fields raise ValueError with their original
    cause. Python/NumPy booleans, nonfinite values and nonpositive BPM are
    rejected. Other user exceptions propagate. No field completeness, score
    range, window count or validity of unreferenced values is promised.
    """
    prefix = f"{model}." if model else ""
    return (_NumericRow(full, prefix + "full"),
            _NumericWindows(windows, prefix + "window"))
