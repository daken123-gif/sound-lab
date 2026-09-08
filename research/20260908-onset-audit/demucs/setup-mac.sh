#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")"
if [[ "$(uname -s)" != Darwin ]]; then
  echo "この導入スクリプトはMac用です。" >&2; exit 1
fi
command -v python3.11 >/dev/null || { echo "Python 3.11を先に導入してください。" >&2; exit 1; }
command -v ffmpeg >/dev/null || { echo "ffmpegを先に導入してください。" >&2; exit 1; }
echo "PyPIから無料ライブラリ、Metaの配布元からhtdemucsモデルを取得します。音源は送信しません。"
python3.11 -m venv .venv-demucs
P="$PWD/.venv-demucs/bin/python"
"$P" -m pip install "numpy==1.26.4" "torch==2.2.2" "torchaudio==2.2.2" "demucs==4.0.1"
"$P" -m pip check
"$P" - <<'PY'
from pathlib import Path
import hashlib, json, shutil
import torch
from demucs.pretrained import get_model, REMOTE_ROOT
model = get_model("htdemucs")
root = Path("models")
root.mkdir(exist_ok=True)
shutil.copy2(REMOTE_ROOT / "htdemucs.yaml", root / "htdemucs.yaml")
cache = Path(torch.hub.get_dir()) / "checkpoints"
weights = list(cache.glob("955717e8-*.th"))
if len(weights) != 1:
    raise RuntimeError(f"モデルファイルを一意に特定できません: {weights}")
target = root / weights[0].name
shutil.copy2(weights[0], target)
local = get_model("htdemucs", repo=root)
assert list(local.sources) == ["drums", "bass", "other", "vocals"]
(root / "manifest.json").write_text(json.dumps({
    "model": "htdemucs",
    "file": target.name,
    "sha256": hashlib.sha256(target.read_bytes()).hexdigest(),
    "sources": local.sources,
    "validation": "model_load_only; separation not tested"
}, indent=2) + "\n")
print("モデルのローカル読込成功。音源分離はrun.shで実行してください。")
PY
"$P" -m pip freeze > installed-versions.txt
