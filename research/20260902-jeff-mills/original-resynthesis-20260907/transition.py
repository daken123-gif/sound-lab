import hashlib,json,subprocess
from pathlib import Path
import numpy as np
from scipy.signal import butter,sosfiltfilt
p=Path('evolution-audio/428aaaf9341b3d453b977800c1aa65ef92979118483b84c8df0ce1d89e3078a2.mp3')
assert hashlib.sha256(p.read_bytes()).hexdigest()==p.stem
raw=subprocess.check_output(['ffmpeg','-v','error','-xerror','-i',str(p),'-ss','565','-t','100','-ac','2','-ar','44100','-f','f32le','pipe:1'])
x=np.frombuffer(raw,dtype='<f4').reshape(-1,2).astype(float);sr=44100
bands={'full':x}
for name,lo,hi in [('low',30,180),('mid',180,1500),('high',1500,12000)]:
 bands[name]=sosfiltfilt(butter(4,[lo,hi],btype='bandpass',fs=sr,output='sos'),x,axis=0)
rows=[]
for s in range(570,660,5):
 row={'start_s':s,'end_s':s+5}
 for name,a in bands.items():
  seg=a[(s-565)*sr:(s-560)*sr]
  row[name+'_stereo_rms_dbfs']=float(20*np.log10(np.sqrt(np.mean(seg**2))+1e-15))
 rows.append(row)
r={'source_sha256':p.stem,'method':'Stereo energy, 4th-order Butterworth forward-backward bandpass, 5-second bins; 5-second context at analysis ends. Not mono RMS from prior reports; values not directly interchangeable. Bands are not stems.','bands_hz':{'low':[30,180],'mid':[180,1500],'high':[1500,12000]},'rows':rows}
Path('music-findings/transition.json').write_text(json.dumps(r,indent=2)+'\n')
for row in rows:print(row['start_s'],*[round(row[k],2) for k in row if k!='start_s' and k!='end_s'])
