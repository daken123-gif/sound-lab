"""Known synthetic notes: report errors, never treat successful execution as accuracy."""
import json
from pathlib import Path
import tempfile
import numpy as np
import soundfile as sf
import mir_eval
from transcribe import transcribe


def main():
    sr=22050
    reference=[(.5,1.3,60),(1.6,2.4,64),(2.7,3.5,67),
               (3.9,4.7,60),(3.9,4.7,64),(3.9,4.7,67)]
    x=np.zeros(sr*6)
    for start,end,pitch in reference:
        n=round((end-start)*sr); t=np.arange(n)/sr
        f=440*2**((pitch-69)/12)
        envelope=np.minimum(t/.015,1)*np.minimum((n/sr-t)/.03,1)
        tone=sum(np.sin(2*np.pi*f*h*t)/h**2 for h in range(1,6))
        i=round(start*sr);x[i:i+n]+=.18*envelope*tone
    with tempfile.TemporaryDirectory() as d:
        p=Path(d);sf.write(p/'input.wav',x.astype(np.float32),sr,subtype='FLOAT')
        r=transcribe(p/'input.wav',p/'output')
        notes=r['notes']
        ri=np.array([[a,b] for a,b,pitch in reference])
        rp=np.array([440*2**((pitch-69)/12) for a,b,pitch in reference])
        ei=np.array([[n['onset_seconds'],n['offset_seconds']] for n in notes]).reshape(-1,2)
        ep=np.array([440*2**((n['midi_pitch']-69)/12) for n in notes])
        for offset in [None,.2]:
            metrics=mir_eval.transcription.precision_recall_f1_overlap(ri,rp,ei,ep,offset_ratio=offset)
            print(json.dumps({'offset_ratio':offset,'reference_count':6,'estimate_count':len(notes),
                              'precision':metrics[0],'recall':metrics[1],'f1':metrics[2]}))
        try:
            transcribe(p/'input.wav',p/'output')
        except ValueError:
            pass
        else:
            raise AssertionError('Overwrite protection failed')
        assert len(notes)>0, 'No notes returned'
        print('Execution and readback passed; metrics above are synthetic-only.')


if __name__=='__main__':
    main()
