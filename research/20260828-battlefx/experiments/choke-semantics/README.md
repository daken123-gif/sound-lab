# Choke semantics offline lab

BattleFXの内部実装を推定する前段として、同じdelay networkへ四つのchoke位置を置き、音響的な識別指標を作る独立実験。

## 実行

```bash
node choke_lab.mjs
```

Node.js標準機能だけを使う。実行すると`output/`へ4本の48 kHz / mono / PCM16 WAVと`results.json`を生成する。

## モデル

| mode | chokeする場所 | 解除後の予測 |
| --- | --- | --- |
| output-gate | wet output | choke中も進んだ古いtailが戻る |
| feedback-cut | feedback injection | 循環が途切れ、古いtailは戻らない |
| buffer-clear | delay memoryをchoke開始時に消去 | 古いtailは戻らず、その後の入力から再開始 |
| input-choke | network input | 古いtailは残り、choke中のprobeだけ拒否 |

入力はchoke前の励起とchoke中のprobeを持つ。測定はprobeあり／なしの二回を差分化するため、既存tailと新規入力受理を分けて観測できる。

## 境界

- BattleFX binary、実機録音、AUv3 parameterは使用していない。
- 数値はこの最小delay modelの結果であり、BattleFX固有値ではない。
- 目的は、後の実機録音をどのsemanticsへ照合するかの識別子を作ること。
- Field Looper製品コードとUIは変更しない。

