#!/usr/bin/env bash
set -euo pipefail

ROOT=$(cd "$(dirname "$0")" && pwd)
WORK=${SOUND_LAB_SEED_WORK:-"$ROOT/.linux-demucs-seed-work"}
VENV="$WORK/venv"
PREVIEWS="$WORK/previews"
STEMS="$WORK/stems"
OUTPUT="$ROOT/demucs-seed-sensitivity-20260903.json"
IDS=(B06 B09 B10 B14 B16 B17 B19)
SEEDS=(0 1 2 3 4)

python3 -m venv "$VENV"
"$VENV/bin/pip" install --index-url https://download.pytorch.org/whl/cpu torch==2.8.0+cpu torchaudio==2.8.0+cpu
"$VENV/bin/pip" install demucs==4.0.1 essentia==2.1b6.dev1389
"$VENV/bin/python" "$ROOT/download_blind20_previews.py" --output "$PREVIEWS" --ids "${IDS[@]}"

mkdir -p "$STEMS"
for seed in "${SEEDS[@]}"; do
  mkdir -p "$STEMS/seed-$seed"
  for blind_id in "${IDS[@]}"; do
    input="$WORK/$blind_id.wav"
    ffmpeg -hide_banner -loglevel error -y -i "$PREVIEWS/$blind_id.m4a" -ar 44100 -ac 2 -c:a pcm_s16le "$input"
    if [[ ! -f "$STEMS/seed-$seed/$blind_id-drums.wav" ]]; then
      SOUND_LAB_DEMUCS_SEED=$seed "$VENV/bin/python" "$ROOT/demucs_cpuinfo_compat.py" \
        -n htdemucs -d cpu --shifts 1 --overlap 0.25 --two-stems drums \
        -o "$WORK/demucs-seed-$seed" "$input"
      cp "$WORK/demucs-seed-$seed/htdemucs/$blind_id/drums.wav" "$STEMS/seed-$seed/$blind_id-drums.wav"
    fi
  done
done

"$VENV/bin/python" "$ROOT/demucs_seed_sensitivity.py" \
  --stems-root "$STEMS" --output "$OUTPUT" --ids "${IDS[@]}" --seeds "${SEEDS[@]}"
"$VENV/bin/python" "$ROOT/demucs_seed_sensitivity.py" \
  --stems-root "$STEMS" --output "$WORK/result-second-pass.json" --ids "${IDS[@]}" --seeds "${SEEDS[@]}"
cmp "$OUTPUT" "$WORK/result-second-pass.json"
sha256sum "$OUTPUT"
