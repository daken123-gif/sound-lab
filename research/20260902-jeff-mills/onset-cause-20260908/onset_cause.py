import json, hashlib, subprocess, sys
from pathlib import Path
import numpy as np
from scipy.signal import find_peaks
sys.path.insert(0,str(Path('source-main/research/music-analysis').resolve()))
from calibrate_analyzer import frame_rms, SR
p=Path('evolution-audio/428aaaf9341b3d453b977800c1aa65ef92979118483b84c8df0ce1d89e3078a2.mp3')
assert hashlib.sha256(p.read_bytes()).hexdigest()==p.stem
raw=subprocess.check_output(['ffmpeg','-v','error','-xerror','-i',str(p),'-ss','620','-t','30','-ar',str(SR),'-ac','2','-f','f32le','pipe:1'])
x=np.frombuffer(raw,dtype='<f4').reshape(-1,2)
def novelty(a):
 r=frame_rms(a);return np.maximum(0,np.diff(r,prepend=r[0]))
n10=novelty(x[:10*SR]);n30=novelty(x)
s10=float(np.percentile(n10,99));s30=float(np.percentile(n30,99))
def peaks(n,s):
 ix,props=find_peaks(n/s,height=.12,prominence=.08,distance=int(.08*SR/256))
 return {int(i):{'time_s':620+float(i)*256/SR,'rise':float(n[i]),'normalized_height':float(h),'normalized_prominence':float(p)} for i,h,p in zip(ix,props['peak_heights'],props['prominences']) if 620.1<=620+i*256/SR<629.9}
a=peaks(n10,s10);b=peaks(n30,s30);swap=peaks(n10,s30)
lost=sorted(set(a)-set(b))
rows=[]
for i in lost:
 d=dict(a[i]);d['height_with_long_scale']=d['rise']/s30;d['prominence_with_long_scale']=d['normalized_prominence']*s10/s30
 d['fails_long_height']=d['height_with_long_scale']<.12;d['fails_long_prominence']=d['prominence_with_long_scale']<.08
 rows.append(d)
r={'source_sha256':p.stem,'scope_seconds':[620.1,629.9],'experiment':'Same decoded source. Replace only 99th percentile normalization in short window with long-window value; leave peak parameters and audio unchanged.','short_scale':s10,'long_scale':s30,'scale_ratio':s30/s10,'shared_raw_novelty_max_absolute_difference':float(np.max(np.abs(n10-n30[:len(n10)]))),'short_count':len(a),'long_count':len(b),'short_with_long_scale_count':len(swap),'swap_exactly_matches_long_indices':set(swap)==set(b),'lost_events':rows,'limitations':['Causal test of detector window sensitivity, not proof of physical attacks or their absence.','Frame-start timestamps retain previous extractor timing convention.','No attribution to instrument or performer.']}
Path('music-findings/onset-cause.json').write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps({k:v for k,v in r.items() if k!='lost_events'},indent=2))
print('fail height',sum(d['fails_long_height'] for d in rows),'fail prominence',sum(d['fails_long_prominence'] for d in rows))
