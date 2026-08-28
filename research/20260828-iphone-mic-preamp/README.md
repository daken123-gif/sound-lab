# iPhoneマイクプリ研究

- research-id: `20260828-iphone-mic-preamp`
- 研究対象: iPhone内蔵／接続マイクをField Looperの演奏入力として使う入力段
- 現在の問い: 小さい声から大きい打音まで、原音の輪郭を失わず、ループと監聴へ適正レベルで渡せるか
- 更新日時: 2026-08-28 UTC

## ユーザーの実機評価

- 音は入るが音質が最悪だった。
- 入力ゲインと出力ゲインが必要。
- 入力・出力はピークメーター形式が必要。
- 自動録音は不要。
- 今回は「マイクプリの設計」として進める。

## 現行実装で観測できた事実

- `echoCancellation`、`noiseSuppression`、`autoGainControl` はヘッドホン用CLEANモードで無効。
- 入力段はGain → 25 Hz HPF → 19 kHz LPFだけだった。
- `inputComp` は宣言されていたが生成・接続されていなかった。
- 入力メーターはRMSへ係数を掛けた0–100表示で、dBFSやクリップを判定できなかった。
- 録音はループ円を押すまで開始しない。

## 今回の実装

対象: `field-processor/index.html`

```
MIC
 → TRIM (-18…+24 dB)
 → HPF (20…180 Hz)
 → LPF (19 kHz)
 → DENSITY compressor
 → 4x oversampled soft saturation
 → dBFS input meter / recorder / monitor
```

- TRIM初期値: +6 dB
- HPF初期値: 65 Hz
- DENSITY初期値: 35%
- MONITOR初期値: -6 dB
- OUTPUT初期値: -3 dB
- 入力ピークが -0.5 dBFSを超えると1.2秒間 `CLIP` を保持する。
- DENSITYは圧縮率、閾値、ソフト飽和量を一つの演奏用ノブへまとめる。

## 推論・仮説

- 通話処理を切ったまま軽い圧縮とソフト飽和を後段へ置けば、声量差を詰めてもノイズ抑制特有の欠落は増やさずに済む。
- HPFを可変にすると、声では近接低音を残し、屋外では風・ハンドリングノイズを削れる。
- 初期OUTPUTを -3 dBに下げることで、ループ合成時の後段ヘッドルームを確保できる。

## 採用しない点

- 常時ノイズゲート
- 強制AGC
- 常時エコーキャンセル
- 録音の自動開始
- 固定された「ボーカル向け」EQ

## 依存する研究

- Loopy Pro: 手動録音と監聴の分離
- RC-505mkII: 入出力ゲインと演奏中のレベル監視
- KAOSS master FX: マイクプリ後段とは分離

## 未検証

- iPhone 13 mini実機での内蔵マイク、Lightning/USBマイク、イヤホンマイク別の入力レベル
- Safariが実際に選んだsample rateと入力デバイス
- TRIM +24 dB、DENSITY 100%時のノイズ床
- 有線／Bluetoothイヤホン別の遅延


## 2026-08-28 アナログプリ試聴

- `PREAMP · CLEAN`: TRIM → HPF → LPFの完全バイパス基準
- `PREAMP · ANALOG`: 可変コンプレッサー → 非対称ソフト飽和 → 18 Hz DCブロック
- 切替は12 msクロスフェード。
- 4倍オーバーサンプリングを維持し、偶数次成分を含む非対称カーブを使用。
- ノイズ、ヒス、ハムは追加しない。
- 既存のiPhone内蔵マイク優先選択と `BT MIC / HFP` 経路表示を維持する。

### 実機判定

1. `PREAMP · CLEAN`でVoice Memosとの差を確認する。
2. 上部の入力経路表示が `iPHONE MIC` か `BT MIC / HFP` か確認する。
3. CLEANが正常な場合だけANALOGへ切り替え、DENSITYを0から上げる。
4. CLEANの時点で帯域が狭ければ、アナログ処理ではなく入力経路を原因候補とする。
