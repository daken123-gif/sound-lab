import json,hashlib,subprocess
from pathlib import Path
import importlib.metadata as md
import numpy as np
import basic_pitch
from basic_pitch.inference import predict
root=Path('music-findings/basic-pitch-result');root.mkdir(exist_ok=True)
p=Path('evolution-audio/428aaaf9341b3d453b977800c1aa65ef92979118483b84c8df0ce1d89e3078a2.mp3')
assert hashlib.sha256(p.read_bytes()).hexdigest()==p.stem
wav=root/'source.wav'
subprocess.run(['ffmpeg','-v','error','-y','-i',str(p),'-ss','615','-t','15','-ar','22050','-ac','1',str(wav)],check=True)
model=next(Path(basic_pitch.__file__).parent.rglob('*.onnx'))
out,midi,notes=predict(wav,model)
midi.write(str(root/'candidate.mid'))
import scipy.io.wavfile
scipy.io.wavfile.write(root/'candidate.wav',22050,midi.synthesize(fs=22050).astype(np.float32))
rows=[{'start_s':float(n[0])+615,'end_s':float(n[1])+615,'midi_pitch':int(n[2]),'amplitude':float(n[3]),'pitch_bends':np.asarray(n[4]).tolist() if n[4] is not None else None} for n in notes]
r={'source_sha256':p.stem,'scope_seconds':[615,630],'basic_pitch_version':md.version('basic-pitch'),'onnxruntime_version':md.version('onnxruntime'),'model_sha256':hashlib.sha256(model.read_bytes()).hexdigest(),'parameters':'predict defaults, ONNX model, mono22050','notes':rows,'status':'unverified automatic transcription of mixed recording; instrument assignments and physical attacks not established','synthesis':'pretty_midi sine synthesis, diagnostic pitch/timing playback, not original timbre'}
(root/'notes.json').write_text(json.dumps(r,indent=2)+'\n')
print('NOTES',len(rows));print(json.dumps(rows[:12]))
