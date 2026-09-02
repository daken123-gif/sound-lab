#!/bin/bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
WORK="$ROOT/.mac-demucs-work"
INPUTS="$WORK/inputs"
WAVS="$WORK/wavs"
SEPARATED="$WORK/separated"
STEMS="$WORK/stems"
VENV="$WORK/venv"
RESULT="$ROOT/demucs-results-mac-local.json"

if [[ "$(uname -s)" != "Darwin" ]]; then
  echo "停止: このランナーはMac実機専用です。" >&2
  exit 2
fi
if [[ "$(uname -m)" != "arm64" ]]; then
  echo "停止: demucs-mlxにはApple Silicon（arm64）が必要です。" >&2
  exit 2
fi

MACOS_MAJOR="$(sw_vers -productVersion | cut -d. -f1)"
if (( MACOS_MAJOR < 13 )); then
  echo "停止: macOS 13以降が必要です。現在: $(sw_vers -productVersion)" >&2
  exit 2
fi

mkdir -p "$WORK" "$INPUTS" "$WAVS" "$SEPARATED" "$STEMS"

if command -v uv >/dev/null 2>&1; then
  uv venv --python 3.11 --clear "$VENV"
elif command -v python3.11 >/dev/null 2>&1; then
  python3.11 -m venv --clear "$VENV"
elif command -v brew >/dev/null 2>&1; then
  if ! brew list python@3.11 >/dev/null 2>&1; then
    brew install python@3.11
  fi
  "$(brew --prefix python@3.11)/bin/python3.11" -m venv --clear "$VENV"
else
  echo "停止: Python 3.11、uv、Homebrewのいずれも見つかりません。Codexへこの表示を渡してください。" >&2
  exit 2
fi

PYTHON="$VENV/bin/python"
PIP="$VENV/bin/pip"
"$PIP" install --disable-pip-version-check --upgrade pip
if (( MACOS_MAJOR >= 15 )); then
  ESSENTIA_VERSION="2.1b6.dev1389"
else
  ESSENTIA_VERSION="2.1b6.dev1177"
fi
"$PIP" install --disable-pip-version-check \
  "demucs-mlx==1.4.6" \
  "essentia==$ESSENTIA_VERSION"

"$PYTHON" "$ROOT/download_blind20_previews.py" --output "$INPUTS"

for INPUT in "$INPUTS"/B??.m4a; do
  BLIND_ID="$(basename "$INPUT" .m4a)"
  WAV="$WAVS/$BLIND_ID.wav"
  afconvert "$INPUT" "$WAV" -f WAVE -d LEI16@44100 -c 2
  rm -rf "$SEPARATED/htdemucs/$BLIND_ID"
  "$VENV/bin/demucs-mlx" \
    -n htdemucs \
    -o "$SEPARATED" \
    --shifts 1 \
    --seed 0 \
    --overlap 0.25 \
    "$WAV"
  CANDIDATE="$(find "$SEPARATED" -type f -path "*/$BLIND_ID/drums.wav" -print -quit)"
  if [[ -z "$CANDIDATE" ]]; then
    echo "停止: $BLIND_ID のDemucs drums.wavが見つかりません。" >&2
    exit 3
  fi
  cp "$CANDIDATE" "$STEMS/$BLIND_ID-drums.wav"
done

"$PYTHON" "$ROOT/demucs_blind20_audit.py" --stems "$STEMS" --output "$RESULT"
FIRST_SHA="$(shasum -a 256 "$RESULT" | awk '{print $1}')"
"$PYTHON" "$ROOT/demucs_blind20_audit.py" --stems "$STEMS" --output "$RESULT"
SECOND_SHA="$(shasum -a 256 "$RESULT" | awk '{print $1}')"
if [[ "$FIRST_SHA" != "$SECOND_SHA" ]]; then
  echo "停止: 同じstemから生成した解析JSONが一致しません。" >&2
  exit 4
fi

"$PYTHON" -m json.tool "$RESULT" >/dev/null
echo "完了: $RESULT"
echo "解析JSON SHA-256: $SECOND_SHA"
echo "音源、WAV、stem、仮想環境は $WORK にあり、Git対象外です。"

