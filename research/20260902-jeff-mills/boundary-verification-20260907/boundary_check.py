"""Measure source evidence around candidate gaps; do not equate contour gaps to rests."""
import json,hashlib,subprocess
from pathlib import Path
import numpy as np
from scipy.signal import stft, find_peaks
root=Path('music-findings');notes=json.loads((root/'resynthesis-results.json').read_text())['notes']
p=Path('evolution-audio/428aaaf9341b3d453b977800c1aa65ef92979118483b84c8df0ce1d89e3078a2.mp3');assert hashlib.sha256(p.read_bytes()).hexdigest()==p.stem
sr=44100
raw=subprocess.check_output(['ffmpeg','-v','error','-xerror','-i',str(p),'-ss','613','-t','19','-ar',str(sr),'-ac','1','-f','f32le','pipe:1'])
x=np.frombuffer(raw,dtype='<f4').astype(float)
# Original spectral energy at the observed F component, not a claimed F fundamental.
analyses=[]
for size in [2048,4096,8192]:
 f,t,z=stft(x,fs=sr,nperseg=size,noverlap=size-128);t=t+613
 amp=np.sqrt(np.sum(abs(z[(f>=335)&(f<=362)])**2,axis=0))
 def med(a,b):
  v=amp[(t>=a)&(t<b)];return float(np.median(v)) if len(v) else None
 def db(v):return float(20*np.log10(max(v,1e-15)))
 spans=[n for n in notes if n['midi_pitch']==65]
 gaps=[]
 for prev,nxt in zip(spans,spans[1:]):
  a,b=prev['end_s'],nxt['start_s'];m=med(a,b)
  before=med(max(prev['start_s'],a-.2),a);after=med(b,min(nxt['end_s'],b+.2))
  gaps.append({'start_s':a,'end_s':b,'gap_ms':(b-a)*1000,'gap_median_db':db(m) if m is not None else None,'adjacent_median_db':db(np.sqrt(before*after)),'gap_relative_db':db(m/np.sqrt(before*after)) if m is not None else None,'shorter_than_window':b-a<size/sr})
 bins=[{'start_s':s,'end_s':s+.5,'f_component_db':db(med(s,s+.5))} for s in np.arange(615,630,.5)]
 peaks,_=find_peaks(amp,distance=round(.8*sr/128),prominence=float(amp.max())*.15)
 peaks=peaks[(t[peaks]>=615)&(t[peaks]<625)]
 modulation={'peak_times_s':t[peaks].tolist(),'peak_intervals_s':np.diff(t[peaks]).tolist()}
 analyses.append({'modulation':modulation,'window_samples':size,'window_ms':size/sr*1000,'gaps':gaps,'half_second_bins':bins})
r={'source_sha256':p.stem,'band_hz':[335,362],'method':'STFT Hann defaults, hop128, original mono; absolute dB is STFT band amplitude, not waveform dBFS','source_range_s':[613,632],'analysis':analyses,'limits':'Narrow-band time smearing prevents resolving very short gaps; energy continuity alone cannot prove same instrument or no reattack.'}
(root/'boundary-results.json').write_text(json.dumps(r,indent=2)+'\n')
for a in analyses:
 print('window',a['window_samples'])
 for g in a['gaps']:print(round(g['start_s'],3),round(g['end_s'],3),round(g['gap_relative_db'],2) if g['gap_relative_db'] is not None else None,g['shorter_than_window'])
