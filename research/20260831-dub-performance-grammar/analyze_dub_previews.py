#!/usr/bin/env python3
"""Superseded Dub-specific preview analyzer.

Do not use this file for current research results. It introduced a second,
uncalibrated measurement definition instead of using the shared analyzer in:

  main:research/music-analysis/analyze_previews.py
  main:research/music-analysis/calibrate_analyzer.py

Historical output remains in preview-analysis.json with status "superseded".
Current output is preview-analysis-standard.json.
"""

raise SystemExit(
    "superseded: use the shared calibrated analyzer recorded in "
    "preview-analysis-standard.json"
)
