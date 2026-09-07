"""Attack-rise alternative, tested on the same fixtures without changing common code."""
import json
from pathlib import Path
import numpy as np
from scipy.signal import find_peaks
from rhythm_probe import synth,score,detect
import sys
sys.path.insert(0,str(Path('source-main/research/music-analysis').resolve()))
from calibrate_analyzer import onset_times,SR

def attack(x,sr):
    if x.ndim==2:x=x.mean(axis=1)
    frame=512;hop=64;lag=7
    f=np.lib.stride_tricks.sliding_window_view(x,frame)[::hop]
    e=np.sqrt(np.mean(f.astype(float)**2,axis=1))
    if e.max()<1e-10:return np.array([])
    prev=np.r_[np.repeat(e[0],lag),e[:-lag]]
    novelty=np.maximum(0,(e-prev)/(prev+.10*e.max()))
    peaks,_=find_peaks(novelty,height=.7,prominence=.4,distance=round(.020*sr/hop))
    return (peaks*hop+frame/2)/sr

def main():
    cases=[('sixteenth',np.arange(.5,9.5,60/117.45/4),'tone'),('thirtysecond',np.arange(.5,9.5,60/117.45/8),'tone'),('noise_roll',np.arange(.5,9.5,60/117.45/8),'noise'),('low_pulses',np.arange(.5,9.5,.5),'low'),('ringing_single_hits',np.arange(.5,9.5,.5),'ring'),('flams_30ms',np.sort(np.r_[np.arange(.5,9,.5),np.arange(.5,9,.5)+.03]),'tone'),('silence',np.array([]),'tone')]
    rows=[]
    for name,t,kind in cases:
        x=synth(t,SR,kind)
        rows.append(dict(name=name,old_frame_midpoint=score(t,onset_times(x,SR)+512/SR),attack_rise=score(t,attack(x,SR))))
    Path('precision-study/round2/attack-results.json').write_text(json.dumps(rows,indent=2)+'\n')
    print(json.dumps(rows,indent=2))
if __name__=='__main__':main()
