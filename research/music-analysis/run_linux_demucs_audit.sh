#!/bin/bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
WORK="$ROOT/.linux-demucs-work"
INPUTS="$WORK/inputs"
WAVS="$WORK/wavs"
SEPARATED="$WORK/separated"
STEMS="$WORK/stems"
VENV="$WORK/venv"
RESULT="$ROOT/demucs-results-linux-cpu.json"

if [[ "$(uname -s)" != "Linux" ]]; then
  echo "停止: このランナーはLinux CPU監査用です。" >&2
  exit 2
fi
if ! command -v ffmpeg >/dev/null 2>&1; then
  echo "停止: ffmpegが見つかりません。" >&2
  exit 2
fi

mkdir -p "$WORK" "$INPUTS" "$WAVS" "$SEPARATED" "$STEMS" "$WORK/torch-home"
python3 -m venv --clear "$VENV"
"$VENV/bin/pip" install --disable-pip-version-check \
  --index-url https://download.pytorch.org/whl/cpu \
  "torch==2.8.0" "torchaudio==2.8.0"
"$VENV/bin/pip" install --disable-pip-version-check \
  "demucs==4.0.1" "essentia==2.1b6.dev1389"

"$VENV/bin/python" "$ROOT/download_blind20_previews.py" --output "$INPUTS"

export TORCH_HOME="$WORK/torch-home"
export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1
export ATEN_CPU_CAPABILITY=default

DEMUCS=("$VENV/bin/python" "$ROOT/demucs_cpuinfo_compat.py")

for input in "$INPUTS"/B??.m4a; do
  blind_id="$(basename "$input" .m4a)"
  wav="$WAVS/$blind_id.wav"
  ffmpeg -nostdin -hide_banner -loglevel error -y \
    -i "$input" -ar 44100 -ac 2 -c:a pcm_s16le "$wav"
  "${DEMUCS[@]}" \
    -n htdemucs -d cpu --shifts 1 --overlap 0.25 --two-stems drums \
    -o "$SEPARATED" "$wav"
  candidate="$SEPARATED/htdemucs/$blind_id/drums.wav"
  if [[ ! -s "$candidate" ]]; then
    echo "停止: $blind_id のDemucs drums.wavが見つかりません。" >&2
    exit 3
  fi
  cp "$candidate" "$STEMS/$blind_id-drums.wav"
done

first="$WORK/result-first.json"
second="$WORK/result-second.json"
for output in "$first" "$second"; do
  "$VENV/bin/python" "$ROOT/demucs_blind20_audit.py" \
    --stems "$STEMS" --output "$output" \
    --implementation official-demucs \
    --implementation-version 4.0.1 \
    --device "PyTorch CPU" \
    --seed 0
done
if ! cmp -s "$first" "$second"; then
  echo "停止: 同じstemから生成した解析JSONが一致しません。" >&2
  exit 4
fi
cp "$first" "$RESULT"
"$VENV/bin/python" -m json.tool "$RESULT" >/dev/null
echo "完了: $RESULT"
sha256sum "$RESULT"
echo "音源、WAV、stem、モデル、仮想環境は $WORK にあり、Git対象外です。"
