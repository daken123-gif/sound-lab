# 接触因果場 simulation-v0

## 目的

`sound-lab.contact-gesture/v0.1` のpointer event列から、接触claim、可聴node、関係edge、直接操作に由来するaudio event、pocketの状態を決定的に生成する研究用シミュレーター。

音源、DSP、UI、完成フレーズ生成は含まない。製品実装ではない。

## 実行

```bash
node --test contact-causal-field.test.mjs
```

## v0で確認すること

- 1、3、5接触を同じ規則で受理し、三接触を上限にしない。
- node数に対してedgeを `n - 1` に抑え、全接触ペアの総当たりにしない。
- 同じ入力列から同じ状態、描画対象、audio event列を返す。
- release後に新しい演奏eventを自走生成せず、残存energyが有限時間でゼロになる。
- CUT後の再接触が新しい完成loopを始めず、無音化した同じnodeを現在状態へREVEALする。
- pressure取得不能時に架空値を使わない。
- timestamp逆行を拒否する。

## この試作で露出したschema不足

現行 `ContactGestureFrame` はpointer、phase、track、座標、速度を保持するが、接触が `node | edge | empty` のどれを狙ったかを明示しない。

v0は座標から既存nodeへのhitを決定し、新規nodeを最も近い可聴nodeへ接続する。これはシミュレーションを進めるための暫定規則であり、演奏面の最終mappingではない。特にedgeを直接claimする入力はまだ表現できない。

次段階では、描画と音響が別々にhit testしないよう、一度だけ解決した `targetKind` と `targetId` を受理eventへ付加するadapter出力を検討する。現行schemaそのものはこの研究で変更しない。

## 演奏責任の境界

- `contact`、`press`、`slide`だけがenergyを供給する。
- active contactは直接的な持続を保てるが、無接触から新しいphraseを生成しない。
- `release`後に認めるのは有限tailと、その終了eventだけである。
- cut、濁り、空白、broken状態は自動undoしない。
- 5接触の受理は、iPhone実機で5接触が実用的に演奏できる証明ではない。

