"""Local audio -> candidate notes + MIDI. No download, registration or upload."""
import argparse
import hashlib
import importlib.metadata
import json
import math
from pathlib import Path
import tempfile


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def transcribe(audio, output, start=0., end=None):
    import soundfile as sf
    import pretty_midi
    from basic_pitch import build_icassp_2022_model_path, FilenameSuffix
    from basic_pitch.inference import predict
    audio, output = Path(audio), Path(output)
    if output.exists():
        raise ValueError('Output directory already exists; choose a new path')
    if not math.isfinite(start) or start < 0 or (end is not None and (not math.isfinite(end) or end <= start)):
        raise ValueError('Require finite 0 <= start < end')
    model = build_icassp_2022_model_path(FilenameSuffix.onnx)
    if not model.is_file():
        raise ValueError('Installed ONNX model missing; no automatic download')
    source_hash = sha(audio)
    with sf.SoundFile(audio) as f:
        sr, frames, channels = f.samplerate, len(f), f.channels
        duration = frames / sr
        end = duration if end is None else end
        if end > duration or start >= duration:
            raise ValueError('Requested interval exceeds audio duration')
        first, last = round(start * sr), round(end * sr)
        if last <= first:
            raise ValueError('Empty sample interval')
        f.seek(first)
        data = f.read(last-first, dtype='float32', always_2d=True)
    with tempfile.TemporaryDirectory(prefix='basic-pitch-') as tmp:
        wav = Path(tmp) / 'input.wav'
        sf.write(wav, data, sr, subtype='FLOAT')
        _, midi, events = predict(wav, model)
    actual_start = first / sr
    notes = sorted([{'onset_seconds':float(n[0])+actual_start,
                     'offset_seconds':float(n[1])+actual_start,
                     'midi_pitch':int(n[2]), 'name':pretty_midi.note_number_to_name(int(n[2])),
                     'model_amplitude':float(n[3])} for n in events],
                   key=lambda n:(n['onset_seconds'],n['midi_pitch']))
    result = {'status':'unverified_transcription_candidates',
              'source_sha256':source_hash, 'source_duration_seconds':duration,
              'sample_rate':sr,'channels':channels,'scope_seconds':[actual_start,last/sr],
              'midi_time_origin_seconds':actual_start,
              'model_sha256':sha(model), 'script_sha256':sha(__file__),
              'versions':{p:importlib.metadata.version(p) for p in
                          ['basic-pitch','onnxruntime','librosa','numpy','scipy','pretty_midi']},
              'parameters':{'onset_threshold':.5,'frame_threshold':.3,'minimum_note_length_ms':127.7},
              'notes':notes}
    output.mkdir(parents=True, exist_ok=False)
    midi.write(str(output/'notes.mid'))
    (output/'notes.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    assert json.loads((output/'notes.json').read_text()) == result
    readback = pretty_midi.PrettyMIDI(str(output/'notes.mid'))
    assert sum(len(i.notes) for i in readback.instruments) == len(notes)
    return result


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('audio',type=Path)
    parser.add_argument('--output',required=True,type=Path)
    parser.add_argument('--start',type=float,default=0)
    parser.add_argument('--end',type=float)
    args=parser.parse_args()
    r=transcribe(args.audio,args.output,args.start,args.end)
    print(json.dumps({'notes':len(r['notes']),'scope_seconds':r['scope_seconds'],'status':r['status']}))
