# BattleFX研究 Phase 3 — 4トラック共有テイルバス

- research-id: `20260828-battlefx`
- status: `active`
- 更新日: 2026-08-28
- この文書の位置: Phase 2の三時計と演奏文法を、4トラック楽器で破綻しない信号経路と状態遷移へ落とす。
- 実装状態: 未実装
- 実機状態: 未検証

## 1. 今回の問い

4トラックのどの音を、いつ、どれだけBattleFX型テイルへ入れ、そのテイルをどう残し、どう記録するか。

ここで解くのはsend matrixの作り方ではない。演奏中の身体が迷わず次を決められることを目標にする。

1. いま何をテイルへ入れているか。
2. 指を離したあと何が残るか。
3. 別トラックを選んだとき、残響の出自が勝手に変わらないか。
4. CATCHがRAWや既存4トラックを壊さないか。
5. BattleFX型がSkulptur型主演奏面を奪わないか。

## 2. 現在の結論

最小構成は、4トラックに共通する**一基のwet-only tail bus**とする。

- 同時に新規入力できるsourceは一つ。
- 既存tailはsource選択を変えても鳴り続ける。
- `EXCITE`開始時にsourceを固定し、指を離すまで切り替えない。
- `EXCITE`を離すと入力だけが閉じ、tailは`STARVE`状態で残る。
- `CATCH`はwet-only出力だけを明示録音する。
- dry 4-trackは常に直通し、RAWを上書きしない。
- tail bus出力はSkulptur型主演奏面の**前**へ戻す。
- `KILL`は周期、gesture、captureより優先して即時にtailを止める。
- 4トラック別のsend量保存、send matrix、trackごとのBattleFX複製は初期構成へ入れない。

## 3. 信号経路

```text
Track 1 RAW -> track playback/gain/mute --\
Track 2 RAW -> track playback/gain/mute ----> dry 4-track mix ---------\
Track 3 RAW -> track playback/gain/mute ----/                         |
Track 4 RAW -> track playback/gain/mute --/                           |
                                                                     v
selected audible track -> EXCITE envelope -> shared tail network -> wet return
                                                   |                  |
                                                   +-> wet-only CATCH |
                                                                      v
                                                        Skulptur main surface
                                                                      |
                                                                    output
```

### 3.1 sendの取得位置

初期候補は**post track-gain / post track-mute / pre Skulptur**。

理由:

- 小さくしたtrackは小さくtailへ入り、聞こえないmuted trackは勝手にtailへ入らない。
- 演奏者が聞いているsourceと、tailが記憶するsourceが一致する。
- Skulptur処理済み出力を再びBattleFXへ戻すfeedback loopを避ける。
- wet returnもSkulpturの材料になるため、BattleFXが最終masterを奪わない。

pre-fader sendやmuted sourceからのghost sendは表現力があるが、初期構成では信号の所在を見えにくくするため採らない。

### 3.2 wet-only

tail busへdry copyを混ぜない。dryは4-track mix側に既に存在する。

BattleFX実機のMix/Solo経路には未確認点があるため、製品AUv3を検証に使う場合はdry leakageを測る。Field Looper側の構造候補では、bus returnをwet-onlyとして契約する。

### 3.3 CATCHの取得位置

CATCHはtail networkの出力から、dry mixへ戻る前を録る。

含む:

- delay tail
- reverb tail
- chokeによる空白
- BREAK / LEAN / S.RATE相当の演奏結果
- KILL直前までのwet出力

含まない:

- 元trackのdry
- Skulptur型の後段処理
- master gain
- 他の3 track
- 録音済みCATCHの自動再入力

これによりCATCHは「演奏した残響」だけを派生素材として残す。

## 4. source選択の契約

### 4.1 armed source

通常時のtrack選択を`armed source`と呼ぶ。次にEXCITEしたときだけ、このtrackがtail inputになる。

trackを選んだだけでは送信を開始しない。

### 4.2 latched source

EXCITEを押した瞬間、armed sourceを`latched source`へ固定する。

```text
armed = Track 2
EXCITE_BEGIN
  -> latched = Track 2
  -> Track 2だけを送る
```

EXCITE保持中に画面上の選択がTrack 3へ変わっても、そのgestureはTrack 2のまま続ける。Track 3は次回EXCITEから有効になる。

これは意図しないsource jumpと、delay/reverb memoryへ別素材が突然混入する事故を防ぐ。

### 4.3 source handoff

最初の実装候補では、EXCITE中のsource handoffを許可しない。

二つのtrackを混ぜたい場合は次の順で人間が行う。

```text
Track 2を選ぶ
-> EXCITE
-> release / STARVE
-> Track 3を選ぶ
-> EXCITE
```

一基のmemoryへ異なる時点のsourceが積層される。これは自動crossfadeではなく、演奏者が投入順を決める。

### 4.4 複数source同時送信

Phase 2に残したtwo-track pairは、初期候補から外すのではなく**後段試験へ延期**する。

採用条件:

- 一つの指で意図せず二つをarmedにしない。
- どちらがlatchedされているか見失わない。
- 4×send matrixを要求しない。
- iPhone 13 miniでEXCITE、BREAK、LEANを同時に触れる面積を奪わない。

## 5. send量

### 5.1 EXCITEはon/offだけではない

EXCITEは二つの情報を持つ。

- contact: 入力を開く／閉じる
- amount: tailへ入れる量

iPhoneには一般的な圧力入力を前提にしない。候補gestureは、押下位置または保持中の短い移動からamountを取る。ただしUI配置はこの文書で固定しない。

### 5.2 amountの挙動

- EXCITE_BEGIN時、0から短いfadeで現在amountへ上げる。
- 保持中のamount変化はzipper noiseを避けて平滑化する。
- release時は入力gateだけを短く閉じる。
- releaseでfeedback、reverb memory、wet outputを消さない。
- amount 0は完全mute。
- 数値曲線とfade時間は実装試験で決める。

線形gainは低い領域の操作を狭くしやすい。知覚上の操作幅を取るためdB系curveを候補にするが、式はまだ固定しない。

### 5.3 remembered amount

EXCITE量をtrackごとに記憶させない。最初はtail bus一基に一つのlast amountだけを持つ。

trackごとのsend level記憶は、小型send matrixを隠して作ることになる。切替時に予想外の大音量差も生む。

## 6. tailの状態機械

source input、tail memory、captureを一つの状態名へ潰さない。三軸で管理する。

### 6.1 input axis

| state | 意味 |
| --- | --- |
| CLOSED | 新しいsourceは入らない |
| OPEN | latched sourceがtailへ入る |
| FADING | click防止の遷移中 |

### 6.2 memory axis

| state | 意味 |
| --- | --- |
| EMPTY | 有効なtailがない |
| ACTIVE | 入力またはfeedbackでtailが十分に鳴っている |
| STARVING | 新規入力なしで既存tailだけが減衰している |
| KILLING | 緊急fadeまたはclear中 |

### 6.3 capture axis

| state | 意味 |
| --- | --- |
| OFF | wetを記録しない |
| RECORDING | wet-onlyを記録する |
| FINALIZING | 明示終了後の派生take確定中 |

### 6.4 基本遷移

```text
EXCITE_BEGIN:
  latch armed source
  input CLOSED -> FADING -> OPEN
  memory EMPTY/STARVING -> ACTIVE

EXCITE_END:
  input OPEN -> FADING -> CLOSED
  memory ACTIVE -> STARVING

CATCH_BEGIN:
  capture OFF -> RECORDING

CATCH_END:
  capture RECORDING -> FINALIZING -> OFF

KILL:
  input -> CLOSED
  memory -> KILLING -> EMPTY
  captureは停止せず、killによる終端まで記録可能
```

KILLでCATCHまで勝手に終了させない。無音へ落ちる瞬間も演奏結果だからである。CATCH終了は人間が別に決める。

## 7. BREAKを一ノブへ潰さない

Phase 2では演奏語をBREAK一つにまとめたが、BattleFX固有性はdelayとreverbのchokeが独立している点にもある。

内部の二時計を常に同じ値へ縛ると、次の差を失う。

- echoだけを細かく刻み、roomを長く残す
- roomだけを断ち、echoを乾いた骨格として残す
- 二つを異なるnudgeで噛み合わせる
- 一方をbuzzedまで上げ、他方をsparseに保つ

したがって契約上は次を分離する。

- `BREAK_ECHO`: delay interruption clock
- `BREAK_ROOM`: reverb interruption clock

これは二つのstep editorを置くという意味ではない。どちらも演奏者が知覚できる`sparse / breathing / broken / buzzed`の密度として扱い、内部のsteps/hits/rotationを常設表示しない。

UIで二つをどう配置するかは未固定。ただし以下は必須とする。

- EXCITE保持中にどちらも触れる。
- BREAK_ECHOとBREAK_ROOMを同時に触れられる。
- 片方を動かしても他方が自動追従しない。
- KILLは二つより大きな優先順位を持つ。

## 8. LEAN

LEANはchoke onsetを拍より前後へ置く演奏である。random humanizeへ変えない。

- negative側: tailを拍の前で引かせる
- center: choke clock本来の位置
- positive側: tailを次の拍へ食い込ませる

delayとreverbのoffsetを完全独立にすると操作が増える。一方、常に同値にすると二時計の噛み合わせを失う。

初期候補:

- LEANは一つの両方向gesture。
- BREAK_ECHOとBREAK_ROOMの**現在選択側**だけへ作用する。
- 両方同時選択時は両方へ同じgesture deltaを加える。
- 選択を離してもoffset値は残る。
- resetはcenterへ明示的に戻す。

「現在選択側」が視覚的に曖昧なら、この案は棄却する。自動判定で救済しない。

## 9. KILLと安全

KILLは音楽イベントであると同時に安全経路でもある。

最低条件:

- transport syncを待たない。
- Euclidean cycle終端を待たない。
- source選択を問わない。
- EXCITE保持中でも入力を閉じる。
- feedback上限、wet出力上限、safety clipより手前でtailの励起を止める。
- audio thread上でallocationやfile I/Oを起こさない。
- UI gestureを失ってもaudio側が有限時間で閉じる。
- app interruption、route change、background移行ではsafe fadeを行う。

KILLの内部方式は実機BattleFXのchoke方式と分ける。製品固有のchokeがoutput gateに近くても、Field Looperの緊急KILLには再発しない停止が必要である。

## 10. CATCHは第5トラックではない

CATCH結果を常設第5トラックへ置くと、4トラック楽器という制約が崩れる。

候補となる保存単位:

- Performance Take内のwet stem
- 明示的な派生clip
- 次回録音時に人間が4トラックのどれかへ配置するresample候補

自動配置しない。CATCH完了直後に元trackを置換しない。再生開始もしない。

最低metadata候補:

```json
{
  "kind": "rhythmic-tail-capture",
  "sourceTrackSequence": [2, 3],
  "wetOnly": true,
  "startedBy": "CATCH_BEGIN",
  "endedBy": "CATCH_END",
  "rawModified": false
}
```

これは保存schemaの確定ではない。必要な意味境界だけを示す。

## 11. Performance Take event候補

```text
TAIL_ARM(track)
EXCITE_BEGIN(track, amount, gestureId)
EXCITE_AMOUNT(amount, gestureId)
EXCITE_END(gestureId)
BREAK_ECHO(stateOrDensity, gestureId)
BREAK_ROOM(stateOrDensity, gestureId)
LEAN(target, offset, gestureId)
TAIL_KILL(reason=user)
CATCH_BEGIN(captureId)
CATCH_END(captureId)
```

記録しない候補:

- every-sampleのraw finger座標
- 内部Euclidean step列の全再生成履歴
- meter表示値
- UI animation state

再演時に必要な意味イベントと、音声としてCATCH済みの結果を混同しない。CATCH stemが正本なら、全DSP parameter再現を必須にしない。

## 12. 競合する操作の優先順位

| 同時操作 | 結果 |
| --- | --- |
| EXCITE + track selection change | 現gestureのlatched sourceを維持。次回だけ新track |
| EXCITE + BREAK | 両方動く |
| EXCITE + LEAN | 両方動く |
| BREAK_ECHO + BREAK_ROOM | 独立して両方動く |
| CATCH + EXCITE | wet録音しながら新しいsourceを投入 |
| CATCH + STARVE | 既存tailの減衰を録音 |
| CATCH + KILL | kill終端を録音。captureは継続 |
| EXCITE + KILL | KILL優先。source gateを閉じる |
| route change + any gesture | safe fade。未確定gestureを再開しない |

## 13. 失敗として棄却する挙動

### F1: 選択しただけで送られる

track selectionはarmingであり、録音・send開始ではない。

### F2: 指を離すとtailも消える

EXCITE releaseはSTARVEへの移行であり、KILLではない。

### F3: trackを替えると古いtailのsourceまで変わる

既にbufferへ入った音の出自は変更できない。新sourceは次のEXCITEから加わる。

### F4: CATCHにdry mixが混ざる

派生素材としての意味を失うため失敗。

### F5: CATCHが自動で再入力されfeedbackする

明示操作なしの再帰経路は失敗。

### F6: BREAKが一つのCHAOS量になる

delay/reverb chokeの独立性と、Brownian instabilityとの差を失うため失敗。

### F7: tail busがSkulpturの後段masterになる

プロジェクト全体の主演奏面を奪うため失敗。

### F8: 4 track分の小ノブが常設される

send matrix編集へ戻るため失敗。

## 14. 人間向け受入試験

### H1: 一つのsourceを送る

1. 異なる音の4 trackを再生する。
2. Track 2を選ぶ。
3. EXCITEを押す。
4. 離す。

合格:

- Track 2だけがtailへ入る。
- dry 4-trackは途切れない。
- release後もtailが残る。
- RAWは変わらない。

### H2: sourceを替える

1. Track 2のtailをSTARVEさせる。
2. Track 3を選ぶ。
3. EXCITEする。

合格:

- 既存Track 2 tailは突然Track 3へ置換されない。
- Track 3は新しい投入として同じmemoryへ加わる。
- 選択だけではTrack 3が入らない。

### H3: gesture中に選択を替える

1. Track 2でEXCITEを保持する。
2. 保持中にTrack 4を選ぶ。
3. EXCITEを離す。
4. 再びEXCITEする。

合格:

- 最初のgestureはTrack 2のまま。
- 二回目だけTrack 4になる。

### H4: 二つの中断時計

1. EXCITEを保持する。
2. BREAK_ECHOだけをbuzzedへ動かす。
3. BREAK_ROOMはsparseに保つ。
4. 役割を逆転する。

合格:

- echoの刻みとroomの残り方を耳で区別できる。
- 片側操作が他方を勝手に動かさない。
- マルチタッチが途切れない。

### H5: CATCH

1. STARVE中にCATCHを開始する。
2. BREAKとLEANを演奏する。
3. KILLする。
4. 無音後にCATCHを終了する。

合格:

- wet-only stemにtail、空白、kill終端が入る。
- dry trackは混ざらない。
- 既存4 trackとRAWは変わらない。
- capture終了後に自動再生・自動配置しない。

### H6: 安全停止

1. 短delay、高feedback、低S.RATE相当でtailを励起する。
2. EXCITE保持中にKILLする。
3. audio routeを変更する。

合格:

- KILLが周期を待たない。
- 音量が再上昇しない。
- route復帰後に古いgestureが勝手に再開しない。

## 15. 実装前に必要な次の証拠

- BattleFX iOS実機でwet-only経路を作れるか。
- Choke解除後に古いtailが戻るか。
- Delay/Reverb Chokeを独立automationできるか。
- AUv3 parameter gestureをマルチタッチ中に安定送信できるか。
- host tempo変更時にNudgeがどう再計算されるか。
- iPhone 13 miniで一基のshared busが安全に動くか。
- Skulptur型の実際の信号入口と、wet returnを前段へ置けるか。
- Performance Take現行schemaがCATCH stemをどう参照するか。

最後の二点は他研究本文の現行Git正本を取得してから決める。この文書だけで統合仕様を更新しない。

## 16. Phase 3の現在判断

- 一基のshared wet busを維持する。
- sourceはEXCITE開始時にlatchedし、gesture中は切り替えない。
- releaseはSTARVEでありKILLではない。
- wet returnはpre Skulptur。
- CATCHはwet-onlyで、RAWと4 trackを変更しない。
- BREAK_ECHOとBREAK_ROOMは契約上独立させる。
- KILLは全周期とgestureより優先する。
- 4-track send matrix、個別instance、第5トラック常設は採らない。
- 研究は進めるが、実装開始はまだ`no`。

