# 標準Demucs seed感度監査

状態: **7曲 × 5 seed、計35分離を実行し、二重集計一致まで検証済み**

## 問い

`htdemucs --shifts 1`はランダムな時間移動を使う。単一seedで得たカテゴリを曲の安定した特徴として扱えるかを検査するため、前回の監査でモデル間不一致またはseed感度が見つかった7曲をseed 0〜4で再分離した。

これは4400万曲規模の学習ではない。固定した少数標本に対し、推定stemと凍結済み判定規則の再現性を先に測る監査である。

## 実行文脈と固定条件

- 会話端末: iPhoneアプリ
- ツール実行環境: サーバーLinux x86_64
- Macローカル接続: 未確認・未使用
- 入力: `curtis-blind20-v1`から事前理由で選んだB06、B09、B10、B14、B16、B17、B19
- Preview同一性: 7/7でmanifestのSHA-256と一致
- separator: official `demucs 4.0.1` / `htdemucs`
- device: PyTorch 2.8.0 CPU
- stems: `--two-stems drums`
- shifts: 1
- seeds: 0、1、2、3、4（Python、NumPy、PyTorchを各runで固定）
- overlap: 0.25
- 入力変換: 44.1 kHz、stereo、16-bit PCM WAV
- 特徴抽出・閾値: 前回監査から変更なし

## パネル選択理由

| ID | 選択理由 |
|---|---|
| B09 | Billy Jack。MDXとseed 0 Demucsが一致した陽性対照 |
| B06 / B10 / B14 | seed 0 Demucsのみが極端判定 |
| B16 / B17 | MDXは棄却、seed 0 Demucsはstable intermediate |
| B19 | seed未固定runとseed 0でカテゴリが変化 |

結果を見てから都合のよい曲を追加したパネルではない。ただしblind20全体の無作為なseed感度推定ではなく、問題例へ意図的に濃縮した診断パネルである。

## 結果

| ID | 曲名 | seed 0〜4のカテゴリ件数 | 全seed一致 | MDXとの関係 |
|---|---|---|---|---|
| B06 | Just a Little Bit of Love | concentrated non-triplet 5 | Yes | Demucs多数と不一致 |
| B09 | Billy Jack | concentrated non-triplet 5 | Yes | 一致 |
| B10 | Something to Believe In | concentrated non-triplet 5 | Yes | Demucs多数と不一致 |
| B14 | Make Me Belive In You | concentrated non-triplet 3 / stable intermediate 2 | No | 境界で揺れる |
| B16 | Right On for the Darkness | stable intermediate 4 / rejected 1 | No | seed 2のみMDXと同じ棄却 |
| B17 | We Got to Have Peace | stable intermediate 5 | Yes | Demucs多数と不一致 |
| B19 | We the People Who Are Darker Than Blue | stable intermediate 3 / concentrated non-triplet 2 | No | 多数カテゴリはMDXと一致 |

7曲中4曲は5 seedでカテゴリが一致し、3曲は一致しなかった。

### 安定して残ったもの

- **B09 Billy Jack**は5/5で`concentrated_non_triplet_reproduced`だった。stemのバイト列はseedごとに異なるが、カテゴリは維持された。MDX A/B合意とDemucs 5 seedが同じ方向を示すため、現標本内では最も頑健な再現例である。
- B06とB10も5/5で極端判定だった。ただしMDX合意は`stable_intermediate`なので、曲の確定特徴ではなくseparator系列間の不一致として保持する。
- B17は5/5で`stable_intermediate`だったが、MDXでは棄却された。これはDemucs内のseed安定性が異なるseparatorとの一致を保証しない例である。

### 境界で揺れたもの

- **B14**はphase entropyがseed 2で0.497、seed 3・4で0.502となり、固定閾値0.5の両側へ移動した。カテゴリ差は大きな音楽的断絶ではなく、閾値近傍の小差が離散ラベルへ増幅されたものと読む。
- **B16**はseed 2だけ10秒窓BPMが不安定となり棄却された。他4 seedはstable intermediateだった。
- **B19**はseed 2・3だけ極端判定、seed 0・1・4はstable intermediateだった。full-excerpt値だけでなく「3窓中2窓」の条件がカテゴリを分けた。

## 決定性検査

- 同じ35 stemから結果JSONを二回生成し、両方のSHA-256は`378081c7560db7009d09964a7d79475401f214f77afeeb79cb9c9943430d3049`で一致した。
- B09をseed 0・同一入力・同一条件で再分離し、既存stemと再実行stemのSHA-256は双方`67accbc03a536ea797b64df7aa86241d93ff652022770edf8ccb99280ceea83d`だった。
- seed間ではstem SHA-256が異なる。したがって、観測した差は同一seedの非決定性ではなく、意図的に変更したrandom shiftへ対応している。

## 採用判断

1. 今後`shifts > 0`のDemucs由来カテゴリは、単一seedで確定しない。
2. 極端判定を主張する場合は最低5 seedを使い、5/5一致を「seed-stable」、3〜4/5を「majority only」、2/5以下を「unstable」と記録する。
3. 閾値との差も併記する。B14のような0.497対0.502を別種のグルーヴとして文章化しない。
4. 同一separator内の5 seedは独立モデル5個ではない。証拠数を5倍に数えない。
5. B09は研究継続候補へ残すが、全曲、演奏者、意図、楽器奏法の断定には進まない。

## 境界

- 7曲は問題例へ濃縮した診断パネルで、blind20全体のseed不安定率を推定しない。
- 正解stemがないためSDRを測っていない。
- 30秒Previewであり全曲を代表しない。
- feature extractorと閾値はMDX監査と共有している。
- Linux公式Demucsの結果であり、Mac実機`demucs-mlx`は依然として未実施である。

## 保存物

- `demucs-seed-sensitivity-20260903.json` — 35 stemのSHA-256、全特徴、窓特徴、カテゴリ、集計
- `demucs_seed_sensitivity.py` — 複数seed集計器
- `run_demucs_seed_sensitivity.sh` — 取得、照合、変換、35分離、二重集計の再現ランナー
- `demucs_cpuinfo_compat.py` — `SOUND_LAB_DEMUCS_SEED`でseedを指定可能な制限容器用wrapper
