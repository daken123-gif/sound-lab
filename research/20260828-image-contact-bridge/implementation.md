# ContactGestureFrame 実行可能入力境界

- 状態: `candidate` / `implemented-unverified`
- 対象: 画像接触研究とSkulptur入力mappingの間
- 製品UI・DSP接続: なし
- iPhone／Mobile Safari検証: 未実施

## 実装

`contact-gesture.mjs` は外部依存のない参照実装で、次の二段階を分離する。

1. `normalizeContactGestureFrame(input)`
   - JSON Schemaと同じ必須field、範囲、列挙値、追加field禁止を検査する。
   - `trackIds` を昇順へ正規化し、元入力は変更しない。
   - 値のclamp、pressureの捏造、未知fieldの黙認をしない。
   - 戻り値と `trackIds` はfreezeする。
2. `ContactGestureGate.accept(input)`
   - 各 `gestureId + pointerId` の列が `contact` から始まることを検査する。
   - `press / slide / release / cancel` の因果を検査する。
   - 同じgesture内で `timestampMs` が後戻りする入力を拒否する。同時刻は許す。
   - `release / cancel` 後の再開を拒否する。pointer IDを再利用する側は `clear()` で明示的に閉じた列を破棄する。

この層は `trackIds` の所有権をフレームごとに明示させるが、複数トラックをmasterへ変換しない。x/y、pressure、contactAreaを音響parameterへ割り当てるfieldも受け付けない。

## 実行

```sh
node --test research/20260828-image-contact-bridge/contact-gesture.test.mjs
```

## 2026-08-28 Node検証

- tests: 11
- pass: 11
- fail: 0
- 検証対象:
  - track ownershipの正規化、空／重複／範囲外の拒否
  - hardware／estimated／unavailable pressureの由来整合
  - 0〜1範囲と有限数
  - 未知fieldの拒否
  - contact起点、許可phase遷移、terminal後の再開拒否
  - timestamp後戻り拒否
  - 複数pointerの独立状態

Node上の単体検証は、ブラウザevent adapter、描画同期、音響制御、Performance Take、Mobile Safari、iPhone実機の動作証拠ではない。

## 次のゲート

Pointer Event adapterの純粋層とlistener接続は `pointer-adapter.md` まで実装した。次は実ブラウザでPointer Eventsを発火させ、取得不能pressureが `unavailable + null` になること、`pointercancel`、capture喪失、画面向き変更が `cancel` になることを確認する。Skulpturの具体mappingはその後も別判断とする。
