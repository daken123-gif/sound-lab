"""Fixed error-injection comparison. Tests metric sensitivity, not ground-truth accuracy."""
import hashlib,json,subprocess,struct,csv
from pathlib import Path
import numpy as np
from scipy.signal import stft
from scipy.io import wavfile
SR=44100;D=15;root=Path('music-findings')
r=json.loads((root/'polyphonic-results.json').read_text());notes=r['consensus_notes']
p=Path('evolution-audio')/(r['source_sha256']+'.mp3');assert hashlib.sha256(p.read_bytes()).hexdigest()==r['source_sha256']
raw=subprocess.check_output(['ffmpeg','-v','error','-xerror','-i',str(p),'-ss','615','-t',str(D),'-ac','1','-ar',str(SR),'-f','f32le','pipe:1'])
x=np.frombuffer(raw,dtype='<f4').astype(float)
def synth(pitch_shift=0,time_shift=0):
 y=np.zeros(D*SR)
 for n in notes:
  lo=max(0,n['start_s']-615+time_shift);hi=min(D,n['end_s']-615+time_shift)
  if hi<=lo:continue
  i,j=round(lo*SR),round(hi*SR);t=np.arange(j-i)/SR
  f=440*2**((n['midi_pitch']+pitch_shift-69)/12)
  env=np.minimum(1,np.minimum(t/.005,(hi-lo-t)/.005))
  for h in range(1,5):y[i:j]+=.10/h*np.sin(2*np.pi*h*f*t)*env
 return y
variants={'candidate':(0,0),'semitone_up':(1,0),'semitone_down':(-1,0),'octave_down':(-12,0),'early_100ms':(0,-.1),'late_100ms':(0,.1),'early_250ms':(0,-.25),'late_250ms':(0,.25)}
ys={k:synth(*v) for k,v in variants.items()}
results={k:{} for k in variants}
for size in [2048,8192]:
 def spec(a):
  f,t,z=stft(a,fs=SR,nperseg=size,noverlap=size-256,boundary='zeros')
  return np.abs(z[(f>=80)&(f<=1760)])
 target=spec(x)
 for key,y in ys.items():
  estimate=spec(y);den=np.linalg.norm(target,axis=0)*np.linalg.norm(estimate,axis=0)
  similarity=np.divide(np.sum(target*estimate,axis=0),den,out=np.zeros_like(den),where=den>1e-12)
  results[key][str(size)]={'mean_spectral_cosine_all_frames':float(similarity.mean()),'active_synthesis_fraction':float(np.mean(np.linalg.norm(estimate,axis=0)>1e-8))}
for name in ['candidate','semitone_up','late_250ms']:
 wavfile.write(str(root/(name+'.wav')),SR,(np.clip(ys[name],-1,1)*32767).astype(np.int16))
# MIDI uses a 120 BPM timing container; not an inferred tempo. Absolute times retained in CSV.
def vlq(n):
 b=[n&127];n>>=7
 while n:b.insert(0,(n&127)|128);n>>=7
 return bytes(b)
events=[]
for n in notes:
 events.extend([(round((n['start_s']-615)*960),bytes([0x90,n['midi_pitch'],80])),(round((n['end_s']-615)*960),bytes([0x80,n['midi_pitch'],0]))])
events.sort(key=lambda q:(q[0],q[1][0]));track=b'\x00\xff\x51\x03\x07\xa1\x20';prev=0
for tick,msg in events:track+=vlq(tick-prev)+msg;prev=tick
track+=b'\x00\xff\x2f\x00'
(root/'candidate.mid').write_bytes(b'MThd'+struct.pack('>IHHH',6,0,1,480)+b'MTrk'+struct.pack('>I',len(track))+track)
with (root/'candidate-notes.csv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=['midi_pitch','start_s','end_s']);w.writeheader();w.writerows(notes)
out={'source_sha256':r['source_sha256'],'scope_s':[615,630],'notes':notes,'n_notes':len(notes),'synthesis':'4 additive harmonics 1/h, 5ms edge ramps, constant note strength, no source samples','comparison':'Magnitude STFT cosine 80–1760Hz, average includes silent synthesis frames; two preselected resolutions, no fitted timbre','variants':variants,'results':results,'claim_boundary':'Error sensitivity only. Candidate pitches selected from original, so this is not independent transcription accuracy. No real stem ground truth or listening validation. No timbre, drum or instrument reconstruction.'}
(root/'resynthesis-results.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(results,indent=2))
