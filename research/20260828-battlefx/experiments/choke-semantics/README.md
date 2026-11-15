# Choke semantics offline lab

BattleFXの内部実装を推定する前段として、同じdelay networkへ四つのchoke位置を置き、音響的な識別指標を作る独立実験。

## 実行

```bash
node choke_lab.mjs
```

Node.js標準機能だけを使う。実行すると`output/`へ、各方式の`tail-only`と`with-probe`、計8本の48 kHz / mono / PCM16 WAVと`results.json`を生成する。

## 分類器

```bash
node choke_classifier.mjs \
  --tail-only output/output-gate-tail-only.wav \
  --with-probe output/output-gate.wav \
  --choke-start 0.957 \
  --choke-end 1.557 \
  --probe-time 1.170 \
  --delay-ms 100
```

実機でも同じ演奏を二回録る。

1. choke前の励起だけを入れる`tail-only`
2. 同条件へchoke中の短いprobeを加える`with-probe`

分類器は二録音の差から新規入力受理を取り出し、`OUTPUT_GATE / FEEDBACK_CUT / BUFFER_CLEAR / INPUT_CHOKE / UNKNOWN`のいずれかを返す。単一方式へ一致しない結果、録音ずれ、複合方式は`UNKNOWN`として人間の確認へ残す。

```bash
node self_test.mjs
```

自己試験は四つの既知model、probe欠落時の`UNKNOWN`、sample-rate不一致と短すぎる録音の拒否を確認する。結果は`output/classifier-self-test.json`へ保存する。

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
- 分類結果だけでBattleFX仕様を確定しない。実機録音、操作条件、versionを同じrunへ残す。
- Field Looper製品コードとUIは変更しない。
