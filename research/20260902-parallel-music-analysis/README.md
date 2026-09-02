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
| Curtis Mayfield | `research/20260831-curtis-mayfield` | `research/20260831-curtis-mayfield/README.md` | `916ee140477db082415df0b77aad4f7bcbcf2c38` | BODY / VOICE / HORIZON、総ループ非形成 |
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
| A | “Billy Jack” blind20結果をEVENT / RELATION形式へ再記述 | music-analysis / Curtis | 観測、推論、反例が分離される |
| A | J Dilla 4曲反例コーパスの同一音源を固定 | J Dilla / music-analysis | edition、hash、区間、入手境界が記録される |
| A | “Spanish Joint”の声部・音価・休符を測定 | Charlie / J Dilla / .Paak | 原mix再確認付きイベント列が得られる |
| B | James BrownのOne収束とDillaのclock競合を同じ指標で比較 | James Brown / J Dilla | 同一指標で差が消えない |
| B | DubのCUT / THROW / tailをabsolute audio timeで記録 | Dub / theory | loop phaseだけでない事件列が得られる |
| B | Curtis三時計の同時非リセットを反証する | Curtis / theory | 総周期候補と反例小節が記録される |
| C | Jeff Mills正本の所在を確定 | Charlie / .Paak / Curtis依存 | branch/path/blob SHAまたは取得不能境界が確定する |

これらは同じ順番で実行する必要はない。各研究ブランチで並行し、接続層には主張単位の差分だけを戻す。

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
