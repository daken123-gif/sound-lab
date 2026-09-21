#!/usr/bin/env python3
"""Validate the J Dilla clock-relation acquisition manifest using stdlib only."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


SCHEMA_VERSION = "sound-lab.j-dilla.clock-relation/v1"
REQUIRED_TRANSFORMS = {
    "original", "quantize_all", "quantize_kick", "quantize_snare",
    "unify_hat_swing", "align_bass_to_grid", "exchange_voice_offsets",
    "invert_offset_signs", "shuffle_positions_keep_magnitudes",
    "random_humanize_same_distribution",
}
REQUIRED_RECORDINGS = {
    "runnin-analysis-master", "players-analysis-master",
    "keep-it-on-this-beat-analysis-master", "come-get-it-album",
    "come-get-it-instrumental", "come-get-it-cassette-demo",
    "come-get-it-alt-beat",
}
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
IDENTITY_BLOCK_STATUS = {
    "ambiguous": "blocked_version_ambiguous",
    "release_family_resolved_master_ambiguous": "blocked_master_ambiguous",
}


def validate_manifest(data: dict) -> list[str]:
    errors: list[str] = []
    if data.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"schema_version must be {SCHEMA_VERSION!r}")
    if data.get("research_id") != "20260902-j-dilla":
        errors.append("research_id must be '20260902-j-dilla'")
    if data.get("minimum_region_bars") != 16:
        errors.append("minimum_region_bars must be 16")

    transforms = data.get("transforms")
    if not isinstance(transforms, list) or set(transforms) != REQUIRED_TRANSFORMS:
        errors.append("transforms must contain the exact ten v1 conditions")
    elif len(transforms) != len(set(transforms)):
        errors.append("transforms must not contain duplicates")

    recordings = data.get("recordings")
    if not isinstance(recordings, list):
        return errors + ["recordings must be a list"]
    ids = [item.get("recording_id") for item in recordings if isinstance(item, dict)]
    if set(ids) != REQUIRED_RECORDINGS:
        errors.append("recordings must contain the exact seven v1 recording IDs")
    if len(ids) != len(set(ids)):
        errors.append("recording_id values must be unique")

    required_fields = {
        "recording_id", "artist", "title", "version_label", "identity_status",
        "catalog_candidates", "excluded_versions", "reference_intervals",
        "source_status", "source_kind", "source_locator", "rights_basis",
        "local_filename", "sha256", "duration_seconds", "sample_rate_hz",
        "channels", "file_size_bytes", "codec", "analysis_status", "regions",
    }
    candidate_fields = {
        "release_title", "release_year", "track_number", "catalog_duration_seconds",
        "locator", "authority", "identity_note",
    }

    for index, item in enumerate(recordings):
        prefix = f"recordings[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{prefix} must be an object")
            continue
        missing = sorted(required_fields - item.keys())
        if missing:
            errors.append(f"{prefix} missing fields: {', '.join(missing)}")
            continue

        identity_status = item["identity_status"]
        if identity_status not in {"resolved_candidate", *IDENTITY_BLOCK_STATUS}:
            errors.append(
                f"{prefix}.identity_status must be resolved_candidate, ambiguous, "
                "or release_family_resolved_master_ambiguous"
            )
        candidates = item["catalog_candidates"]
        if not isinstance(candidates, list) or not candidates:
            errors.append(f"{prefix}.catalog_candidates must be a non-empty list")
        else:
            for candidate_index, candidate in enumerate(candidates):
                cprefix = f"{prefix}.catalog_candidates[{candidate_index}]"
                if not isinstance(candidate, dict):
                    errors.append(f"{cprefix} must be an object")
                    continue
                candidate_missing = sorted(candidate_fields - candidate.keys())
                if candidate_missing:
                    errors.append(f"{cprefix} missing fields: {', '.join(candidate_missing)}")
                    continue
                for field in ("release_title", "locator", "authority", "identity_note"):
                    if not isinstance(candidate[field], str) or not candidate[field].strip():
                        errors.append(f"{cprefix}.{field} must be a non-empty string")
                catalog_duration = candidate["catalog_duration_seconds"]
                if catalog_duration is not None and (
                    not isinstance(catalog_duration, (int, float)) or catalog_duration <= 0
                ):
                    errors.append(f"{cprefix}.catalog_duration_seconds must be positive or null")

        for field in ("excluded_versions", "reference_intervals"):
            if not isinstance(item[field], list):
                errors.append(f"{prefix}.{field} must be a list")

        source_status = item["source_status"]
        if source_status not in {"unobtained", "acquired"}:
            errors.append(f"{prefix}.source_status must be unobtained or acquired")
        if source_status == "acquired":
            for field in (
                "source_kind", "source_locator", "rights_basis", "local_filename",
                "sha256", "duration_seconds", "sample_rate_hz", "channels",
                "file_size_bytes", "codec",
            ):
                if item[field] in (None, ""):
                    errors.append(f"{prefix}.{field} is required when acquired")
            if item["source_kind"] not in {"full_length", "preview"}:
                errors.append(f"{prefix}.source_kind must be full_length or preview")
            if not isinstance(item["sha256"], str) or not SHA256_RE.fullmatch(item["sha256"]):
                errors.append(f"{prefix}.sha256 must be lowercase 64-character hex")

        regions = item["regions"]
        if not isinstance(regions, list):
            errors.append(f"{prefix}.regions must be a list")
            continue
        for region_index, region in enumerate(regions):
            rprefix = f"{prefix}.regions[{region_index}]"
            if not isinstance(region, dict):
                errors.append(f"{rprefix} must be an object")
                continue
            for field in ("region_id", "start_seconds", "end_seconds", "start_bar", "bar_count", "alignment_note"):
                if field not in region:
                    errors.append(f"{rprefix}.{field} is required")
            if isinstance(region.get("bar_count"), int) and region["bar_count"] < data.get("minimum_region_bars", 16):
                errors.append(f"{rprefix}.bar_count must be at least 16")
            if all(isinstance(region.get(x), (int, float)) for x in ("start_seconds", "end_seconds")):
                if region["end_seconds"] <= region["start_seconds"]:
                    errors.append(f"{rprefix}.end_seconds must be greater than start_seconds")

        analysis_status = item["analysis_status"]
        if analysis_status not in {
            "blocked_source_unobtained", "blocked_version_ambiguous",
            "blocked_master_ambiguous", "ready",
        }:
            errors.append(f"{prefix}.analysis_status is not a recognized v1 state")
        required_block = IDENTITY_BLOCK_STATUS.get(identity_status)
        if required_block and analysis_status != required_block:
            errors.append(f"{prefix} must remain {required_block} while identity is unresolved")
        if analysis_status == "ready" and identity_status != "resolved_candidate":
            errors.append(f"{prefix} cannot be ready before version identity is resolved")
        if analysis_status == "ready" and source_status != "acquired":
            errors.append(f"{prefix} cannot be ready before source acquisition")
        if analysis_status == "ready" and not regions:
            errors.append(f"{prefix} cannot be ready without an analysis region")

    return errors


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(f"usage: {Path(argv[0]).name} MANIFEST.json", file=sys.stderr)
        return 2
    path = Path(argv[1])
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"manifest read failed: {exc}", file=sys.stderr)
        return 2
    errors = validate_manifest(data)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"valid: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
