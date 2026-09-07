"""Fit competing pulse grids on 570-580 s; evaluate unchanged grids on 580-590 s."""
import sys,json,subprocess,hashlib
from pathlib import Path
import numpy as np
from scipy.signal import butter,sosfiltfilt
from scipy.io import wavfile
sys.path.insert(0,str(Path('source-main/research/music-analysis').resolve()))
from calibrate_analyzer import onset_envelope,SR
p=Path('evolution-audio/428aaaf9341b3d453b977800c1aa65ef92979118483b84c8df0ce1d89e3078a2.mp3')
assert hashlib.sha256(p.read_bytes()).hexdigest()==p.stem
raw=subprocess.check_output(['ffmpeg','-v','error','-xerror','-i',str(p),'-ss','568','-t','24','-ar',str(SR),'-ac','2','-f','f32le','pipe:1'])
a=np.frombuffer(raw,dtype='<f4').reshape(-1,2).astype(float)
mono=a.mean(axis=1)
out=Path('precision-study/round2');rows=[]
for band,limits in [('full',None),('low',[30,180]),('mid',[180,1500]),('high',[1500,12000])]:
    x=mono if limits is None else sosfiltfilt(butter(4,limits,btype='bandpass',fs=SR,output='sos'),mono)
    env=onset_envelope(x)
    times=np.arange(len(env))*256/SR+568+512/SR
    for bpm in [58.725,78.3,117.45]:
        period=60/bpm
        phases=np.arange(0,period,.002)
        def value(phase,start,end):
            grid=570+phase+np.arange(-30,60)*period;grid=grid[(grid>=start)&(grid<end)]
            return float(np.mean(np.interp(grid,times,env)))
        train=np.array([value(ph,570,580) for ph in phases]);k=int(train.argmax());phase=float(phases[k])
        held=np.array([value(ph,580,590) for ph in phases]);score=float(held[k]);percentile=float(np.mean(held<=score))
        rows.append(dict(band=band,bpm_candidate=bpm,phase_after_570_s=phase,training_score=float(train[k]),heldout_score=score,heldout_phase_rank_fraction=percentile,heldout_best_phase_s=float(phases[int(held.argmax())])))
        if band=='full':
            y=np.zeros(20*SR);t=np.arange(int(.025*SR))/SR;click=.22*np.sin(2*np.pi*1800*t)*np.exp(-150*t)
            grid=phase+np.arange(60)*period;grid=grid[grid<20]
            for ev in grid:
                i=int(ev*SR);n=min(len(click),len(y)-i);y[i:i+n]+=click[:n]
            wavfile.write(str(out/f'pulse-{bpm}.wav'),SR,(y*32767).astype(np.int16))
            original=a[2*SR:22*SR]
            overlay=original*.7+y[:,None]
            wavfile.write(str(out/f'comparison-{bpm}.wav'),SR,(np.clip(overlay,-1,1)*32767).astype(np.int16))
r=dict(source_sha256=p.stem,training_seconds=[570,580],heldout_seconds=[580,590],phase_step_s=.002,method='fixed periodic-grid mean envelope sampling; frame midpoint timestamps; bandpass with 2s context',limitations=['Not beat or downbeat validation','Phase percentile is descriptive, not a p-value','Period candidates selected from prior same-recording observations; heldout only for phase fitting','More than one harmonic grid may fit; no automatic winner','Filtered bands are not instruments or separated stems','No perceptual listening validation'],results=rows)
(out/'pulse-results.json').write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps(rows,indent=2))
