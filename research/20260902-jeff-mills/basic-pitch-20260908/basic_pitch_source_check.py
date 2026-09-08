import json
from pathlib import Path
import numpy as np
from scipy.io import wavfile
from scipy.signal import stft
root=Path('music-findings/basic-pitch-result')
sr,x=wavfile.read(root/'source.wav');x=x.astype(float)/32768
f,t,z=stft(x,fs=sr,nperseg=8192,noverlap=8192-128,boundary=None)
power=abs(z)**2;t+=615
r=json.loads((root/'notes.json').read_text());rows=[]
for n in sorted(r['notes'],key=lambda a:a['start_s']):
 hz=440*2**((n['midi_pitch']-69)/12)
 use=(t>=n['start_s'])&(t<n['end_s'])
 if not use.any():continue
 spectrum=np.median(power[:,use],axis=1)
 target=(f>=hz*2**(-.5/12))&(f<=hz*2**(.5/12))
 if not target.any():target[np.argmin(abs(f-hz))]=True
 surround=(f>=hz*2**(-2/12))&(f<=hz*2**(2/12))&~target
 peak=int(np.flatnonzero(target)[np.argmax(spectrum[target])])
 contrast=10*np.log10((spectrum[peak]+1e-20)/(np.median(spectrum[surround])+1e-20)) if surround.any() else None
 rows.append({**{k:n[k] for k in ['start_s','end_s','midi_pitch','amplitude']},'target_hz':hz,'local_peak_bin_hz':float(f[peak]),'contrast_db':float(contrast) if contrast is not None else None})
out={'source_sha256':r['source_sha256'],'scope_seconds':[615,630],'method':'Original mono waveform STFT8192 hop128 Hann; median power over each predicted interval. Max bin within half semitone vs median surrounding +/-2 semitone bins.','limits':'372ms window smears short notes; spectral presence can be harmonic, not independent fundamental or attack evidence. No acceptance threshold.','notes':rows}
(root/'source-check.json').write_text(json.dumps(out,indent=2)+'\n')
for pitch in [55,57,60,62,65,67,72,79]:
 a=[n for n in rows if n['midi_pitch']==pitch]
 print(pitch,len(a),'median contrast',round(float(np.median([n['contrast_db'] for n in a if n['contrast_db'] is not None])),2))
print('A3 candidates', [n for n in rows if n['midi_pitch']==57])
