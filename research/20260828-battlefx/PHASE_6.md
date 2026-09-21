# BattleFX研究 Phase 6 — 実機録音用Choke分類器

- research-id: `20260828-battlefx`
- status: `classifier-self-test-passed`
- 更新日: 2026-08-28
- BattleFX実機録音: 未取得
- Field Looper製品実装: 未実施

## 1. Phase 5から進めた点

Phase 5は四方式の対照音を作った。Phase 6では、その差を人間の印象だけで判定せず、将来のBattleFX実機録音へ同じ測定を適用できるCLI分類器へした。

必要な録音は二つ。

| take | 入力 |
| --- | --- |
| tail-only | choke前の励起だけ |
| with-probe | 同条件にchoke中probeを追加 |

二録音を引くと、元から存在したtailを消さずに、choke中probeだけへの応答を分離できる。

## 2. 分類signature

| signature | output gate | feedback cut | buffer clear | input choke |
| --- | --- | --- | --- | --- |
| choke中に既存tailが聞こえる | no | yes | no | yes |
| 解除後に古いtailが戻る | yes | no | no | yes |
| choke中probeを受理する | yes | yes | yes | no |
| late recurrenceが残る | yes | no | no | yes |

最初の三項目が既知四modelへ一意に対応する。late recurrenceは補助観測として結果へ残す。

一致しない組合せを近いmodelへ丸めず`UNKNOWN`にする。これは次の可能性を残すためである。

- delayとreverbで方式が異なる
- 複数箇所を同時にchokeしている
- crossfadeやduck-and-returnがある
- 二takeの演奏または録音位置がずれた
- noise floorがtailを上回った

## 3. 実装

`choke_classifier.mjs`はNode.js標準機能だけを使う。

- RIFF/WAVE chunkを読み取る
- PCM16 / PCM24 / PCM32 / Float32を受理する
- stereo以上はmonoへ平均する
- 二takeのsample rate不一致を拒否する
- 測定windowに必要な長さがなければ拒否する
- 冒頭noiseとchoke前tailから検出thresholdを作る
- metric、boolean signature、分類、入力formatをJSONで返す

PCM16 mono以外のformat branchはコード化済みだが、このPhaseの自動試験素材はPCM16 monoだけである。

## 4. 自己試験

Phase 5 rendererへ`tail-only` WAV出力を追加し、既存の`with-probe` WAVと対にした。

| case | expected | actual |
| --- | --- | --- |
| output-gate | OUTPUT_GATE | OUTPUT_GATE |
| feedback-cut | FEEDBACK_CUT | FEEDBACK_CUT |
| buffer-clear | BUFFER_CLEAR | BUFFER_CLEAR |
| input-choke | INPUT_CHOKE | INPUT_CHOKE |
| probe欠落control | UNKNOWN | UNKNOWN |
| sample rate不一致 | ERROR | ERROR |
| 短すぎる録音 | ERROR | ERROR |

結果: `7/7 pass`。

probe欠落controlを誤ってoutput gateまたはinput chokeへ寄せなかった。分類器が未知条件を保持する経路を確認した。

## 5. 実機runへの入力契約

分類器へ渡す前に次を同一にする。

- BattleFX version/build
- hostとhost version
- sample rate
- buffer size
- presetとparameter値
- 入力素材とgain
- choke start/end
- probe時刻
- delay/reverbのどちらをSoloにしたか

二takeを別演奏で録る場合、sample単位の完全一致は期待できない。最初はhost上で同じ入力fileを再生し、probeだけを加えた決定論的test signalを使う。

## 6. 現在判断

- classifier artifact: 作成済み
- model自己試験: 7/7 pass
- PCM16 mono path: 実行済み
- PCM24 / PCM32 / Float32 / multichannel path: 未試験
- BattleFX実機分類: 未実施
- 製品仕様への昇格: しない
- Field Looper製品コードとUI: 未変更
