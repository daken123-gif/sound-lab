# Things – Motor 研究

- status: `active`
- research-id: `20260828-things-motor`
- 研究対象: AudioThing / Hainbach「Things – Motor」と、その原型であるBBC Radiophonic Workshop「Crystal Palace」
- 現在の問い: 二入力Motorの核を4トラックField Looperへどう移し、操作を複雑化させず人間が直接演奏できる構造にするか
- 更新日時: 2026-08-28

## 現在位置

この記録は製品採用の決定ではない。Motorの製品仕様、Crystal Palaceの構造、4トラック化の設計候補を分離して記録する。`integration/` に統合判断が記録されるまでは、Field Looperへ採用済みと扱わない。

## 一次資料

1. AudioThing公式製品ページ  
   https://www.audiothing.net/effects/things-motor/
2. AudioThing公式ユーザーガイド  
   https://www.audiothing.net/docs/AudioThing_ThingsMotor.pdf
3. Apple App Store「Things – Motor」  
   https://apps.apple.com/app/things-motor/id6473037203
4. Science Museum Group収蔵記録「Crystal Palace Capacitive Fader」  
   https://collection.sciencemuseumgroup.org.uk/objects/co8355715/bbc-radiophonic-workshop-items
5. Crystal Palace VCV Rack再構築実装  
   https://github.com/djpeterso23662/CrystalPalace

取得日: 2026-08-28。

## 観測できた事実

### Things – Motor

- 通常入力とサイドチェイン入力の二つの音声信号を組み合わせるエフェクトである。
- サイドチェインは検出信号としてだけ使うコンプレッサー方式ではなく、第二の音素材を入力する経路である。
- LFOにより、二信号の滑らかなモーフィングからリズミカルなチョップまでを作る。
- LFOを高速化すると、リングモジュレーションに近い生成物が生じる。
- Tremolo、Vibrato、Pannerは同一のMotor LFOへ同期する。
- Motorの始動・停止には可変の加減速時間がある。
- 公式波形は Sine、Triangle、Ramp Up、Ramp Down、Square、Sine Up、Sine Down、Exp Up、Exp Down、S&H。
- 主要パラメーターは Rate、Sync、Wave/Phase、Balance、Mix、Tremolo、Vibrato、Panner、Speed、Motor。
- iOS/iPadOS版はAUv3とStandaloneで提供されている。
- 公式掲載のv1.2（2025-12-03）ではCPU/メモリ使用量の改善、出力ヘッドルーム、Motor停止時の位相ジャンプなどが修正された。

### Crystal Palace

- Dave YoungがBBC Radiophonic Workshopで設計した容量結合式の回転フェーダーである。
- 可変速ディクテーションマシンのモーターが、円周上の固定入力板に対して容量結合板を回転させる。
- 容量結合板はFETアンプへ接続され、入力へ物理接触せずに音を読み取る。
- 16入力を滑らかに組み合わせることができた。
- 未接続入力は後続端子へ前の信号を引き継ぐnormalled構造を持つ。
- Science Museumの記録ではBrian Hodgsonによる1966年の『The Machine Stops』音楽で使用されたことが確認できる。
- 公式AudioThing資料では『Doctor Who: The Krotons』での使用も由来として挙げられている。

### VCV Rack再構築から観測できる実装選択

- 16入力を円周上へ配置する。
- 回転位置が隣接入力間を移動するとequal-power crossfadeで受け渡す。
- 未接続端子が直前の信号を引き継ぐnormalled挙動を再構築している。
- CLOCK、RESET、CV、SPEEDが追加されている。これは原機そのものの仕様ではなく、VCV環境向けの拡張である。

## 解釈

Motorの中心はトレモロ、ビブラート、パンの個別機能ではない。中心は、二つの音のどちらを鳴らすかではなく、両者の関係を一つの回転位相として扱うことにある。

Crystal Palaceではさらに、入力配置とnormalled区画によって、各音が円周上で占める時間を変えられる。したがって原型は「順番ミュート」よりも「円形の音声ミキサー／読み取りヘッド」と捉えるほうが構造に近い。

## 4トラック化の候補

### A. 二入力Motorをそのまま再現

4トラックからA/Bの二本を選び、Motorへ入れる。

利点:

- 製品の挙動へ最も近い。
- DSPと検証範囲が小さい。

問題:

- A/B選択操作が必要になる。
- 残り二トラックとの関係が見えなくなる。
- 選択切替が増え、iPhone 13 miniでの演奏アクセスを悪化させる。

判定: 比較用の最小DSPとしては有効だが、最終UI候補にはしない。

### B. 4入力Rotor

Track 1〜4を円周上へ置き、隣接二トラックだけを連続的に受け渡す。

位相を `phi`、現在区画内の位置を `t` とすると、基本ゲイン候補は次とする。

```text
g0 = cos(pi * t / 2)
g1 = sin(pi * t / 2)
y  = g0 * x[current] + g1 * x[next]
```

利点:

- 4トラックを一つの演奏対象として扱える。
- 一つの動作で前景となる録音を移動できる。
- Crystal Palaceの多入力思想を保持できる。

問題:

- 元のThings Motorそのものではなく、新しい派生設計になる。
- 相関したトラックをequal-powerで混ぜると中央でレベルが膨らむ。
- トラック順序が固定だと、隣接関係が音楽的に合わない場合がある。

判定: 現在の中心候補。ただし未検証であり、統合へは上げない。

### C. 二組のMotorを階層化

1/2、3/4を別々にモーフし、その二出力をさらにモーフする。

利点:

- すべてのトラックを使いながらMotorの二入力構造を保持できる。

問題:

- 三つの位相または速度関係が必要になる。
- 操作と説明が複雑化する。
- 人間が現在どの音を出しているか把握しにくい。

判定: 採用しない。

## 現在のDSP候補

### 回転位相

```text
targetSpeed = performer input
speed += accelerationCoefficient * (targetSpeed - speed)
phase = wrap01(phase + speed / sampleRate)
```

- Motor停止はバイパスにしない。
- `targetSpeed` を0へ移し、位相を現在位置で保持する。
- 再始動は保持位置から行う。
- 正転／逆転を同じ速度軸で扱う。
- 再生中のトラック追加・除外では短いクロスフェードを入れ、係数を不連続に切り替えない。

### クロスフェード

初期候補は隣接二入力のequal-power crossfade。ただし以下を比較試験する。

1. equal-power: 非相関素材のエネルギーを保ちやすい。
2. linear/equal-gain: 同一または強相関素材の中央膨張を抑えやすい。
3. correlation-aware: 相関に応じてカーブを補間するが、計算量と挙動説明が増える。

第一試作ではequal-powerとlinearを切替可能な検証パラメーターにし、製品UIへは出さない。

### ヘッドルーム

- ローター出力には最初から最低3 dB、試験では6 dBまでの内部ヘッドルームを確保する。
- レベル問題を無断のコンプレッサー、リミッター、サチュレーションで隠さない。
- クリップ防止処理を入れる場合も、ローターDSPとは別段として測定する。

### BLEND

`BLEND` はエフェクト量ではなく、隣接区画の受け渡し幅を変える。

- SMOOTH側: 区画全体を使って連続クロスフェード。
- 中央: 各トラックの保持区間と短い受け渡し。
- CHOP側: 境界付近だけを短くクロスフェード。

完全な瞬時切替はクリックを発生させるため、最小ランプ時間を残す。

### 空トラックと除外トラック

候補を分離する。

- `SKIP`: 空トラックを飛ばし、残りトラックへ円周を再配分する。
- `HOLE`: 空区画を無音として残す。
- `HOLD`: 原機のnormalled挙動に近く、直前トラックを空区画へ延長する。

演奏事故を避ける初期既定値は `SKIP`。ただし原機研究として `HOLD` を比較試験する。`HOLE` は意図したリズムゲート用途に限定する。

### オーディオレート

Things Motorの高速変調は音色生成として重要だが、4入力Rotorで矩形に近い係数を可聴域まで上げるとエイリアシングが増える。

初期実装では低周波の演奏領域と音色生成領域を分離する。

- PERFORMANCE: 自由速度＋テンポ同期。滑らかな係数。
- AUDIO: 帯域制限した変調波形。必要なら2倍オーバーサンプリングを比較。

AUDIO領域は第一UIへ露出させない。

## 演奏操作の候補

表示の装飾として歯車やヴィンテージ機材を模倣しない。操作対象は回転位相そのものにする。

- タップ: その位置へ移動して保持。
- ドラッグ: トラック間を手動でモーフ。
- フリック: 方向と速度を与える。
- MOTOR: 現在位置から慣性始動／慣性停止。
- Track 1〜4: ローターへの参加／除外。

常時自動で回す機能ではなく、手で止め、戻し、速度を乱せる演奏面として扱う。プリセット選択や複数ページ切替を主要操作にしない。

## Field Looperへ採用候補の点

- 複数録音を一つの位相で直接演奏する発想。
- 停止時に混合位置を保持するMotor慣性。
- 4トラックの隣接クロスフェード。
- 手動スクラブと自動回転を同一位相で接続すること。
- 低速モーフからリズミカルなチョップまでを一つのBLEND軸で扱うこと。

## 採用しない点

- AudioThingの外観や歯車アニメーションの模倣。
- Tremolo、Vibrato、Pannerを最初から一括搭載すること。
- 二段・三段Motorによる階層的な4トラック合成。
- 独立ドラムエンジンを常時Rotorへ飲み込ませること。
- KAOSS型Masterを復活させる根拠としてMotorを使うこと。
- ランダマイザーを主要演奏操作にすること。

## 他研究との境界

- 4トラック録音部: Rotorへ入る素材を作る。Rotorが録音操作を置き換えない。
- 独立IDMドラム部: 原則として独立バスを保つ。クロック同期候補はあるが、音声を常時Rotorへ入れない。
- 合成波形／時間操作: Rotor出力を受け取る候補。正確な順序は統合研究で決める。
- Skulptur研究: 現行の主演奏面候補を侵食しない。RotorをMaster FXとして扱わない。
- Microcosm研究: 音の記憶・再演奏との役割重複を統合時に検査する。
- KAOSS研究: main/masterから撤回された判断を復活させない。必要なら限定的な副要素としてのみ比較する。

## 触る実装パス

現時点では研究記録のみ。製品コードの実体と現在の統合ブランチを取得していないため、実装パスは未確定。パスを推測して記載しない。

## 未検証事項

- iPhone実機で、4入力equal-power crossfadeが素材の種類ごとにどう聞こえるか。
- 同一ループを複製した場合のレベル膨張。
- MOTOR始動／停止時のクリックと位相連続性。
- Track参加状態を演奏中に変えた場合の安全な再配置。
- `SKIP` と原機由来の `HOLD` のどちらが演奏に使えるか。
- 正転／逆転の切替を一つの速度操作で誤操作なく扱えるか。
- iPhone 13 miniの横画面・縦画面で、録音操作を隠さずRotorへ触れられるか。
- マルチタッチ中にTrack保持とRotorドラッグが同時に成立するか。
- AUDIO領域のエイリアシングとCPU負荷。
- Skulptur、Microcosm、合成波形処理との正確な信号順。

## 最小検証順序

1. オフラインDSPで4つの既知信号を円周クロスフェードする。
2. ゲイン合計、RMS、ピーク、位相連続性を測定する。
3. equal-powerとlinearを同じ素材で比較する。
4. Motor加速・停止・逆転時の不連続を測定する。
5. iPhone実機で声、環境音、シンセ、ノイズの4録音を使って聴感試験する。
6. 手動ドラッグと自動回転が同じ位相を共有する操作試験を行う。
7. その後にのみ統合候補を作る。

## 現在の判定

`4入力Rotor` は研究候補として継続する。Things Motorの全機能を移植する判断も、Field Looperへ採用済みとする判断も行わない。次の有効な作業は、UI制作ではなく、既知信号を使った4入力クロスフェードDSPの測定試作である。

## 2026-08-28 coefficient measurement prototype

UIを作る前に、4入力Rotorの係数モデルをオフライン実装した。

- model: [`rotor_measure.py`](rotor_measure.py)
- tests: [`test_rotor_measure.py`](test_rotor_measure.py)
- observed measurements: [`MEASUREMENTS.md`](MEASUREMENTS.md)

実行した8件の単体試験は通過した。測定で確認した境界は次のとおり。

- equal-powerは `g0² + g1² = 1` を浮動小数点誤差内で保った。
- 同一信号をequal-powerで重ねると中央で `+3.0102999566398116 dB` 膨らんだ。
- linearは同一信号の振幅を保つが、非相関入力の中央では電力和が `0.5` になる。
- Track 4からTrack 1への一周境界は係数連続にできた。
- 150 ms時定数の指数慣性モデルは停止命令で位相をリセットしなかった。

これは係数と位相モデルの検証であり、実音、iPhone、AUv3、聴感、CPU負荷、UIを検証したものではない。研究状態は引き続き `active` とする。
