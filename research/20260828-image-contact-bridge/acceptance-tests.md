# 接触入力bridge 合格条件

この文書は実行済みテスト報告ではなく、Skulptur入力層を実装するときに満たすべき検査条件である。

## A. Schema

### A-01 有効な単指contact

- `trackIds: [0]`
- `phase: contact`
- x/yは0〜1
- pressure取得不能時は `pressure: null` と `pressureSource: unavailable`
- 期待: schema合格

### A-02 架空pressureの拒否

- `pressureSource: unavailable`
- `pressure: 0.5`
- 期待: schema不合格

### A-03 トラック範囲

- `trackIds: [4]` または空配列
- 期待: schema不合格

### A-04 接触範囲

- x、y、contactArea、pressureのいずれかが0〜1外
- 期待: schema不合格

## B. 接触の因果

### B-01 指だけ動く状態を禁止

接触フレームを受理したのに、対象トラックと制御イベントのどちらも変化しない場合は不合格。視覚効果だけを接触成立と扱わない。

### B-02 音だけ変わる状態を禁止

gesture由来の音響制御が発生したのに、どのトラック・位置・phaseが作用したか描画側で追跡できない場合は不合格。

### B-03 同じ接触境界を共有

描画変形と音響制御が、同じ `gestureId`、`pointerId`、`timestampMs`、`trackIds` に由来すること。別々の推定器で接触対象を再計算しない。

## C. 形状と所有権

### C-01 無断モーフィングを禁止

gesture中に、画面向きやレイアウト変更がないのにタッチ対象の幾何学的な大きさが変化しないこと。音響効果量の変化をヒット領域の拡縮で表現しない。

### C-02 4トラックの所有権

各フレームが少なくとも一つの `trackIds` を持ち、UI上でも同じトラックを識別できること。複数トラック時は暗黙にmasterへ昇格しない。

### C-03 orientation非依存

縦横画面で同じ素材位置を指す操作は、正規化x/yとして同じ意味を保つ。ピクセル座標をPerformance Takeへ保存しない。

## D. 時系列

### D-01 phase遷移

通常終了は `contact -> press/slide -> release`。OS割込み、入力喪失、向き変更で継続不能なら `cancel` を発行し、releaseを捏造しない。

### D-02 単調時刻

同じgesture内の `timestampMs` は後戻りしない。

### D-03 release連続性

release直前と直後で不連続な音量・feedback jumpを起こさない。具体的な平滑化時間と合格閾値はSkulptur DSP確定後に固定する。

### D-04 Performance Take再生

記録再生時、音響制御と接触軌跡が同じイベント列を読むこと。見た目用に別の補間済みgestureを正本にしない。

## E. 端末情報の誠実性

### E-01 pressure取得不能

端末がpressureを返さない場合、`pressureSource: unavailable` とする。推定を導入する場合は `estimated` と明示し、hardwareと同じ検証結果へ混ぜない。

### E-02 cancel回復

cancel後にpointer所有権、トラック選択、feedback状態が残留しないこと。

## 未固定

次はこのbridgeの合格条件ではなく、後続研究で決める。

- x/yと音響パラメータのmapping
- 実時間同期の許容遅延
- release smoothingの時間
- pressure推定方式
- マルチタッチの最大同時数
- 触覚フィードバック
