# 統合状況

最終観測: 2026-08-29 01:12 UTC

観測対象:

- `daken123-gif/sound-lab` — `main` `3d1a47ccffc884f437574dfe6a0e0ebb7fc74439`、49ブランチ、全44 PR、open PR 12件
- `daken123-gif/sympathia` — 音楽研究のDraft PRとnon-Canon branch。採用先ではなく、研究本文と検証状態を確認する補助リポジトリ

## 現在位置

| 領域 | Gitで観測した証拠 | 統合状態 | 未完了 |
|---|---|---|---|
| 4トラック録音 | `sound-lab/main` 実装、Koala・Teenage Engineering研究、PR #15 | `adopted` / `implemented-unverified` | iPhone実機の録音・再生・実波形・位置表示 |
| iPhone入力段 | `sound-lab/main`、`20260828-iphone-mic-preamp` | `integrating` | 内蔵、有線、Bluetooth別の実機測定 |
| Skulptur型主演奏面 | 役割は`integration/DIRECTION.md`と`sympathia` PR #410。専用候補は`sound-lab` Draft PR #44、37ファイルの研究実装、Node 77/77、4次／8次比較WAV | 役割 `adopted` / 実体 `candidate` / `implemented-unverified` | 製品コード未統合。ブラウザ音響、Mobile Safari、iPhone、聴感、負荷、Feedback音量安全性、4次／8次とmappingの採否 |
| 接触入力bridge | `sound-lab` merged PR #36 / #37 / #40 / #43。frame schema、runtime gate、Pointer adapter、ブラウザ診断面 | `candidate` / `implemented-unverified` | Chrome実行はURL安全制約でblocked。Mobile Safari、iPhone、実音未検証 |
| Contact Performance Take | PR #44。同じ受理frame列から音響・描画・一回記録／再生、停止時cancel | `candidate` / `implemented-unverified` | 複数Take、命名、永続保存、製品UI、ブラウザ／iPhone時間精度 |
| KAOSS | 古い研究と旧実装。現在の中心判断とPR #410 v0.2契約でMaster / XY / follow / layerを退役 | `superseded` | 主演奏層として再統合しない |
| Live Canvas UI | `sound-lab/main` `169d15d`、QA記録 `3e71909` | `active-local` / `render-unverified` | static/source確認のみ。ブラウザ描画、操作、iPhone QAはblocked |
| 旧Field Looper UI | KAOSS中心の円形UIと強制横画面 | `rejected`（設計再利用） | Live Canvasとは分離し、復活させない |
| Loopy Wave | `sympathia` PR #412。4-track静的実装、source 9/9・runtime integrity 28 files・Vite build報告 | `experimental` / `quarantine` | ユーザー試行は「演奏できません」。iPhone／ブラウザ音声runtime未実行 |
| 旧Performance Take核 | `sound-lab` Draft PR #15。明示開始、イベント核、29テスト成功の報告 | `implemented-unverified` | KAOSS依存イベントの除去、PR #44 Contact Takeとの統合判断 |
| Koala Sampler | `sound-lab` open PR #12 | `researching` | 複雑度上限以外の採否 |
| THE PIPE | `sound-lab` open PR #16 | `researching` | 人声、実機、入力経路 |
| BODY resonator | `sound-lab` open PR #18、独立DSP、26テスト成功の報告 | `candidate` / `implemented-unverified` | 人声、iPhone、Safari AudioWorklet、4トラック統合 |
| Things Motor | `sound-lab` branch `research/20260828-things-motor`、8係数テスト | `candidate` | 実音、相関別カーブ、iPhone、UI。PR未確認 |
| Chroma Console | `sound-lab` Draft PR #19 | `candidate` | 実機比較、実楽器、リアルタイム負荷、統合判断 |
| Dedalus | `sound-lab` PR #26の研究をPR #27で統合文書へ接続 | `candidate` / `research-only` | 共有send/return、二読取ヘッド、実音、iPhone負荷、UI。第五トラックにはしない |
| BattleFX | `sound-lab` PR #23の研究をPR #27で統合文書へ接続 | `candidate` / `research-only` | selected-track send、choke、nudge、S.RATE結合、iPhone負荷 |
| Abbey Road入力 | `sound-lab` PR #29 merged。REDD/TG入力DSP試作、Node 7/7報告 | 入力原則 `adopted` / DSP `implemented-unverified` | CLEAN以外のUI・HTML・録音経路は未接続。実測・実音・実機比較なし |
| J37世代バウンス | `sound-lab` Draft PR #34。4トラック接続候補、Node 25/25報告 | `candidate` / `implemented-unverified` | 録音保護はコード報告。ブラウザ、iPhone、実音、聴感未検証 |
| 独立DRUMS | 分離方針と`sound-lab` open PR #38 | 役割 `adopted` / 接続 `implemented-unverified` | Live Canvas実音、同期、iPhone負荷、Skulptur迂回のruntime確認 |
| Sound Lab Skill / Plugin | merged PR #31 / #33 / #35 / #39 / #42。repo Skill、plugin bundle、private marketplace manifestをGitで読戻し、Skill同一blobとvalidator成功を確認 | 配布物 `validated` / 自動発火 `unverified` | ChatGPTアカウントへのインストール、別チャットでの自動発火、Marketplace UI登録 |
| Max/MSP / RNBO | `sympathia` Draft PR #410。LooperCore、host/control契約、Node 27/27報告 | `candidate` / `implemented-unverified` | RNBO runtime、Max compile、実音 |
| AUM | `sympathia` Draft PR #414。AUv3 Host Input / Main / Aux契約とportable reference tests | `candidate` / `source-unverified` | Swift compile、AUM、iPhone runtime |
| Microcosm | `sympathia` Draft PR #425。source-aware memory設計 | `candidate` / `research-only` | 実装、runtime、実機比較 |
| 1176LN Blackface | `sympathia` Draft PR #426。線形reference core、7 tests報告 | `candidate` / `implemented-unverified` | 非線形、実機校正、resampling、iPhone |
| Transit 2 | `sympathia` Draft PR #439。Motion EngineとAUv3参照役割を分離 | `candidate` / `research-only` | 実装、端末検証 |
| Combustor | `sympathia` branch `research/combustor-resonator-20260828`。DSP、tests、比較WAV、metrics | `candidate` / `audition-fixtures` | PR、製品同等性、統合・端末検証 |
| Loop Station | `sympathia` Draft PR #432。foundation only / HOLD | `not-adopted` / `research-only` | 独立appは未採用。実装・runtimeなし |

## sound-lab open PR

- #12 Koala Sampler研究
- #15 Field Looper録音・実波形・共通テープ・旧Performance Take（Draft）
- #16 THE PIPE中心研究
- #18 THE PIPE由来BODY独立DSP
- #19 Chroma Console研究と非可換性・固有DRIFT実験（Draft）
- #23 BattleFX rhythmic-tail研究（Draft）
- #24 J37 reduction mix・世代管理・varispeed研究
- #26 Dedalus共有時間メモリ研究（Draft）
- #28 UI state ownership研究（Draft）
- #34 J37世代バウンスの4トラック接続（Draft）
- #38 Live Canvas本体への独立DRUMS接続
- #44 Skulptur接触演奏とContact Performance Take（Draft）

## Skulptur PR #44の候補と境界

候補として実装済み:

- `ContactGestureFrame`の`x`→10帯域、`1-y`→Cut / Neutral / Feedback
- 1 LP + 8 BP + 1 HP、4次／8次候補、Dry bypass、smoothing、AudioWorklet wrapper
- Elastic、Throw、Flow、明示REC、マルチタッチ
- 4ループ合成後の共通スペクトル面と独立DRUM bypass
- 同じ受理frame列を描画、音響、Contact Performance Takeへ渡す
- 一つの`TAKE`ボタンによる記録、停止、一回再生、中断
- pointer cancel回復、画面非表示時のcancel、AudioContextの明示`RESUME`
- ローカルファイル試奏、4秒整形、同期クロスフェード

Gitで読んだ検証記録:

- `node --check`成功、`node --test` 77 pass / 0 fail
- 4次／8次の48 kHz stereo比較WAV生成
- HTTP 10資産が200
- ただしクラウドブラウザからローカルURLへの接続が遮断され、ブラウザ自動操作は未実行

固定していない:

- `pressure` / `contactArea`の音響割当
- 4次／8次の採用、周波数、`wetTrim`、oversampling
- 4トラック個別処理へ進む場合のownership
- 製品画面、複数Take、永続保存
- ブラウザ音響、Mobile Safari、iPhone、聴感、負荷、発熱、Feedback音量安全性
- 製品採用判断

## sympathiaで確認した補助研究

| PR / branch | 状態 | 読み取った限界 |
|---|---|---|
| PR #410 Max/MSP / RNBO | Draft / open | SculptorCore位置はあるがDSP契約は`NOT_FIXED`。runtime未検証 |
| PR #412 Loopy Wave | open / quarantine | 静的検査・build報告のみ。ユーザー試行失敗、音声runtime未実行 |
| PR #414 AUM | open | source契約まで。Swift・AUM・iPhone未検証 |
| PR #425 Microcosm | open | 研究のみ。実装未着手 |
| PR #426 1176LN Blackface | open | 線形reference coreまで |
| PR #432 Loop Station | open / HOLD | foundationsのみ。独立appは未採用 |
| PR #439 Transit 2 | open | 研究のみ。実装未着手 |
| `research/combustor-resonator-20260828` | branch only | `v0.2-audition-fixtures`。PR・製品同等性なし |

これらは`Draft`またはnon-Canon研究であり、`sound-lab/main`統合、iPhone実機検証、聴感採用の証拠ではない。

## 被覆欠落と未解決

専用研究本文または十分な実装契約をまだ確認できていないもの:

- Elektron固有研究と独立ドラムの最終同期仕様
- OTO BIM / BAM / BOUM
- Strymon固有研究本文
- Home Bake Instruments DRUMSを独立対象にする場合の専用研究

SkulpturはPR #44で専用研究と候補実装を確認したため、被覆欠落ではない。ただし最終DSP、mapping、製品統合、端末検証は未解決である。Microcosm、Max/MSP / RNBO、1176LN Blackface、AUM、Transit 2、Combustorも、`sympathia`のDraftまたはnon-Canon branchで本文を確認したため、欠落ではなく候補研究として扱う。

## 監査境界

島・会話の横断検索結果はlocatorとしてのみ扱い、返却された要約や抜粋を方向判断の証拠には使っていない。今回の訂正は、両Gitリポジトリから直接読み戻した文書、branch、PR状態、差分、テスト報告に基づく。テスト報告はruntime成功へ読み替えない。PR #44はDraft / openであり、この統合文書更新はPR #44のmergeまたは製品採用を意味しない。

## 次の統合順

1. PR #44を実ブラウザ、Mobile Safari、iPhone実機で動かし、入力順序、同一frame追跡、AudioWorklet負荷、Feedback音量安全性、Take時間精度を検証する。
2. 実機証拠を基に4次／8次、`x / y` mapping、周波数、`pressure / contactArea`の不使用継続または割当を判断する。
3. その後にだけ、PR #44の製品コード統合、Live Canvas接続、4トラック共通処理／個別処理、PR #15旧Takeとの関係を決める。
4. iPhone入力、明示録音、4トラック再生、実波形、位置表示を同じ端末試験で確認する。
5. Abbey入力、J37、独立DRUMSを一系統ずつ接続し、CLEAN比較、録音保護、同期を実音で検証する。
6. Dedalus、BattleFX、Microcosm、1176LN、Transit 2、Combustor、AUMを一件ずつ統合判定し、Draftを一括採用しない。
7. Elektron、OTO、Strymonの専用研究をGitで読める状態にしてから信号順を決める。
