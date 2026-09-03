# 音楽分析方式・並行研究接続

- status: `active`
- research-id: `20260902-parallel-music-analysis`
- 更新日時: 2026-09-02 UTC
- 起点: `main@f5c694e47f9ed115e9c2de6433dbd6976847a2e4`
- 変更範囲: 研究記録のみ
- 採用状態: draft / research-only

## 0. 目的

音楽分析方式を、個別のアーティスト研究や演奏文法研究の後段へ置く汎用ツールではなく、各研究が並行したまま観測・反証・比較できる共通インターフェースとして定義する。

この記録は既存研究を一つの一般理論へ還元しない。各研究の差異と失効履歴を保持したまま、次を接続する。

1. 録音・記号資料の同一性と証拠境界
2. 発音、音価、休符、attack、音色、強度の観測
3. clock、声部、前景、記憶、回帰点の関係
4. 反復で保つものと変えるもの
5. 変形実験、反例、ブラインド比較
6. 演奏可能性への写像

製品採用、UI決定、DSP実装、`integration/`更新はこの研究の範囲外とする。

## 1. 訂正した現在地

- “Billy Jack”は未分析の最初の候補ではない。`research/music-analysis`にはCurtis Mayfield 100曲の30秒プレビュー、20曲監査、MDX分離、合成fixture、blind20監査が保存されている。
- Charlie Hunter、Curtis Mayfield、J Dilla、James Brown、Anderson .Paak、Dub演奏文法、楽理研究にはGit上の研究実体がある。
- Jeff Millsは複数READMEから依存研究として参照されているが、2026-09-02時点の`sound-lab`ブランチ検索では正本ブランチを取得できなかった。別研究の要約をJeff Mills研究本文へ昇格させない。
- 各研究は直列の工程ではなく並行研究である。本記録はそれらの統合結果ではなく、相互検証のための接続層である。

## 2. 取得した正本

| 研究 | ref | 取得ファイル | blob SHA | 現在の役割 |
| --- | --- | --- | --- | --- |
| 研究運用 | `main` | `RESEARCH_WORKFLOW.md` | `9cbf45a4035fb0c4c0e51bfb835730a82a87f0d7` | 並行研究、証拠層、統合境界 |
| 音楽分析方式 | `main` | `research/music-analysis/README.md` | `a351f478d4e9d80c9532ac952748b7306e9efbac` | 音源同一性、分離、BPM、phase/onset、fixture |
| blind20監査 | `main` | `research/music-analysis/blind20-audit-20260902.md` | `5f68b76ea105ada904bec58b3385575164045ced` | 濃縮非三連則のブラインド反例監査 |
| J Dilla | `research/20260902-j-dilla` | `research/20260902-j-dilla/README.md` | `e0e5e1b2d7f329091ddb12b483fee9c6a05f9058` | 複数clock候補、声部間摩擦、変形実験 |
| Charlie Hunter | `research/20260902-charlie-hunter` | `research/20260902-charlie-hunter/README.md` | `080c91224ccbf2fbc224ac8cb40790c6c122797f` | 拘束された対位法、同一身体内の声部関係 |
| Curtis Mayfield | `research/20260831-curtis-mayfield` | `research/20260831-curtis-mayfield/README.md` | `7fe9816c4f0613d8c566cf140fe0d03fcc82e6ce` | BODY / VOICE / HORIZON、総ループ非形成 |
| Dub演奏文法 | `research/20260831-dub-performance-grammar` | `research/20260831-dub-performance-grammar/README.md` | `ed38441b9220eb17ea0e7fee93a5970fdfb7ad88` | CUT / THROW / REVEAL、tail、事件時刻 |
| James Brown | `research/20260831-james-brown` | `research/20260831-james-brown/README.md` | `947ba74bbab1da7e0632929d6f188914076b7c81` | 共通拍内の散開とOneへの収束、不在声部の記憶 |
| Anderson .Paak | `research/20260831-anderson-paak` | `research/20260831-anderson-paak/README.md` | `b3798491a5e88d1680920516b901a9548adb16cb` | 不変骨格、前景交替、「一定」と「同一」の分離 |
| 楽理研究 | `research/20260901-music-theory` | `research/20260901-music-theory/README.md` | `59b775936eb5bad4e8b0f9416cd2f5a6b787b17d` | 多次元イベント、反復変形規則 `μ` |

blob SHAは内容同一性の記録であり、各仮説の真実性やmain統合を証明しない。

## 3. 共通分析インターフェース

### 3.1 Source

測定前に次を固定する。

```text
SOURCE = (
  source_id,
  recording_identity,
  edition_or_master,
  acquisition_route,
  time_scope,
  sha256_if_available,
  legal_or_access_boundary
)
```

30秒プレビュー、フル尺、ライブ映像、別マスター、分離stemを同一証拠として混ぜない。

### 3.2 Event

楽理研究のイベント表現を、音響分析と複数時計へ接続する。

```text
EVENT = (
  source_id,
  absolute_time,
  bar_beat_subdivision,
  clock_candidate,
  offset_from_clock,
  role,
  pitch_relation,
  timbre,
  intensity_envelope,
  duration_or_rest,
  onset_confidence,
  separation_provenance,
  original_mix_recheck,
  repeat_transform
)
```

`clock_candidate`は必須の複数時計を意味しない。James Brownのように共通拍内部の時間形状を扱う場合は同一clockを共有し、J Dillaでは競合候補を残す。

### 3.3 Relation

個別イベントだけでなく、演奏を成立させる関係を保存する。

```text
RELATION = (
  participants,
  shared_or_competing_clock,
  coupling,
  invariant,
  variable,
  foreground_role,
  memory_type,
  transition,
  return_condition,
  confidence,
  counterevidence
)
```

- `invariant`: pulse、重心、音程集合、役割、距離など、反復中に保持するもの
- `variable`: 発音位置、休符、密度、音価、attack、編成、遠近、主導権など
- `memory_type`: 過去イベント、tail、不在声部、長周期、物語圧力
- `return_condition`: Oneへ収束、局所合流、基準層へ回帰、総リセットなし、未確定
- `counterevidence`: 現仮説に合わない小節、曲、変形版、測定失敗

## 4. 並行研究の接続と非同一性

| 研究 | 保持されるもの | 演奏中に変わるもの | 戻り方 | 他研究へ一般化しない点 |
| --- | --- | --- | --- | --- |
| J Dilla | 安定層または参照候補 | 細分、位相、attack、声部間差、長周期 | 曲ごとに未確定 | 「遅いsnare」や固定swingへ縮約しない |
| James Brown | 共通拍、primary / secondary One | 休符、アクセント、timing shape、主導権 | 異なる経路からOneへ収束 | 複数独立周期とは扱わない |
| Anderson .Paak | pulse、重心、反復周期 | ghost、fill、声、前景役割 | 身体が骨格を維持 | 同じ音列の再生を「一定」と呼ばない |
| Charlie Hunter | 同一身体、共有拍感、実行制約 | 低音と上声の音価、ミュート、局所前後差 | 相互拘束内で連続調整 | 完全独立した二演奏者とみなさない |
| Curtis Mayfield | BODYの場、語りと圧力の関係 | VOICE句読、HORIZON緊張、介入密度 | 三層の同時初期化を避ける | 総ループやOneへの一斉収束へ還元しない |
| Dub | 素材と基礎リズムの同一性 | 編成、距離、因果、tail、出現時刻 | 操作事件ごとに状態変更 | 自動エフェクト列やジャンル音色へ縮約しない |

共通項は「ずれ」ではない。**反復中の同一性を保ちながら、関係の一部を現在形で更新すること**である。

## 5. 音楽分析方式が担う位置

音楽分析方式は次の三層を分離する。

1. **観測層**  
   source hash、区間、波形、spectrogram、onset候補、attack、BPM候補、分離由来を保存する。

2. **関係推定層**  
   clock、coupling、foreground、memory、returnを仮説として記述する。数値から自動的に作家性を断定しない。

3. **変形・反証層**  
   量子化、声部別量子化、偏差交換、符号反転、random humanize、短周期化、tail除去、前景固定を比較する。

製品への写像は第四層として別記録に置く。観測値、研究仮説、設計候補、採用判断を同じ状態へ置かない。

## 6. 共通の反証実験

### T1. Clock topology

- 単一clock
- 単一clock内の声部別timing shape
- 複数clock候補
- clockを確定できない状態

の四つを先に比較し、「複雑に聞こえる」ことを複数時計の証拠にしない。

### T2. Relation-preserving transformation

同じ偏差分布でも、声部間の対応を壊した版と保った版を比較する。関係を壊しても知覚が保たれるなら、coupling仮説を弱める。

### T3. Return topology

- primary Oneへ収束
- secondaryな局所合流
- 指定層だけ基準へ戻る
- 全層が同時には戻らない
- tailだけ別時間に残る

を区別する。「ループ末尾へ戻る」を共通回帰モデルにしない。

### T4. Invariant versus replay

pulse、重心、役割を保持しながらイベント列を変えた版と、同じ音声を再生する版を比較する。「一定」と「同一」を聴取試験でも分離する。

### T5. Embodiment and foreground

演奏者が現在操作する層を交替できるか、保持層が崩れないか、指の追加・離脱が音楽的状態変更になるかを実機で検証する。自動化が結果を作った場合は身体的演奏の証拠にしない。

## 7. 直近の並行作業

| 優先 | 作業 | 接続先 | 完了条件 |
| --- | --- | --- | --- |
| A（ケース化済み） | “Billy Jack” blind20結果をEVENT / RELATION形式へ再記述 | music-analysis / Curtis | `cases/billy-jack-v1.md`。EVENT列生成は未完了 |
| A | J Dilla 4曲反例コーパスの同一音源を固定 | J Dilla / music-analysis | edition、hash、区間、入手境界が記録される |
| A | “Spanish Joint”の声部・音価・休符を測定 | Charlie / J Dilla / .Paak | 原mix再確認付きイベント列が得られる |
| B | James BrownのOne収束とDillaのclock競合を同じ指標で比較 | James Brown / J Dilla | 同一指標で差が消えない |
| B | DubのCUT / THROW / tailをabsolute audio timeで記録 | Dub / theory | loop phaseだけでない事件列が得られる |
| B | Curtis三時計の同時非リセットを反証する | Curtis / theory | 総周期候補と反例小節が記録される |
| C | Jeff Mills正本の所在を確定 | Charlie / .Paak / Curtis依存 | branch/path/blob SHAまたは取得不能境界が確定する |

これらは同じ順番で実行する必要はない。各研究ブランチで並行し、接続層には主張単位の差分だけを戻す。

## 7.1 実証ケース

- [ケース01 — Curtis Mayfield “Billy Jack”](cases/billy-jack-v1.md)  
  blind20の実測JSONをSOURCE / EVENT / RELATIONへ再記述。ドラム集約で直接言えることと、BODY / VOICE / HORIZON仮説の未検証部分を分離した。

## 8. 設計候補への境界

研究から共通して現れる設計候補は次の通り。

- 完成音声ではなく、イベント関係または状態を反復する
- 一つの基準を保持しながら別層へ介入できる
- foregroundを交替できる
- 指を離したとき、全体ではなく対象層だけが変化または回帰する
- 無音、休符、tail、不在声部を状態として保持する
- confidenceと人手訂正履歴を残す

ただし、これらは候補である。既存の4トラック、RAW、Skulptur、独立ドラム等の統合判断を変更しない。製品採用には、各研究の反証結果、iPhone実機評価、明示的な統合判断が別途必要である。

## 9. 未解決事項

1. Jeff Mills、Autechre、Aphex Twin各研究の正本refと本文。
2. Charlie Hunterの音源測定。現在の「内部位相差」は未検証仮説。
3. Curtis三時計の小節単位注釈と総周期反証。
4. 分離モデル間でonset順位が変わる区間の処理。
5. attackの違いによる知覚時刻と物理onsetの分離。
6. 複数clock候補を残したまま比較できる評価指標。
7. relation annotationの人手一致率。
8. iPhone上で三点以上の接触を使ったときの遮蔽、誤接触、遅延。
9. 「関係を演奏する」操作がノンミュージシャンに説明なしで伝わるか。

## 10. Git状態境界

このREADMEは次を証明しない。

- 各アーティストの演奏原理が確定したこと
- フル尺音源で全仮説を検証したこと
- 共通分析インターフェースが妥当と実証されたこと
- Field LooperまたはSound Labへ採用されたこと
- 製品コードへ実装されたこと
- mainへ統合されたこと

ブランチ保存は研究の存在と内容を固定するだけであり、PR作成、merge、製品採用を意味しない。


## 11. 2026-09-02追加 — Hunter × Millsから接触因果場へ

### 11.1 取得状態の訂正

第1版の「Jeff Mills正本ブランチを取得できなかった」という記述は、この時点の取得状態として失効した。現在は次の正本を取得した。

| 研究 | ref | blob SHA | この接続で使う差分 |
| --- | --- | --- | --- |
| Charlie Hunter | `research/20260902-charlie-hunter` | `8328d29a5968264075cb38d1549dbdf3ebaf8938` | 指が固定声部ではなくチームとして働き、低音・上声・リズムを一つのポケットへ従属させる |
| Jeff Mills | `research/20260902-jeff-mills` | `2fe28c9091a24cf9fadaee690d7f2b6d29fa3c93` | 素材のentry / exit / phase / recoveryを短い判断窓で更新する |
| Autechre | `research/20260831-autechre` | `c57156415879d6ce6ee49511b9586182b26e55d0` | event列でなくrelationとstate transitionを演奏する |
| J Dilla | `research/20260902-j-dilla` | `fb32ed2b1eb7d6c485e7e3261b29449ea1f48f71` | 一括swingでなく、安定層と競合するclock／声部間摩擦を分離する |
| James Brown | `research/20260831-james-brown` | `947ba74bbab1da7e0632929d6f188914076b7c81` | 声部の散開、主導権移動、primary / secondary Oneへの回帰 |
| Dub演奏文法 | `research/20260831-dub-performance-grammar` | `53ddca03d44a7b8f334ab38d6d4525d63302cd5f` | CUT、THROW、REVEAL、dryとtailの別時計 |
| ノンミュージシャン演奏 | `research/20260831-non-musician-performance` | `e330526ebcb08fb53e7caf394445de25ad10302e` | 指番号でなくnode / edge / cluster / bridgeとして接触数を増やす |
| 楽理研究 | `research/20260901-music-theory` | `3a1085488be642ae22b5dd6d9cf4163d3cf13a28` | eventへ反復変形規則 `μ` を持たせる |

Aphex Twinについては独立した `research/...` ブランチを現在の全研究ブランチ一覧から取得できていない。別README内の名称、短い境界、外部インタビュー参照はあるが、それをAphex Twin研究の正本とは扱わない。

### 11.2 共通化しない差

接続は全員を「関係を演奏する」という一語へ潰さない。

| 研究 | 演奏者が保持する責任 | システムへ渡してよい補助 | 渡さないもの |
| --- | --- | --- | --- |
| Hunter | 同時声部の音価、ミュート、押し引き、共通ポケット | 音域制約、相対音程の可視化 | 完成bass / chord / melody |
| Mills | entry、stay、exit、位相差、事故後の回復 | 一時lock、可視位相、有限tail | 常時完全sync、完成trackの長時間所有 |
| Dilla | clock間の摩擦と再合流 | 複数clock候補、関係保持 | 全声共通swing、random humanize |
| James Brown | 主導権、空白、Oneへの異なる帰路 | 不在声部の記憶、局所return候補 | Oneの自動強調、全声一斉帰還 |
| Dub | dryの存在、過去のthrow、tailの終了 | 安全上限、tail状態表示 | 自動drop、自動dub mix |
| Autechre | 現状態へ介入し、返答へ次の操作で応じる | 履歴と有限の状態依存応答 | 放置して完成曲を作るprocess |

### 11.3 接触因果場

固定した「一本目はbass、二本目はchord、三本目はeffect」を廃止する。接触は指の番号ではなく、現在見えて聞こえる関係へclaimを持つ。

```text
CONTACT_CLAIM {
  contactId
  target: node | edge | empty
  phase: enter | hold | deform | cut | release
  causalEnergy
}

POCKET_STATE {
  clocks[]
  voices[]
  couplings[]
  returnPoints[]
  absentVoiceMemory[]
  liveTail[]
  floor: absent | forming | held | tensioned | broken | rebuilt
}
```

- 空白へ触れる: 薄いvoiceまたはclock候補を一つだけ開始する。完成phraseは開始しない。
- nodeへ触れる: そのvoiceの音価、再発音、音高、attackのいずれかを現在動作で直接変える。
- edgeへ触れる: 二voice間の位相、coupling、return条件を変える。
- nodeを外へ払う: dryをCUTするが、関係記憶または明示されたtailは残せる。
- 消えたnodeへ再接触する: 保存済みloop頭でなく、現在のpocketへREVEALする。
- releaseする: 対象claimへのエネルギー供給を止める。他のnodeを勝手に止めない。

画面はnodeとedgeを表示し、分類を隠れたジェスチャー認識へ任せない。同じ接触が時間とともに `enter -> hold -> deform -> release` へ移れるため、指ごとの固定役割も不要になる。

### 11.4 因果エネルギー — 放置再生を構造的に止める

接触中の操作は各claimへ有限の `causalEnergy` を供給する。発音、再発音、位相移動、tail帰還はenergyを消費する。

```text
energy_next
  = clamp(
      energy_now
      + performed_input
      - event_cost
      - elapsed_decay,
      0,
      safe_max
    )
```

- `performed_input` は現在のtap、移動、保持中の微小運動、複数接触関係の変化からだけ入る。
- release後は新しいenergyを補給しない。
- Dubのtail、Mills型の位相事故、Autechre型の状態応答は残存energyの範囲で続く。
- energyが尽きたvoiceは無期限ループせず、発音を止める。ただし不在声部の関係記憶は無音状態として残せる。
- energyを音量そのものへ直結しない。大音量化による危険と、演奏継続時間を分離する。

これは「手を離した瞬間に全部止める」規則ではない。人間が起こした因果が有限の寿命を持ち、その寿命を再び触って延ばすか、CUT / TAIL CHOKEで終えるかを演奏に残す。

### 11.5 状態遷移

```text
ABSENT
  -> FORMING      最初のevent / clock候補
  -> HELD         二つ以上の関係が可聴に維持
  -> TENSIONED    位相、主導権、密度、clock関係を変形
  -> BROKEN       floorまたは主要voiceを意図的／偶発的に喪失
  -> REBUILT      現在状態から別のreturn pointを成立
  -> HELD
```

`BROKEN` を自動undoしない。Mills型の回復は、残ったfloor、tail、不在声部記憶のどれを新しい基準にするかを次の接触で選ぶ。Hunter型のポケットは、常時完全同期ではなく、声部が違う局所offsetを持ちながら共通の前進感を失わない `HELD / TENSIONED` の往復として扱う。

### 11.6 24秒の具体演奏列

| 時間 | 接触 | 可聴結果 | 接続する研究 |
| --- | --- | --- | --- |
| 0–3秒 | 空白へ一接触し、短く往復する | 低域の単発列。往復ごとに再発音し、放置反復しない | Hunter / James Brown |
| 3–6秒 | 二接触を追加し、低域nodeとのedgeを保つ | 上声二つ。各指の動きが音価と局所offsetを作る | Hunter |
| 6–9秒 | 一つのedgeだけを前へずらす | 低域、上声、細分のclock関係に摩擦が生じる | J Dilla |
| 9–12秒 | 三nodeを寄せ、別々の経路で局所returnへ向かわせる | 一度だけ強い合流。その後は再散開する | James Brown |
| 12–15秒 | 上声nodeを外へ払う | dryは消えるが、短いtailと不在声部記憶が残る | Dub |
| 15–18秒 | 残ったedgeをずらし、一時lockして解放する | floorを保ったまま位相が揺れ、別の配置へ移る | Mills |
| 18–21秒 | 消えたnodeへ現在位置で再接触する | loop頭でなく現在pocketへ上声が戻る | Mills / Dub |
| 21–24秒 | 全接触を離し、tailを一度だけchokeする | 残存energyが尽き、無期限の完成loopを残さず終了 | Autechre / Dub |

この演奏列は成功例の自動保証ではない。指の時刻、移動量、release順が変われば、濁り、空白、位相崩壊、回復失敗も起こる必要がある。

### 11.7 反証条件

1. 接触を止めても、完成度の高い伴奏が長時間自走するなら不採用。
2. node / edgeの表示を見ても、どのclaimを操作しているかノンミュージシャンが判別できないなら接触因果場を修正する。
3. Hunter型のvoice保持とMills型のcut / phase介入が同じgestureとして誤認されるなら、同一surfaceへの統合を棄却する。
4. 因果エネルギーが「忙しく指を動かし続ける義務」にしかならず、音価と空白を作れないなら不採用。
5. 複数clockを導入しても、聴感がrandom humanizeと区別できないならDilla接続を弱める。
6. `BROKEN -> REBUILT` が実演で選択できず、自動補正だけが回復を作るならMills接続とは呼ばない。
7. 4本以上の接触で遮蔽、誤接触、cancelが増え、三本より表現責任が減るなら、認識上限ではなく実用同時接触数を下げる。

### 11.8 採用状態と次の検証

この追加は `research-only / candidate` である。製品採用、UI決定、音響実装、PR作成、main統合は行っていない。

次の検証単位は、音色を作る前のイベントシミュレーションとする。

1. 1、3、5接触の疑似`ContactGestureFrame`列を作る。
2. 同じ入力から`CONTACT_CLAIM`、`POCKET_STATE`、可聴event列、表示node / edgeを生成する。
3. release後に因果エネルギーが有限時間でゼロになることを検査する。
4. 一つのnodeだけCUT / REVEALしても他voiceのpocketが保持されるか調べる。
5. `BROKEN -> REBUILT` が自動undoなしで成立する入力列と、失敗する入力列を両方残す。


## 12. 2026-09-02追加 — 接触因果場 simulation-v0

### 保存物

- `simulation-v0/contact-causal-field.mjs` — 現行 `sound-lab.contact-gesture/v0.1` を受理し、claim、node、edge、audio event、floor状態を生成する決定的シミュレーター。
- `simulation-v0/fixtures.mjs` — 1、3、5接触、release後の減衰、CUT後のREVEALを含む疑似入力列。
- `simulation-v0/contact-causal-field.test.mjs` — Node.js標準test runnerによる構造テスト。
- `simulation-v0/README.md` — 目的、実行方法、schema不足、演奏責任の境界。

### 実行した検証

```text
node --test research/20260902-parallel-music-analysis/simulation-v0/contact-causal-field.test.mjs
tests 6
pass 6
fail 0
```

確認できた範囲:

1. 1、3、5接触は同じ規則で受理され、edge数は `n(n-1)/2` でなく `n-1` に留まる。
2. 同じ入力列は同じstateとaudio event列を返す。
3. release後は新しい演奏eventを自走生成せず、有限減衰後は `decay-stop` だけを発行して無音になる。
4. CUT後の再接触は同じnodeをREVEALし、`broken -> rebuilt` へ移る。
5. pressure取得不能時の架空pressureとtimestamp逆行を拒否する。

### 実装中に判明した不足

現行schemaには `targetKind: node | edge | empty` と `targetId` がない。このためv0ではnodeのhitを座標から一度だけ決定できるが、edgeを直接claimする入力は表現できない。

これはUIの見た目の問題ではなく、Hunter型の声部関係を保持したままMills型に位相をずらす操作を、同じevent列で音響と描画へ渡すための不足である。描画側と音響側が別々にhit testすると、同じ指が別の対象へ作用する破綻が起こる。

ただし、この研究では既存bridge schemaを変更していない。次段階はadapter出力へ一度だけ解決したtargetを付加する候補の比較であり、製品採用ではない。

### 証拠境界

この検証はNode.js上の決定的イベントシミュレーションである。音源、DSP、聴感、描画、iPhone実機の同時接触、遮蔽、cancel、遅延、発熱は未検証。5接触をデータとして受理できたことは、iPhoneで5本指演奏が実用的である証明ではない。


## 13. 2026-09-03追加 — target解決を一回に固定

現行 `ContactGestureFrame` を保持したまま、node / edge / emptyのhit結果を一度だけ解決する `ResolvedContactAdapter` を `simulation-v0/` へ追加した。

採用候補は、入力frameへ未定義fieldを直接追加する方式ではなく、次のenvelopeで包む方式である。

```text
ContactGestureFrame
  -> 一回だけhit test
  -> ResolvedContactEnvelope
       ├─ 同一objectをaudioへ
       └─ 同一objectをvisualへ
```

これにより、edgeを掴んだ指が移動中にnodeを横切っても、接触が終わるまでedge claimを保持する。Hunter型のvoice nodeとMills型のphase edgeが、音響側と描画側で別々の対象へ化ける経路を閉じる。

Node.js標準test runnerで7件を実行し、7件成功・0件失敗を確認した。5接触について確認したのは独立claimの保持であり、実機上の演奏可能性ではない。

未実装:

- edgeのdragをphase / coupling / return条件へ変換する操作文法
- nodeとedgeの表示上のhit幅
- iPhone実機での遮蔽、誤接触、cancel
- haptic、音響、描画
- 既存bridge schemaへの採用判断

したがって現在状態は `adapter prototype verified in Node.js / research-only` であり、製品実装済みではない。

## 14. 2026-09-03追加 — onset候補・拍参照・分離証拠のDeep Research監査

- [Deep Research監査 — onset候補・拍参照・分離証拠の境界](./report-source.md)
- RMS出力器を音楽的onset検出器ではなく、未レビューのenergy-rise候補器としてschema v2へ訂正。
- stereo逆相相殺を防ぎ、人手referenceとの最大一対一照合器を追加。
- 合成fixtureは9件成功。Billy Jack実音源／stem、人手onset、beat/downbeatは未取得のため、B09イベントJSONは未生成。
