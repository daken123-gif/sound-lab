import copy
import json
import tempfile
import unittest
from pathlib import Path

from validate_public_dataset_manifest import ManifestError, validate_manifest


HERE = Path(__file__).resolve().parent


class PublicDatasetManifestTest(unittest.TestCase):
    def setUp(self):
        with (HERE / "public-dataset-manifest.json").open(encoding="utf-8") as handle:
            self.manifest = json.load(handle)

    def test_repository_manifest_is_valid(self):
        summaries = validate_manifest(self.manifest, HERE)
        self.assertEqual(len(summaries), 4)
        self.assertTrue(all("ready=false" in item for item in summaries))

    def test_ready_requires_verified_checksum(self):
        changed = copy.deepcopy(self.manifest)
        changed["datasets"][0]["evaluation_ready"] = True
        with self.assertRaisesRegex(ManifestError, "checksum_verified"):
            validate_manifest(changed, HERE)

    def test_ready_requires_checked_annotation_schema(self):
        changed = copy.deepcopy(self.manifest)
        dataset = changed["datasets"][0]
        dataset["evaluation_ready"] = True
        dataset["annotation_schema_checked"] = False
        dataset["acquisition"]["state"] = "checksum_verified"
        dataset["acquisition"]["local_root"] = "fixtures/e-gmd"
        dataset["acquisition"]["checksum_observed"] = dataset["artifact"]["checksum_declared"]
        with self.assertRaisesRegex(ManifestError, "checked annotations"):
            validate_manifest(changed, HERE)

    def test_ready_requires_existing_local_root(self):
        changed = copy.deepcopy(self.manifest)
        dataset = changed["datasets"][0]
        dataset["evaluation_ready"] = True
        dataset["annotation_schema_checked"] = True
        dataset["acquisition"]["state"] = "checksum_verified"
        dataset["acquisition"]["local_root"] = "fixtures/e-gmd"
        dataset["acquisition"]["checksum_observed"] = dataset["artifact"]["checksum_declared"]
        with tempfile.TemporaryDirectory() as temporary_directory:
            with self.assertRaisesRegex(ManifestError, "local_root does not exist"):
                validate_manifest(changed, Path(temporary_directory))

    def test_all_synthetic_cases_have_a_public_data_target(self):
        targets = {
            case
            for dataset in self.manifest["datasets"]
            for case in dataset["case_targets"]
        }
        self.assertEqual(targets, {f"S{number:02d}" for number in range(1, 13)})

    def test_partial_acquisition_requires_component_evidence(self):
        changed = copy.deepcopy(self.manifest)
        changed["datasets"][0]["acquisition"].pop("verified_components")
        with self.assertRaisesRegex(ManifestError, "needs verified_components"):
            validate_manifest(changed, HERE)


if __name__ == "__main__":
    unittest.main()
