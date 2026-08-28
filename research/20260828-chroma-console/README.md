# Hologram Electronics Chroma Console 研究

- research-id: `20260828-chroma-console`
- 研究対象: Hologram Electronics Chroma Console
- 状態: 研究記録。製品実装・統合採用は未実施
- 更新日時: 2026-08-28
- 対象リポジトリ: `daken123-gif/sound-lab`

## 1. 現在の問い

Chroma Consoleを20種類のエフェクト集として模倣するのではなく、音の組み替え方、演奏性、入力レベル設計、時間バッファ、操作記録、意図的な制限を分解する。

そのうえで、4トラック、Skulptur型の主演奏面、Microcosm、Strymon、OTO BIM／BAM／BOUM、1192 Blackface、iPhoneマイク入力、Max/MSP・Elektronのモーション研究へ、どの設計原理を接続できるかを判定する。

KAOSS Pad型はプロジェクトのマスター主演奏面から外れ、録音後の主演奏系はSkulptur型へ移行している。Chroma Console研究によってKAOSS型Masterを復活させない。

## 2. 資料と証拠区分

### 一次資料

1. Hologram Electronics, Chroma Console製品ページ  
   <https://www.hologramelectronics.com/pages/chroma-console>
2. Hologram Electronics, Chroma Console User Manual, Firmware v1.042  
   <https://cdn.shopify.com/s/files/1/0920/2928/8752/files/CC_manual_WEB.pdf?v=1758823440>
3. Hologram Electronics, Chroma Console Firmware  
   <https://www.hologramelectronics.com/pages/chroma-console-firmware>
4. Hologram Electronics Store, Chroma Console製品仕様  
   <https://www.hologramelectronics.com/products/chroma-console>

### 実機評価として参照

1. Ian Rapp, Waveform Magazine, Chroma Console Review  
   <https://waveformmagazine.com/waveform-reviews/chroma-console-hologram-electronics/>
2. Alexandr, SINESQUARES, Hologram Electronics Chroma Console Review  
   <https://www.sinesquares.net/musicgear/hologram-electronics-chroma-console-review>
3. Sound On Sound, Hologram Electronics Chroma Console  
   <https://www.soundonsound.com/reviews/hologram-electronics-chroma-console>

一次資料で確認した仕様、第三者の実機評価、この研究で行ったDSP推論を以下では分離する。

## 3. 設計者の狙い

公式マニュアルの設計者ノートは、特定のヴィンテージ機材を忠実に再現することを目的としていない。4トラック・カセットのプリアンプを過大入力する、ミキサー卓をクリップさせる、古いサンプラーの低品位コンバーターを利用する、アナログディレイを発振させる、といった本来の用途から外れた使い方で生まれる音を対象にしている。

したがってChroma Consoleの中心は次の三点である。

- 機材の制限や故障を、音楽的に操作可能な範囲へ閉じ込める
- 複数の単純な処理を並べ替え、相互作用から複雑な結果を得る
- メニュー編集より先に、聴く、触る、偶然を保持する

公式はChroma Consoleを特定機材の厳密なエミュレーションではないと明記している。この研究でも、Drive、Cassette、Reels等を特定実機の回路モデルとして断定しない。

## 4. 全体構造

Chroma Consoleには4つの役割別モジュールがあり、各モジュールから同時に使用できるエフェクトは一つである。モジュール自体はOFFにできる。

| モジュール | 音響上の役割 | エフェクト |
|---|---|---|
| Character | 入力の輪郭、反応、飽和 | Drive / Sweeten / Fuzz / Howl / Swell |
| Movement | 周期、複声、音程、振幅の運動 | Doubler / Vibrato / Phaser / Tremolo / Pitch |
| Diffusion | 遅延、残響、反転、時間バッファ | Cascade / Reels / Space / Collage / Reverse |
| Texture | 周波数整理、圧縮、媒体劣化、破損 | Filter / Squash / Cassette / Broken / Interference |

最大4エフェクトを直列で使用し、4モジュールの順番は24通りに変更できる。並列配線、Send／Return、同じモジュールから二つのエフェクトを同時使用する構造はない。

基本信号モデルは次になる。

```text
INPUT / CALIBRATION
  -> CAPTURE PRE（選択時）
  -> 4 MODULE PERMUTATION
  -> GLOBAL DRY/WET MIX
  -> CAPTURE POST（選択時）
  -> OUTPUT LEVEL
```

CaptureはPREまたはPOSTの一方に置く。プリセットはCapture位置を保存するが、Captureの録音内容は保存しない。

## 5. 入力キャリブレーションとヘッドルーム

### 公式仕様

Chroma Consoleは入力を聴き、Low、Medium、High、Very Highの4段階から入力ヘッドルームを選ぶ。手動選択もできる。

- 高いヘッドルーム: 大きな入力をよりクリーンに扱う
- 低いヘッドルーム: 小さい入力でも早く飽和・圧縮へ入る

キャリブレーションは単なる入力音量補正ではない。圧縮・飽和の閾値と複数のエフェクトパラメータを入力素材へ合わせる。CharacterのSensitivityで、キャリブレーション後のブレークアップ位置をさらに調節できる。

### この研究からの採用判断

iPhone内蔵マイク、イヤホンマイク、外部インターフェース、内部音声、シンセ出力へ同じ固定ゲインを使わない。入力開始時に次を観測し、内部ヘッドルームを選ぶ必要がある。

- 通常演奏レベル
- 瞬間ピーク
- トランジェント量
- ノイズ床
- 入力経路

これがない状態でDrive、Fuzz、Squash、Cassetteを実装すると、音源ごとに反応が変わり、声は潰れ、ライン入力はクリップし、低出力入力は何も起きない。

## 6. 20エフェクトの観測

### 6.1 Character

CharacterはToneではなくTiltを持つ。中央が概ね中立、右で明るく、左で暗くなる。飽和系ではTiltがEQだけでなくトランジェントやバイアス特性にも作用する。

| エフェクト | 公式に確認できた挙動 | 主操作 |
|---|---|---|
| Drive | 温かいプリアンプからフルオーバードライブ | Tilt / Amount / Sensitivity |
| Sweeten | EQ、圧縮、穏やかな飽和を同時に増加 | Tilt / Amount / Sensitivity |
| Fuzz | 丸いファズからブロウンスピーカー的な荒さ。Tiltでトランジェントとバイアスも変化 | Tilt / Amount / Sensitivity |
| Howl | 共振フィルター付きファズ。持続音または短いシンセ的スタブ | Tilt / Amount / Sensitivity |
| Swell | 入力エンベロープで音量を立ち上げる | Tilt / Attack-Decay / Trigger Sensitivity |

Sweetenは「音を良くする固定プリセット」ではなく、次段へ送る信号の密度と飽和量を調節する前段として扱う。

### 6.2 Movement

| エフェクト | 公式に確認できた挙動 | Drift |
|---|---|---|
| Doubler | タイトな複声から短いスラップバックまで | 瞬間的なランダム・ピッチずれ |
| Vibrato | 正弦波のピッチ変調からテープ状の揺れ | 不規則波形化とステレオ幅増加 |
| Phaser | 2段から12段へ段数も変化するフェイザー | 位相変調波形の不安定化 |
| Tremolo | 滑らかな振幅変調から矩形的チョップ | 周期・深さ・波形の変動 |
| Pitch | -1オクターブから+1オクターブを連続移動 | 解像度低下と不安定化 |

MovementはLFO一覧ではない。Doublerは短い遅延、Pitchは可変速度読出し、Vibratoはステレオ相関まで含み、Driftはエフェクトごとに異なる内部へ入る。

### 6.3 Diffusion

| エフェクト | 公式に確認できた挙動 | Drift |
|---|---|---|
| Cascade | BBD系を強調した暗いディレイ。最大フィードバックで発振・歪み | 反復のピッチ変調、劣化 |
| Reels | 明るく変化し続ける古いテープエコー | テープ再生の不安定化、反復の崩壊 |
| Space | 小さな録音室から巨大な音雲まで5種の残響を連続移行 | 残響内部のピッチ変調 |
| Collage | TIME操作でディレイラインを破壊的編集するルーピングディレイ | ランダム倍速ループ、ピッチ変調 |
| Reverse | -1から+1オクターブ相当の再生速度を持つ逆再生ディレイ | 反復のピッチ変調 |

DiffusionのEffect Volumeはモジュール全体ではなくウェット成分だけを増減する。これにより原音を保ったままディレイタップ、残響、ループを後段へ強く送れる。

### 6.4 Texture

| エフェクト | 公式に確認できた挙動 | 制限・特徴 |
|---|---|---|
| Filter | Tilt / LPF / HPFをプリセットごとに選択 | レゾナンス操作はない |
| Squash | 強い圧縮からオーバードライブ | 後段で暴れるチェーンを押さえられる |
| Cassette | 飽和、圧縮、フィルター、wow、flutter、pitch artifact | Amount一本の範囲内で複数の劣化状態を移行 |
| Broken | 周期的ピッチ落下、振幅・周波数変調 | 壊れたモーター機器の挙動 |
| Interference | 通信・無線由来の妨害を音楽的な層として追加 | Amountで妨害の種類と強度が変化 |

Textureの重要点は、Cassetteだけでなく「一時的に正常動作しない機器」を扱うことにある。BrokenとInterferenceは常時かかるEQではなく、正常な信号へ間欠的な事故を混ぜる。

## 7. 順番による相互作用

同じエフェクトでも順番が音色になる。

| 配線 | 音響結果の推論 |
|---|---|
| Sweeten -> Collage -> Cassette | 整えた入力を切り刻み、断片とフィードバック全体を媒体劣化させる |
| Cassette -> Collage -> Sweeten | 劣化済みの断片を循環させ、最後に密度とピークをまとめる |
| Space -> Fuzz | 残響尾まで歪み、入力停止後も飽和した壁が残る |
| Fuzz -> Space | 歪んだ原音から比較的滑らかな残響が伸びる |
| Collage -> Squash | 断片・発振・ピークを圧縮し、音量を演奏可能な範囲へ押し込む |
| Squash -> Collage | 入力振幅が均されるため、バッファへ入る断片密度が安定する |
| Pitch -> Reverse | 移調された素材を逆再生する |
| Reverse -> Pitch | 逆再生バッファ全体の速度・音程を再変換する |

これは観測したChroma Console内部コードではなく、公式が示す各エフェクト挙動と直列配線からの信号処理上の推論である。

## 8. 各段の音量は音色パラメータ

各モジュールはEffect Volumeを持つ。前段出力を上げると、後段のDrive、Fuzz、Squash、Cassette、ディレイフィードバックへ強い信号を送れる。公式マニュアルは、モジュール同士をオーバードライブでき、信号列全体もヘッドルーム付近で穏やかにソフトクリップすると説明している。

一般モジュールの実装候補は次になる。

```text
y[n] = G * ((1 - mix) * x[n] + mix * F(x[n]))
```

Diffusionはウェット音量だけが独立する。

```text
yD[n] = xD[n] + Gwet * FD(xD[n])
```

全モジュールを同じWet/Dry式へ押し込むと、残響だけを後段へ強く送る挙動を失う。

## 9. DRIFT

DRIFTは全エフェクト共通のランダムLFOではない。MovementとDiffusionの各アルゴリズムに固有の「故障量」である。

| 対象 | DRIFTが触る内部状態 |
|---|---|
| Doubler | 短時間の読出し遅延またはピッチ |
| Vibrato | 変調波形と左右差 |
| Phaser | 位相変調波形 |
| Tremolo | 振幅変調の周期・深さ・波形 |
| Pitch | ピッチシフター解像度と安定性 |
| Cascade | 反復のピッチと信号劣化 |
| Reels | テープ再生安定性と反復劣化 |
| Space | 残響ネットワーク内のピッチ |
| Collage | 倍速断片の発生確率とピッチ |
| Reverse | 逆再生反復のピッチ |

採用時は、各DSPが独自のDrift関数を持つ。全体へ一本のノイズLFOを加える実装は採用しない。

## 10. GESTURE

### 公式仕様

Gestureは主要ノブの動きを記録し、反復再生する。複数ノブへ個別の録音を追加できる。既に記録されたノブをGestureモードで動かすと、そのノブの記録を上書きする。通常演奏状態で動かすと、そのノブの記録だけを消去する。

記録後にTap Tempoまたは外部MIDI Clockを変えると、元の動き全体を高速化・低速化できる。ゆっくりした手の動きを記録してから高速化し、人間の手では直接作れない変調を作れる。

記録対象は主要操作である。

- Tilt
- Rate
- Time
- Mix
- 各モジュールのAmount

マニュアル上、次をGestureで記録するとは確認できない。

- モジュール順
- エフェクト選択
- Drift
- Effect Volume
- Capture位置
- Filter形式

### GestureとDriftの分離

Gestureは人間が作った再現可能な運動、Driftはエンジン固有の非再現的な故障である。

```text
parameter(t) = Gesture(t) + DriftContinuous(t) + RareEvent(t)
```

CollageならGestureは読み出し位置の大きな運動、DriftContinuousはピッチの小さな揺れ、RareEventは低確率の倍速断片として分ける。Driftを上げてもGestureの形そのものは消さない。

### iPhoneへ採用する操作

タイムライン編集を設けない。

1. 動かしたい操作子を長押し
2. 指を動かす
3. 離すと反復開始
4. 通常状態で再び触ると、その記録だけ解除

これはUI実装ではなく、研究上の操作仕様候補である。

## 11. CAPTURE

### 公式仕様

- 最大30秒
- Tapフットスイッチを押している間だけ録音
- 離した瞬間に反復再生
- 短い録音は端をソフトに重ね、サステイン／ドローン化
- 長い録音は通常のフレーズループ
- PRE-FXまたはPOST-FXをプリセットごとに選択
- 録音内容はプリセットへ保存されない

### 実機評価で確認された制限

Captureはオーバーダブできない。新しく録音すると以前の録音を消して置き換える。Waveform MagazineとSINESQUARESの実機評価も、単一保持・即時操作として扱っている。

### 4トラックとの境界

Captureは保存、編集、複数レイヤー管理を行うトラック・ルーパーではない。4トラックとは統合せず、その前後で「いま鳴った音を一時的につかむ手」として使う。

重要なのは30秒という数値ではなく、押す、録る、離す、保持する、次の録音で置き換える、という因果関係である。

## 12. CollageのDSP仮説

公式説明では、CollageはTIMEを動かすとディレイラインを破壊的に編集し、ピッチベンド、倍速・半速ループ、短いグラニュラー断片を反復へ畳み込む。

この挙動から、次の構造を仮説とする。

```text
stereo circular buffer
  -> movable read head
  -> variable playback rate
  -> short-region latch
  -> interpolation / crossfade
  -> feedback reinjection
```

必要になる処理候補:

- ステレオ円形バッファ
- 可変読出しヘッド
- 再生速度補間
- 短区間ラッチ
- フィードバック内部への断片再投入
- 読出し位置ジャンプ時のクロスフェード
- 倍速／半速／逆方向の速度状態

これは公式ソースコードや回路を取得した結果ではない。公式に記載された音響挙動からの実装仮説であり、実音比較は未実施。

## 13. プリセット、バイパス、MIDI

### プリセット

80ユーザープリセットが保存するもの:

- エフェクト選択とモジュール順
- 主要操作値
- 副操作値
- Gesture録音
- Filter形式
- Dual Bypass設定
- Capture位置
- Expression割当
- Tap Tempo

Capture音声は保存しない。

### Dual Bypass

通常は全体バイパスだが、選択したモジュールだけを一つのフットスイッチで出し入れできる。さらに全体バイパスも残る。プリセットごとに設定できる。

### MIDI

DINとUSB-C MIDIに対応する。主要・副パラメータ、モジュール選択、個別バイパス、Gesture、Capture、Capture位置、Filter形式、キャリブレーション、Tap Tempo、プリセット呼出しをMIDIから操作できる。

同期対象:

- Vibrato
- Phaser
- Tremolo
- Cascade
- Reels
- Collage
- Reverse

Pitch、Doubler、Spaceをクロック同期対象として公式表は列挙していない。

## 14. 技術仕様

公式マニュアルで確認した値:

- AD/DA: 24-bit / 48 kHz
- 最大入力: +8 dBu
- 入力インピーダンス: 1 MΩ
- 出力インピーダンス: 1 kΩ未満
- Stereo Input / Output
- Mono to Stereo、Stereo to Monoを接続状態から自動判定
- 9 V DC、500 mA以上、センターマイナス
- True Bypass、Buffered Bypass、Buffered Bypass with Trails
- DIN MIDI In / Out
- USB-C MIDI
- Expression: TRS、推奨10 kΩ超

公式ファームウェアページで確認した最新掲載版:

- Version: 1.04
- 公開日: 2025-05-05
- Preset Browser読込み高速化
- モジュール個別Bypass／Engage用MIDI CC追加
- 安定性改善と不具合修正

確認日は2026-08-28。将来の更新可能性があるため、固定的な最終版とは扱わない。

## 15. 実機評価から見えた境界

第三者の実機評価で報告された点:

- ルーティング変更時には音が切れる
- Captureはオーバーダブできない
- Filterはレゾナンスを操作できず、主に周波数整理向け
- 同じモジュール内の二エフェクトを併用できない
- 4モジュールを常時使うより、一つか二つだけ使う運用へ落ち着く場合がある
- Character単体でもDrive／Fuzz用途として成立するという評価
- Texture、とくにCassette、Broken、Interferenceの間欠的故障が独自性として高く評価されている

評価者の感想は製品仕様とは分離する。音質の優劣はこの研究では実機比較していない。

## 16. 意図的な制限

Chroma Consoleが持たないもの:

- 並列ルーティング
- 任意の同カテゴリ複数使用
- Captureオーバーダブ
- Capture波形編集
- Gestureタイムライン編集
- Filter Resonance操作
- 画面上の詳細パラメータ編集
- 無音なしのルーティング切替

これらをすべて補うと、Chroma Consoleの研究をDAW型マルチエフェクトへ変えてしまう。採用時も「不足を埋める」ことを自動的な正解にしない。

## 17. プロジェクト全体への位置づけ

### 現在の役割分担候補

| 研究 | 担当 |
|---|---|
| 4トラック | 録音された時間、レイヤー、再生 |
| Skulptur型 | 録音後の主演奏面、素材へ直接触る音色運動 |
| Microcosm | 入力から予想外のフレーズを発生させる時間変換 |
| Chroma Console | 高品質エンジンを並べ替え、経路と故障を演奏する枠 |
| Strymon | 残響・空間エンジンの基礎研究 |
| OTO BIM／BAM／BOUM | Delay／Reverb／Saturationの専用機研究 |
| 1192 Blackface | ダイナミクスと音像の前進 |
| iPhoneマイク | 入力段、ヘッドルーム、声の取得 |
| Max/MSP／Elektron | 操作記録、モジュレーション、状態遷移 |

Chroma ConsoleはSkulptur型の代替ではない。Skulptur型は素材そのものへ触る主演奏面、Chromaはその音を通す信号経路の構造である。

### Chromaの4枠へ接続する研究候補

| Chromaの枠 | 接続候補 |
|---|---|
| Character | 1192 Blackface、OTO BOUM、iPhone入力段 |
| Movement | Doubler、Vibrato、Things Motor系の運動研究 |
| Diffusion | OTO BIM、BAM、Strymon、Collage |
| Texture | Cassette、Broken、Interference、Combustor |
| Gesture | Max/MSP・Elektronのモーション記録 |
| Capture | Microcosmとは分離した一時保持層 |

これは統合採用済みの記録ではない。各研究の結果をChroma型の枠へ接続できるという設計候補である。統合判断は`integration/`の正本で別途行う。

## 18. 採用する点

研究から採用候補とするもの:

1. 音響役割をCharacter / Movement / Diffusion / Textureへ分ける
2. 各役から同時に一エンジンだけ選ぶ
3. 全モジュールOFFから始め、必要な役だけ追加する
4. 4段の順番を変更できる
5. 各段のゲインを後段との相互作用へ使う
6. Diffusionのウェット出力を独立させる
7. 主要操作の手の動きを反復記録する
8. Gestureとエフェクト固有Driftを別系統にする
9. Captureを単一の一時保持層とする
10. CaptureをPRE／POSTへ置く
11. 入力素材に応じて内部ヘッドルームを選ぶ
12. 故障量をエフェクト固有の複数パラメータへ写像する

## 19. 採用しない点

現時点で採用しないもの:

- Chroma Console筐体外観の模倣
- 色だけに依存する状態表示
- A+B、C+D、A+Dなどの同時押しメニュー
- 主要／副操作を同じノブへ重ねる構造
- 20エフェクトの一括実装
- 80プリセットの階層ブラウザ
- KAOSS型Master主演奏面の復活
- 4モジュール常時ON
- Captureの4トラック化
- 全DSPへ共通ランダムLFO一本を送るDrift
- Collageを通常ディレイ＋ランダム値だけで済ませる実装

## 20. UIへ持ち込む場合の境界

専用筐体では、印刷された操作一覧、色付きLED、物理ノブの位置が隠れた状態を補う。iPhoneでは同じ方式を採らない。

持ち込まない:

- ボタン同時押し
- 色だけによるモード表示
- ノブの表裏切替
- 長押しとタップへの多数機能の集中
- 20エフェクト一覧
- ルーティング専用の深い画面

操作候補:

- 4役を一画面で確認
- モジュール単位の明示的ON/OFF
- 使用中の一エンジンだけ表示
- 順番は4要素の直接移動
- Gesture記録中の操作子だけ明示
- Captureは押して録音、離して保持

UIの視覚デザインはこの研究では作成していない。既存試作の外観を流用していない。

## 21. 最小実験構成

実装を始める場合の研究用最小構成候補:

- Character: Sweeten相当の入力密度、または外部研究から一エンジン
- Movement: DoublerまたはVibrato
- Diffusion: Collage簡易検証または既存の高品質Delay／Reverb一つ
- Texture: CassetteまたはBroken
- 共通: モジュール順、ON/OFF、Gesture、固有Drift、Capture PRE/POST

ただし最初から4エンジンを同時に作らない。まず二つの非可換な処理を用意し、順番変更で実際に音が変わることを検証する。

推奨する最初の検証対:

- Diffusion -> Texture
- Texture -> Diffusion

たとえば短いDelayとCassetteを使えば、反復ごとに劣化する経路と、劣化済み入力を反復する経路の差を確認できる。

## 22. 触る実装パス

現時点では研究保存のみで、実装パスは未決定。製品コードは変更していない。

## 23. 依存する研究

- `20260828-iphone-mic-preamp`
- KAOSS退役とSkulptur採用を記録する統合判断
- Microcosm研究
- Strymon空間・残響研究
- OTO BIM／BAM／BOUM研究
- 1192 Blackfaceコンプ研究
- Max/MSP研究
- Elektron研究
- Things Motor研究
- Combustor研究

Git上のresearch-idが未確認の研究は、ここでは名称だけを記録した。存在を推定してresearch-idを作っていない。

## 24. 失効した判断

### 失効

- KAOSS Pad型をマスター主演奏面として維持し、その後段または代替としてChroma Consoleを置く判断。

### 現在

- KAOSS Pad型はマスター主演奏面から外れている。
- 録音後の主演奏系はSkulptur型が中心。
- Chroma ConsoleはSkulptur型と競合するXY演奏面ではなく、複数の音響研究を接続する可変直列経路として研究する。

## 25. 未検証事項

- 実機音を同一入力・同一ラウドネスで比較していない
- 各アルゴリズムの内部DSP構造は非公開で未取得
- Gestureの厳密な最大時間を一次資料本文から確定していない
- ルーティング切替時の無音時間を計測していない
- 各エフェクトのレイテンシーを計測していない
- Mono to Stereo時の左右生成規則を測定していない
- Spaceの5残響間の補間方法を解析していない
- CassetteのAmount位置と各劣化要素の対応を測定していない
- Broken／Interferenceの確率分布とイベント密度を測定していない
- Collageのバッファ長、読出し速度、クロスフェード時間を測定していない
- iPhone上でのCPU負荷と安全な同時DSP数を測定していない
- Skulptur主演奏面との同一画面上の関係をUI検証していない

## 26. 次の研究段階

次段階はUI制作ではなく、音響挙動の検証とする。

1. 非可換な二処理の順番比較
2. エフェクト固有Driftの確率モデル
3. Gestureの記録・再生・テンポ伸縮
4. Capture短時間録音の境界クロスフェード
5. 入力キャリブレーションと飽和閾値
6. Collageの円形バッファ仮説検証

各段階で、公式仕様、こちらの実装、実音観測を別欄へ追記する。

## 27. 音響検証1: DelayとCassetteの非可換性

合成テスト信号と決定論的な簡易DSPモデルを使い、`Delay -> Cassette` と `Cassette -> Delay` を同一RMSで比較した。

既定条件の結果:

- Cross Correlation: `0.9983051715`
- Difference RMS: `-42.6597475 dBFS`
- `Delay -> Cassette` の6 kHz以上Energy Ratioは反対順の約`1.4950`倍

Drive 3段階、Feedback 3段階の9条件を掃引した。最も弱い条件から最も強い条件へ、Difference RMSは約11.55 dB増加した。強条件では高域Energy Ratio比が約1.93になった。

この結果は次を支持する。

- 非線形段と時間段の順番は同一結果にならない
- 順序差の大きさは飽和量、フィードバック量、各段への入力レベルに依存する
- 各段のEffect Volumeは音量補正だけでなく、後段との相互作用を作る

一方、既定条件の相関は高く、順番を変えるだけで常に劇的な差になるとは判定しない。

実験資料:

- [`experiments/noncommutative_chain.py`](experiments/noncommutative_chain.py)
- [`experiments/noncommutative-chain-results.md`](experiments/noncommutative-chain-results.md)
- [`experiments/noncommutative-chain-metrics.json`](experiments/noncommutative-chain-metrics.json)

検証状態:

- 同一スクリプトの二回実行で数値が完全一致
- 生成した3つのWAVがbyte単位で一致
- Python構文検査に成功
- 実機一致、実楽器での知覚差、リアルタイム負荷は未検証
