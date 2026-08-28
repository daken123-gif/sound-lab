# 画像接触研究 → Sound Lab 接触入力bridge

- research-id: `20260828-image-contact-bridge`
- 状態: `candidate` / `research-only`
- 更新日: 2026-08-28
- 接続先候補: 4トラック録音後のSkulptur型主演奏面の入力層
- 製品コード変更: なし
- 採用判断: 未実施
- 実機検証: 未実施

## 現在の問い

画像研究で扱ってきた「手の移動ではなく接触を成立させる」「接触境界を相互に連動させる」「変形中に手や対象の大きさを勝手に変えない」という知見を、Sound Labの4トラック／Skulptur型主演奏面へ、視覚装飾ではなく演奏入力として渡せるか。

## 権威と証拠境界

### 現在ユーザー判断

- 画像研究からSound Labへ使えるものを接続する。
- KAOSS中心階層は復活させない。
- 画像研究全体を複製せず、接触入力の契約として渡す。
- 音響方式はSkulptur側が決め、画像側は接触状態までを渡す。

### Gitで確認できたSound Lab側の境界

- `integration/DIRECTION.md`: 4トラック、Skulptur型主演奏面、KAOSS中心退役、簡単な演奏経路。
- `integration/DECISIONS.md`: D-001、D-007、D-008、D-010。
- `integration/STATUS.md`: Skulpturの具体DSP、パラメータ、タッチ割当は未固定。

### 取得できていないもの

画像研究側の触覚可視化、衣服と身体の接触、Live2D／モンタージュ研究について、安定したGit pathとcommitは今回取得できていない。そのため本bridgeは画像研究の正本を再構成せず、現在ユーザー判断とSound Lab側の境界だけで定義する。画像研究側の正本locatorは `coverage-gap` とする。

## 渡すもの

画像側から渡すのは、音色やエフェクト名ではなく「どこへ、どの状態で、どの程度接触したか」のフレームである。

`contact-gesture.schema.json` が機械可読の境界、`acceptance-tests.md` が破綻を防ぐ検査条件である。

## 接触状態

| phase | 意味 |
|---|---|
| `contact` | 画面へ触れ、対象が確定した |
| `press` | 利用可能な圧力または接触面積の変化が成立した |
| `slide` | 接触を保ったまま位置が移動した |
| `release` | 接触が終了した |
| `cancel` | OS、向き変更、入力喪失などでgestureが中断した |

iPhoneの通常タッチでは接触前の `approach` を観測できないため、必須phaseにしない。

## 正規化座標

- `x`, `y`: 主演奏面内の0〜1。画面ピクセルでは保存しない。
- `contactArea`: 対象面に対する正規化接触面積。取得不能なら `null`。
- `pressure`: 0〜1。ハードウェア値が無ければ `null` とし、推定値を実測値として偽装しない。
- `pressureSource`: `hardware | estimated | unavailable`。推定方式は本研究では固定しない。
- `trackIds`: 0始まりの `0..3`。複数トラックへの接触を許すが、空配列は許さない。
- `timestampMs`: 同一Performance Take内の単調増加時刻。

## Sound Lab側が決めるもの

本bridgeは次を固定しない。

- x/yを周波数、再生位置、帯域、別の素材座標のどれへ割り当てるか
- pressure/contactAreaをCut、Feedback、圧縮、歪み、粒子密度のどれへ割り当てるか
- Skulpturの具体DSP
- 画面構成、縦横配置、色、アニメーション表現
- `estimated` pressureの推定方式
- 触覚フィードバックの種類

これらはSkulptur研究とiPhone実機検証の後に決める。

## 非採用

- KAOSS型XYパッドとしての再解釈
- 指の下で光だけが動き、音または制御イベントが変化しない演出
- 見た目を滑らかにするための接触範囲の無断拡縮
- 画像研究の顔、髪、身体、衣服表現をSound Lab UIへ持ち込むこと
- pressureが取得不能な端末で、架空のhardware pressureを生成すること

## Field Looperへの扱い

- [x] 研究記録
- [x] 機械可読な接触入力候補
- [x] 検証条件
- [ ] Skulptur具体mapping
- [ ] 製品コード統合
- [ ] ブラウザruntime
- [ ] iPhone実機
- [ ] 音響・聴感採用

## 触る実装パス

なし。今回は研究bridgeと統合島からのlocatorだけを追加する。

## 依存する研究

- Sound Lab統合正本: `integration/`
- Skulptur専用研究: `coverage-gap`
- UI状態分離研究: open PR #28（研究候補。統合済みとは扱わない）
- 画像接触研究のGit正本: `coverage-gap`

## 失効した判断

なし。D-003のKAOSS中心案はすでにD-007／D-008で失効しており、本bridgeはそれを復活させない。

## 未検証事項

- Mobile Safariが返す接触面積・forceの端末差
- マルチタッチ時の4トラック所有権
- 音響イベントと描画イベントの時刻同期
- release時の平滑化と音飛び
- Performance Takeへの記録形式
- 縦横切替、バックグラウンド化、割込み時のcancel
- 実際のSkulptur mappingが人間に演奏可能か
