"""Run with python -m unittest test_phase_input_validation (no audio imports)."""
import ast
import math
from pathlib import Path
import unittest
import numpy as np
from phase_input_validation import validate_phase_inputs

ROOT = Path(__file__).parent

def functions(name, names, namespace):
    tree = ast.parse((ROOT / name).read_text())
    selected = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name in names]
    exec(compile(ast.Module(body=selected, type_ignores=[]), name, 'exec'), namespace)
    return namespace

class ValidationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        ns = {'np': np, 'validate_phase_inputs': validate_phase_inputs}
        functions('reliability_audit.py', ['pulse_family', 'classify_bpm'], ns)
        a = functions('blind20_audit.py', ['bpm_family_distance', 'classify'], dict(ns))
        b = functions('demucs_blind20_audit.py', ['classify'], dict(ns))
        cls.blind = staticmethod(a['classify']); cls.demucs = staticmethod(b['classify'])

    def inputs(self):
        full = {'bpm_candidate':100.,'beat_confidence':2.,'triplet_spacing_score':.3,'binary_spacing_score':.4,'phase_entropy_0_concentrated_1_diffuse':.6}
        return full, [dict(full) for _ in range(3)]

    def test_normal_contract(self):
        f, w = self.inputs()
        for result in [self.blind(f,f,w,w), self.demucs(f,w)]:
            self.assertEqual(result, ('stable_intermediate',['passed_reliability_gate_but_did_not_meet_extreme_pattern_rules']))

    def test_nonfinite_all_consumed_fields(self):
        for location in ['full','window']:
            f,w=self.inputs()
            fields = list(f) if location=='full' else [k for k in f if not k.startswith('phase_entropy')]
            for field in fields:
                for value in [float('nan'),float('inf'),-float('inf')]:
                    with self.subTest(location=location,field=field,value=value):
                        f,w=self.inputs();(f if location=='full' else w[0])[field]=value
                        with self.assertRaises(ValueError):self.blind(f,f,w,w)
                        if not (location=='full' and field=='bpm_candidate'):
                            with self.assertRaises(ValueError):self.demucs(f,w)

    def test_nonpositive_bpm(self):
        for value in [0,-1]:
            f,w=self.inputs();w[0]['bpm_candidate']=value
            with self.assertRaises(ValueError):self.blind(f,f,w,w)
            with self.assertRaises(ValueError):self.demucs(f,w)
            f,w=self.inputs();f['bpm_candidate']=value
            with self.assertRaises(ValueError):self.blind(f,f,w,w)

    def test_unused_fields(self):
        f,w=self.inputs();del f['bpm_candidate']
        for row in w:del row['phase_entropy_0_concentrated_1_diffuse']
        self.assertEqual(self.demucs(f,w)[0],'stable_intermediate')
        f['bpm_candidate']=100
        self.assertEqual(self.blind(f,f,w,w)[0],'stable_intermediate')

    def test_bad_and_missing_values(self):
        for value in [None,True,{},'not a number']:
            f,w=self.inputs();f['beat_confidence']=value
            with self.assertRaises(ValueError):self.blind(f,f,w,w)
            with self.assertRaises(ValueError):self.demucs(f,w)
        f,w=self.inputs();del w[0]['bpm_candidate']
        with self.assertRaises(ValueError):self.demucs(f,w)

    def test_numeric_string_compatibility(self):
        f,w=self.inputs();f={k:str(v) for k,v in f.items()};w=[{k:str(v) for k,v in row.items()} for row in w]
        self.assertEqual(self.blind(f,f,w,w)[0],'stable_intermediate')
        self.assertEqual(self.demucs(f,w)[0],'stable_intermediate')

    def test_validation_precedes_bpm_call(self):
        def bomb(_):raise AssertionError('BPM executed before validation')
        ns={'validate_phase_inputs':validate_phase_inputs,'classify_bpm':bomb}
        functions('demucs_blind20_audit.py',['classify'],ns)
        f,w=self.inputs();w[0]['bpm_candidate']=0
        with self.assertRaises(ValueError):ns['classify'](f,w)

if __name__=='__main__': unittest.main()
