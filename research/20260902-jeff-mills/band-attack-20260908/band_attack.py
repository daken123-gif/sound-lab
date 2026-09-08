"""Local source-band growth at disputed anchors; not instrument transcription."""
import hashlib,json,subprocess
from pathlib import Path
import numpy as np
from scipy.signal import butter,sosfiltfilt
sr=44100
p=Path('evolution-audio/428aaaf9341b3d453b977800c1aa65ef92979118483b84c8df0ce1d89e3078a2.mp3')
assert hashlib.sha256(p.read_bytes()).hexdigest()==p.stem
x=np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-xerror','-i',str(p),'-ss','619','-t','12','-ar',str(sr),'-ac','2','-f','f32le','pipe:1']),dtype='<f4').reshape(-1,2).astype(float)
bands={'low':[30,180],'mid':[180,1500],'high':[1500,10000]}
signals={k:sosfiltfilt(butter(4,v,btype='bandpass',fs=sr,output='sos'),x,axis=0) for k,v in bands.items()}
events=json.loads(Path('music-findings/onset-cause.json').read_text())['lost_events']
rows=[]
for e in events:
 anchor=e['time_s']+512/sr
 measures={}
 for name,a in signals.items():
  measures[name]={}
  for ms in [10,20,40]:
   i=round((anchor-619)*sr);w=round(ms*.001*sr)
   pre=np.mean(a[i-w:i]**2,axis=0);post=np.mean(a[i:i+w]**2,axis=0)
   measures[name][str(ms)]={'left_growth_db':float(10*np.log10((post[0]+1e-15)/(pre[0]+1e-15))),'right_growth_db':float(10*np.log10((post[1]+1e-15)/(pre[1]+1e-15))),'stereo_growth_db':float(10*np.log10((sum(post)+1e-15)/(sum(pre)+1e-15)))}
 robust=[k for k,m in measures.items() if all(m[str(ms)][ch]>3 for ms in [10,20,40] for ch in ['left_growth_db','right_growth_db'])]
 rows.append({'original_frame_start_s':e['time_s'],'frame_center_anchor_s':anchor,'measurements':measures,'bands_above_3db_both_channels_all_three_spans':robust})
r={'source_sha256':p.stem,'bands_hz':bands,'method':'Fourth-order Butterworth bandpass, forward-backward filtering; per-channel mean square in fixed adjacent pre/post spans of 10,20,40ms around original RMS frame center. No peak search or optimization of anchor.','criterion':'Exploratory >3dB growth in both channels at all three spans; not calibrated physical-attack classification.','limitations':['Zero-phase filtering smears transients, especially low frequencies.','Same source and selected RMS candidates; not independent ground truth.','Growth can be modulation/interference; does not identify instrument, player, or exact onset.'],'events':rows}
Path('music-findings/band-attack.json').write_text(json.dumps(r,indent=2)+'\n')
for row in rows:
 print(round(row['frame_center_anchor_s'],4),row['bands_above_3db_both_channels_all_three_spans'],{k:round(v['20']['stereo_growth_db'],2) for k,v in row['measurements'].items()})
