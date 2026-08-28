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


## 2026-08-28 INPUT未接続フォールバック修正

- 停止時表示を `TAP マイクを起動` とし、未接続と故障を分離した。
- 起動操作直後は `入力へ接続中…` を表示する。
- iPhone内蔵マイクの指定取得が失敗しても、最初に取得済みの入力ストリームを停止せず使用する。
- この場合は入力経路へ `FALLBACK` を表示する。
- `NotAllowedError`、`NotFoundError`、`NotReadableError`、`OverconstrainedError` を別の日本語表示にした。
- 模擬検査で、内蔵マイク取得失敗時に初期ストリームが維持され、成功時だけ初期ストリームが停止されることを確認した。


## 2026-08-28 ANALOG周波数色付け

- 操作子は増やさず、DENSITYへ3段の穏やかなカーブを連動させた。
- BODY: 160 Hzローシェルフ、DENSITY 100%で +1.8 dB。
- PRESENCE: 4.3 kHz、Q 0.65のピーキング、DENSITY 100%で -2.2 dB。
- AIR: 10.5 kHzハイシェルフ、DENSITY 100%で -1.2 dB。
- DENSITY 0%では3段とも0 dBとなり、歪み量も最小へ戻る。
- CLEAN経路は従来どおりTRIM → HPF → LPFから直接出力し、周波数色付けを通さない。
- 狙いは低域の胴鳴りを少し足し、iPhone内蔵マイクで硬く感じやすい中高域と最上部を穏やかに抑えること。実機聴感は未検証。


## 2026-08-28 ANALOGレベル連動AIR

- ANALOGコンプレッサーの実際のゲインリダクションを読み、強い入力のときだけ10.5 kHzハイシェルフを追加で下げる。
- DENSITY 35%では静音時 -0.42 dB、6 dBリダクション時 -0.798 dB。
- DENSITY 100%では静音時 -1.2 dB、12 dBリダクション時 -3.36 dBを上限とする。
- 60 msで追従させ、子音や打音の瞬間だけ丸くなりすぎる挙動を避ける。
- CLEAN経路はこの制御を通らない。
- iPhone実機での声・打音による聴感は未検証。


## 2026-08-28 ANALOG並列トランジェント保持

- ANALOG経路を、コンプレッサー直後のDRY成分と、BODY/PRESENCE/AIR・ソフト飽和を通るCOLOR成分へ分岐した。
- DENSITY 0%: DRY 75% / COLOR 25%。
- DENSITY 35%: DRY 57.5% / COLOR 42.5%。
- DENSITY 100%: DRY 25% / COLOR 75%。
- 常に合計1.0を保ち、DENSITY操作による単純な音量増加を避ける。
- コンプレッサーの12 msアタックで通した立ち上がりをDRY側へ残し、色付けを全量へ強制しない。
- CLEAN経路は従来の直結を維持する。
- iPhone実機での位相感、声の子音、打音の輪郭は未検証。
