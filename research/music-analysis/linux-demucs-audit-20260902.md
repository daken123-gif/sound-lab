# 標準Demucs Linux CPU独立分離監査

状態: **20件の分離・固定解析・再実行一致まで検証済み**

## 実行文脈

- 会話端末: iPhoneアプリ（ユーザー申告および現在コンテキスト）
- ツール実行環境: サーバーLinux x86_64
- Macローカル接続: 未確認
- 今回の実行: Macを使わず、サーバーLinux上で実施

会話端末、ツール実行環境、ローカル接続状態を別の軸として扱う。今回の結果はiPhone上で計算したものではなく、iPhoneからの会話中にサーバーLinuxで実行した結果である。

## 固定条件

- 入力: `curtis-blind20-v1` のB01〜B20
- 同一性: Apple Previewを再取得し、manifestのSHA-256と20/20一致
- separator: official `demucs 4.0.1`
- model: `htdemucs`
- device: PyTorch 2.8.0 CPU
- stems: `--two-stems drums`
- shifts: 1
- seed: 0（Python、NumPy、PyTorchをwrapper起動時に固定）
- overlap: 0.25
- 変換: `ffmpeg`、44.1 kHz、stereo、16-bit PCM WAV
- 特徴抽出と判定: 既存の`phase_features`と固定済み閾値

## 実行環境固有の互換処理

このサーバー容器では`/proc/cpuinfo`を参照できず、PyTorchが公式Demucs checkpointを通常のコピー経路で読み込む際に停止した。`demucs_cpuinfo_compat.py`は、checkpoint内のfloat16 tensorをNumPyでfloat32へ変換し、`load_state_dict(assign=True)`で割り当てる。また、公式CLIにseed引数がないため、wrapper起動時にPython、NumPy、PyTorchのseedを0へ固定する。

この処理はモデル構造、checkpoint、入力、`htdemucs`推論条件を変更しない。ただし通常の公式loaderとはweight読込経路が異なるため、環境差の注記を残す。Macの`demucs-mlx`監査を置き換えるのではなく、別実装・別実行環境の証拠として扱う。

## 検証

- PreviewのSHA-256: 20/20一致
- Demucs drum stem: 20/20生成
- stem形式: 20/20が44.1 kHz stereo
- 分離再実行: B01を同じseedで再分離し、drum stem SHA-256が二回とも`03479a3b17d2b1e2b386a3866e83987e7faa9d792457dbcad837b73a2aac62ca`
- 固定解析: 同じ20 stemから二回実行
- JSON SHA-256: 二回とも`ea228890815483707d4d56aab359df3b731483595e0f2abbbfea647a920e3387`
- `run_linux_demucs_audit.sh`: shell構文検査に合格。構成処理は今回個別に実行したが、作成後のランナー全体を新規環境で一命令再実行する検査は未実施

## 結果

| Demucs判定 | 件数 |
|---|---:|
| stable intermediate | 14 |
| rejected | 2 |
| concentrated non-triplet reproduced | 4 |
| triplet spacing reproduced | 0 |

MDX A/B合意判定との完全一致は15/20だった。

| ID | 曲名 | 標準Demucs | MDX合意 |
|---|---|---|---|
| B06 | Just a Little Bit of Love | concentrated non-triplet reproduced | stable intermediate |
| B10 | Something to Believe In | concentrated non-triplet reproduced | stable intermediate |
| B14 | Make Me Belive In You | concentrated non-triplet reproduced | stable intermediate |
| B16 | Right On for the Darkness | stable intermediate | rejected |
| B17 | We Got to Have Peace | stable intermediate | rejected |

一致した15件のうち、B09 `Billy Jack`はMDX合意と標準Demucsの両方で`concentrated non-triplet reproduced`だった。標準Demucsでは全体BPM 141.88、beat confidence 3.566、triplet spacing score 0.023、phase entropy 0.459だった。10秒窓BPMも140.78 / 140.24 / 142.58で安定していた。

seed未固定で先行実行した20件では、B16が`rejected`、B19が`concentrated non-triplet reproduced`だった。seed 0固定後は両方とも`stable intermediate`へ変わった。MDXとの一致総数はどちらも15/20だが、境界事例のカテゴリは`shifts=1`のランダム移動に感応した。このため、単回分離の15/20一致をそのままモデル間再現率とは呼ばない。

## 読み方

`Billy Jack`の集中した非三連系打点は、MDX系列だけに固有のartifactでは説明しにくくなった。少なくとも30秒Preview、推定drum stem、固定したonset-spacing規則という範囲では、別アーキテクチャでも再現した。

一方、標準Demucsだけが追加で3件を極端判定したため、`concentrated non-triplet reproduced`全般を確定特徴へ昇格しない。B16とB17はMDXで棄却、標準Demucsで安定中間となった。同じ`We Got to Have Peace`という曲名のB05とB17は別release IDであり、曲名一致を同一音声の証明には使わない。

blind20には`Sweet Exorcist`本体が含まれず、`triplet spacing reproduced`も0件だった。したがって、この監査は`Sweet Exorcist`の三連系仮説を再検証していない。

## 境界

- 正解stemがないためSDRを測っていない。
- 比較対象は推定stemから得た派生カテゴリであり、実演奏者や個別楽器の断定ではない。
- 特徴抽出器と閾値はMDX監査と共有している。
- Apple Preview開始位置は制御できず、全曲構成を代表しない。
- Mac実機の`demucs-mlx`分離は依然として未実施である。

## 保存物

- `demucs-results-linux-cpu.json` — 全20件の測定値と比較結果
- `demucs_cpuinfo_compat.py` — 制限容器用の公式Demucs読込wrapper
- `run_linux_demucs_audit.sh` — 取得、照合、変換、分離、二重解析の再現ランナー
