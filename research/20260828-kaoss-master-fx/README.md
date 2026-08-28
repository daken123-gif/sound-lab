# KAOSS PAD / KAOSSILATOR master FX research

- research-id: `20260828-kaoss-master-fx`
- status: `active`
- 更新日時: 2026-08-28
- 研究対象: KORG KAOSS PAD、KAOSSILATOR、およびField Looperへの統合
- 現在の問い: 4トラックのルーパーと直接触れる合成波形に、KAOSSの演奏性を複雑化させず統合するにはどうするか

## 現在の統合要件

以下は外部製品の事実ではなく、この製品で採用する現在の要求である。

- iPhoneは横画面を前提にする。
- ループは4トラック。
- 4トラックを合成した波形を直接触れる。
- 録音済みのレイヤーをリアルタイムに切り替えて波形処理できる。
- KAOSSは各トラックの挿入エフェクトではなく、合成後のマスターエフェクトとして使う。
- 人間が直感的に使え、内部の複雑さを演奏画面へ露出させない。
- アプリ起動、マイク許可、画面復帰を録音開始のトリガーにしない。録音は人間がRECを押したときだけ始める。
- 常時入力は録音ではなく、外音・声を演奏素材として監視する状態。
- INPUT / OUTPUTはピークメーター形式で表示し、それぞれ入力ゲインと出力ゲインを持つ。
- Echo Cancellationはオン／オフ可能にする。
- 発振音だけでなく、マイクから声や外音が実際の処理経路へ入ることを基本動作とする。

## 他の島との同期（2026-08-28）

- `field-processor/index.html` の現行 `main` は、4個のループ操作子、`lanes.length = 4`、4要素の再生レート／レベルを持つ。
- `research/20260828-iphone-mic-preamp/README.md` も、CLEAN経路と4トラック構成を現行の維持対象として記録している。
- したがって、この研究の統合基準を3レイヤーから4トラックへ更新する。
- 会話横断検索では他の島の直接発話本文を取得できず、検索器の制御文だけが返ったため隔離した。ユーザー原文を取得したとは扱わない。
- 3レイヤー案は履歴として残し、現在の実装判断へ復活させない。

## 一次資料

### KAOSS PAD

- [KAOSS PAD KP3+ 公式製品ページ](https://www.korg.com/us/products/dj/kaoss_pad_kp3_plus/)
- [KAOSS PAD KP3+ 公式機能](https://www.korg.com/us/products/dj/kaoss_pad_kp3_plus/page_1.php)
- [KAOSS PAD KP3+ 公式仕様](https://www.korg.com/us/products/dj/kaoss_pad_kp3_plus/page_2.php)
- [KAOSS Replay 公式製品ページ](https://www.korg.com/us/products/dj/kaoss_replay/)
- [KAOSS Replay 公式取扱説明書](https://www.korg.com/download/global/html_manual/kaossreplay/us/index.html)
- [KAOSS PAD QUAD 公式機能](https://www.korg.com/hken/products/dj/kaoss_pad_quad/page_1.php)
- [mini KAOSS PAD 2 公式エフェクト一覧](https://www.korg.com/au/products/dj/mini_kaoss_pad2/page_4.php)

### KAOSSILATOR

- [KAOSSILATOR PRO+ 公式製品ページ](https://www.korg.com/us/products/dj/kaossilator_pro_plus/)
- [KAOSSILATOR PRO+ 公式機能](https://www.korg.com/hken/products/dj/kaossilator_pro_plus/page_1.php)
- [KAOSSILATOR PRO+ 公式仕様・プログラム一覧](https://www.korg.com/hken/products/dj/kaossilator_pro_plus/page_2.php)

## 観測できた事実

### KAOSS PAD

- KAOSS PADは入力音へリアルタイムエフェクトを適用し、XYパッドで複数パラメータを同時操作する。
- KP3+には150のエフェクトプログラムがある。
- KAOSS PAD QUADはLooper、Modulation、Filter、Delay/Reverbの四系統を組み合わせる。
- Touch Holdは最後の座標を保持する。
- KAOSS ReplayのPad MotionはXY操作を約12秒記録して再生でき、逆再生にも対応する。
- KAOSS Replayのプログラムメモリーには、エフェクト、FX Target、FX Depth、Pad Motion、Touch Hold状態、XY座標が保存される。
- FX Releaseはタッチ終了時に処理音を即座に切断せず、残響やディレイの尾を利用して原音へ戻すための機能である。

### KAOSSILATOR

- 横方向が主に音程、縦方向が音色パラメータとして機能する。
- Key、Scale、Note Rangeにより、横方向の音程を音楽的な範囲へ拘束できる。
- KAOSSILATOR PRO+は35スケール、250プログラム、4ループバンクを持つ。
- Gate Arpeggiatorはパッド上の音を時間方向に刻み、Gate TimeとGate Speedを演奏中に変更できる。
- KAOSSILATOR PRO+のループ録音は最大4小節で、各バンクのミュート、音量、ループ長を操作できる。

## ユーザーの実機・試奏評価

- 以前の試作は「ノイズマシン」で、アンビエントになっていない。
- KAOSSILATORを参考にした後、さらにノイズマシン化した。
- 発振音は出たが、声や外音が処理経路へ入らなかった。
- マイク入力が動いた段階でも音量が小さく、INPUT / OUTPUTゲインが必要だった。
- 自動で録音開始する動作は意味が分からず、採用しない。
- イヤホンでの現在の試奏結果も不合格。
- UIと音響設計を別々に扱わず、実際に人間が演奏できるものにする必要がある。

## 推論・設計判断

### XYの役割を混ぜない

KAOSS PADとKAOSSILATORは同じXYパッドを使うが、役割は異なる。

- KAOSSILATOR: 音を生成してフレーズを弾く。
- KAOSS PAD: すでに流れている音を変形し、指を離すと戻す。

単純にXを連続音程、Yをレゾナンス、指速度をFM量へ接続すると、動かすほど高域・変調・フィードバックが増え、ノイズ化しやすい。KAOSSILATOR側では音階量子化と音色専用マクロを先に設計する。

### レイヤー波形処理とKAOSSマスターを分離する

採用する信号構造:

```text
MIC / LIVE INPUT
        |
   INPUT GAIN
        |
  LOOP 1 --+
  LOOP 2 --+
  LOOP 3 --+--> track / MIX waveform performance --> KAOSS MASTER --> final space --> OUTPUT GAIN
  LOOP 4 --+
```

- 中央の波形面は、録音素材の位置と断片を直接操作する。
- 右側のKAOSS面は、4トラック合成後の全体を処理する。
- トラック選択は中央の `1 / 2 / 3 / 4 / MIX` に置く。
- KAOSSにはレイヤー対象選択を置かず、常にマスターとして扱う。

### 横画面UI

| 左 | 中央 | 右 |
| --- | --- | --- |
| LOOP 1〜4のREC / PLAY / STOP | 大きな合成波形 | KAOSS XY |
| 各トラックの小波形と状態 | `1 2 3 4 MIX` | プリセット |
| INPUTメーター / ゲイン | 選択範囲と再生位置 | OUTPUTメーター / ゲイン |

主操作を長押し、二本指、隠れたスワイプへ依存させない。マルチタッチは、片方の指で波形またはKAOSSを保持しながら、もう片方でレイヤーやプリセットを切り替える用途に使う。

### 合成波形の操作

- X: ループ内の音の位置。
- Y下部: 通常再生に近い。
- 上へ移動: 選択位置から取得する断片を短くし、反復を強める。
- 横ドラッグ: 捕捉した断片をスクラブする。
- 指を離す: 本来の同期再生位置へ短いクロスフェードで復帰する。
- 選択対象: `1`、`2`、`3`、`4`、または4トラック合成後の `MIX`。
- 波形上で捕捉中の範囲を明示し、操作結果を推測させない。

### KAOSSプリセット

エフェクトチェーン編集は演奏画面へ出さず、複数処理を調整済みのプログラムとして選ぶ。

| Program | 内部の組合せ | X | Y |
| --- | --- | --- | --- |
| SPACE | filter + diffusion + long reverb | small / large space | dry / deep |
| TAPE | tape delay + wow/flutter + gentle degradation | slow / fine repeats | clean / aged |
| DUB | BPM delay + filter + reverb | rhythmic division | feedback |
| BLOOM | granular diffusion + freeze + reverb | grain/window | density/spread |
| CUT | beat repeat + short delay + filter | repeat division | processing depth |

共通規則:

- 左下を安全域とする。
- 上へ行くほど処理を深くする。
- 指を離すと新規入力を閉じ、残響尾を残して原音へ戻す。
- 切替時はXY座標を保持し、音量を短くクロスフェードする。
- 前プログラムのディレイ・リバーブ尾を不自然に切らない。
- プリセット間の知覚音量を揃える。
- 歪み、リングモジュレーション、強いデシメーションを初期の中心に置かない。

### KAOSSILATORの最小統合

KAOSSILATORは常時モードにせず、明示的な `PLAY` 操作中だけ発音する。

- Xは選択スケールへ量子化する。
- Yは全音色共通のレゾナンスではなく、音色ごとに調整した複合マクロとする。
- 初期版は一音色から始め、上方向を「最大破壊」にしない。
- タップは短音、保持は持続、横移動は音階上の移動。
- KAOSSILATOR内部で過剰な残響を重ねず、外側の空間系と競合させない。

### 録音状態

- 起動時はモニターのみで、全ループは空。
- RECボタンだけが録音開始の入口。
- マイク許可、AudioContext開始、Echo Cancellation変更、画面復帰、プリセット変更は録音開始の入口にしない。
- 最初のループはRECで開始し、もう一度押して終了する。勝手に録音終了やオーバーダブへ移行しない。
- 録音、再生、待機、オーバーダブ、停止は文字と色の両方で区別する。
- CLEARは停止中にだけ露出させ、演奏中の誤消去を防ぐ。

## Field Looperへ採用する点

- 4トラック。
- iPhone横画面。
- 常時マイク監視と録音状態の分離。
- 4トラックとMIXを切り替えられる中央の直接波形操作。
- 合成後に置くKAOSSマスター。
- 5つの調整済みマスタープリセット。
- INPUT / OUTPUTピークメーターと独立ゲイン。
- Echo Cancellation切替。
- FX Release相当の自然な復帰。
- 主要状態と現在対象を常時表示する。

## 採用しない点

- 3ループを現在構成として固定する案。
- KAOSS自体への `LIVE / 1 / 2 / 3 / ALL` ターゲット選択。
- KAOSSを録音レイヤーごとの挿入エフェクトとして使う案。
- アプリ起動後の自動録音。
- マイク取得成功を録音開始と同一視する設計。
- 大量のプリセットを最初から表示する設計。
- 主操作を説明なしの長押しや二本指へ隠す設計。
- XY上端を歪み、発振、レゾナンス最大へ直結する設計。
- 発振音が鳴ることだけを基本動作の成功判定にすること。

## 失効した判断

後の島が古い判断を復活させないため、撤回履歴を残す。

1. 「3つのループ」  
   現行 `main` の4トラック構成と他研究の実装記録により、現在は4トラックへ変更。
2. 「KAOSSの対象をLIVE / 各レイヤー / ALLから選ぶ」  
   KAOSSをマスターとする現在設計と矛盾するため撤回。レイヤー切替は中央の波形処理側へ移した。
3. 「録音中はKAOSSを入力へ焼き込み、非録音時は全体へかける」  
   状態で役割が勝手に変わり、操作結果を予測しにくいため採用しない。
4. 「起動・マイク許可後に自動録音」  
   ユーザーの明示操作なしに録音を始めるため撤回。
5. 「縦画面中心の一画面」  
   合成波形、4トラック、KAOSSマスターを同時に直接操作するため横画面へ変更。

## 2026-08-28 波形対象切替の統合

- 中央波形へ `1 / 2 / 3 / 4 / MIX` を常時表示し、録音済みトラックまたは全体を明示的に選ぶ。
- Xは選択対象のループ位置、Yは上へ行くほど短い断片反復とする。
- 指を離したとき、タッチ開始前の再生位置へ戻すのではなく、操作中も進んでいたはずの同期位置へ短いクロスフェードで復帰する。
- KAOSSの信号経路は変更せず、常に4トラック合成後のマスターとして維持する。
- KAOSSプリセットはこの統合へ混ぜず、波形対象切替の実機評価後に別差分として追加する。

## 触る実装パス

この統合では `field-processor/index.html` の波形操作と対象表示を変更する。

統合時の候補:

- `field-processor/index.html`
- 将来オーディオ処理を分割した場合のaudio engine / worklet
- 将来UIを分割した場合のwaveform / track / kaoss components

## 依存する研究

- Loopy Pro: 入力経路、ループ状態、Echo Cancellation、UI。
- RC-505mkII: 3トラックの明示状態、REC / PLAY / OVERDUB / STOP。
- Strymon: SPACE、BLOOM、残響尾、知覚音量。
- Dedalus: 合成波形への直接接触、断片捕捉、スクラブと復帰。
- KAOSS PAD / KAOSSILATOR: XYプログラム、FX Release、音階拘束。

各依存研究は別research-idで保存し、この研究ブランチへ直接mergeしない。

## 未検証事項

- iPhone 13 mini横画面で、中央波形とKAOSS XYの両方が十分なタッチ面積を確保できるか。
- 実機イヤホン使用時のマイク入力経路、レイテンシ、モニター音量。
- Echo Cancellationオン／オフ時の音質、ループ再入力、フィードバック挙動。
- 4トラック波形描画とリアルタイムグラニュラー処理を同時実行した際のCPU負荷。
- 中央波形でMIXを捕捉した際の位相、音量、復帰クロスフェード。
- KAOSS各プリセットの安全なパラメータ範囲と知覚音量。
- プリセット切替時の古い残響尾の保持方法。
- KAOSSILATORの初期音色、スケール、音域。
- 実機で「声を入れる、録る、波形を触る、全体へKAOSSをかける」が説明なしに成立するか。
- 現行試作がイヤホンで不合格になった具体的原因の切り分け。

## 次の検証順序

1. 発振器を止めても、声がINPUTメーター、モニター、録音バッファへ到達することを確認。
2. 自動録音が存在せず、RECだけで録音が始まることを確認。
3. 4トラックの録音・再生・停止を確認。
4. 1レイヤーの波形をX位置で捕捉し、指を離すと同期位置へ戻ることを確認。
5. MIX波形でも同じ操作を確認。
6. KAOSS SPACEのみをマスターへ接続し、左下で原音を保持できることを確認。
7. TAPE、DUB、BLOOM、CUTを一つずつ追加し、各追加後にノイズ化と音量跳躍を検査。
8. 最後にKAOSSILATORを一音色だけ追加する。

