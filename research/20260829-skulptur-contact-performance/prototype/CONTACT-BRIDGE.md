# 画像接触研究の技術移植

Sound Labの`main`に入った画像接触研究を、Skulptur試奏面の入力層へ接続した記録です。

## Git上の供与元

- `b1d0ee3`: 接触状態bridge、JSON Schema、合格条件（PR #36）
- `688a040`: 実行時検証とphase gate（PR #37）
- `cb0228b`: Pointer Event adapterと中断規則（PR #40）
- upstream path: `research/20260828-image-contact-bridge/`

供与元の状態は`candidate / implemented-unverified`です。Skulpturの製品DSP mappingとiPhone実機検証までは供与元で行われていません。

## このprototypeで採用したもの

| 層 | 採用内容 |
| --- | --- |
| 入力契約 | `sound-lab.contact-gesture/v0.1` |
| phase | `contact / press / slide / release / cancel` |
| 座標 | surface内の正規化`x / y`。範囲外はclampせず拒否 |
| 所有権 | 共通スペクトル面が作用する4トラックを`[0,1,2,3]`と明示 |
| pressure | `hardware / estimated / unavailable`の出自を検査。既定は`null + unavailable` |
| 中断 | `pointercancel / lostpointercapture / blur / pagehide / orientationchange`をcancelへ変換 |
| Skulptur mapping | `x`→10帯域、`1-y`→Cut・Neutral・Feedbackの既存位置 |
| Take | 受理済みframe列を相対時刻で保存し、再生instanceへ展開 |
| Player | 単調時刻でframeを順次発行し、中断時は全active接触をcancel |

描画と音響操作は`gestureId / pointerId / timestampMs / trackIds`を持つ同じframeから導出します。KAOSS型の汎用XY effect選択へは戻していません。

## 保留

- pressure/contactAreaの音響割当
- track別の独立スペクトル処理（現DSPは4ループ合成後の共通処理）
- Mobile SafariとiPhone実機のevent順序、同時pointer数、遅延
- 複数Takeの一覧、命名、永続保存UI

## Skulptur側で追加した改良

- `pointercancel`は画面外座標を再計算せず、最後に成立した接触点から終了する。
- capture中の`pointerup`がsurface外で拒否された場合、releaseを捏造せずcancelを発行して所有権を解放する。
- Takeは空、時刻後退、未終了gesture、改変されたdurationを拒否する。
- Take再生時は元のgesture IDを再利用せず、新しい再生instance IDを付与する。
- 再生pointer IDも高い合成IDへ分離し、同時に触れた実pointerと衝突させない。
- デモの一つの`TAKE`ボタンで録音、停止、一回再生、再生中断を循環する。

pressure非対応時の`0.5`をhardware値とみなさず、接触面積も実機由来を確認するまで推定しません。
