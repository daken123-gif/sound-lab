# Pointer Event → ContactGestureFrame adapter

- 状態: `candidate` / `implemented-unverified`
- 対象: ブラウザ入力eventから研究bridgeへの変換
- 製品UI・DSP接続: なし
- ブラウザ／iPhone実行: 未実施

## 変換

`pointer-contact-adapter.mjs` は次を行う。

| ブラウザ入力 | bridge phase |
|---|---|
| `pointerdown` | `contact` |
| 位置が変わった `pointermove` | `slide` |
| 位置は同じでpressure／contactAreaが変わった `pointermove` | `press` |
| `pointerup` | `release` |
| `pointercancel` | `cancel` |
| active中の `lostpointercapture` | `cancel` |
| `blur` / `pagehide` / `orientationchange` | active pointerをすべて `cancel` |

座標は対象surfaceの `getBoundingClientRect()` から0〜1へ正規化する。surface外の値は境界へ丸めず拒否する。`trackIds` は画面構成を推定せず、呼出側の `resolveTrackIds` が毎frame明示する。

## pressureの証拠境界

Pointer Events Level 3では、pressure非対応のhardware／platformでもactive buttons state中の `pressure` は `0.5` と規定されている。このためadapterは `event.pressure === 0.5` をhardware測定と判定しない。

既定値は常に次である。

```js
{ pressure: null, pressureSource: "unavailable" }
```

hardwareまたは推定値を使う場合だけ、呼出側が `pressureResolver` を明示的に渡す。adapterはその戻り値を既存の`ContactGestureFrame`検査へ通す。

contact geometryも未対応時にwidth／heightが各1 CSS pixelとなる仕様なので、既定の `contactArea` は `null` とする。実機で由来を確認するまで自動推定しない。

## pointer中断

Pointer Events Level 3は、入力streamを継続できないとき `pointercancel` を発火し、画面向き変更もstream抑制理由になり得るとしている。adapterは実際の `pointercancel` に加え、`lostpointercapture` とglobal interruptionを明示的な `cancel` frameへ変換する。

通常の `pointerup` 後にpointer captureが解放されても、そのpointerはすでにactive集合から外れているため、後続の `lostpointercapture` で偽のcancelを追加しない。

## 実行

```sh
node --test \
  research/20260828-image-contact-bridge/contact-gesture.test.mjs \
  research/20260828-image-contact-bridge/pointer-contact-adapter.test.mjs
```

## 2026-08-28 Node検証

- 全体: 25/25成功
- 既存ContactGesture検査: 11
- Pointer adapter検査: 14
- 検証したもの:
  - surface座標の正規化と明示的track所有権
  - pressure `0.5`をhardware扱いしない既定動作
  - 明示resolverによるhardware／estimated pressure
  - slide速度とpress判定
  - 無変化moveの抑制
  - release、cancel、capture喪失、global interruption
  - pointer ID再利用時のgesture ID分離
  - surface外座標とtimestamp後戻りの拒否
  - listener接続、pointer capture要求、dispose

## 未検証

- 実ブラウザでPointer Eventsが発火すること
- Mobile Safariのevent順序とpressure／width／height
- `setPointerCapture()`の成功可否
- orientation変更時の実event順序
- UI上のtrack hit test
- 描画、音響制御、Performance Takeとの同期
- iPhone実機の同時pointer数、遅延、発熱

## 一次仕様

- W3C Pointer Events Level 3: https://www.w3.org/TR/pointerevents3/
- pressure非対応時の既定値: 同仕様 §4.1 `pressure`
- stream抑制とorientation: 同仕様 §4.1.3.3
- `pointercancel`: 同仕様 §4.2.7
- pointer capture: 同仕様 §9
