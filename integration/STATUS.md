# 統合状況

最終観測: 2026-08-28 08:17 UTC / GitHub `daken123-gif/sound-lab`

観測時の `main`: `7578007f1b3b3ed7f8fcf0d63e1a58145f62efe5`

観測範囲: 30ブランチ、全26 PR、open PR 8件、`main`、各open研究PRの本文と取得可能な研究README・実験・テスト。

## 現在位置

| 領域 | Gitで観測した証拠 | 統合状態 | 未完了 |
|---|---|---|---|
| 4トラック録音 | `main` 実装、Koala・Teenage Engineering研究、PR #15 | `adopted` / `implemented-unverified` | iPhone実機の録音・再生・実波形・位置表示 |
| iPhone入力段 | `main` と `20260828-iphone-mic-preamp` | `integrating` | 内蔵、有線、Bluetooth別の実機測定 |
| Skulptur型主演奏面 | Chroma、Things研究が現在判断として参照 | `adopted` / `coverage-gap` | Skulptur研究本文、具体DSP、UI、検証証拠がGit未確認 |
| KAOSS | 古い研究と旧実装。`main` UI隔離宣言が中心利用を否定 | `superseded` | 主演奏層として再統合しない |
| 現行Field Looper UI | `main` 冒頭の隔離宣言 | `rejected`（設計再利用） | 音声経路・DSPだけ個別に再検証 |
| Performance Take | Draft PR #15。明示開始、イベント核、29テスト成功の報告 | `implemented-unverified` | KAOSS依存イベントの除去、iPhone実機、ブラウザ音声 |
| Koala Sampler | open PR #12、研究README | `researching` | 複雑度上限以外の採否 |
| THE PIPE | open PR #16 | `researching` | 人声、実機、入力経路 |
| BODY resonator | open PR #18、独立DSP、26テスト成功の報告 | `candidate` / `implemented-unverified` | 人声、iPhone、Safari AudioWorklet、4トラック統合 |
| Things Motor | branch `research/20260828-things-motor`、8係数テスト | `candidate` | 実音、相関別カーブ、iPhone、UI。PR未確認 |
| Chroma Console | Draft PR #19、28節研究、非可換性・固有DRIFT実験 | `candidate` | 実機比較、実楽器、リアルタイム負荷、統合判断 |
| Dedalus | Draft PR #26、`20260828-dedalus-wave` README | `candidate` / `research-only` | 共有send/return、二読取ヘッド、実音、iPhone負荷、UI。第五トラックにはしない |
| BattleFX | Draft PR #23、`20260828-battlefx` README | `candidate` / `research-only` | selected-track send、choke semantics、nudge、S.RATE結合、iPhone負荷 |
| Abbey Road | `main` の `20260828-abbey-road-equipment`、open PR #24 | 入力構造は `adopted` / DSPは `candidate` | REDD/TG等のDSP、正規IR、J37世代管理、varispeed、iPhone実機、音量一致 |
| 独立ドラム | 統合判断のみ | `adopted`（分離） / `coverage-gap` | Elektron等の研究本文と接続仕様 |

## open PR

- #12 Koala Sampler研究
- #15 Field Looper録音・実波形・共通テープ・Performance Take（Draft、実機未検証）
- #16 THE PIPE中心研究
- #18 THE PIPE由来BODY独立DSP
- #19 Chroma Console研究と非可換性・固有DRIFT実験（Draft）
- #23 BattleFX rhythmic-tail研究（Draft）
- #24 J37 reduction mix・世代管理・varispeed研究
- #26 Dedalus共有時間メモリ研究（Draft）

open PR、branch、テスト成功は、`main`統合、iPhone実機検証、聴感採用の証拠ではない。

## Gitで本文を取得できた研究

- `20260828-iphone-mic-preamp`
- `20260828-kaoss-master-fx`（歴史資料。現行中心判断ではない）
- `20260828-teenage-engineering`
- `20260828-koala-sampler`
- `20260828-soma-organismic`
- `20260828-things-motor`
- `20260828-chroma-console`
- `20260828-abbey-road-equipment`
- `20260828-battlefx`
- `20260828-dedalus-wave`
- `prototype/body-engine`

Loopy Pro、RC-505mkII、Strymonはブランチ名を観測したが、監査時点で固有研究READMEを確認できなかった。

## 被覆欠落

次は現行Git文書から名称または役割を確認できるが、固有研究本文を取得できていない。

- Skulptur
- Microcosm
- Max/MSP
- Elektron / 独立ドラム
- OTO BIM / BAM / BOUM
- 1192 Blackface
- AUM
- Transit 2
- Combustor

この一覧は研究が存在しないという断定ではない。Git監査で本文を取得できなかったという状態。

## 監査境界

島・会話の横断取得は二回とも検索ラッパーまでで止まり、一次会話本文へ到達できなかった。返却された要約や抜粋は方向判断の証拠に使っていない。現在の統合判断は、Gitで全文を読み戻せた文書、差分、PR状態だけに基づく。

## 次の統合順

1. Skulptur研究本文とKAOSS退役の根拠をGitへ保存し、主演奏面の具体境界を確定する。
2. iPhone実機で入力、明示録音、4トラック再生、実波形、位置表示を検証する。
3. PR #15からKAOSS中心UIとイベント依存を分離し、再利用可能な録音核だけを判定する。
4. Dedalusの共有時間メモリとBattleFXのselected-track rhythmic-tailを、いずれも一基の明示send候補として、dry比較・routing・CPU・操作衝突から先に検証する。
5. BODY、Rotor、Chromaを主演奏面の代替にせず、個別候補として音響検証する。Abbey Roadは採用済み入力原則と未検証DSPを分け、REDD/TGから一系統ずつ検証する。
6. Microcosm、Max/MSP、Elektron、OTO、1192等の未収載研究をGitで読める状態にしてから信号順を決める。
