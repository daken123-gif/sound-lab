# BattleFX研究

- status: `active`
- research-id: `20260828-battlefx`
- 更新日時: 2026-08-28T08:30:00Z
- 研究対象: Unfiltered Audio BattleFX
- 現在の問い: BattleFX固有の「残響バッファを別周期でchokeする」構造は、4トラック録音素材を人間が再演奏する個人用iPhone楽器へ何を持ち込めるか。

## 継続研究

- [Phase 2 — 三時計と演奏文法](./PHASE_2.md)
  - material / interruption / instabilityの三時計
  - Chokeの内部位置による音楽的差
  - S.RATEによる時間とpitchの結合
  - `EXCITE / STARVE / BREAK / LEAN / KILL / CATCH`の演奏単位

## 先に固定する現在判断

BattleFXをField Looperのマスターエフェクトまたは主演奏面として採用しない。Git正本の現行判断では、録音後の主演奏面はSkulptur型であり、KAOSS中心階層は退役済みである。

BattleFXから研究する中心は、delay/reverbの種類数ではない。**入力音ではなく、入力後に生じた反復と残響を、原音とは別の周期でchokeして再びリズムへ戻す構造**である。

現時点では製品採用済みではない。研究候補は次の限定位置に置く。

```text
RAW / 4 tracks
  -> selected track or explicit send
  -> rhythmic-tail processor (BattleFX研究領域)
  -> resample / Performance Take候補

4-track mix
  -> Skulptur型主演奏面
  -> master/output
```

## 取得した一次資料

1. Unfiltered Audio BattleFX製品ページ
   - https://www.unfilteredaudio.com/products/battlefx
2. Unfiltered Audio公式ブログ「One Battle After Another (Week 2)」
   - https://www.unfilteredaudio.com/blogs/news/one-battle-after-another-week-2
3. Unfiltered Audio Battalion User Manual
   - https://cdn.shopify.com/s/files/1/1439/4216/files/Unfiltered_Audio_Battalion_Manual.pdf?v=1751045249
4. Apple App Store BattleFX
   - https://apps.apple.com/us/app/battlefx/id6764648922
5. Unfiltered Audio iOS案内
   - https://www.unfilteredaudio.com/pages/ios

## 取得した二次資料

1. Bedroom Producers Blog, BattleFX review
   - https://bedroomproducersblog.com/2026/05/16/unfiltered-audio-battlefx/
2. Audio Plugin Guy, BattleFX review
   - https://www.audiopluginguy.com/free-plugin-review-battlefx-by-unfiltered-audio/
3. Data Broth, Battle FX review
   - https://www.databroth.com/blog/battle-fx-review
4. CDM, BattleFX article
   - https://cdm.link/battle-fx/

二次資料は、公式資料に記載のないモード名、実使用上の信号経路、操作感を補うために分離して使う。二次資料の記述をUnfiltered Audio公式仕様へ昇格させない。

## 観測できた事実

### 製品の位置

- BattleFXはBattalionのsend effectsとmaster processingを独立させた無償プラグインである。
- 中核は`Shatter Delay`、`Headspace Reverb`、3-band EQ、`Maximize`、clipping部である。
- BattleFX独自の追加として、delayとreverbのbufferを反復間隔で自動chokeする系がある。
- chokeはdelayとreverbで独立制御でき、tempo syncまたはfreeで走り、拍の前後へnudgeできる。
- Euclidean pattern knobを含む。
- iPhone/iPad版は無料で、App Store表示ではiOS/iPadOS 12.0以降、容量23.8 MBである。
- Unfiltered AudioはiOS版プラグインをAUv3ホスト（AUM、Logic Pro、GarageBand、Drambo、Cubasis等）で使う経路を案内している。

### エフェクト間の接続

Battalion公式マニュアルでは、Shatter DelayとHeadspace Reverbは独立でも動作し、中央SENDでdelay出力をreverb入力へ送れる。

```text
input -> Shatter Delay ---------> output
                    \-> SEND -> Headspace Reverb -> output
input -------------------------> Headspace Reverb -> output
```

BattleFXの完全な内部回路図は取得できていない。上図は公式に明記された独立動作とdelay-to-reverb SENDだけを表し、dry/master直通を含む全配線を断定しない。

## Shatter Delay

### 公式資料で確認した処理

| control | 観測できた意味 |
| --- | --- |
| TIME | Sync時はhost BPMに基づく音価、free時はHzでdelay timeを設定する |
| FEEDBACK | delay出力を入力へ戻し、反復数を決める |
| FB TILT | feedback経路で反復ごとに低域または高域を削る |
| GLITCH | delay timeへ滑らかなBrownian motionを加える。大きい値では反復間隔が均一にならない |
| STEREO | GLITCHの乱数値を左右独立にする。offでは左右が値を共有する |
| PONG | 左delayへ右出力、右delayへ左出力を交差帰還する |
| DUCKING | 新しい入力でfeedback bufferの音量を下げ、入力を前へ出し、既存反復を減らす |
| S.RATE | 単なる出力bitcrushではなくeffect DSP全体の処理率を下げる。delay timeが伸び、buffer内容が低くpitch shiftする |
| GAIN | delay effectの出力レベル |

### Instant Delayの意味

公式マニュアルは、Shatter Delayがgranular bufferを使い、delay time変更時のpitch artifactを避けるInstant Delay系だと説明する。

ここで確認できるのは、時間変更時に通常の可変delayで生じる連続的なテープ式pitch sweepを抑える目的でgranular bufferを使うことまでである。grain長、window、overlap数、read-head数、crossfade則は未公開であり、同一実装を断定しない。

### 音楽的状態

Shatter Delayは一つのdelayではなく、設定によって三状態を横断する。

1. **echo**: tempo sync、低feedback、低glitch
2. **unstable repeat**: 中程度glitch、stereo、feedback tilt
3. **excited resonator**: sync off、極短time、高feedback、低sample rate

公式開発者は、極短delayと高速chokeからKarplus-Strong的buzz、flam、ruff、digital glitchが生じると説明している。したがってdelayを「音の後ろに足す処理」だけで扱うと、この製品の中心を落とす。

## Headspace Reverb

### 公式資料で確認した処理

- SILO Granulatorのreverbを更新したもの。
- MODEは内部delay networkの調律を変える。
- PREDELAYはsync時にhost tempoの音価、free時にmillisecondsで指定する。
- PREDELAYもInstant Delay系で、変更時の不快なpitch artifactを避ける設計と説明されている。
- DECAYは知覚上のroom sizeを変える。
- S.RATEはreverb DSP全体の処理率を変え、低下させるとartifactが増え、知覚上の空間が広がり、buffer内のechoが低くpitch shiftする。
- IN TILTはbuffer内で特定帯域が蓄積する前に抑える。
- OUT TILTは残響出力の最終音色を整える。

### mode名

二次資料では次の10 modeが報告されている。

`Dark / Rusty / Saturated / Glitter / Crayon / Bokeh / Flare / Flutter / Hollow / Austere`

公式BattleFXマニュアルは現在取得できず、公式製品ページにも一覧がないため、名称と各modeの正確なアルゴリズムは二次資料観測として隔離する。

### S.RATEはlo-fi量ではない

重要なのは、S.RATEを静的な「汚し量」にしないことである。公式説明では処理率そのものが変わるため、次が結合する。

- artifact量
- delay/reverbの知覚時間
- buffer内のpitch
- feedback/reverb networkの安定性

Field Looperへ抽出する場合も、`DIRT`のような外観上の一ノブへ潰すと構造が失われる。

## Automatic Choke / Euclidean system

### BattleFX固有の中心

Battalion本体ではdrum voice同士のtriggerで別voiceをchokeできる。BattleFXにはそのdrum sequencerがないため、Joshがdelay/reverb用のEuclidean choking systemを追加したと公式ブログが説明している。

これは通常のsidechain duckingと異なる。

| 処理 | 何が引き金か | 何を変えるか |
| --- | --- | --- |
| input ducking | 新しい入力音 | feedback bufferの音量 |
| choke | 内部周期／Euclidean pattern | delay/reverbのtailまたはbuffer |
| nudge | 演奏者のoffset設定 | chokeの発生位置 |

入力音の発音周期と、残響を止める周期を分離できる。そのため一発の声、環境音、持続noiseからでも、入力にはなかった休符とアクセントが生まれる。

### Euclidean実装の仮説

一般的なEuclidean rhythmは、`n`個のstepへ`k`個のeventをできるだけ均等に分配する。BattleFXの正確なstep数、rotation、knob mappingは未取得である。

実装研究では次の最小モデルから始められるが、これはBattleFXの複製仕様ではない。

```text
pattern = bjorklund(steps, hits)
phase = (transportPhase + nudge) mod cycleLength
if pattern[currentStep] == hit:
    applyChokeEnvelope(delayBufferGain or reverbBufferGain)
```

必要な状態は`steps`、`hits`、`cycleLength`、`nudge`、`choke envelope`である。ただしiPhone演奏面へ全値を常設しない。

### 「残響を殺す」時間設計

chokeはbinary muteだけでは不十分である。Battalion本体のCHOKEは対象を`smoothly silence`すると公式マニュアルにある。BattleFXのchoke envelope形状は未取得だが、実装実験では最低でも以下を分けて比較する。

- hard clear: bufferを即時消去
- output gate: bufferを残し出力だけ閉じる
- feedback cut: feedback注入だけ止める
- short fade: clickを避けながらtailを消す
- duck-and-return: 一時的に抑えて以前のtailを戻す

これらは聴感と次のchoke後の挙動が異なる。BattleFXを見た目だけ模倣せず、実機録音で判定する。

## Maximize / EQ / clipping

公式Battalionマニュアルでは、MAXIMIZEは小さい信号を大きく持ち上げ、decay tailの形を変え、reverbを過剰に強調するeffectである。

3-band EQはLOW/MID/HIGH gain。clip modeは次の4状態を持つ。

- No Clipping
- Soft Clipping
- Hard Clipping
- Wavefolding

Maximizeを通常の透明なlimiterとして扱わない。noise floor、iPhone micのroom noise、feedback tailも押し上げる可能性が高い。Field Looperへ採る場合は、RAWまたは4-track masterへ無条件に置かず、BattleFX系wet bus内で明示的に使う候補とする。

## 信号経路上の注意

Audio Plugin Guyの実使用報告では、BattleFXのMasterが独立destinationとしてdry inputのcopyを受け、`Mix 100%`だけでは通常のsend effectとして完全wetにならない。delay/reverbをSoloにしてMaster直通を外す運用が必要だとされる。

これは公式回路図で確認できていないため二次資料観測である。iOS実機試験では、impulseを入力してdry impulseが残るかを録音し、次を個別に確認する。

- Mix 0 / 50 / 100%
- Delay Solo
- Reverb Solo
- Delay + Reverb Solo
- Master section on/off
- Delay-to-Reverb SEND 0 / 100%

## Field Looperへの採用候補

### 採用候補A: 選択trackのRhythmic Tail Send

4トラック全部へ常時insertしない。人間が一つのtrackを選び、必要な瞬間だけtail busへ送る。

```text
selected track
  -> pre-filter
  -> short/granular delay
  -> character reverb
  -> independent delay/reverb choke clocks
  -> wet capture
```

元trackは保持し、tail処理を非破壊にする。処理結果を第5トラックとして常設せず、Performance Takeまたは明示resampleとして記録する案を優先する。

### 採用候補B: 声からリズムを作る

- 子音を短いShatter系delayへ送る。
- 母音を長いHeadspace系reverbへ残す。
- delay chokeを速くする。
- reverb chokeを2〜4小節程度の疎な周期にする。
- 二つのnudgeを逆方向へずらす。

狙いは声のwaveformをstep sequencerで切ることではない。声が残した空間だけから、flam、ruff、空白、長いbloomを作る。

### 採用候補C: Chokeを演奏記録する

Performance Take候補として記録すべきなのは全parameterの連続automationではなく、次の少数eventで足りる可能性がある。

```text
TAIL_SEND_ON(track)
CHOKE_DENSITY(value)
CHOKE_NUDGE(value)
TAIL_KILL()
TAIL_CAPTURE()
TAIL_SEND_OFF(track)
```

これは未統合の設計仮説であり、現在のPerformance Take仕様を更新したものではない。

## 主演奏面へ持ち込まないもの

- BattleFXの全ノブを常設すること
- 10 reverb modeを主演奏中に階層メニューから選ばせること
- 4トラックすべてへ個別のdelay/reverb/chokeを複製すること
- Maximizeを常時masterへ置くこと
- BattleFXの軍事テーマ、配色、パネル外観を模倣すること
- Euclidean step editorをそのまま表示すること
- XY padへ全処理を再回収し、KAOSS中心階層を復活させること

## iPhone用の操作抽出

BattleFXそのものはノブが多い。Field Looperでは次の三つを第一候補にする。

| 演奏語 | 内部で動く候補 | 手触り |
| --- | --- | --- |
| TAIL | delay/reverb sendとdecay | 残す量 |
| BREAK | Euclidean hits/densityとchoke envelope | 残響を殺す密度 |
| LEAN | nudgeとdelay/reverb間offset | 拍の前へ出す／後ろへ溜める |

ただし名称、gesture、画面配置は固定しない。Skulptur型主演奏面の本文がGit未収載であるため、そこへどう接続するかは未決定とする。

## 他研究との境界

Gitで本文を取得できていない研究の内容を補わない。現時点で確認できるのは統合正本の参照だけである。

- Skulptur型: 主演奏面。具体DSP/UIは未取得。
- Microcosm型: 時間変換候補。正確なresearch-idと本文は未取得。
- Strymon / OTO: 空間候補。本文は未取得。
- Chroma Console型: 可変直列経路候補。本文は未取得。
- Performance Take: 明示開始の記録核候補。最終event形式は未固定。

したがってBattleFXとの重複または統合可否は、名称や会話要約では確定しない。

## 採用しない点

1. 製品全体の再実装。
2. 既存DAWのようなsend matrixの常設。
3. 「無料だから」という採用理由。
4. presetを演奏判断の代わりにすること。
5. 自動chokeを自動作曲として扱うこと。
6. loudnessを音質向上と同一視すること。
7. dry/wet経路をUIから隠すこと。

## 実装へ進む前の検証プロトコル

### T1: impulse response / routing

- 一発のimpulseを入力する。
- dry、delay、reverb、delay-to-reverbの各経路を個別録音する。
- Solo/Mute/Mixによるdry leakageを測る。

### T2: choke semantics

- 長いreverb tailへ単一chokeを入れる。
- choke中と解除後を録音する。
- buffer clear、output gate、feedback cutのどれに近いか判定する。

### T3: Euclidean mapping

- 同じRateでEuclidean knobだけを段階変更する。
- onset列を抽出し、steps/hits/rotationの変化を推定する。
- freeとsyncを分ける。

### T4: nudge

- host clickとchoke onsetのsample差を測る。
- 正負方向、最大offset、tempo依存を確認する。

### T5: S.RATE coupling

- impulseと定常toneを入力する。
- delay time、reverb decay、pitch、aliasingを同時測定する。
- 単なるdownsamplerとの差を確認する。

### T6: iPhone負荷

- iPhone 13 mini相当実機でAUv3をAUM等に読み込む。
- 48 kHz、128/256/512 framesでCPU、dropout、発熱を記録する。
- 1 instanceと4 instancesを比較する。ただし設計候補は1 shared busを優先する。

### T7: 音楽素材

- iPhone micの声
- 室内環境音
- 単発percussion
- 4-track合成bus
- YouTube等の内部音声は、取得経路と権利境界を別研究の実測条件に従う

## 音量・安全上の境界

短delay、高feedback、S.RATE変更、Maximize、hard clip/wavefoldの組合せは急激な高域・大音量を生み得る。試験では次を固定する。

- effect前後にpeak meterを置く。
- 初期出力を十分下げる。
- feedbackへ上限とemergency killを設ける。
- headphone試験より先に低音量speakerまたは記録波形で確認する。
- RAWを上書きしない。

## 触る実装パス

現段階ではなし。研究記録だけを保存する。

将来試作する場合も、既存`field-processor/index.html`は隔離対象なので直接継ぎ足さない。新しい独立実験パスと現役PR／修理ロックを取得してから決める。

## 依存する取得済み正本

- `RESEARCH_WORKFLOW.md`
- `research/README.md`
- `integration/DIRECTION.md`
- `integration/DECISIONS.md`

## 失効した判断

- BattleFXをKAOSSの代わりのマスターFXとして扱う案: 採らない。
- BattleFXの全機能を4トラックへ埋め込む案: 採らない。

## 未検証事項

- BattleFX iOS版の実機音、latency、CPU、発熱、state restore。
- App Store版がstandaloneで外部fileを直接読めるか。
- AUv3 parameter公開範囲とhost automation。
- chokeがbufferを消去するのか、出力をmuteするのか、feedbackだけを切るのか。
- Euclidean knobのsteps/hits/rotation mapping。
- Nudgeの単位、最大幅、tempo依存。
- 10 reverb modeの正確な内部差。
- Mix/Solo/Muteを含む完全な信号図。
- Maximizeのtransfer、time constants、multiband構造。
- mono/stereo input時のPONGとSTEREO挙動。
- sample-rate変更時のanti-aliasingと内部oversampling。
- iPhone mic、内部音声、4-track busでの音楽的有効性。

## 現在の採否

- 研究継続: `yes`
- Field Looperへ統合済み: `no`
- 候補部品: `selected-track rhythmic-tail send`
- 主演奏面: `no`
- master effect: `no`
- 実装開始: `no`
