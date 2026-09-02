# 音源取得・解析方式の校正記録

最終更新: 2026-09-02 UTC

## 目的

音楽について既存の批評やメタデータを言い換えるのではなく、取得した音そのものから何を測定でき、何を測定できないかを先に固定する。人間にCDリッピング、区間指定、特徴の書き起こしを押し付けない取得経路も同時に検証する。

## 証拠層

解析結果は次の層を混同しない。

1. **取得・同定** — Apple Music Previewなどから得た音源と曲ID
2. **信号測定** — RMS、スペクトル、オンセット、周期候補など
3. **アルゴリズム推定** — BPM、調、音源分離結果など
4. **解釈** — 複数の測定値から導いた音楽的仮説
5. **外部資料** — 本人発言、クレジット、論文、批評
6. **反証・矛盾** — 区間差、別アルゴリズム差、校正失敗

表示語は `測定` / `推定` / `解釈` / `外部資料` / `不明` を使う。

## 取得実験

- Apple Music Catalog APIの30秒Previewを使い、Curtis Mayfieldの100曲を自動取得した。
- 合計は約50分、約106MB。全件をAAC 44.1kHz stereo、約30秒、非無音として検査した。
- ChatGPT Workの週間表示は実験前後とも残り93%だった。表示が整数丸めのため、消費ゼロとは断定しない。少なくとも表示上の1ポイント未満だった。
- 100曲は100回のShazamではない。アルバム単位のカタログ取得とローカル処理が中心である。
- Previewの開始位置は不明。局所的なグルーヴ、音色、密度には使えるが、全曲構成、長期展開、意図の断定には使わない。

## 基本解析の校正

合成信号12ケースを使い、最低限の解析器を検査した。

- 440Hz主周波数
- スペクトル重心
- ノイズを音高と誤認しない信頼度
- RMS dBFS
- 無音開始の棄却
- 120 BPMの等間隔パルス
- 2:1 swing
- 100→140 BPMのtempo drift
- 120+180 BPMの3:2 polyrhythm候補保持
- stereo左右差

Essentiaの全体BPM推定は、等間隔120 BPMと2:1 swingでは成功したが、3:2 polyrhythmでは約184.6 BPMだけを選び120 BPM層を落とした。100→140 BPM driftは約104.6 BPMへ平坦化した。このため、単一の全体BPMを事実として扱わない。

## 20 Preview監査

Curtis Mayfieldの決定的に選んだ20 Previewで、10秒窓3個を比較した。

| 判定 | 件数 | 比率 |
|---|---:|---:|
| BPMが3窓で安定 | 15/20 | 75% |
| BPMが不安定 | 5/20 | 25% |
| 調が3窓で一致 | 5/20 | 25% |
| 調が2/3窓のみ一致 | 11/20 | 55% |
| 調が不安定 | 4/20 | 20% |

この標本では、無条件の出力ならBPMの4分の1、調の4分の3を過大断定する。調は全窓一致時だけ採用する。

## Billy Jack / Sweet Exorcist

### 分離前の全ミックス

| 曲 | BPM推定 | 安定性 | 打点位相の観測 |
|---|---:|---|---|
| Billy Jack | 約141 | 3窓で安定 | 二分系の間隔へ集中。後半ほど拡散 |
| Sweet Exorcist | 約111 | 3窓で安定 | 三連系の間隔が優勢で、全体に拡散 |

位相間隔は回転不変に測った。したがって、検証済みdownbeat anchorなしに「裏拍」「シンコペーション」とは呼ばない。

## 音源分離の校正

### 実装

- `audio-separator 0.47.0`
- `torch 2.8.0+cpu`
- `torchvision 0.23.0+cpu`
- `onnxruntime 1.29.0`
- MDX `kuielab_b_drums.onnx` / `kuielab_b_bass.onnx`
- モデル合計50MB、CPU環境のみ

通常の `audio-separator[cpu]` 依存解決は、LinuxでCUDA版PyTorchとCUDA一式を取得し始めたため停止した。CPU専用PyTorch indexを明示し、必要依存だけを固定した。

### 既知ステム人工混合による方向検査

30秒のdrums / bass / otherを個別生成し、真値ステムを保持したまま混合した。これは実録音品質のベンチマークではなく、対象を取り違えないかのsanity checkである。

| 推定対象 | 真値とのcosine | 非対象との最大cosine | SI-SDR |
|---|---:|---:|---:|
| drums | 0.9237 | 0.0138 | 7.644 dB |
| bass | 0.9747 | 0.0288 | 12.790 dB |

混合再構成のRMS残差はdrums分離0.00490、bass分離0.00607でゼロではない。分離後の音を本物のmultitrackとして扱わない。

### 2曲への適用

| 曲・推定stem | BPM | beat confidence | onset/s | 位相entropy | 二分間隔 | 三連間隔 | 判定 |
|---|---:|---:|---:|---:|---:|---:|---|
| Billy Jack drums | 141.78 | 3.589 | 2.969 | 0.333 | 0.143 | 0.016 | 3窓で約140–142 BPM、打点が集中 |
| Billy Jack bass | 139.97 | 0.368 | 1.168 | 0.916 | 0.846 | 0.677 | 全体信頼度が低く、窓BPMも129–141。棄却 |
| Sweet Exorcist drums | 111.63 | 3.524 | 4.243 | 0.698 | 0.142 | 0.715 | 3窓の三連間隔が0.625→0.684→0.747 |
| Sweet Exorcist bass | 111.27 | 1.760 | 1.871 | 0.774 | 0.239 | 0.662 | 窓BPMが75/112/110、窓三連値も不一致。棄却 |

### 現時点の解釈

両曲とも安定したpulseと非一様な内部運動を持つように聞こえるが、同じ機構ではない可能性が高い。

- **Billy Jack** — 推定ドラム自体は約141 BPMの集中した打点。全ミックスで見えた二分系の細かな運動は、ドラムだけでなくギター、声、その他の層間関係から増えている可能性がある。
- **Sweet Exorcist** — 約111 BPMの推定ドラム内に三連系の間隔が3窓連続で残る。少なくともPreview区間では、liltの一部がドラム層に存在するという仮説を支持する。

これは演奏者、個別楽器、意図、全曲構造の断定ではない。分離モデル由来のbleedやartifactという競合仮説を残す。

## 採用規則

- BPMは複数候補と窓推移を保持する。
- 調は全窓一致時だけ採用する。
- 位相特徴はbeat confidence 1.5以上かつ窓間に重大矛盾がない場合だけ解釈する。
- source separationは二次証拠であり、元ミックス測定より権威を上げない。
- 演奏者・楽器・意図は信号だけから断定しない。
- Previewから全曲構成を断定しない。
- 同一ライブラリ内の複数方式は、完全に独立した再現とは数えない。

## 20資産・事後復号ブラインド監査

既存100 PreviewからSHA-256順位で20資産を決定論的に固定し、B01〜B20だけをMDX A/Bドラムモデルへ渡した。曲名を結合する前に、beat confidence、3窓BPM安定性、A/B BPM一致を信頼性ゲートとして適用した。

| 判定 | 件数 |
|---|---:|
| stable intermediate | 15 |
| rejected | 4 |
| concentrated non-triplet reproduced | 1 |
| triplet spacing reproduced | 0 |

事後復号すると、唯一の`concentrated non-triplet reproduced`はBilly Jackだった。A/B BPMは141.14/141.78、triplet scoreは0.005/0.016で、各モデルの3窓条件も通過した。All Night Longはfull triplet scoreが0.808/0.845だったが区間BPM不安定のため棄却した。

この20資産は曲名文字列で19種であり、`We Got to Have Peace`が別リリースIDで2件含まれる。Sweet Exorcist本体は無作為標本に入っていない。詳細は`blind20-audit-20260902.md`を参照する。

## 主要な外部資料

- Demucs README: https://github.com/facebookresearch/demucs — Meta版はarchive済みで、作者は非保守・forkも重要修正のみと明記。
- python-audio-separator: https://github.com/nomadkaraoke/python-audio-separator
- MLX Audio Separator: https://github.com/ssmall256/mlx-audio-separator — Apple Silicon用。Mac実機候補であり、今回のLinux試験には未使用。
- Essentia: https://essentia.upf.edu/

## Mac実機の独立分離監査

MDXの共有バイアスを検査するため、固定済みB01〜B20を`demucs-mlx`の`htdemucs`で再分離するMac用ランナーを作成した。Apple Previewの再取得、SHA-256照合、`afconvert`、分離、固定ルールによる再解析までを自動化する。

現時点ではランナー作成、構文検査、20 Previewの再取得・SHA-256一致、既存stemを使った比較器の決定性検査まで完了した。Mac実機の`demucs-mlx`分離と`afconvert`は未実施。実行条件と独立性の範囲は`mac-demucs-protocol.md`に記録する。

## 標準Demucs Linux CPU独立分離監査

Mac接続を待たず、サーバーLinux上でofficial `demucs 4.0.1`の`htdemucs`を使い、固定済みB01〜B20を再分離した。20 Previewは元manifestのSHA-256と全件一致し、20 drum stemを44.1 kHz stereoで生成した。

Python、NumPy、PyTorchのseedを0へ固定した。固定解析は同じstemから二回実行し、JSON SHA-256が二回とも`ea228890815483707d4d56aab359df3b731483595e0f2abbbfea647a920e3387`で一致した。B01の分離も同じseedで再実行し、drum stemのSHA-256が一致した。MDX A/B合意判定との完全一致は15/20。`Billy Jack`は両方式で`concentrated non-triplet reproduced`となった。標準Demucsのみが極端判定した3件と、MDXで棄却・Demucsで安定中間となった2件は不一致として保持する。

この結果はMacの`demucs-mlx`実機試験ではない。分離アーキテクチャの独立性は増したが、特徴抽出器と閾値は共有している。詳細は`linux-demucs-audit-20260902.md`を参照する。

## ファイル

- `calibrate_analyzer.py` — 合成信号による基礎校正
- `analyze_previews.py` — Preview測定
- `essentia_compare.py` — Essentia比較
- `reliability_audit.py` — 20曲の窓安定性監査
- `phase_analysis.py` — 回転不変の打点位相間隔
- `make_separation_fixture.py` — 既知ステムfixture生成
- `evaluate_separation.py` — fixture分離の数値検査
- `stem_window_audit.py` — 分離stemの窓監査
- `separation-fixture-results.json` — fixture結果
- `stem-window-results.json` — 2曲のstem結果
- `prepare_blind20.py` / `blind20-manifest.json` — 盲検標本の固定と由来
- `blind20_audit.py` / `blind20-results-blinded.json` — 復号前解析
- `blind20-title-map.json` / `decode_blind20.py` / `blind20-results-decoded.json` — 事後復号
- `blind20-audit-20260902.md` — 結果、限界、次の検証
- `download_blind20_previews.py` — Apple Preview再取得とSHA-256照合
- `run_mac_demucs_audit.sh` — Mac実機の取得・変換・Demucs分離・解析ランナー
- `demucs_blind20_audit.py` — Demucs結果とMDX合意結果の比較
- `mac-demucs-protocol.md` — 固定条件、独立性、未実施境界
- `run_linux_demucs_audit.sh` — Linux CPUでの取得・変換・標準Demucs分離・解析ランナー
- `demucs_cpuinfo_compat.py` — `/proc/cpuinfo`を参照できない制限容器用wrapper
- `demucs-results-linux-cpu.json` — 標準Demucsによる全20件の測定結果
- `linux-demucs-audit-20260902.md` — 実行証拠、MDXとの一致・不一致、解釈境界

音源本体、Preview、モデル、仮想環境、分離WAVはGitへ保存しない。
