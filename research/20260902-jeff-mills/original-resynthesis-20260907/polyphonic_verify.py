import hashlib,json,subprocess
from pathlib import Path
import numpy as np
import essentia,essentia.standard as es
SR=44100;H=128
p=Path('evolution-audio/428aaaf9341b3d453b977800c1aa65ef92979118483b84c8df0ce1d89e3078a2.mp3')
assert hashlib.sha256(p.read_bytes()).hexdigest()==p.stem
raw=subprocess.check_output(['ffmpeg','-v','error','-xerror','-i',str(p),'-ss','610','-t','25','-ar',str(SR),'-ac','1','-f','f32le','pipe:1'])
x=np.frombuffer(raw,dtype='<f4').copy()
methods={'klapuri':es.MultiPitchKlapuri,'multimelodia':es.MultiPitchMelodia}
def extract(a):
 r={}
 for name,method in methods.items():
  pitches=method()(a)
  r[name]=[sorted(set(int(round(69+12*np.log2(f/440))) for f in frame if f>0)) for frame in pitches]
 return r
# Known overlap: F3 held throughout; G3 then A3, equal harmonic amplitudes.
t=np.arange(3*SR)/SR;fixture=np.zeros(len(t),dtype=np.float32)
for note,lo,hi in [(53,.25,2.75),(55,.5,1.5),(57,1.5,2.5)]:
 f=440*2**((note-69)/12);mask=(t>=lo)&(t<hi)
 for harm in range(1,5):fixture[mask]+=(.12/harm*np.sin(2*np.pi*f*harm*t[mask])).astype(np.float32)
cal=extract(fixture);validation={}
for method,frames in cal.items():
 good=total=fp=fn=0
 for i,notes in enumerate(frames):
  sec=i*H/SR
  if any(abs(sec-b)<.08 for b in [.25,.5,1.5,2.5,2.75]):continue
  truth={n for n,lo,hi in [(53,.25,2.75),(55,.5,1.5),(57,1.5,2.5)] if lo<=sec<hi}
  good+=len(set(notes)&truth);fp+=len(set(notes)-truth);fn+=len(truth-set(notes));total+=1
 validation[method]={'frame_note_precision':good/(good+fp) if good+fp else None,'frame_note_recall':good/(good+fn) if good+fn else None,'frames':total}
print('fixture',validation,flush=True)
r=extract(x)
n=min(map(len,r.values()));consensus=[sorted(set(r['klapuri'][i])&set(r['multimelodia'][i])) for i in range(n)]
notes=[]
for pitch in sorted(set(v for f in consensus for v in f)):
 start=None
 for i in range(n+1):
  on=i<n and pitch in consensus[i] and 615<=610+i*H/SR<630
  if on and start is None:start=i
  if not on and start is not None:
   if (i-start)*H/SR>=.15:notes.append({'midi_pitch':pitch,'start_s':610+start*H/SR,'end_s':610+i*H/SR})
   start=None
out={'source_sha256':p.stem,'essentia_version':essentia.__version__,'decode_range_s':[610,635],'evaluation_range_s':[615,630],'hop_samples':H,'sample_rate':SR,'fixture':validation,'methods':r,'consensus_notes':sorted(notes,key=lambda x:x['start_s']),'limits':'Method agreement is not ground truth. Shared Essentia spectral front end; no instrument attribution; 150ms contiguous runs omit short notes; no gap filling.'}
Path('music-findings/polyphonic-results.json').write_text(json.dumps(out,indent=2)+'\n')
print('consensus',out['consensus_notes'],flush=True)
