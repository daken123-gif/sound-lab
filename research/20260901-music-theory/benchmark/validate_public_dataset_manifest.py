#!/usr/bin/env python3
"""Validate the round-2 public-dataset evidence and acquisition contract."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ALLOWED_ACQUISITION_STATES = {
    "not_acquired",
    "metadata_only",
    "acquired_unverified",
    "partial_checksum_verified",
    "checksum_verified",
}
EXPECTED_CASES = {f"S{number:02d}" for number in range(1, 13)}


class ManifestError(ValueError):
    """Raised when the dataset manifest violates the evidence contract."""


def _require(mapping: dict[str, Any], key: str, context: str) -> Any:
    if key not in mapping:
        raise ManifestError(f"{context}: missing {key}")
    return mapping[key]


def validate_manifest(manifest: dict[str, Any], workspace: Path) -> list[str]:
    if manifest.get("schema_version") != 1:
        raise ManifestError("schema_version must be 1")

    datasets = _require(manifest, "datasets", "manifest")
    if not isinstance(datasets, list) or not datasets:
        raise ManifestError("manifest: datasets must be a non-empty list")

    seen_ids: set[str] = set()
    covered_cases: set[str] = set()
    summaries: list[str] = []

    for dataset in datasets:
        dataset_id = _require(dataset, "id", "dataset")
        context = f"dataset {dataset_id}"
        if dataset_id in seen_ids:
            raise ManifestError(f"{context}: duplicate id")
        seen_ids.add(dataset_id)

        for key in ("name", "version", "official_url", "split_unit"):
            value = _require(dataset, key, context)
            if not isinstance(value, str) or not value.strip():
                raise ManifestError(f"{context}: {key} must be a non-empty string")
        if not dataset["official_url"].startswith("https://"):
            raise ManifestError(f"{context}: official_url must use https")

        license_record = _require(dataset, "license", context)
        for key in ("spdx_like", "url", "review"):
            _require(license_record, key, f"{context} license")

        evidence = _require(dataset, "evidence", context)
        for key in ("audio", "annotations", "known_limit"):
            value = _require(evidence, key, f"{context} evidence")
            if not isinstance(value, str) or not value.strip():
                raise ManifestError(f"{context}: evidence.{key} must be non-empty")

        artifact = _require(dataset, "artifact", context)
        for key in (
            "url",
            "size_display_declared",
            "checksum_algorithm",
            "checksum_declared",
        ):
            _require(artifact, key, f"{context} artifact")

        targets = set(_require(dataset, "case_targets", context))
        unknown_targets = targets - EXPECTED_CASES
        if unknown_targets:
            raise ManifestError(f"{context}: unknown case targets {sorted(unknown_targets)}")
        covered_cases.update(targets)

        acquisition = _require(dataset, "acquisition", context)
        state = _require(acquisition, "state", f"{context} acquisition")
        if state not in ALLOWED_ACQUISITION_STATES:
            raise ManifestError(f"{context}: invalid acquisition state {state}")
        if state != "not_acquired" and not acquisition.get("verified_components"):
            raise ManifestError(f"{context}: acquired state needs verified_components")

        ready = _require(dataset, "evaluation_ready", context)
        schema_checked = _require(dataset, "annotation_schema_checked", context)
        if ready:
            if state != "checksum_verified":
                raise ManifestError(f"{context}: ready data must be checksum_verified")
            if not schema_checked:
                raise ManifestError(f"{context}: ready data needs checked annotations")
            if license_record["review"] == "manual_review_required":
                raise ManifestError(f"{context}: license review is still required")
            local_root = acquisition.get("local_root")
            if not local_root:
                raise ManifestError(f"{context}: ready data needs local_root")
            if not (workspace / local_root).exists():
                raise ManifestError(f"{context}: local_root does not exist")
            if acquisition.get("checksum_observed") != artifact["checksum_declared"]:
                raise ManifestError(f"{context}: observed checksum does not match")

        summaries.append(f"{dataset_id}: {state}, ready={str(ready).lower()}")

    missing_cases = EXPECTED_CASES - covered_cases
    if missing_cases:
        raise ManifestError(f"manifest: uncovered synthetic cases {sorted(missing_cases)}")
    return summaries


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "manifest",
        nargs="?",
        type=Path,
        default=Path(__file__).with_name("public-dataset-manifest.json"),
    )
    parser.add_argument(
        "--workspace",
        type=Path,
        default=Path(__file__).resolve().parent,
    )
    args = parser.parse_args()
    with args.manifest.open(encoding="utf-8") as handle:
        manifest = json.load(handle)
    for summary in validate_manifest(manifest, args.workspace):
        print(summary)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
