# BattleFX研究 Phase 2 — 三時計と演奏文法

- research-id: `20260828-battlefx`
- status: `active`
- 更新日: 2026-08-28
- この文書の位置: `README.md`の観測と採否を前提に、音響構造と人間の演奏単位を掘る。実機観測または実装完了を主張しない。

## 1. 今回確定した研究の焦点

BattleFXを「複数エフェクトを一画面へ並べたmulti-FX」として読むと弱い。Shatter Delay、Headspace Reverb、Chokeが一つの音へ別々の時間を持ち込む点を中心に読む。

最低でも三つの時計がある。

| clock | 進めるもの | 主な操作 |
| --- | --- | --- |
| material clock | 原音、delay反復、reverb decay | TIME、FEEDBACK、DECAY、PREDELAY |
| interruption clock | delay/reverb tailを止める時点 | CHOKE、RATE、Euclidean pattern、NUDGE |
| instability clock | delay timeの滑らかな不規則運動 | GLITCH、STEREO |

この三つは交換可能ではない。

- delay TIMEを短くしても、choke patternの休符にはならない。
- chokeを密にしても、Brownian motionの揺れにはならない。
- GLITCHを増やしても、tailを意図した時点で終わらせる操作にはならない。

したがって、Field Looperへ抽出するときに全てを`CHAOS`、`GLITCH`、`INTENSITY`の一ノブへまとめない。

## 2. Material clock

### 2.1 delayは反復間隔だけではない

Shatter Delayでは、次が結合する。

```text
TIME
  -> echo spacing
  -> feedback resonance pitch at very short values
  -> Brownian modulation target
  -> perceived relation to choke rate
```

極短TIMEと高FEEDBACKでは、反復が個別のechoとして聞こえず、一つのpitchまたは粗いbuzzへ融合する。この状態でchokeを入れると、chokeはechoを切るのではなく、**励起された仮想物体の発音長を切る**ように働く可能性がある。

これが声との接続で重要になる。声のpitchを追跡してsynth oscillatorを鳴らすのではなく、声のtransientまたはnoiseで短delay networkを励起し、別の物体音へ変えられる。

### 2.2 reverbは空間ではなく記憶として扱う

Headspace ReverbのDECAYとS.RATEは、現実のroom simulationだけを目的にしない。長いtailを持つreverb bufferは、直前の入力を保持する短期記憶として使える。

```text
voice / noise input
  -> spectral selection by IN TILT
  -> memory accumulation in reverb network
  -> interruption by CHOKE
  -> final shaping by OUT TILT
```

ここでは`IN TILT`と`OUT TILT`を同じtone controlへまとめない。

- IN TILT: 何を記憶させるか
- OUT TILT: 記憶をどの音色で聞くか

この差は、後からEQを一つ置くことでは再現できない。input側の帯域制限はnetwork内部の蓄積とfeedbackの偏りを変える。

## 3. Interruption clock

### 3.1 Chokeはgateとは限らない

Chokeを単純なvolume gateとして実装すると、見た目は近くても音楽的結果が変わる。

| choke方式 | choke中 | choke解除後 | 聴感 |
| --- | --- | --- | --- |
| output gate | bufferは進み続ける | 古いtailの後半が戻る | 窓を開閉する |
| buffer gain fade | buffer内容を減衰 | 古いtailはほぼ戻らない | 発音を殺す |
| feedback cut | 新しい循環だけ止める | 残存tailは自然減衰 | sustainを離す |
| buffer clear | 記憶を消去 | 無音から再開始 | resetする |
| input choke | 新規入力だけ止める | 既存tailは残る | exciteを止める |

公式製品ページはdelay/reverb bufferをchokeすると書くが、内部のどこへgain envelopeを置くかまでは公開していない。実機取得前に一方式へ固定しない。

### 3.2 人間の演奏に必要なのはpattern編集ではない

Euclidean rhythmのstep列を画面へ並べると、演奏者はsequencer編集へ引き戻される。BattleFXから抽出したいのはstep programmingではなく、**同じtailへ休符の密度を与えること**である。

演奏時の知覚単位を次へ限定する。

- `sparse`: 長いbloomが残り、ときどき消える
- `breathing`: 規則的だが均等ではない呼吸
- `broken`: 音節または反復が欠ける
- `buzzed`: chokeが発音周期に近づき、音色化する
- `kill`: 次の周期を待たず、その場で消す

内部ではsteps/hits/rotationを使っても、演奏者へ常に数値を要求しない。

### 3.3 Nudgeは「humanize」ではない

Nudgeをrandom humanizeにすると、演奏者の意図を機械へ渡してしまう。BattleFXの説明では、chokeをbeatの前後へずらせる。これは二方向の意味を持つ。

- beatより前: tailが先に引き、次の原音へ場所を空ける
- beatより後: tailが拍をまたぎ、次の原音へ食い込む

Field Looperでは、Nudgeをランダム値ではなく`rush / drag`の演奏判断として保持する。

## 4. Instability clock

### 4.1 Brownian motion

公式BattalionマニュアルはGLITCHを、delay TIMEへ加える滑らかなrandom Brownian motionと説明する。

概念上の最小モデルは次である。

```text
x[n] = clamp(x[n-1] + sigma * random(-1, 1), -limit, limit)
delayTime[n] = baseTime * ratio(x[n])
```

これは実装仮説であり、BattleFXの分布、積分率、境界処理、平滑化係数を示さない。

white-noise modulationと違い、Brownian motionは前の値を記憶する。したがってdelay timeは毎sampleばらばらになるのではなく、ある方向へ漂い、しばらく留まり、また戻る。反復の輪郭が崩れても完全なnoiseへ直行しにくい。

### 4.2 Stereoはwidthノブではない

STEREO offでは左右が同じrandom valueを共有し、onでは独立値を持つ。これは単純なmid-side wideningではない。

```text
off: deltaL(t) = deltaR(t)
on:  deltaL(t) != deltaR(t)
```

onでは左右のecho onsetと微細pitchが別々に漂う。mono compatibilityを含む実機試験が必要である。

## 5. S.RATEが作る時間と音程の結合

### 5.1 観測できた範囲

公式マニュアルは、S.RATEがeffect全体のDSP処理率を変え、値を下げると次が同時に起きると説明する。

- crunch / artifactが増える
- perceived delay timeまたはroom sizeが伸びる
- buffer内の音が低くpitch shiftする

したがってS.RATEは通常のpost-effect downsamplerではない。

### 5.2 実装理解のための仮説式

内部処理率の比を`r`とする。`r = 1`を通常、`r < 1`を低速化と仮定する。bufferの読出しを新しいrateへ追従させず、保持データの再生速度として現れる単純モデルでは、概念上次になる。

```text
perceivedTime ≈ baseTime / r
pitchShiftSemitones ≈ 12 * log2(r)
```

例として`r = 0.5`なら時間は約2倍、pitchは約-12 semitonesとなる。ただしBattleFXのknob mapping、内部resampling、補間、parameter compensationは未取得であり、実製品がこの式へ一致するとは主張しない。

重要なのは数値の一致ではなく、**時間を伸ばす操作と音を低くする操作が同じ物理的比率から生じる可能性**である。

### 5.3 Field Looperへの含意

これを`LO-FI`へまとめると、音が汚れるだけのdecorative effectになる。演奏上は次の変化として扱う。

- slow: tailが長くなり、音程が沈む
- normal: transportまたは設定時間へ戻る
- crush: artifactを前景化する

名称とUIは未固定だが、時間とpitchの連動を解除しない候補を残す。

## 6. 入力素材別の作用仮説

### 6.1 声

| 声の要素 | 入力側の処理 | tail側の結果候補 |
| --- | --- | --- |
| 破裂音・歯擦音 | high寄りIN TILT、短delay | hat、ruff、grain burst |
| 母音 | reverb、低密度choke | bloom、drone、断続する和声残像 |
| 息 | Maximize前のnoise素材 | 有機的なEuclidean pulse |
| 低い有声音 | 極短delay、高feedback | resonator、metallic bass tone |

これは実機結果ではない。テスト素材の設計である。

### 6.2 環境音

環境音はtransientが少ない場合、通常のdelayでは輪郭が出にくい。BattleFX公式ブログはnoisy inputとMaximizeの組合せでorganic ducking patternを作れると説明する。

ここではMaximizeが音を良くするのではない。noise floorと微細変動をchokeが読める持続素材まで持ち上げる。

### 6.3 4-track mix

全mixへ常時処理すると、原音の拍、delay、reverb、chokeが競合して濁る。最初の実験では次の優先順位にする。

1. selected single track
2. two-track temporary pair
3. explicit 4-track bus capture
4. permanent master insertは試さない

## 7. 人間が演奏するための最小文法

### 7.1 操作イベント

常設parameterの羅列ではなく、時間を持つ動詞へ変える。

| event | 行為 | 終了後 |
| --- | --- | --- |
| EXCITE | selected trackをtail networkへ入れる | tailは残る |
| STARVE | inputを止め、既存tailだけを鳴らす | memoryだけ進む |
| BREAK | choke密度を変える | 以後の休符が変わる |
| LEAN | chokeをrush/dragする | 原音との食い込みが変わる |
| KILL | 次の周期を待たずtailを殺す | network状態は方式に依存 |
| CATCH | wet tailを明示的に記録する | RAWは不変 |

### 7.2 一回の演奏

```text
trackを選ぶ
  -> EXCITEを押して声またはloopをtailへ入れる
  -> 離してSTARVEへ移る
  -> tailが残っている間にBREAKを動かす
  -> LEANで次の拍との接触を決める
  -> 残すならCATCH、終えるならKILL
```

録音開始を自動化しない。CATCHは人間が明示する。

### 7.3 マルチタッチ条件

実装時に一つだけ先に固定する必要がある。EXCITEを保持しながらBREAKまたはLEANを触れること。過去試作のように、押しながら別操作ができないUIにしない。

ただし画面配置、縦横、pad形状はSkulptur研究本文を取得するまで固定しない。

## 8. Performance Takeへの記録候補

continuous automationを全sample保存する前に、意味を持つeventを記録する。

```json
{
  "t": 12.420,
  "event": "EXCITE_BEGIN",
  "track": 2,
  "tailBus": "A"
}
```

```json
{
  "t": 13.080,
  "event": "BREAK",
  "density": 0.63,
  "gestureId": 81
}
```

```json
{
  "t": 14.005,
  "event": "KILL",
  "tailBus": "A"
}
```

これはevent schemaの候補であり、統合正本を更新していない。時間単位、parameter sampling、gesture compression、undo単位は未決定である。

## 9. DSP分解候補

BattleFXの複製ではなく、構造検証に必要な最小blockを分ける。

```text
Input Select
  -> Pre Tilt
  -> Excite Gate
  -> Short Delay / Feedback / Tilt
  -> Delay Choke Envelope
  -> Delay-to-Reverb Send
  -> Reverb Network / Input Tilt / Output Tilt
  -> Reverb Choke Envelope
  -> Wet Density / Safety Clip
  -> Wet Capture
```

必要なschedulerはaudio-rate parameter、transport-synced event、free-running eventを混ぜない。

- audio-rate / smoothed: TIME modulation、gain envelope
- transport event: sync choke
- free event: unsynced choke
- user event: EXCITE、KILL、CATCH

## 10. 実装前に棄却できる失敗

### 10.1 「それっぽいグリッチ」だけ鳴る

random mute、bitcrusher、delayを直列に置くだけでは、material/interruption/instabilityの三時計が分かれない。

### 10.2 音源がなくても勝手に演奏する

Euclidean patternを自動生成音源へ変えない。入力は人間の声、録音loop、環境音であり、Chokeはそれらが残したtailへ休符を与える。

### 10.3 操作がparameter編集になる

steps、hits、rotation、feedback、decay、rate、nudgeを全部常設すると、演奏前の設定画面になる。主演奏時はEXCITE / BREAK / LEAN / KILL / CATCHの行為を優先する。

### 10.4 Maximizeがmaster loudnessになる

Maximizeはquiet tailとnoiseを前景化するwet処理候補である。4-track masterを常時大きくする機能へ変えない。

### 10.5 RAWが変わる

tail processing、CATCH、resampleのどれもRAWを上書きしない。

## 11. 次に必要な証拠

### 外部資料で追加取得できるもの

- iOS AUv3の公開parameter一覧
- preset名とparameter snapshot
- standalone/AUv3のrouting差
- release notesとversion履歴

### 実機でしか確定しないもの

- chokeがbuffer memoryを消すか
- choke envelopeのattack/release
- Euclidean knobのmapping
- Nudgeの範囲
- S.RATEと時間/pitchの実測比
- Maximizeのgain/time response
- mono fold-down時のGLITCH STEREO
- iPhone 13 miniでのCPU、thermal、dropout

## 12. Phase 2の現在判断

- BattleFX研究の中心を`rhythmic-tail effect`から、より正確な`three-clock tail instrument`へ更新する。
- ただし製品名、統合正本、Field Looper主演奏面は更新しない。
- 採用候補はshared wet bus一基。4トラック個別複製は候補から外す。
- 演奏単位はparameterではなく、`EXCITE / STARVE / BREAK / LEAN / KILL / CATCH`。
- 実装開始はまだ`no`。実機証拠と他研究本文の取得前に製品コードへ入れない。

