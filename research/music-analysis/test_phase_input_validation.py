"""Non-audio regression: python -m unittest test_phase_input_validation."""
import ast
from decimal import Decimal
from fractions import Fraction
from pathlib import Path
import unittest
import numpy as np
from phase_input_validation import phase_input_views
ROOT = Path(__file__).parent

def functions(name, names, namespace):
    tree = ast.parse((ROOT / name).read_text())
    selected = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in names]
    exec(compile(ast.Module(body=selected, type_ignores=[]), name, 'exec'), namespace)
    return namespace

class ValidationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        ns = {'np': np, 'phase_input_views': phase_input_views}
        functions('reliability_audit.py', ['pulse_family','classify_bpm'], ns)
        cls.blind = staticmethod(functions('blind20_audit.py',['bpm_family_distance','classify'],dict(ns))['classify'])
        cls.demucs = staticmethod(functions('demucs_blind20_audit.py',['classify'],dict(ns))['classify'])
    def inputs(self):
        f = dict(bpm_candidate=100., beat_confidence=2., triplet_spacing_score=.8,
                 binary_spacing_score=.1, phase_entropy_0_concentrated_1_diffuse=.2)
        return f,[dict(f) for _ in range(3)]
    def test_numeric_types(self):
        for convert in [float,int,str,np.float32,np.float64,Decimal,Fraction]:
            f,w=self.inputs()
            # Integers use equivalent integer-valued feature fixture.
            f.update(triplet_spacing_score=1,binary_spacing_score=0,phase_entropy_0_concentrated_1_diffuse=0)
            f={k:convert(v) for k,v in f.items()};w=[dict(f) for _ in w]
            self.assertEqual(self.demucs(f,w)[0],'triplet_spacing_reproduced')
            self.assertEqual(self.blind(f,f,w,w)[0],'triplet_spacing_reproduced')
    def test_short_circuit_unread_values(self):
        f,w=self.inputs();f['beat_confidence']=.1
        del f['phase_entropy_0_concentrated_1_diffuse'];f['triplet_spacing_score']=float('nan')
        for row in w:del row['binary_spacing_score']
        self.assertEqual(self.demucs(f,w)[0],'rejected')
        self.assertEqual(self.blind(f,f,w,w)[0],'rejected')
    def test_bad_bpm_before_folding(self):
        for value in [0,-1,float('nan'),float('inf'),-float('inf'),True,np.bool_(True),None,'bad']:
            f,w=self.inputs();w[0]['bpm_candidate']=value
            for fn,args in [(self.demucs,(f,w)),(self.blind,(f,f,w,w))]:
                with self.subTest(value=value,fn=fn),self.assertRaises(ValueError):fn(*args)
    def test_all_positions_and_causes(self):
        for model in ['A','B']:
            for i in [None,0,1,2]:
                f,w=self.inputs();g,z=self.inputs()
                row=(f if model=='A' else g) if i is None else (w if model=='A' else z)[i]
                del row['beat_confidence']
                with self.assertRaises(ValueError) as cm:self.blind(f,g,w,z)
                loc=model+'.'+('full' if i is None else f'window[{i}]')
                self.assertTrue(str(cm.exception).startswith(loc+'.beat_confidence'))
                self.assertIsInstance(cm.exception.__cause__,KeyError)
    def test_accessed_non_bpm_invalid_values(self):
        # Explicit fields, not a self-derived oracle: entropy is read only
        # on the concentrated non-triplet branch; window entropy is unused.
        cases = [('beat_confidence', .8), ('triplet_spacing_score', .8),
                 ('binary_spacing_score', .8),
                 ('phase_entropy_0_concentrated_1_diffuse', 0.)]
        for field, score in cases:
            positions = [None] if field.startswith('phase_entropy') else [None, 0, 1, 2]
            for model in ['single', 'A', 'B']:
                for index in positions:
                    for bad in [float('nan'), float('inf'), -float('inf'),
                                True, np.bool_(False), None, 'bad']:
                        f,w=self.inputs();g,z=self.inputs()
                        for row in [f,g,*w,*z]:row['triplet_spacing_score']=score
                        full,rows=(g,z) if model=='B' else (f,w)
                        row=full if index is None else rows[index]
                        row[field]=bad
                        fn,args=(self.demucs,(f,w)) if model=='single' else (self.blind,(f,g,w,z))
                        prefix='' if model=='single' else model+'.'
                        loc=prefix+('full' if index is None else f'window[{index}]')
                        with self.subTest(field=field,model=model,index=index,bad=bad):
                            with self.assertRaises(ValueError) as cm:fn(*args)
                            self.assertTrue(str(cm.exception).startswith(loc+'.'+field+':'))
    def test_unused_nonfinite_fields_remain_unread(self):
        f,w=self.inputs()
        f['bpm_candidate']=float('nan')  # Demucs never reads full BPM.
        f['phase_entropy_0_concentrated_1_diffuse']=float('nan')
        for row in w:row['phase_entropy_0_concentrated_1_diffuse']=float('nan')
        self.assertEqual(self.demucs(f,w)[0],'triplet_spacing_reproduced')
        f['bpm_candidate']=100.
        self.assertEqual(self.blind(f,f,w,w)[0],'triplet_spacing_reproduced')
    def test_generator_not_cached(self):
        f,w=self.inputs()
        self.assertEqual(self.demucs(f,iter(w))[0],'stable_intermediate')
        self.assertEqual(self.blind(f,f,iter(w),iter(w))[0],'stable_intermediate')
    def test_iterator_exception_order(self):
        f,w=self.inputs();del w[0]['bpm_candidate'];events=[]
        def rows():
            events.append('first');yield w[0]
            events.append('second');raise RuntimeError('later failure')
        with self.assertRaises(ValueError) as cm:self.demucs(f,rows())
        self.assertEqual(events,['first']);self.assertIsInstance(cm.exception.__cause__,KeyError)
    def test_conversion_count_and_runtime_error(self):
        class Number:
            def __init__(self,value):self.value=value;self.calls=0
            def __float__(self):self.calls+=1;return self.value
        f,w=self.inputs();n=Number(100.);w[0]['bpm_candidate']=n
        self.demucs(f,w);self.assertEqual(n.calls,1)
        class Bad:
            def __float__(self):raise RuntimeError('custom')
        w[0]['bpm_candidate']=Bad()
        with self.assertRaisesRegex(RuntimeError,'custom'):self.demucs(f,w)
    def test_list_iteration_not_eager(self):
        class Rows(list):
            def __iter__(self):
                self.count+=1
                if self.count==2:raise RuntimeError('second pass')
                return super().__iter__()
        f,w=self.inputs();r=Rows(w);r.count=0
        with self.assertRaisesRegex(RuntimeError,'second pass'):self.demucs(f,r)
        self.assertEqual(r.count,2)

if __name__=='__main__':unittest.main()

