# 非可換エフェクト順序 実験1

- 対象研究: `20260828-chroma-console`
- 実行日: 2026-08-28
- 状態: 合成テスト信号によるDSPモデル検証
- 境界: Chroma Console実機の再現・測定ではない

## 問い

Chroma Console型の可変順序を採る根拠として、同じ二処理でも `Delay -> Cassette` と `Cassette -> Delay` が同一出力にならないことを、同一入力・同一RMSで確認する。

## テスト条件

- Sample Rate: 48 kHz
- Length: 4.0 s
- 入力: 110 / 220 / 330 / 880 / 1760 Hzの倍音群、周期ゲート、固定seedの減衰ノイズバースト3回
- 3.05 sから入力をフェードし、3.20 s以降を残響尾として測定
- Delay: 237 ms、既定feedback 0.67、wet 0.58
- Cassetteモデル: deterministic wow / flutter、pre-emphasis、非対称tanh飽和、6.7 kHz low-pass、低速レベル変動
- 出力: 両経路を -18 dBFS RMSへ個別に整合
- ランダム性: 入力ノイズのみ固定seed `20260828`。Cassette変動は決定論的

## 既定条件の結果

| 指標 | Delay -> Cassette | Cassette -> Delay |
|---|---:|---:|
| RMS | -18.0000 dBFS | -18.0000 dBFS |
| Peak | -8.9863 dBFS | -8.9915 dBFS |
| Crest Factor | 9.0137 dB | 9.0085 dB |
| Spectral Centroid | 167.1406 Hz | 159.1881 Hz |
| 6 kHz以上のEnergy Ratio | 0.0019575 | 0.0013093 |
| 3.20 s以降のTail RMS | -22.0112 dBFS | -22.3650 dBFS |

経路間:

- Cross Correlation: `0.9983051715`
- Difference RMS: `-42.6597475 dBFS`
- Spectral Centroid差: `+7.9525 Hz`
- 6 kHz以上のEnergy Ratio比: `1.4950`

## パラメータ掃引

| Drive | Feedback | Correlation | Difference RMS | Centroid差 | High-band比 A/B |
|---:|---:|---:|---:|---:|---:|
| 1.20 | 0.35 | 0.9995550 | -48.4970 dBFS | +5.0547 Hz | 1.2310 |
| 1.20 | 0.67 | 0.9989414 | -44.7204 dBFS | +4.5220 Hz | 1.2132 |
| 1.20 | 0.82 | 0.9977498 | -41.4386 dBFS | +5.5667 Hz | 1.2177 |
| 2.35 | 0.35 | 0.9991820 | -45.8567 dBFS | +7.9080 Hz | 1.4690 |
| 2.35 | 0.67 | 0.9983052 | -42.6597 dBFS | +7.9525 Hz | 1.4950 |
| 2.35 | 0.82 | 0.9968543 | -39.9621 dBFS | +10.5123 Hz | 1.5293 |
| 4.00 | 0.35 | 0.9982441 | -42.5434 dBFS | +9.0483 Hz | 1.7184 |
| 4.00 | 0.67 | 0.9963158 | -39.2824 dBFS | +9.4577 Hz | 1.8382 |
| 4.00 | 0.82 | 0.9936962 | -36.9471 dBFS | +13.0970 Hz | 1.9321 |

## 観測

1. 9条件すべてで相関は1.0にならず、処理順は同一結果にならなかった。
2. DriveとFeedbackを上げるほど、概ね相関が下がり、差分RMSが上がった。
3. 強条件 `Drive 4.0 / Feedback 0.82` ではDifference RMSが弱条件より約11.55 dB大きくなった。
4. `Delay -> Cassette` は全条件で6 kHz以上のエネルギー比が高く、強条件では約1.93倍になった。
5. 既定条件では相関が0.9983であり、順序差は存在するが波形全体はかなり似ている。順序変更だけで常に劇的な差になるとは判定しない。

## 解釈

`Delay -> Cassette` では、原音と複数の反復が加算された後に非線形飽和へ入る。時点ごとの合成振幅に応じて飽和量と新しい倍音が変わる。

`Cassette -> Delay` では、入力を先に一度だけ飽和・帯域制限し、その処理済み信号をDelayが反復する。このモデルでは反復同士の合成後にCassette非線形へ再入力されない。

したがって差は、DelayとCassetteという名前からではなく、**非線形処理が反復の合成前にあるか、合成後にあるか**から生まれる。

## Chroma Console研究への反映

- 可変順序は見た目の機能ではなく、非線形段と時間段の位置関係を変える音響機能として残す。
- 順序差を明確にするには、飽和量、フィードバック量、処理段への入力レベルが重要。
- 各段のEffect Volumeを単なる音量補正として固定しない。
- 初期検証は4モジュールではなく、非線形段と時間段の二つで成立する。
- UI上で全24順序をプリセット化する前に、二処理の直接交換だけで音を判断できる必要がある。

## 検証

- 同一スクリプトを二回実行
- 数値結果: 完全一致
- 3つのWAV: byte単位で一致
- Python構文検査: 成功

## 生成物

Gitへ保存するもの:

- `experiments/noncommutative_chain.py`
- `experiments/noncommutative-chain-results.md`
- `experiments/noncommutative-chain-metrics.json`

WAVは現段階ではGitへ保存しない。再生成可能であり、各ファイル約376 KiBのため、研究コードと数値だけを履歴へ残す。

ローカル生成WAVのSHA-256:

- input.wav: `a4193e8b78400dcddc01e8c880b95b43c5e5246e7a75a943825bb2200aa905ad`
- delay-then-cassette.wav: `62ed4ee351478f47a14a831e284ee9e209673bae04ab6fd92053579e0dd3d19d`
- cassette-then-delay.wav: `2542ff88935685d1ce6eaa93503bb7fb5f6ff87e033215f1a9b0faf4f82a2fed`

## 未検証

- 実機Chroma Consoleとの一致
- 人声・実楽器での知覚差
- Loudness規格に基づくLUFS整合
- CassetteをDelay feedback loop内部へ置いた場合
- ステレオDoubler／Reels／Collageとの非可換性
- リアルタイム実行時のCPU負荷とレイテンシー

