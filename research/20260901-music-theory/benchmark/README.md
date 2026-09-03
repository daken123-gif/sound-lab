# B層・合成反証ベンチマーク

単一のBPM、拍子、境界、音源分離結果を正解として固定する解析器を検出するための、再生成可能な合成音源群。

## 生成

```bash
cd research/20260901-music-theory/benchmark
python3 generate_synthetic_benchmark.py
```

`generated/`にS01〜S12の48 kHz／16-bit／stereo WAVと`ground-truth.json`を生成する。WAVは検証入力であり、正本は生成器と正解JSONの生成規則である。

## 検査

```bash
cd research/20260901-music-theory/benchmark
python3 -m unittest -v test_synthetic_benchmark.py
```

## 音声解析の最小基準線

```bash
cd research/20260901-music-theory/benchmark
python3 baseline_analyzer.py generated/s01.wav generated/s02.wav
python3 -m unittest -v test_baseline_analyzer.py
```

`baseline_analyzer.py`は音声だけを入力し、複数の周期候補、位相、左右チャンネル別周期、低域のtempo curve、高域と低域の発音残差を返す。正解JSONは解析時に読まない。

解析器だけは`numpy`と`scipy`を使用する。必要条件は`requirements.txt`に記録した。合成音源生成器はPython標準ライブラリだけで動作する。

これはS01〜S04へ答えるための最小基準線であり、周期候補のscoreは確率ではない。固定周波数帯とenergy fluxに依存し、楽器・役割・文化的意味は推定しない。

## librosa 1.0比較基準線

```bash
cd research/20260901-music-theory/benchmark
python3 -m venv --system-site-packages .venv-librosa
.venv-librosa/bin/python -m pip install -r requirements-librosa.txt
.venv-librosa/bin/python librosa_analyzer.py generated/s01.wav
.venv-librosa/bin/python -m unittest -v test_librosa_analyzer.py
```

`librosa_analyzer.py`はlibrosaのonset strength、onset detection、tempogramを使う。tempo curve、位相、周波数帯間残差の後処理は現行基準線と共有し、音響フロントエンドの差を比較する。共有処理を独立実装と偽装しないため、出力JSONにも`shared_postprocessors`を記録する。

## フロントエンド比較

```bash
.venv-librosa/bin/python compare_frontends.py \
  --audio-dir generated \
  --repeats 3 \
  --output generated/frontend-comparison.json
```

各解析器を一度ウォームアップした後、S01〜S04を反復計測する。比較対象は合否、周期候補と順位、onset数、tempo curve、周波数帯間残差、処理時間。共有後処理があるため、比較結果はシステム全体の独立再現ではなく音響フロントエンド比較として解釈する。

初回比較では周期検査だけなら合格した現行基準線が、S01の18発音中9、S02の19発音中5、S03の19発音中3しか検出していない評価漏れが判明した。onset数を合否条件へ追加し、ゼロ値の多いsparse envelopeに固定prominenceを使わないよう修正した。古い周期合格をイベント観測の成功として扱わない。

実測結果と判断は[frontend-comparison.md](frontend-comparison.md)に記録した。

## 周期関係グラフ

```bash
.venv-librosa/bin/python relational_fusion.py \
  generated/s01.wav generated/s02.wav generated/s03.wav generated/s04.wav \
  --output generated/relational-period-graphs.json

.venv-librosa/bin/python -m unittest -v test_relational_fusion.py
```

両解析器のscoreを平均せず、近い周期候補を同定したうえで、解析器、手法、mix／channel、順位を証拠として保持する。周期間には整数倍関係を張り、`pulse_candidate`、`accent_cycle_candidate`、`recurrence_cycle_candidate`、`layer_period_candidate`、`joint_recurrence_candidate`、`time_varying_pulse_candidate`を付ける。これらは確定ラベルではなく、反証可能な役割候補である。

S01〜S04の読戻し結果と限界は[relational-graph-results.md](relational-graph-results.md)に記録した。

## 文脈証拠ストリーム

```bash
.venv-librosa/bin/python contextual_analyzer.py \
  generated/s05.wav generated/s06.wav generated/s07.wav generated/s08.wav \
  --output generated/contextual-s05-s08.json

.venv-librosa/bin/python -m unittest -v test_contextual_analyzer.py
```

S05では符号つきmicrotiming形状と偏差量を分離し、groove品質を数値から推定しない。S06ではtimbre、pitch、amplitude、rhythmの境界を別ストリームに保つ。S07ではlow／highを固定役割にせずpulse-anchorの移動を関係として表す。S08では直接音終了と減衰tail終了を別の定義と証拠で出力する。

実測値、読戻しで除去した誤判定、一般化上の限界は[contextual-results.md](contextual-results.md)に記録した。

## 拡張関係証拠

```bash
.venv-librosa/bin/python extended_evidence_analyzer.py \
  generated/s09.wav generated/s10.wav generated/s11.wav generated/s12.wav \
  --output generated/extended-s09-s12.json

.venv-librosa/bin/python -m unittest -v test_extended_evidence_analyzer.py
```

S09ではmono onset周期とstereo空間周期を分ける。S10ではonset topologyの同一性とcycleごとのdynamics変形を併存させる。S11では伸縮するcycle-local period列を中央値で置換しない。S12では混合音中のresonance候補を観測するが、kick／bassというsource identityは付与しない。

実測値と一般化上の限界は[extended-results.md](extended-results.md)に記録した。

## ケース

| ID | 反証対象 |
| --- | --- |
| S01 | half／double tempoの早期一意化 |
| S02 | ファイル先頭と周期位相の同一視 |
| S03 | 複数レイヤーの周期を単一拍子へ統合 |
| S04 | tempo curveとmicrotimingの混同 |
| S05 | タイミング偏差量とgrooveの同一視 |
| S06 | 音色だけの境界を全体境界へ変換 |
| S07 | 音域・音源と役割の固定 |
| S08 | 直接音終了と残響終了の混同 |
| S09 | モノラル化による空間周期の消失 |
| S10 | velocity変形を無視した完全反復判定 |
| S11 | 伸縮する周期の固定長化 |
| S12 | 音源分離結果を観測上の正解として扱うこと |

合成音源は実録音の代替ではない。正解を完全に制御できる第一輪として使い、公開データと実際の参照音源による第二・第三輪で一般化を検証する。

## 第二輪・公開データ受入れ

第二輪の候補、利用条件、取得状態、S01〜S12との対応は[public-data-audit.md](public-data-audit.md)と`public-dataset-manifest.json`に記録する。公式資料を確認したことと、音源を取得・解析したことを分離する。

```bash
python3 validate_public_dataset_manifest.py
python3 -m unittest -v test_public_dataset_manifest.py
```

E-GMDはmetadata＋MIDI schema、RWCは現行注釈とRWC-R音声15曲のchecksum・schema・ID結合を検証済みである。MAESTROとMUSDB18は未取得で、4候補とも全体としては`evaluation_ready: false`を維持する。

```bash
python3 public_dataset_probe.py \
  --egmd-csv /path/to/e-gmd-v1.0.0.csv \
  --egmd-midi-zip /path/to/e-gmd-v1.0.0-midi.zip \
  --rwc-root /path/to/rwc-annotations \
  --rwc-revision <commit> \
  --rwc-audio-zip /path/to/RWC-R.zip \
  --rwc-audio-md5 63e3b6263656a42c592ce1e90a88caa3

python3 rwc_period_pilot.py \
  --audio-zip /path/to/RWC-R.zip \
  --annotations-root /path/to/rwc-annotations
```

観測値は`public-data-probe-results.json`、15曲pilotの判断は[rwc-period-pilot-results.md](rwc-period-pilot-results.md)に記録する。外部音源・注釈そのものはGitへ転載しない。
