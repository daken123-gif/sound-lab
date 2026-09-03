# Deep Research監査 — onset候補・拍参照・分離証拠の境界

- research-id: `20260902-parallel-music-analysis/deep-research-onset-audit`
- date: 2026-09-03 UTC
- status: `research-only / implementation corrected / real-audio validation pending`
- 対象: `tools/export_onset_events.py`、既存`research/music-analysis`のEssentia解析、Billy Jackケース

## 結論

現行の出力器は、音楽的onsetを確定する検出器ではなく、**短時間RMSの正方向差分からenergy-rise候補を保存する透明な補助器**としてのみ妥当である。候補時刻を捨てない点には価値があるが、人手注釈との評価、楽器役割、拍・downbeat、原mix照合を経るまでは、grooveやmicrotimingの証拠へ昇格できない。

今回、名称とschemaをこの証拠レベルへ合わせ、ステレオ逆相でイベントが消える欠陥を修正した。また、参照時刻との一対一照合器を追加し、最大一致数を保証する動的計画法と評価境界を実装した。合成fixture 9件は成功した。ただしBilly Jackの実音源またはstemはこの実行環境にないため、B09イベントJSONは生成していない。

## 1. 一次資料から固定できること

### 1.1 onsetは振幅上昇だけではない

Bello et al.のtutorialはonset検出を、energy burstだけでなく、スペクトル・位相・統計的変化を含む複数の検出関数として整理している。Dixonの比較もspectral flux、weighted phase deviation、complex-domain differenceを別方式として評価している。したがってRMS上昇は一つの観測器であり、一般的なonsetの定義ではない。

- [Bello et al., A Tutorial on Onset Detection in Music Signals (2005)](https://www.eecs.qmul.ac.uk/~josh/documents/2005/Bello%20et%20al%20-%202005%20-%20A%20tutorial%20on%20onset%20detection%20in%20music%20signals.pdf)
- [Dixon, Onset Detection Revisited (2006)](https://www.eecs.qmul.ac.uk/~simond/pub/2006/dafx.pdf)

既存`research/music-analysis/phase_analysis.py`はEssentia `OnsetRate`を呼び、個別onset時刻を得ているが、現在の保存結果ではrateとphase集約だけを残し、時刻列を捨てている。Essentia公式仕様では`OnsetRate`はHFCとcomplex-domain detection functionを組み合わせ、onset位置とrateを出力する。次の本命修正は、別のRMS検出器だけを強化することではなく、**既存Essentia経路がすでに持つonset位置をprovenance付きで保存すること**である。

- [Essentia OnsetRate reference](https://essentia.upf.edu/reference/std_OnsetRate.html)

### 1.2 onset評価は一対一対応と注釈品質を必要とする

MIREX Audio Onset Detectionは、推定時刻と参照時刻を許容窓内で対応づけ、TP・FP・FNからprecision、recall、F-measureを算出する。公式説明は一部データについて注釈精度自体が50 msより良くないことも明記している。またsolo drums、pitched instruments、polyphonic、complex mixesを分け、複数人のcross-annotationを使う。

- [MIREX 2021 Audio Onset Detection](https://www.music-ir.org/mirex/wiki/2021:Audio_Onset_Detection)

ゆえに今回の`0.05 s`既定値は「50 ms以内ならmicrotimingが正しい」という意味ではない。特定注釈との一致を数える便宜的な窓であり、目的・資料精度に応じて事前固定する必要がある。楽器別・音源種別の内訳なしに総F値だけを採用しない。

### 1.3 BPMとbeat列、downbeatは別の証拠である

MIREX Beat Trackingはtempo値を返す課題ではなく、録音中の全beat位置を推定し、聴取者注釈に対して評価する。F-measureのほか、連続性指標と許容されるmetrical levelを考慮した指標がある。Essentia `RhythmExtractor2013`もBPMだけでなく`ticks`を返す。

- [MIREX 2025 Audio Beat Tracking](https://www.music-ir.org/mirex/wiki/2025:Audio_Beat_Tracking)
- [Essentia RhythmExtractor2013 reference](https://essentia.upf.edu/reference/std_RhythmExtractor2013.html)

したがって`BPM + beat origin`から作る等間隔gridはcaller-provided仮説にすぎない。tempo drift、expressive timing、half/double tempo、offbeat解釈、拍子、downbeatを確定しない。Billy Jackの次の検証では、BPM集約値ではなく完全なbeat-time列、bar/downbeat注釈、代替metrical解釈を保存する。

### 1.4 分離モデル同士の一致はground truthではない

MUSDB18はmixtureと4つのisolated stemを持つ150曲の基準データで、100 train / 50 test、stereo 44.1 kHzとして配布される。公式ページは一部のbleedingやstemsの問題もerrataとして公開し、musevalによる評価を案内している。HT Demucs論文は、MUSDBだけの学習では性能が弱く、追加データが結果を大きく左右したと報告する。

- [MUSDB18 official dataset page](https://sigsep.github.io/datasets/musdb.html)
- [Rouard et al., Hybrid Transformers for Music Source Separation](https://arxiv.org/abs/2211.08553)

このためBilly Jackで二つのMDX推定が近いことは再現性候補にはなるが、正解stemの証明ではない。各候補は原mix上で再確認し、方式比較はisolated ground truthを持つ基準データで別に評価する。

## 2. 監査結果と実装修正

| 項目 | 監査前 | 問題 | 今回の状態 |
| --- | --- | --- | --- |
| 出力名 | onset candidate | 音楽的onsetと誤読可能 | `energy-rise candidate`へ限定 |
| schema | `parallel-onset-events-v1` | detectorと評価状態が不明 | v2でframe、hop、分離能、未評価を記録 |
| stereo | channel波形平均 | 逆相信号が相殺される | channel RMSでenergy-preserving collapse |
| role | `unknown_onset` | onset確定を含意 | `unknown_energy_rise` |
| 注釈状態 | なし | candidateと確認済みを区別不能 | `unreviewed_candidate` |
| clock | BPM＋origin時のみgrid | 仮説であることが弱い | `caller-provided`を維持し、未指定はnull |
| 評価 | なし | P/R/Fを再現不能 | 最大一対一照合器を追加 |
| 照合方式 | なし | greedyは重複窓で取りこぼす | 最大一致数、同数なら総誤差最小 |

ステレオcollapseは検出用であり、レンダリングや位相解析用ではない。左右チャンネルの構造を捨てるため、将来はL/R別候補と統合候補を併記する余地がある。

## 3. 並行研究との接続

| 研究 | この監査が供給する証拠 | まだ供給しないもの |
| --- | --- | --- |
| Curtis Mayfield / Billy Jack | source固定、候補時刻、分離由来、原mix再確認欄 | BODY / VOICE / HORIZON、総ループ非形成 |
| J Dilla | clock候補ごとのoffsetを比較できる形式 | 複数clock、laid-back、swingの自動判定 |
| James Brown | beat/downbeat列が得られればOne前後の偏差曲線を作れる | 「Oneへの収束」の現時点での実証 |
| Anderson .Paak | bar間event列から不変項と変化量を分離できる | 身体的重心や前景交替の自動ラベル |
| Charlie Hunter | voice別onsetと拘束関係を同じEVENTへ格納できる | 同一身体内対位法の推定 |
| Dub | CUT / THROW / REVEALをabsolute timeへ置ける | 操作意図、dry/tail因果の自動復元 |

共通点を「ずれ」に還元せず、各研究が要求するclock、role、return、memoryの証拠を別フィールドとして保持する。候補検出器は接続面であり、個別研究の解釈器ではない。

## 4. 受入れゲート

実音源に対して次を順番に通す。

1. **G1 Stereo:** mono、同相stereo、逆相stereoでcandidate消失や時刻偏りを検査する。今回、合成逆相fixtureは通過。
2. **G2 Human reference:** 複数注釈者のreference timesを固定し、source/instrument class別にprecision、recall、F1、時刻誤差分布を出す。
3. **G3 Detector comparison:** RMS候補と既存Essentia HFC＋complex-domain onset列を同一sourceで比較し、差分を保存する。
4. **G4 Beat authority:** BPMだけでなく全beat ticks、bar/downbeat、metrical alternativesを保存する。等間隔gridは仮説のまま残す。
5. **G5 Separation:** 二つの分離結果と原mixを対応づけ、candidateごとに原mix確認を行う。基準データではground-truth stemと評価する。
6. **G6 Research claim:** event列から関係仮説へ進む際、各claimの反例・未観測層・time scopeを明示する。

## 5. 実行確認

```text
python3 -m unittest discover -s research/20260902-parallel-music-analysis/tests -v
Ran 9 tests in 0.036s
OK
```

確認済み:

- absolute timeとcaller-provided grid offset
- beat origin未指定時にclockを捏造しない
- BPMだけの半指定を拒否
- stereo逆相eventを相殺しない
- 推定と参照の一対一対応
- doubled / merged detectionの計数
- greedy反例で最大一致数を保持
- 完全一致および負のtolerance拒否

## 6. 停止理由と次の実証単位

停止理由は、Billy Jackの対象WAV／分離stemと、人手onset・beat/downbeat注釈がこの環境に存在しないためである。数値を補完せず、B09は`aggregate-only`のまま保持する。

次の実証単位は、既存`phase_analysis.py`からEssentia onset timesとbeat ticksを保存する互換変更、その出力とRMS候補の同一音源比較、そして原mix上の人手確認である。製品採用、main統合、PR作成は本報告の範囲外とする。
