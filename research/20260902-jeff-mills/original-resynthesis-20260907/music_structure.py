import sys,json,subprocess,hashlib
from pathlib import Path
import numpy as np
import essentia,essentia.standard as es
sys.path.insert(0,str(Path('source-main/research/music-analysis').resolve()))
from essentia_compare import rhythm
p=Path('evolution-audio/428aaaf9341b3d453b977800c1aa65ef92979118483b84c8df0ce1d89e3078a2.mp3')
assert hashlib.sha256(p.read_bytes()).hexdigest()==p.stem
raw=subprocess.check_output(['ffmpeg','-v','error','-xerror','-i',str(p),'-ss','540','-t','120','-ar','44100','-ac','1','-f','f32le','pipe:1'])
x=np.frombuffer(raw,dtype='<f4').copy();sr=44100
rows=[]
for start in [540,570,600,630]:
 a=x[(start-540)*sr:(start-510)*sr]
 rows.append(dict(start_s=start,end_s=start+30,rhythm=rhythm(a)))
 print(rows[-1],flush=True)
# Selected for mid-band rise while low band falls (615 s), not a presumed solo.
a=x[60*sr:100*sr]
pitch,confidence=es.PredominantPitchMelodia()(es.EqualLoudness()(a))
notes=[];voiced=pitch>0
midi=np.full(len(pitch),-100);midi[voiced]=np.rint(69+12*np.log2(pitch[voiced]/440)).astype(int)
start=0
for i in range(1,len(midi)+1):
 if i==len(midi) or midi[i]!=midi[start]:
  if midi[start]>0 and (i-start)*128/sr>=.10:
   notes.append(dict(start_s=600+start*128/sr,end_s=600+i*128/sr,midi_candidate=int(midi[start]),median_frequency_hz=float(np.median(pitch[start:i])),median_confidence=float(np.median(confidence[start:i]))))
  start=i
r=dict(source_sha256=p.stem,essentia_version=essentia.__version__,rhythm_windows=rows,pitch_method='PredominantPitchMelodia defaults after EqualLoudness; only contiguous rounded-pitch runs >=100ms; not polyphonic transcription',pitch_scope=[600,640],pitch_frame_hop=128,pitch_candidates=notes,voiced_fraction=float(voiced.mean()))
Path('music-findings/music-structure.json').write_text(json.dumps(r,indent=2)+'\n')
print('Pitch runs',len(notes),'voiced',voiced.mean(),flush=True)
print(notes,flush=True)
