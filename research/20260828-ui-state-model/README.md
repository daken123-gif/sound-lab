# UI状態遷移研究

- research-id: `20260828-ui-state-model`
- 更新日時: 2026-08-28
- 状態: `research-only`
- 変更範囲: 研究記録のみ。製品コード、統合判断、画面デザインは変更しない。

## 研究対象と現在の問い

iPhone上で、入力、4トラック録音、共通再生、録音素材への主演奏、候補処理、Performance Takeが同時に存在するとき、操作の意味が隠れたモードによって変わらない状態構造を作れるか。

この研究は画面の見た目を決めない。特にGit未収載のSkulptur研究本文を推測して、主演奏面の具体ジェスチャーやレイアウトを固定しない。

## 現在取得できた根拠

### 現行統合文書

- `integration/DIRECTION.md`
  - 4トラックを録音の中心にする。
  - 録音開始は人間が明示的に決める。
  - 入力元、接続状態、録音中かを判別可能にする。
  - RAWと後段の音作りを分離する。
  - Skulptur型を録音後の主演奏面にするが、具体DSP、画面、操作割当は未固定。
  - KAOSS型Masterは失効し、現行Field Looper UIは設計資産として隔離されている。
- `integration/DECISIONS.md`
  - D-001、D-004、D-007、D-008、D-009、D-010を境界とする。
- `integration/STATUS.md`
  - 4トラック録音とPerformance Takeは `implemented-unverified`。
  - Skulpturは `coverage-gap`。
  - Chroma、Things Motor、Dedalus、BattleFX等は候補であり、統合済みではない。

### open PRで観測した実装候補

Draft PR #15 `integration/performance-take-core` の説明と差分で次を観測した。

- `INPUT ON` と各トラックの録音開始を分離。
- 4トラックを同じAudioContext時刻から再生する共通時間。
- 実波形、合成波形、共通プレイヘッド。
- 素材位置と独立した演奏経過時間でPerformance Takeイベントを記録。
- iPhone実機は未検証。
- PRは現在mainと競合しており、main統合済みではない。

PR #15にあるGRAB、共通ループ、REVERSE、イベント線編集は実装候補として観測しただけで、本研究から現行UIへ採用しない。

### ユーザーによる現在訂正

- KAOSSは退役している。
- 他研究も進行している。

この訂正を現在境界とし、古いKAOSS中心研究を状態モデルへ復活させない。

## 観測から分離した問題

一つの巨大な「アプリ状態」で管理すると、次の操作がモードごとに別の意味を持ちやすい。

- RECが入力許可、録音開始、オーバーダブ、Take記録を兼ねる。
- PLAYがトラック単体再生と共通テープ再生を兼ねる。
- 波形への接触がSEEK、素材演奏、時間メモリsend、イベント編集を兼ねる。
- 色だけで録音、選択、処理中、Take記録を区別する。
- 第二指、長押し、同時押しで、表示されていない機能へ切り替わる。

この混線は「機能数」より「誰が現在の時間と音を所有しているか」が不明なことから生じる。

## 状態モデル仮説: 一つのモードではなく六つの直交領域

UI全体を `RECORD MODE`、`FX MODE` のような排他的モードへ分けない。次の六領域を独立して表示・遷移させる。

### 1. Input

```text
DISCONNECTED -> REQUESTING -> READY
                    |
                    v
                  ERROR
```

- `INPUT ON` は許可と経路確立だけを行う。
- `READY` になっても録音は始めない。
- 入力名、経路、準備状態、入力レベルを録音操作と分離して表示する。
- 録音中の経路変更は暗黙実行しない。

### 2. Track Content × 4

```text
EMPTY --REC_i--> RECORDING --REC_i/STOP--> READY
READY --CLEAR_i + visible confirmation--> EMPTY
```

- 4トラックは同じ三状態を持つ。
- `REC_i` は空トラックの録音開始、録音中トラックの停止だけに限定する。
- `READY` で同じRECを押しても、元音を暗黙上書きしない。
- オーバーダブは採用未決定。必要ならRECの多重意味ではなく、別の明示状態として研究する。
- mute、gain、send選択は音声内容の状態と分離した属性とする。

### 3. Common Transport

```text
STOPPED <-> RUNNING
STOPPED/RUNNING -> SCRUBBING -> previous
```

- 再生時間は4本に共通する。
- 各トラックへ独立したPLAYモードを置かず、参加／muteを別属性にする。
- 実波形と共通プレイヘッドは常時同じ時間座標を示す。
- 録音中のSEEKは時間座標を破壊するため候補段階では禁止する。

### 4. Primary Material Performance

```text
IDLE <-> ENGAGED
```

- ここはSkulptur型主演奏面の所有領域。
- `ENGAGED` は素材へ現在触れていることだけを表す。
- 具体的な指位置、音色軸、継続条件、複数指操作はSkulptur本文取得まで固定しない。
- HAND TOOLの表示によって主演奏面の意味を無断でKAOSS型XYへ変えない。

### 5. Hand Tool

```text
CLOSED -> OPEN(tool-id) -> ENGAGED(tool-id) -> OPEN/CLOSED
```

- 同時に前面へ出す候補処理は一つ。
- `tool-id` はRotor、Chroma系経路、Dedalus系時間メモリ、BattleFX系rhythmic-tail等の候補を識別するが、搭載を確定しない。
- send元、処理中、return先を表示する。
- 一時接触、保持、Gesture記録、Captureは同一規則に潰さず、各研究の持続時間の違いを保持する。
- toolを閉じてもRAW、4トラック内容、共通再生位置は変えない。

### 6. Performance Take

```text
IDLE --TAKE REC--> RECORDING --STOP--> STORED
STORED --RUN TAKE--> REPLAYING --STOP/END--> STORED
STORED --NEW TAKE--> RECORDING
```

- Take開始は一回の明示操作にする。素材RECや最初の画面接触から自動開始しない。
- Take時間と素材再生位置を分ける。
- TakeはRAWや4トラックAudioBufferを書き換えない。
- Skulptur、Hand Tool、transportのどの操作を記録対象にするかはevent schemaの取得・整理後に固定する。
- 旧KAOSS座標イベントは現行schemaへ自動継承しない。

## 操作の所有権

| 操作 | 所有領域 | 変えてよい状態 | 変えてはいけない状態 |
| --- | --- | --- | --- |
| INPUT ON | Input | 接続要求、入力準備 | Track録音、Take録音 |
| REC 1–4 | 対象Track | EMPTY / RECORDING | 他Track、Take |
| PLAY / STOP | Common Transport | 共通再生 | Track内容、Input |
| 素材接触 | Primary Material | 演奏中の一時状態 | RAW、Track内容 |
| Tool選択 | Hand Tool | 前面のtool-id | 主演奏面の役割、Track内容 |
| TAKE REC | Performance Take | Take記録 | Track録音 |
| CLEAR | 対象Track | READYからEMPTY | 他Track、Take内容 |

一つの操作が複数領域を変える場合は、連鎖を暗黙化せず、UI上で実行前に結果が読める必要がある。

## 同時操作と衝突の候補規則

| 組合せ | 候補判定 | 理由 |
| --- | --- | --- |
| 他トラック再生中に空トラックを録音 | 許可候補 | 4トラック録音楽器として基本動作になる。同期とモニター遅延は実機未検証。 |
| Track録音中に入力経路を変更 | 禁止候補 | 一つのRAW内で経路が変わり、入力由来が不明になる。 |
| Track録音中に共通SEEK | 禁止候補 | 共通時間と新規録音時間が衝突する。 |
| Take録音中に素材へ触る | 許可候補 | Takeが残す中心行為。ただしSkulptur eventは未定。 |
| Take録音中にHand Toolを触る | 条件付き候補 | tool固有event schemaと再演可能性の確認が必要。 |
| Take録音中にTrackをCLEAR | 禁止候補 | Takeが参照する素材を破壊する。 |
| Track録音中にHand Toolを触る | 条件付き候補 | RAW非破壊は守れるが、monitor、wet記録、CPUの境界が未決定。 |
| 画面回転中に録音・再生 | 状態維持を要求 | D-009により縦横は配置差であり、音声状態の変更理由ではない。 |
| iOS割込み／background | 無言継続を禁止 | 録音継続、停止、失敗を判別可能にする必要がある。実際のiOS挙動は未検証。 |

## 可視性の不変条件

以下はレイアウトではなく、どの縦横配置でも失わない情報条件である。

1. 実際の入力名、接続状態、メーター。
2. どのTrackが `EMPTY / RECORDING / READY` か。
3. 共通transportが停止中か動作中か。
4. 実サンプル由来の波形と現在位置。未録音・無音を装飾波形で埋めない。
5. 素材RECとTake RECを、位置だけでなく語と形で区別する。
6. 現在選択中のHand Tool、send元、処理中か。
7. 操作を拒否した場合の局所的な理由。
8. 色だけに依存しない状態差。

## 採用しない点

- KAOSS型Master、XY面、プリセット階層を状態モデルの中心へ戻す。
- `REC` 一個へ入力許可、Track録音、overdub、Take録音を統合する。
- 同じTrackボタンを押すたび `record -> play -> overdub -> stop` と隠れて循環させる。
- 第二指、同時押し、秘密の長押しで主要状態を変更する。
- Hand Toolを4トラックへ4インスタンス常設する。
- 選択中の機材名だけで処理経路を推測させる。
- 横画面と縦画面で異なる音声状態機械を持つ。
- Skulptur未取得部分を、PR #15の波形ジェスチャーや旧KAOSS操作で補う。

## Field Looperへ採用する点

現時点では統合採用ではなく、次の比較対象を作るための候補とする。

1. 単一モードではなく六つの直交状態領域。
2. INPUT ONとTrack RECの分離。
3. Track ContentとCommon Transportの分離。
4. Track RECとPerformance Take RECの分離。
5. RAWを破壊しないHand Tool。
6. 操作所有権表と衝突表を使った実装前検査。
7. 縦横で同じ状態を維持し、配置だけを変える。

## 失効した判断

- KAOSS型Masterを主演奏面にする判断はD-003からD-007 / D-008へ失効済み。
- 強制横画面はD-005からD-009へ失効済み。
- 3ループ前提はD-001の4トラック化で失効済み。
- PR #15の現在UIを完成UIとみなす判断は存在しない。Draftかつ実機未検証であり、mainとの競合も観測した。

## 触る実装パス

この研究では製品コードを変更しない。

将来、状態機械をコード化する場合も、現在リポジトリに存在しないパスを実装済みとして扱わない。PR #15と同じ `field-processor/index.html` を触る前には、mainとの差分、現役PR、UI隔離境界を再取得する。

## 依存する研究

### Gitで本文または差分を取得できたもの

- `integration/DIRECTION.md`
- `integration/DECISIONS.md`
- `integration/STATUS.md`
- Draft PR #15 Performance Take / shared tape
- Chroma Console研究
- Things Motor研究
- BattleFX研究
- Dedalus研究

### 取得不能／未収載

- Skulptur研究本文
- Loopy Pro固有README
- RC-505mkII固有README
- Transit 2固有README

未取得資料の内容を本研究の根拠として補っていない。

## 未検証事項

- iPhone実機での入力許可、録音、共通再生、割込み復帰。
- 他トラック再生中録音の同期とモニター遅延。
- 画面回転中のWeb Audio状態維持。
- Skulptur主演奏event。
- 各Hand Toolの持続時間とTake再演schema。
- CLEARの誤操作率と、見える確認操作の最小手数。
- VoiceOver、Dynamic Type、色覚差、片手保持時の到達性。
- iPhone 13 mini相当の縦横寸法で、可視性不変条件を同時に満たせるか。
- Web、AUv3、native iOS間で同じ状態意味を維持できるか。

## 次の検証

この状態モデルを実装へ直結させず、まず次の三系列を紙上トレースする。

1. 入力接続 -> Track 1録音 -> Track 1再生 -> Track 2録音。
2. 4トラック再生 -> 素材演奏 -> Hand Tool接触 -> Take記録 -> Take再演。
3. 録音中の入力切断、iOS割込み、画面回転、誤CLEAR。

各操作の前後で六領域の状態を記録し、意図していない領域が変化した遷移を欠陥として扱う。
