import sys,json,hashlib,subprocess
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path('source-main/research/music-analysis').resolve()))
from calibrate_analyzer import SR,onset_times,periodicity_candidates,rms_dbfs,clicks
p=Path('evolution-audio/428aaaf9341b3d453b977800c1aa65ef92979118483b84c8df0ce1d89e3078a2.mp3')
assert hashlib.sha256(p.read_bytes()).hexdigest()==p.stem
raw=subprocess.check_output(['ffmpeg','-v','error','-xerror','-i',str(p),'-ss','570','-t','90','-ar',str(SR),'-ac','2','-f','f32le','pipe:1'])
a=np.frombuffer(raw,dtype='<f4').reshape(-1,2)
rows=[]
for width in (10,20,30):
 for start in range(570,661-width,5):
  x=a[(start-570)*SR:(start-570+width)*SR]
  rows.append(dict(start_s=start,end_s=start+width,rms_dbfs=rms_dbfs(x),periodicity_candidates=periodicity_candidates(x,SR),onset_candidates_absolute_s=(onset_times(x,SR)+start).tolist()))
checks=[]
for subdivision in (4,8):
 step=60/117.45/subdivision
 times=np.arange(.5,9.5,step)
 detected=onset_times(clicks([(float(t),1000.) for t in times],10),SR)
 checks.append(dict(subdivisions_per_quarter=subdivision,true_events=len(times),detected_events=len(detected),spacing_ms=step*1000,meaning='Synthetic capacity diagnostic, not ground truth for recording'))
r=dict(source_sha256=p.stem,scope_seconds=[570,660],method='Existing calibrated extractor unchanged; overlapping window sensitivity, not independent methods',extractor_sha256=hashlib.sha256(Path('source-main/research/music-analysis/calibrate_analyzer.py').read_bytes()).hexdigest(),sample_rate=SR,onset_minimum_distance_ms=80,frame_ms=1024/SR*1000,hop_ms=256/SR*1000,capacity_checks=checks,windows=rows)
Path('precision-study/results.json').write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps(checks))
for row in rows:
 if row['start_s'] in (590,600,610,620,630):print(row['start_s'],row['end_s'],round(row['rms_dbfs'],2),row['periodicity_candidates'][:4])
