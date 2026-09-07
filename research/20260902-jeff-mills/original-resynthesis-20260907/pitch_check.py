import json,subprocess
from pathlib import Path
import numpy as np
from scipy.signal import find_peaks
p='evolution-audio/428aaaf9341b3d453b977800c1aa65ef92979118483b84c8df0ce1d89e3078a2.mp3'
raw=subprocess.check_output(['ffmpeg','-v','error','-xerror','-i',p,'-ss','615','-t','15','-ar','44100','-ac','1','-f','f32le','pipe:1'])
x=np.frombuffer(raw,dtype='<f4');sr=44100;rows=[]
for s,e in [(615.4,616.1),(616.8,617.5),(618.1,618.8),(620,620.5),(621.5,622.1),(624.55,625.1),(625.35,625.8),(627.3,628.1),(628.6,629),(629.2,629.8)]:
 a=x[round((s-615)*sr):round((e-615)*sr)]
 z=np.abs(np.fft.rfft(a*np.hanning(len(a)),n=sr*4));f=np.fft.rfftfreq(sr*4,1/sr)
 peaks,_=find_peaks(z,distance=round(5/.25));peaks=[i for i in peaks if 80<f[i]<1500];peaks=sorted(peaks,key=lambda i:z[i],reverse=True)[:12]
 rows.append({'start_s':s,'end_s':e,'peaks_hz_relative_db':[[float(f[i]),float(20*np.log10(z[i]/z[peaks[0]]))] for i in peaks]})
Path('music-findings/pitch-check.json').write_text(json.dumps(rows,indent=2)+'\n')
for r in rows:print(r)
