# 統合状況

最終観測: 2026-08-28 08:43 UTC

観測対象:

- `daken123-gif/sound-lab` — `main` `3e71909ad27004fc99ebec8d693396656f53d247`、33ブランチ、全29 PR、open PR 9件
- `daken123-gif/sympathia` — 音楽研究のDraft PRとnon-Canon branch。採用先ではなく、研究本文と検証状態を確認する補助リポジトリ

## 現在位置

| 領域 | Gitで観測した証拠 | 統合状態 | 未完了 |
|---|---|---|---|
| 4トラック録音 | `sound-lab/main` 実装、Koala・Teenage Engineering研究、PR #15 | `adopted` / `implemented-unverified` | iPhone実機の録音・再生・実波形・位置表示 |
| iPhone入力段 | `sound-lab/main`、`20260828-iphone-mic-preamp` | `integrating` | 内蔵、有線、Bluetooth別の実機測定 |
| Skulptur型主演奏面 | `sympathia` PR #410のSculptorCore配置・control契約 | `adopted-role` / `coverage-gap` | 専用Skulptur本文、具体DSP、パラメータ、タッチ割当。Draft契約ではDSP未固定 |
| KAOSS | 古い研究と旧実装。現在の中心判断とPR #410 v0.2契約でMaster / XY / follow / layerを退役 | `superseded` | 主演奏層として再統合しない |
| Live Canvas UI | `sound-lab/main` `169d15d`、QA記録 `3e71909` | `active-local` / `render-unverified` | static/source確認のみ。ブラウザ描画、操作、iPhone QAはblocked |
| 旧Field Looper UI | KAOSS中心の円形UIと強制横画面 | `rejected`（設計再利用） | Live Canvasとは分離し、復活させない |
| Loopy Wave | `sympathia` PR #412。4-track静的実装、source 9/9・runtime integrity 28 files・Vite build報告 | `experimental` / `quarantine` | ユーザー試行は「演奏できません」。iPhone／ブラウザ音声runtime未実行 |
| Performance Take | `sound-lab` Draft PR #15。明示開始、イベント核、29テスト成功の報告 | `implemented-unverified` | KAOSS依存イベントの除去、iPhone実機、ブラウザ音声 |
| Koala Sampler | `sound-lab` open PR #12 | `researching` | 複雑度上限以外の採否 |
| THE PIPE | `sound-lab` open PR #16 | `researching` | 人声、実機、入力経路 |
| BODY resonator | `sound-lab` open PR #18、独立DSP、26テスト成功の報告 | `candidate` / `implemented-unverified` | 人声、iPhone、Safari AudioWorklet、4トラック統合 |
| Things Motor | `sound-lab` branch `research/20260828-things-motor`、8係数テスト | `candidate` | 実音、相関別カーブ、iPhone、UI。PR未確認 |
| Chroma Console | `sound-lab` Draft PR #19 | `candidate` | 実機比較、実楽器、リアルタイム負荷、統合判断 |
| Dedalus | `sound-lab` PR #26の研究をPR #27で統合文書へ接続 | `candidate` / `research-only` | 共有send/return、二読取ヘッド、実音、iPhone負荷、UI。第五トラックにはしない |
| BattleFX | `sound-lab` PR #23の研究をPR #27で統合文書へ接続 | `candidate` / `research-only` | selected-track send、choke、nudge、S.RATE結合、iPhone負荷 |
| Abbey Road入力 | `sound-lab` PR #29 merged。REDD/TG入力DSP試作、Node 7/7報告 | 入力原則 `adopted` / DSP `implemented-unverified` | CLEAN以外のUI・HTML・録音経路は未接続。実測・実音・実機比較なし |
| Max/MSP / RNBO | `sympathia` Draft PR #410。LooperCore、host/control契約、Node 27/27報告 | `candidate` / `implemented-unverified` | RNBO runtime、Max compile、実音 |
| AUM | `sympathia` Draft PR #414。AUv3 Host Input / Main / Aux契約とportable reference tests | `candidate` / `source-unverified` | Swift compile、AUM、iPhone runtime |
| Microcosm | `sympathia` Draft PR #425。source-aware memory設計 | `candidate` / `research-only` | 実装、runtime、実機比較 |
| 1176LN Blackface | `sympathia` Draft PR #426。線形reference core、7 tests報告 | `candidate` / `implemented-unverified` | 非線形、実機校正、resampling、iPhone |
| Transit 2 | `sympathia` Draft PR #439。Motion EngineとAUv3参照役割を分離 | `candidate` / `research-only` | 実装、端末検証 |
| Combustor | `sympathia` branch `research/combustor-resonator-20260828`。DSP、tests、比較WAV、metrics | `candidate` / `audition-fixtures` | PR、製品同等性、統合・端末検証 |
| Loop Station | `sympathia` Draft PR #432。foundation only / HOLD | `not-adopted` / `research-only` | 独立appは未採用。実装・runtimeなし |
| 独立ドラム | 統合判断のみ | `adopted`（分離） / `coverage-gap` | Elektron等の研究本文と接続仕様 |

## sound-lab open PR

- #12 Koala Sampler研究
- #15 Field Looper録音・実波形・共通テープ・Performance Take（Draft）
- #16 THE PIPE中心研究
- #18 THE PIPE由来BODY独立DSP
- #19 Chroma Console研究と非可換性・固有DRIFT実験（Draft）
- #23 BattleFX rhythmic-tail研究（Draft）
- #24 J37 reduction mix・世代管理・varispeed研究
- #26 Dedalus共有時間メモリ研究（Draft）
- #28 Live Canvas関連のopen PR

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

## 被覆欠落

現時点で専用研究本文または十分な実装契約を確認できていないもの:

- Skulptur固有の製品研究、具体DSP、パラメータ、タッチ割当
- Elektron / 独立ドラム
- OTO BIM / BAM / BOUM
- Strymon固有研究本文
- Home Bake Instruments DRUMSを独立対象にする場合の専用研究

Microcosm、Max/MSP / RNBO、1176LN Blackface、AUM、Transit 2、Combustorは、`sound-lab`には無かったが`daken123-gif/sympathia`のDraftまたはnon-Canon branchで本文を確認したため、被覆欠落から候補研究へ訂正した。

## 監査境界

島・会話の横断検索結果はlocatorとしてのみ扱い、返却された要約や抜粋を方向判断の証拠には使っていない。今回の訂正は、両Gitリポジトリから直接読み戻した文書、branch、PR状態、差分、テスト報告に基づく。テスト報告はruntime成功へ読み替えない。

## 次の統合順

1. Skulptur専用研究本文を作り、SculptorCoreの具体DSP、パラメータ、タッチ割当を確定する。
2. iPhone実機で入力、明示録音、4トラック再生、実波形、位置表示を検証する。
3. `sound-lab` Live Canvas、`sympathia` Loopy Wave、Max/RNBO契約を照合し、静的検査と実音runtimeを分離したまま録音核を一つに絞る。
4. Abbey入力試作を実際のUI・録音経路へ一系統ずつ接続し、CLEAN比較と音量一致で検証する。
5. Dedalus、BattleFX、Microcosm、1176LN、Transit 2、Combustor、AUMを一件ずつ統合判定し、Draftを一括採用しない。
6. Elektron、OTO、Strymonの専用研究をGitで読める状態にしてから信号順を決める。
