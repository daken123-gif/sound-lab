"""Non-audio regression tests for numerical functions; no file I/O functions executed.
Run: python -m unittest discover -s research/music-analysis -p test_separation_nonmutation.py
"""
import ast
from pathlib import Path
import unittest
import numpy as np

# Select the audited numerical functions to avoid soundfile/audio dependencies.
source = Path(__file__).with_name('evaluate_separation.py').read_text()
tree = ast.parse(source)
selected = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in {'align','cosine','rms','si_sdr'}]
assert len(selected) == 4
ns = {'np': np}
exec(compile(ast.Module(body=selected, type_ignores=[]), '<numeric-functions>', 'exec'), ns)

def reference(a,b):
    n=min(len(a),len(b))
    x=np.array(a[:n].reshape(-1),copy=True); y=np.array(b[:n].reshape(-1),copy=True)
    x-=x.mean();y-=y.mean()
    p=(x@y/(y@y+1e-18))*y
    e=x-p
    return float(10*np.log10((p@p+1e-18)/(e@e+1e-18)))

class Nonmutation(unittest.TestCase):
    def check(self,a,b,readonly=False):
        before_a,before_b=a.copy(),b.copy()
        if readonly:a.flags.writeable=False;b.flags.writeable=False
        raw=(ns['cosine'](a,b),ns['rms'](a),ns['rms'](b))
        result=ns['si_sdr'](a,b)
        self.assertTrue(np.isfinite(result))
        self.assertAlmostEqual(result,reference(before_a,before_b),places=12)
        np.testing.assert_array_equal(a,before_a);np.testing.assert_array_equal(b,before_b)
        self.assertEqual(raw,(ns['cosine'](a,b),ns['rms'](a),ns['rms'](b)))
    def test_contiguous(self):self.check(np.array([[2.],[4.]]),np.array([[1.],[3.]]))
    def test_unequal(self):self.check(np.array([[2.],[4.],[8.]]),np.array([[1.],[3.]]))
    def test_readonly(self):self.check(np.array([[2.],[4.]]),np.array([[1.],[3.]]),True)
    def test_stereo(self):self.check(np.array([[2.,6.],[4.,8.],[3.,2.]]),np.array([[1.,2.],[3.,1.],[2.,4.]]))
    def test_strided(self):self.check(np.arange(24.,dtype=float).reshape(6,4)[::2,::2],np.array([[2.,4.],[3.,1.],[0.,6.]]))
    def test_zero_mean(self):self.check(np.array([[-1.],[1.]]),np.array([[-2.],[2.]]))
    def test_silence(self):self.check(np.zeros((3,2)),np.zeros((3,2)))

if __name__=='__main__':unittest.main()
