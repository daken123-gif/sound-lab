# Mac実機 Demucs-MLX 独立分離監査

状態: **ランナー作成済み・Mac実機では未実行**


## 実行文脈の三軸

ローカル実機処理の可否は、次の三つを分離して判定する。

1. **会話端末** — ユーザーが現在ChatGPTを開いている端末。セッション情報またはユーザー申告で観測し、メッセージごとに変わり得る。
2. **ツール実行環境** — Codexのコマンドが実際に動くhost OS・architecture。会話端末から推定せず、実行環境の取得結果を使う。
3. **ローカル接続状態** — 対象Macのfilesystem／repositoryが現在の実行環境から参照・実行可能か。Macアプリで会話している事実だけでは接続済みとしない。

ローカル依存工程の前には三軸を個別に表示する。取得できない軸は「不明」とし、別軸から補完しない。端末が切り替わっても、ツール実行環境やローカル接続が切り替わったとはみなさない。

### 2026-09-02の齟齬

直前の会話端末はMacアプリ、次の会話端末はiPhoneアプリだった。一方、ツール実行環境はサーバーLinuxのままで、Macローカル接続は未確認だった。会話端末と実行環境を一文に潰した報告が齟齬を生んだため、本プロトコルでは三軸を別状態として保持する。

## 現在までの検証

- Python 2ファイルの構文検査: 成功
- Shell構文検査: 成功
- Appleからの20 Preview再取得と既存SHA-256照合: 20/20一致
- 解析器の入出力経路: 既存MDX model Aのstemを検証用入力として2回実行し、JSON SHA-256一致
- `demucs-mlx`による分離、`afconvert`、Apple Silicon実行: 未実施

MDX stemによる検証値はDemucs結果ではないため保存成果には含めない。これは比較器が20件を読み、分類し、決定論的JSONを書けることだけを確認する試験である。

## 目的

MDXの別weight同士だけでは共有バイアスを除けないため、固定済みB01〜B20をHybrid Transformer Demucsで再分離する。音源取得、照合、変換、分離、解析を一つのランナーへまとめ、人間による曲選択や区間指定を挟まない。

## 固定条件

- 入力: `curtis-blind20-v1` のB01〜B20
- 同一性: AppleのPreviewを再取得し、既存manifestのSHA-256と完全一致した場合だけ使用
- 分離: `demucs-mlx 1.4.6`
- model: `htdemucs`
- shifts: 1
- seed: 0
- overlap: 0.25
- 音声変換: macOS標準`afconvert`、44.1 kHz、stereo、16-bit PCM WAV
- 特徴抽出: 既存のEssentia系`phase_features`
- 判定: MDX監査で固定したbeat confidence、3窓BPM安定性、triplet/non-triplet閾値を変更しない

## 独立性の範囲

分離器はMDXからDemucsへ変わるため、**分離アーキテクチャに対する感度**を検査できる。ただし特徴抽出器、30秒Preview、窓分割、閾値は共有している。したがって完全に独立した音楽分析ではない。

正解stemを持たない実録音なので、分離品質のSDRは計算しない。比較対象は、分離後に得られたonset-spacingカテゴリがMDX合意結果と再現するかどうかである。

## 実行

`research/music-analysis`をカレントディレクトリにして実行する。

```bash
./run_mac_demucs_audit.sh
```

ランナーが行う処理:

1. macOS／Apple Silicon／Python環境を検査
2. 専用仮想環境を作成
3. `demucs-mlx`とApple Silicon用Essentia wheelを導入
4. 20 PreviewをAppleから取得してSHA-256照合
5. AACをWAVへ変換
6. Demucsで20件のドラムstemを推定
7. 固定ルールで解析し、同じJSONを二回生成してSHA-256一致を確認

成功時に`demucs-results-mac-local.json`が生成される。これは実機結果を検査した後でのみGitへ保存する。`.mac-demucs-work/`以下の音源、WAV、stem、モデル、仮想環境はGitへ保存しない。

## 参照

- demucs-mlx: https://github.com/ssmall256/demucs-mlx
- MLX Audio Separator: https://github.com/ssmall256/mlx-audio-separator
- Demucs: https://github.com/facebookresearch/demucs
