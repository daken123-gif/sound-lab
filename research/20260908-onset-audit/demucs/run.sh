#!/bin/bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
if [[ $# -ne 2 ]]; then
  echo '使い方: bash run.sh 音源ファイル 新しい出力フォルダ' >&2; exit 2
fi
[[ -f "$1" ]] || { echo "音源がありません: $1" >&2; exit 1; }
[[ ! -e "$2" ]] || { echo "出力先が既に存在します: $2" >&2; exit 1; }
[[ -x "$ROOT/.venv-demucs/bin/python" && -f "$ROOT/models/manifest.json" ]] || {
  echo "先にsetup-mac.shを完了してください。" >&2; exit 1;
}
"$ROOT/.venv-demucs/bin/python" -m demucs --repo "$ROOT/models" -n htdemucs -d cpu --shifts 0 --float32 -o "$2" "$1"
