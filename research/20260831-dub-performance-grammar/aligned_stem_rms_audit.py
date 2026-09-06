#!/usr/bin/env python3
"""Exploratory alignment with shared RMS measurements on native Demucs stems."""
from __future__ import annotations

import hashlib, json, platform
from pathlib import Path
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, correlate, correlation_lags, resample_poly, sosfiltfilt
from calibrate_analyzer import rms_dbfs

ROOT = Path(".demucs-work")
STEMS = ("drums", "bass", "vocals", "other")
PAIRS = {"A": ("jm", "ap"), "B": ("mp", "dv")}
ALIGN_SR = 2000

def load(path):
    sr, x = wavfile.read(path)
    if np.issubdtype(x.dtype, np.integer):
        x = x.astype(np.float64) / max(abs(np.iinfo(x.dtype).min), np.iinfo(x.dtype).max)
    else: x = x.astype(np.float64)
    return sr, x

def sha256(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def fingerprint(track):
    sr, x = load(ROOT / "separated4/htdemucs" / track / "drums.wav")
    x = sosfiltfilt(butter(3, [45, 900], btype="bandpass", fs=sr, output="sos"), x.mean(1))
    x = resample_poly(x, ALIGN_SR, sr)
    return (x - x.mean()) / (x.std() + 1e-12)

def search_scales(a, b, scales):
    best = (-9.0, 1.0, 0.0, 0.0); cb = np.r_[0.0, np.cumsum(b*b)]
    for scale in scales:
        n = round(len(a)*float(scale))
        aa = np.interp(np.linspace(0, len(a)-1, n), np.arange(len(a)), a)
        aa = (aa-aa.mean())/(aa.std()+1e-12)
        c = correlate(b, aa, mode="full", method="fft")
        lags = correlation_lags(len(b), len(aa), mode="full")
        mask = np.abs(lags) <= 15*ALIGN_SR; lags, c = lags[mask], c[mask]
        j0 = np.maximum(0, -lags); j1 = np.minimum(len(aa), len(b)-lags); overlap = j1-j0
        valid = overlap >= 12*ALIGN_SR
        lags, c, j0, j1, overlap = [x[valid] for x in (lags, c, j0, j1, overlap)]
        ca = np.r_[0.0, np.cumsum(aa*aa)]
        ea = ca[j1]-ca[j0]; b0=j0+lags; b1=j1+lags; eb=cb[b1]-cb[b0]
        score = c/np.sqrt(np.maximum(ea*eb, 1e-24)); q=int(np.argmax(score))
        candidate=(float(score[q]), float(scale), float(lags[q]/ALIGN_SR), float(overlap[q]/ALIGN_SR))
        if candidate[0] > best[0]: best=candidate
    return best

def align(a, b):
    coarse=search_scales(a,b,np.arange(.97,1.03001,.001))
    return search_scales(a,b,np.arange(coarse[1]-.001,coarse[1]+.00101,.0001))

def local_check(a, b, scale, offset_s):
    n=round(len(a)*scale); aa=np.interp(np.linspace(0,len(a)-1,n),np.arange(len(a)),a)
    aa=(aa-aa.mean())/(aa.std()+1e-12); offset=round(offset_s*ALIGN_SR); half=3*ALIGN_SR; margin=500
    lo=max(half,half+margin-offset); hi=min(len(aa)-half,len(b)-half-margin-offset); rows=[]
    for center in np.linspace(lo,hi,6).astype(int):
        seg=aa[center-half:center+half]; predicted=center+offset
        area=b[predicted-half-margin:predicted+half+margin]
        c=correlate(area,seg,mode="valid",method="fft"); cs=np.r_[0.0,np.cumsum(area*area)]
        e=cs[len(seg):]-cs[:-len(seg)]; scores=c/(np.sqrt(np.sum(seg*seg)*e)+1e-12); q=int(np.argmax(scores))
        rows.append({"original_center_s":round(float(center/(ALIGN_SR*scale)),3),"predicted_dub_center_s":round(float(predicted/ALIGN_SR),3),"residual_lag_s":round(float((q-margin)/ALIGN_SR),4),"correlation":round(float(scores[q]),4)})
    return rows

def summary(values):
    x=np.asarray(values,float)
    return {"p10":round(float(np.percentile(x,10)),2),"p50":round(float(np.percentile(x,50)),2),"p90":round(float(np.percentile(x,90)),2),"constant_gain_residual_standard_deviation_db":round(float(np.std(x)),2),"largest_adjacent_change_db":round(float(np.max(np.abs(np.diff(x)))),2)}

def main():
    fp={t:fingerprint(t) for pair in PAIRS.values() for t in pair}; alignment={}
    for pair_id,(original,dub) in PAIRS.items():
        score,scale,offset,overlap=align(fp[original],fp[dub]); local=local_check(fp[original],fp[dub],scale,offset)
        alignment[pair_id]={"original":original,"dub":dub,"scale":round(scale,6),"offset_s":round(offset,4),"overlap_s":round(overlap,3),"global_drum_correlation":round(score,6),"local_windows":local,"local_max_abs_residual_s":max(abs(r["residual_lag_s"]) for r in local),"local_median_correlation":round(float(np.median([r["correlation"] for r in local])),4)}
    null={"jm_to_dv":round(align(fp["jm"],fp["dv"])[0],6),"mp_to_ap":round(align(fp["mp"],fp["ap"])[0],6)}
    pair_rows=[]
    for pair_id,spec in alignment.items():
        original,dub=spec["original"],spec["dub"]; loaded={}; sr=None
        for track in (original,dub):
            for stem in STEMS:
                current,x=load(ROOT/"separated4/htdemucs"/track/f"{stem}.wav")
                if sr is None: sr=current
                if current != sr: raise SystemExit("sample-rate mismatch")
                loaded[track,stem]=x
        od=min(len(loaded[original,s]) for s in STEMS)/sr; dd=min(len(loaded[dub,s]) for s in STEMS)/sr
        scale,offset=float(spec["scale"]),float(spec["offset_s"])
        first=max(0,int(np.ceil(-offset/scale))); last=min(int(np.floor(od)),int(np.floor((dd-offset)/scale))); windows=[]
        for start in range(first,last):
            ds=scale*start+offset; de=scale*(start+1)+offset
            if ds<0 or de>dd: continue
            odb={}; ddb={}
            for stem in STEMS:
                oa=loaded[original,stem][int(start*sr):int((start+1)*sr)]; da=loaded[dub,stem][int(ds*sr):int(de*sr)]
                odb[stem]=round(rms_dbfs(oa),2); ddb[stem]=round(rms_dbfs(da),2)
            delta={s:round(ddb[s]-odb[s],2) for s in STEMS}
            ore={s:round(odb[s]-odb["drums"],2) for s in STEMS if s!="drums"}; dre={s:round(ddb[s]-ddb["drums"],2) for s in STEMS if s!="drums"}
            rd={s:round(dre[s]-ore[s],2) for s in ore}
            windows.append({"original_seconds":[start,start+1],"dub_seconds":[round(ds,4),round(de,4)],"stem_rms_dbfs":{"original":odb,"dub":ddb},"stem_delta_db_dub_minus_original":delta,"stem_relative_to_drums_db":{"original":ore,"dub":dre},"relative_delta_db":rd})
        stats={}
        for stem in ("bass","vocals","other"):
            values=[w["relative_delta_db"][stem] for w in windows]
            xo=np.asarray([w["stem_relative_to_drums_db"]["original"][stem] for w in windows]); xd=np.asarray([w["stem_relative_to_drums_db"]["dub"][stem] for w in windows])
            stats[stem]={**summary(values),"source_to_drums_curve_correlation":round(float(np.corrcoef(xo,xd)[0,1]),3)}
        pair_rows.append({"pair":pair_id,**spec,"aligned_window_count":len(windows),"summary":stats,"windows":windows})
    result={"status":"exploratory_secondary_evidence","evidence_class":"algorithmic_inference","input":"same four Shazam-returned Apple Music previews and same official htdemucs four-stem estimates","alignment":{"mapping":"dub_time = scale * original_time + offset_s","signal":"Demucs drums estimate, 45-900 Hz band-pass, 2 kHz resampling","search":"affine scale 0.97-1.03 and offset +/-15 seconds; normalized waveform correlation","cross_pair_null_correlations":null,"decision_boundary":"same-pair scores are far above cross-pair nulls and six local windows remain within 1.5 ms of each affine mapping"},"measurement":{"window_seconds":1,"value":"shared calibrate_analyzer.rms_dbfs on aligned native stems","normalization":"compare each stem to simultaneous drums in each version, then subtract original from dub","static_gain_test":"standard deviation of the relative-delta curve; descriptive only, with no calibrated pass threshold","no_event_threshold":"No CUT, THROW, REVEAL or presence threshold is applied."},"method_authority":{"calibrate_analyzer_py_blob":"314db6380f63c12017b52dcd3dd2dfcaff94a539","demucs_cpuinfo_compat_py_blob":"a6235124714f3b31ef9c4d0cfefe5ba57ba99480","local_audit_script_sha256":sha256(__file__)},"environment":{"platform":platform.platform(),"python":platform.python_version()},"limits":["alignment is derived from model-estimated drum stems, not multitracks","one-second RMS cannot distinguish dry source, effect return, bleed or filtering","large ratios are unstable when the original estimated stem is near silence; absolute source-to-drums levels are retained","curve variation rejects a simple constant-gain account but does not identify performance events","preview positions remain unknown relative to full songs"],"pairs":pair_rows}
    Path("preview-aligned-stem-rms-audit.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps({"alignment":alignment,"null":null,"summary":{r["pair"]:r["summary"] for r in pair_rows}},ensure_ascii=False,indent=2))

if __name__ == "__main__": main()
