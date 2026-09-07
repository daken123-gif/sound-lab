import copy
import itertools
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import onset_audit as audit


def doc(events, kind="candidate"):
    return {"schema_version": 1, "source_sha256": "a"*64, "scope_seconds": [0, 10],
            "reference_kind": kind, "provenance": "unit test fixture", "onsets_seconds": events}


class MatchingTests(unittest.TestCase):
    def test_identity(self):
        r = audit.compare([1,2], [1,2], 15, True)
        self.assertEqual(r["metrics"]["f1"], 1)

    def test_one_to_one_duplicate(self):
        r = audit.compare([1], [1,1], 15, True)
        self.assertEqual(r["metrics"]["precision"], .5)
        self.assertEqual(r["estimate_only_seconds"], [1])

    def test_both_empty_not_perfect(self):
        r = audit.compare([], [], 15, True)
        self.assertEqual(r["status"], "no_reference_events")
        self.assertIsNone(r["metrics"]["f1"])

    def test_missed_all(self):
        r = audit.compare([1,2], [], 15, True)
        self.assertEqual(r["metrics"]["recall"], 0)

    def test_extra_all(self):
        self.assertEqual(audit.compare([], [1,2], 15)["estimate_only_seconds"], [1,2])

    def test_no_automatic_alignment(self):
        r = audit.compare([1,2], [1.018,2.018], 15, True)
        self.assertEqual(r["metrics"]["matched_events"], 0)

    def test_tolerance_boundary(self):
        self.assertEqual(len(audit.match([1], [1.015], .015)), 1)
        self.assertEqual(len(audit.match([1], [1.01501], .015)), 0)

    def test_minimum_error_among_maximum_matches(self):
        self.assertEqual(audit.match([1,1.01], [1.009], .015), [(1,0)])

    def test_error_sign(self):
        r = audit.compare([1], [1.005], 15)
        self.assertAlmostEqual(r["metrics"]["median_signed_error_ms"], 5)

    def test_candidate_not_accuracy(self):
        r = audit.compare_documents(doc([1]),doc([1]),15)
        self.assertNotIn("precision",r["metrics"])
        self.assertIn("agreement_f1_not_accuracy",r["metrics"])

    def test_declared_reference_accuracy(self):
        r = audit.compare_documents(doc([1],"known_events"),doc([1]),15)
        self.assertEqual(r["metrics"]["precision"],1)
        self.assertIn("not_independently_verified",r["reference_authority"])

    def test_bounded_resources(self):
        with self.assertRaises(ValueError):
            audit.match([1]*1500,[1]*1500,.015)

    def test_exhaustive_against_brute_force(self):
        # Independent enumeration of every monotone matching on small multisets.
        series = [list(c) for n in range(4) for c in itertools.combinations_with_replacement([0,.01,.025], n)]
        for a,b in itertools.product(series,repeat=2):
            best = (0,0.)
            for count in range(1,min(len(a),len(b))+1):
                for left in itertools.combinations(range(len(a)), count):
                    for right in itertools.combinations(range(len(b)), count):
                        errors=[abs(a[i]-b[j]) for i,j in zip(left,right)]
                        if all(e<=.015+1e-12 for e in errors):
                            best=max(best,(count,-sum(errors)))
            pairs=audit.match(a,b,.015)
            self.assertEqual(len(pairs),best[0])
            self.assertAlmostEqual(sum(abs(a[i]-b[j]) for i,j in pairs),-best[1])


class InputTests(unittest.TestCase):
    def test_bad_events(self):
        for values in [[float("nan")],[float("inf")],[-1],[10],[True],["1"],[2,1]]:
            with self.subTest(values=values),self.assertRaises(ValueError):
                audit.document(doc(values))

    def test_mismatched_source(self):
        b=doc([1]); b["source_sha256"]="b"*64
        with self.assertRaises(ValueError): audit.compare_documents(doc([1]),b,15)

    def test_mismatched_scope(self):
        b=doc([1]);b["scope_seconds"]=[0,9]
        with self.assertRaises(ValueError):audit.compare_documents(doc([1]),b,15)

    def test_bad_authority(self):
        with self.assertRaises(ValueError):audit.document(doc([1],"truth_because_models_agree"))

    def test_no_provenance(self):
        d=doc([1]);d["provenance"]=""
        with self.assertRaises(ValueError):audit.document(d)

    def test_invalid_tolerance(self):
        for tol in [0,-1,float("nan"),float("inf")]:
            with self.assertRaises(ValueError):audit.match([1],[1],tol)


def windows():
    return {"source_sha256":"a"*64,"scope_seconds":[0,30],"windows":[
        {"start_s":0,"end_s":10,"onset_candidates_absolute_s":[.01,1,2,3,9.99]},
        {"start_s":0,"end_s":30,"onset_candidates_absolute_s":[1,2,20]}]}


class WindowTests(unittest.TestCase):
    def test_edges_and_disputed_times(self):
        r=audit.window_audit(windows())
        c=r["comparisons"][0]
        self.assertEqual(c["reference_only_seconds"],[3])
        self.assertEqual(c["estimate_only_seconds"],[])
        self.assertEqual(c["metrics"]["agreement_f1_not_accuracy"],.8)

    def test_missing_pair(self):
        d=windows();d["windows"].pop()
        with self.assertRaises(ValueError):audit.window_audit(d)

    def test_duplicate_window(self):
        d=windows();d["windows"].append(copy.deepcopy(d["windows"][0]))
        with self.assertRaises(ValueError):audit.window_audit(d)

    def test_window_outside_scope(self):
        d=windows();d["scope_seconds"]=[0,20]
        with self.assertRaises(ValueError):audit.window_audit(d)


class CLITests(unittest.TestCase):
    def call(self,*args):
        return subprocess.run([sys.executable,str(Path(audit.__file__)),*map(str,args)],capture_output=True,text=True)

    def test_compare_cli_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); a=root/"a.json"; b=root/"b.json"; out=root/"result"
            a.write_text(json.dumps(doc([1],"known_events")));b.write_text(json.dumps(doc([1,2])))
            args=("compare",a,b,"--output-dir",out)
            self.assertEqual(self.call(*args).returncode,0)
            before=(out/"report.json").read_bytes()
            self.assertEqual(self.call(*args).returncode,2)
            self.assertEqual((out/"report.json").read_bytes(),before)
            self.assertTrue((out/"report.html").exists())

    def test_windows_cli(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/"input.json";p.write_text(json.dumps(windows()))
            r=self.call("windows",p,"--output-dir",Path(td)/"out")
            self.assertEqual(r.returncode,0,r.stderr)

    def test_malformed_json_no_output(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/"input.json";p.write_text("{oops")
            out=Path(td)/"out"
            self.assertEqual(self.call("windows",p,"--output-dir",out).returncode,2)
            self.assertFalse(out.exists())

    def test_html_escape(self):
        r=audit.compare_documents(doc([1]),doc([1]),15)
        r["reference_provenance"]="<script>alert(1)</script>"
        page=audit.render(r)
        self.assertNotIn("<script>",page)
        self.assertIn("&lt;script&gt;",page)


if __name__=="__main__": unittest.main()
