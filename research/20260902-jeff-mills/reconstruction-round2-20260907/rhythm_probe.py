"""Experimental onset calibration and rhythm sonification; no instrument transcription."""
import argparse, hashlib, json, sys, subprocess
from pathlib import Path
import numpy as np
from scipy.signal import find_peaks
from scipy.io import wavfile

def detect(x,sr,frame=256,hop=64,gap=.020):
    if x.ndim==2:x=x.mean(axis=1)
    frames=np.lib.stride_tricks.sliding_window_view(x,frame)[::hop]
    energy=np.sqrt(np.mean(frames.astype(float)**2,axis=1)+1e-15)
    e=np.maximum(0,np.diff(energy,prepend=energy[0]))
    scale=np.percentile(e,99)
    if scale<1e-10:return np.array([]),np.array([])
    e=e/scale
    peaks,_=find_peaks(e,height=.12,prominence=.08,distance=round(gap*sr/hop))
    return (peaks*hop+frame/2)/sr,e[peaks]

def score(truth,det):
    # Sorted one-to-one matching within the predeclared 15 ms tolerance.
    i=j=0;errors=[]
    while i<len(truth) and j<len(det):
        d=det[j]-truth[i]
        if abs(d)<=.015:errors.append(d);i+=1;j+=1
        elif d<0:j+=1
        else:i+=1
    n=len(errors)
    return dict(true_events=len(truth),detected_events=len(det),matched=n,precision=n/len(det) if len(det) else None,recall=n/len(truth) if len(truth) else None,median_absolute_error_ms=float(np.median(np.abs(errors))*1000) if n else None)

def synth(times,sr,kind='tone',seed=12):
    rng=np.random.default_rng(seed);x=np.zeros(10*sr)
    for i,t in enumerate(times):
        local=np.arange(int(.20*sr))/sr
        if kind=='noise':y=rng.normal(size=len(local))*np.exp(-local*50)
        elif kind=='low':y=np.sin(2*np.pi*(65*local+70*.03*(1-np.exp(-local/.03))))*np.exp(-local*22)
        elif kind=='ring':y=np.sin(2*np.pi*700*local)*np.exp(-local*7)*(1+.8*np.sin(2*np.pi*35*local))
        else:y=np.sin(2*np.pi*1000*local)*np.exp(-local*90)*(local<.025)
        k=int(t*sr);n=min(len(y),len(x)-k);x[k:k+n]+=y[:n]
    return x

def main():
    p=argparse.ArgumentParser();p.add_argument('--common',type=Path,required=True);p.add_argument('--audio',type=Path,required=True);p.add_argument('--out',type=Path,required=True);args=p.parse_args()
    sys.path.insert(0,str(args.common.resolve()));from calibrate_analyzer import onset_times,SR
    args.out.mkdir(parents=True,exist_ok=True)
    sha=hashlib.sha256(args.audio.read_bytes()).hexdigest()
    if sha!='428aaaf9341b3d453b977800c1aa65ef92979118483b84c8df0ce1d89e3078a2':raise ValueError('Wrong source')
    fixtures=[]
    cases=[('sixteenth',np.arange(.5,9.5,60/117.45/4),'tone'),('thirtysecond',np.arange(.5,9.5,60/117.45/8),'tone'),('noise_roll',np.arange(.5,9.5,60/117.45/8),'noise'),('low_pulses',np.arange(.5,9.5,.5),'low'),('ringing_single_hits',np.arange(.5,9.5,.5),'ring'),('flams_30ms',np.sort(np.r_[np.arange(.5,9,.5),np.arange(.5,9,.5)+.03]),'tone'),('silence',np.array([]),'tone')]
    for name,times,kind in cases:
        x=synth(times,SR,kind)
        fixtures.append(dict(name=name,old=score(times,onset_times(x,SR)),experimental=score(times,detect(x,SR)[0])))
    raw=subprocess.check_output(['ffmpeg','-v','error','-xerror','-i',str(args.audio),'-ss','570','-t','90','-ar',str(SR),'-ac','2','-f','f32le','pipe:1'])
    x=np.frombuffer(raw,dtype='<f4').reshape(-1,2)
    source=[]
    for start in range(570,660,10):
        a=x[(start-570)*SR:(start-560)*SR]
        old=onset_times(a,SR);new,strength=detect(a,SR)
        source.append(dict(start_s=start,end_s=start+10,old_absolute_s=(old+start).tolist(),experimental_absolute_s=(new+start).tolist(),experimental_strength=strength.tolist(),cross_method_matching_not_accuracy=score(old,new)))
    # Separate diagnostic renders, original samples never used in the synthesis.
    a=x[:20*SR];events,weights=detect(a,SR)
    y=np.zeros(len(a));t=np.arange(int(.018*SR))/SR;click=np.sin(2*np.pi*1200*t)*np.exp(-t*250)
    for event,w in zip(events,weights):
        i=int(event*SR);n=min(len(click),len(y)-i);y[i:i+n]+=min(float(w),2)*.2*click[:n]
    wavfile.write(str(args.out/'event-candidates.wav'),SR,(np.clip(y,-1,1)*32767).astype(np.int16))
    # Comparison listening file is scratch only, never in Git.
    overlay=a.astype(float)*.7+y[:,None]*.5
    wavfile.write(str(args.out/'original-with-event-candidates.wav'),SR,(np.clip(overlay,-1,1)*32767).astype(np.int16))
    result=dict(source_sha256=sha,scope_seconds=[570,660],script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),common_sha256=hashlib.sha256((args.common/'calibrate_analyzer.py').read_bytes()).hexdigest(),experimental_parameters=dict(frame=256,hop=64,min_gap_s=.020,height=.12,prominence=.08,timestamp='frame midpoint; not fitted to recording'),fixtures=fixtures,source_windows=source,status='EXPERIMENTAL_NOT_TRANSCRIPTION',limitations=['Synthetic tests are not recording ground truth.','Full mix events have no instrument or performer attribution.','Render is candidate sonification, not musical reconstruction.','No listening validation performed by this script.'])
    (args.out/'results.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(fixtures,indent=2))
    print('Source old/new counts',[(r['start_s'],len(r['old_absolute_s']),len(r['experimental_absolute_s'])) for r in source])
if __name__=='__main__':main()
