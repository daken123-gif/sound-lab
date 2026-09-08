# Basic Pitchを他の島・Macで実行する

Spotify公開のBasic Pitch 0.4.0をONNXで動かす共用キット。無料の公開ソフトで、Spotifyの契約・ログイン・APIキーは不要。入力済みの音声を実行環境内で解析する。実行コードに登録・課金・音声送信・自動インストールはない。

このファイルのあるフォルダを、sound-labの `research/20260908-onset-audit` ブランチから取得する。別の島はこのREADME・requirements・transcribe.py・smoke_test.pyを読む。既存環境の有無を確認し、新規導入はユーザー承認の範囲内で実行する。Git上にあることは全島への導入済みを意味しない。

## 導入

Python 3.12で検証。Macは実機未検証。MacでもPythonを用意し同じ手順で動作確認する。iPhoneアプリからはAIのPython実行環境へ依頼する。iPhone本体にPythonを導入する手順ではない。

以下はパッケージ配布元への通信と、新規仮想環境へのソフト導入を行う。音声送信はしない。既存の仮想環境がある場所では別名を選ぶ。

```bash
python3.12 -m venv .venv-basic-pitch
.venv-basic-pitch/bin/python -m pip install -r requirements-onnx.txt
.venv-basic-pitch/bin/python -m pip install --no-deps basic-pitch==0.4.0
.venv-basic-pitch/bin/python smoke_test.py
```

Basic Pitchの依存宣言はPython 3.12にも古いTensorFlowを要求するため、`basic-pitch[onnx]` 任せにせず、本体とONNX依存を分ける。`pip check` のTensorFlow未導入警告は残る。このキットは明示的にONNXモデルを選択する。setuptoolsはresampyのpkg_resources互換性のため80.9.0に固定。requirementsは主要依存の版指定であり、全推移依存の完全ロックではない。

## 実行

```bash
.venv-basic-pitch/bin/python transcribe.py /path/to/audio.wav --start 620 --end 630 --output output-run-01
```

WAV/MP3等の対応はsoundfileのデコーダに依存する。今回MP3実行済み。出力先は新規ディレクトリが必須。

- notes.json: 音名・MIDI音高・元音源の絶対発音／消音時刻、音源・モデル・コードhash、版、区間。
- notes.mid: 切り出した区間を0秒とするMIDI。JSONの `midi_time_origin_seconds` を加えると元音源の時刻になる。
- 発音強度はモデルの推定振幅であり、正解確率ではない。担当楽器・奏者を識別していない。

## 実行証拠と限界

validation.jsonは初回合成試験。6秒に単音3つと3和音の計6音。6音を検出したが余分なE5を1音検出。音高＋発音のprecision 6/7、recall 6/6。発音許容50ms、音高50cent。音長を含む評価は許容max(真の長さ20%,50ms)。実曲の精度には転用しない。

metamorphoses-notes.jsonは公式BandcampのMetamorphosesを入力した未検証候補。音源hashは既存Jeff Mills研究と一致。620.1–629.9秒の発音候補は10秒切出し96音、前後を含む30秒切出し91音、そのうち音高＋発音50ms以内で76音が対応。これは同一モデルの窓依存性で、正解率ではない。音長・倍音誤検出・打楽器共鳴・声部分離・聴取照合は未確定。候補MIDIを完成採譜として使わない。

音声本体・依存パッケージ・モデル本体はGitに保存しない。音源の取得はmainの `research/music-analysis/SOURCE_POLICY.md` に従う。コードを取得できてもPython実行・通信権限がない島には導入できない。

一次資料: https://github.com/spotify/basic-pitch / https://mir-eval.readthedocs.io/latest/api/transcription.html
