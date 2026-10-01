"""Reproduce the excerpt audit: python analyze.py INPUT.m4a OUTPUT_DIRECTORY.
No download, audio export, beat/bar inference, or full-track offset inference.
"""
import sys, json, hashlib, subprocess
from pathlib import Path
import numpy as np
import scipy
from scipy.signal import find_peaks
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
src, out = Path(sys.argv[1]), Path(sys.argv[2]); out.mkdir(parents=True, exist_ok=True)
expected='ab5d3f767f96e3d62e4abd494654e75974f2579542e113ae8fc0a20d59ebc751'
assert hashlib.sha256(src.read_bytes()).hexdigest()==expected, 'Different source asset'
p=subprocess.run(['ffmpeg','-v','error','-i',str(src),'-ac','1','-ar','22050','-f','f32le','pipe:1'],capture_output=True,check=True)
x=np.frombuffer(p.stdout,dtype='<f4').astype(float); sr=22050; n=2048; hop=256
frames=np.lib.stride_tricks.sliding_window_view(x,n)[::hop]
t=(np.arange(len(frames))*hop+n/2)/sr
mag=np.abs(np.fft.rfft(frames*np.hanning(n),axis=1)); power=mag**2
freq=np.fft.rfftfreq(n,1/sr)
centroid=(power@freq)/np.maximum(power.sum(axis=1),1e-20)
rms=20*np.log10(np.maximum(np.sqrt((frames**2).mean(axis=1)),1e-12))
norm=mag/np.maximum(mag.sum(axis=1,keepdims=True),1e-20)
flux=np.r_[0,np.maximum(np.diff(norm,axis=0),0).sum(axis=1)]
def peaks(z):
 med=np.median(z); mad=np.median(np.abs(z-med))
 return find_peaks(z,height=med+2*mad,prominence=mad,distance=int(np.ceil(.055*sr/hop)))[0]
global_peaks=peaks(flux)
rows=[]
for a,b in [(0,30),(30,60),(60,len(x)/sr)]:
 mask=(t>=a)&(t<b); z=flux[mask]
 rows.append({'start_s':a,'end_s':b,'rms_median_dbfs':float(np.median(rms[mask])), 'centroid_median_hz':float(np.median(centroid[mask])), 'normalized_flux_median':float(np.median(z)), 'normalized_flux_p90':float(np.quantile(z,.9)), 'global_threshold_events':int(np.sum((t[global_peaks]>=a)&(t[global_peaks]<b))), 'local_threshold_events':len(peaks(z))})
result={'source_sha256':expected,'bytes':src.stat().st_size,'decoded_seconds':len(x)/sr,'source_url':'https://audio-ssl.itunes.apple.com/itunes-assets/AudioPreview125/v4/39/76/71/39767108-ea57-c4a2-b8cf-a3dc0d605e99/mzaf_9828120821841368842.plus.aac.ep.m4a','catalog_id':'420210312','isrc_from_prior_catalog':'GBBPW9400118','full_track_offset':None,'method':{'sample_rate':sr,'frame':n,'hop':hop,'centroid':'power weighted','flux':'positive L1-normalized magnitude difference','peaks':'median + 2 MAD, prominence MAD, distance >=55ms','local_threshold':'recomputed separately inside each 30s window; boundary prominence differs'},'versions':{'numpy':np.__version__,'scipy':scipy.__version__,'ffmpeg':subprocess.check_output(['ffmpeg','-version'],text=True).splitlines()[0]},'windows':rows}
(out/'results.json').write_text(json.dumps(result,indent=2)+'\n')
plt.rcParams.update({'font.size':11,'axes.spines.top':False,'axes.spines.right':False})
fig,axs=plt.subplots(3,1,figsize=(10,8),sharex=True,layout='constrained')
for ax,values,label,color in zip(axs,[rms,centroid,flux],['Level (dBFS)','Spectral centroid (Hz)','Normalized spectral change'],['#146b8c','#b45309','#7555aa']):
 bins=np.arange(0,90,1); med=[np.median(values[(t>=a)&(t<a+1)]) for a in bins]
 ax.plot(bins+.5,med,color=color,linewidth=2);ax.set_ylabel(label); ax.grid(alpha=.2)
 for v in [30,60]:ax.axvline(v,color='grey',ls='--',alpha=.6)
axs[-1].set_xlabel('Seconds within this 90-second preview (NOT full-track time)')
fig.suptitle('Flutter: fewer detected attacks, but continuing sound\nGB EPs 1991-2002 | 1-second medians',fontsize=15)
fig.savefig(out/'transition.png',dpi=130);plt.close(fig)
print(json.dumps(rows,indent=2))
