"""Non-audio regression tests for the real main() argument gate.

Run: python3 -m unittest discover -s research/music-analysis -p 'test_demucs_seed_arguments.py' -v
Only main's AST is loaded: Essentia and audio functions are deliberately not imported.
A sentinel stops accepted inputs at the first manifest read; this is not an audio integration test.
"""
import argparse
import ast
import contextlib
import io
from pathlib import Path
import tempfile
import unittest
from unittest import mock


SOURCE = Path(__file__).with_name("demucs_seed_sensitivity.py")


class ManifestReached(Exception):
    pass


def load_main():
    tree = ast.parse(SOURCE.read_text())
    node = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "main")
    scope = {
        "argparse": argparse,
        "Path": Path,
        "ROOT": SOURCE.parent,
        "DEFAULT_IDS": ("B06", "B09", "B10", "B14", "B16", "B17", "B19"),
        "json": __import__("json"),
    }
    exec(compile(ast.Module(body=[node], type_ignores=[]), str(SOURCE), "exec"), scope)
    return scope["main"]


class SeedArgumentsTest(unittest.TestCase):
    def exercise(self, seeds, accepted):
        main = load_main()
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "existing.json"
            output.write_text("preserve-existing-result")
            args = ["audit", "--stems-root", tmp, "--output", str(output)] + seeds
            stderr = io.StringIO()
            with mock.patch("sys.argv", args), contextlib.redirect_stderr(stderr):
                with mock.patch.object(Path, "read_text", side_effect=ManifestReached) as read:
                    if accepted:
                        with self.assertRaises(ManifestReached):
                            main()
                        read.assert_called_once()
                    else:
                        with self.assertRaises(SystemExit) as stopped:
                            main()
                        self.assertEqual(stopped.exception.code, 2)
                        read.assert_not_called()
                        self.assertIn("--seeds must contain unique values", stderr.getvalue())
            self.assertEqual(output.read_text(), "preserve-existing-result")

    def test_default_seeds(self):
        self.exercise([], True)

    def test_original_five_seeds(self):
        self.exercise(["--seeds", "0", "1", "2", "3", "4"], True)

    def test_unique_nonascending_seeds(self):
        self.exercise(["--seeds", "4", "2", "0"], True)

    def test_single_seed(self):
        self.exercise(["--seeds", "3"], True)

    def test_adjacent_duplicate(self):
        self.exercise(["--seeds", "1", "1"], False)

    def test_nonadjacent_duplicate(self):
        self.exercise(["--seeds", "0", "1", "2", "0"], False)

    def test_integer_equivalent_duplicate(self):
        self.exercise(["--seeds", "01", "1"], False)


if __name__ == "__main__":
    unittest.main()
