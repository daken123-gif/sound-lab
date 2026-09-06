# This Heat別版比較 — 速度を作品状態として扱う

- research-id: `20260906-this-heat-versions`
- status: `active`
- 更新日時: 2026-09-06 UTC
- 対象: `Graphic/Varispeed` 16 / 33 / 45 / 78 RPM版、`24 Track Loop`、`Repeat`
- 現在の問い: 同じ素材の別版は、単なる再生速度変更か、それとも別の演奏可能状態か
- 起点: `main` (`ecac4587ec21686d57d43df7ca9046ce66125bec`)

## 結論

`Graphic/Varispeed` の4版は、30秒プレビューの全体スペクトルを45 RPM版へ照合すると、回転数の方向とほぼ同じ周波数比で移動していた。とくに33 RPM版は推定比 `0.738`、ラベル比 `33/45 = 0.733`、相関 `0.934` で強く一致する。

しかし、Field Looperで採るべきものは「速度ノブ」だけではない。速度が変わると、時間長、可聴帯域、密度、イベントの持続、操作できる時間幅が同時に変わる。よって速度を元音へ戻すための補正値ではなく、**保存可能な作品状態**として扱うべきである。

`Repeat` と `24 Track Loop` は、公式説明では前者が後者の拡張ミックスである。プレビュー比較でも無シフトの対数スペクトル相関は `0.821` だった。一方で `Repeat` はプレビュー局所値で約4.5 dB大きく、side/mid比が約7.1 dB広く、centroidも高い。これは「同じループを長く垂れ流したもの」とみなすには不十分で、同じ素材群を別のミックス時間へ開いた版として扱う方が資料と観測に合う。

## 証拠境界

### 取得・実行したもの

- This Heat公式Bandcampの各版説明
- Shazam経由Apple Musicカタログの曲ID、ISRC、全長、30秒プレビューURL
- 6本の30秒プレビューを22.05 kHz stereo PCMへ変換
- RMS、crest、stereo correlation、side/mid、centroid、rolloff、flatness、テンポ候補の計測
- 45 RPM版を基準とする対数周波数スペクトルのシフト推定
- 前研究 `research/20260903-this-heat` のGitHub本文読戻し

### 取得・実行していないもの

- 全長音源の波形比較
- 4版の正確な開始点・終了点・デジタル化工程
- マスターまたは盤からの同一時点同期
- プレビューの直接聴取による聴感評価
- 速度変更以外のEQ、レベル、編集、マスタリング差の分離

30秒プレビューが各版の同じ原素材時点を示す保証はない。したがって、スペクトル相関は速度関係を支持するが、波形同一性の証明ではない。

## 資料から確認できた事実

### `Graphic/Varispeed`

公式Bandcampは、1980年の `Health and Efficiency` のB面として発表されたこと、操作された持続オルガン音を当時利用可能なすべてのターンテーブル速度で再生する意図があったこと、デジタル版に16 / 33 / 45 / 78 RPM相当版があることを記している。

- [Graphic/Varispeed (16 RPM) — official Bandcamp](https://thisheat.bandcamp.com/track/graphic-varispeed-16-rpm)
- [Graphic/Varispeed (33 RPM) — official Bandcamp](https://thisheat.bandcamp.com/track/graphic-varispeed-33-rpm)
- [Graphic/Varispeed (78 RPM) — official Bandcamp](https://thisheat.bandcamp.com/track/graphic-varispeed-78-rpm)
- [Health and Efficiency — official Bandcamp](https://thisheat.bandcamp.com/album/health-and-efficiency)

Shazam経由のApple Musicカタログ値:

| 版 | song ID | ISRC | 全長 | 45版に対する全長比 |
|---|---|---|---:|---:|
| 16 RPM | `1526576464` | `GBTFC2000003` | 1826.000秒 | 2.6645 |
| 33 RPM | `1526176912` | `GBTFC1700035` | 922.480秒 | 1.3461 |
| 45 RPM | `1526171592` | `GBTFC1700032` | 685.307秒 | 1.0000 |
| 78 RPM | `1526179876` | `GBTFC2000005` | 398.280秒 | 0.5812 |

33版と78版の全長比は、ラベルから予測される `45/33 = 1.3636`、`45/78 = 0.5769` に近い。16版はラベルから予測される `45/16 = 2.8125` より約5.3%短い。これは版ごとのトリム、`16 RPM` 表記と実回転数の差、または別工程の可能性があり、今回の資料だけでは原因を決めない。

### `24 Track Loop` と `Repeat`

公式Bandcampは `Repeat` を、1978年の `24 Track Loop` の拡張ミックスと明記している。

- [24 Track Loop — official Bandcamp](https://thisheat.bandcamp.com/track/24-track-loop)
- [Repeat — official Bandcamp](https://thisheat.bandcamp.com/track/repeat)

Shazam経由Apple Musicカタログ値:

| 版 | song ID | ISRC | 全長 |
|---|---|---|---:|
| 24 Track Loop | `1526180627` | `GBTFC1700014` | 356.747秒 |
| Repeat | `1526177118` | `GBTFC1700033` | 1220.320秒 |

`Repeat` は `24 Track Loop` の約3.421倍の全長を持つ。

## 30秒プレビューの機械観測

完全な値は [preview-metrics.csv](./preview-metrics.csv)、版間比較は [version-comparisons.csv](./version-comparisons.csv) に保存した。解析コードは [analyze-version-previews.py](./analyze-version-previews.py)。

| 版 | RMS dBFS | side/mid dB | centroid Hz | flatness | tempo候補 | pulse信頼度 |
|---|---:|---:|---:|---:|---:|---:|
| Graphic/Varispeed 16 | -25.11 | -24.68 | 390 | 0.029 | 76.0 | 0.548 |
| Graphic/Varispeed 33 | -23.68 | -24.45 | 962 | 0.110 | 198.8 | 0.442 |
| Graphic/Varispeed 45 | -22.84 | -23.92 | 1449 | 0.168 | 139.7 | 0.505 |
| Graphic/Varispeed 78 | -19.63 | -24.49 | 2306 | 0.305 | 94.0 | 0.451 |
| 24 Track Loop | -21.15 | -13.91 | 1581 | 0.340 | 67.1 | 0.286 |
| Repeat | -16.67 | -6.83 | 2637 | 0.556 | 139.7 | 0.231 |

`Graphic/Varispeed` では速度ラベルが上がるにつれてcentroidとflatnessが単調に上がる。保持音の倍音群がより高い帯域へ移動し、固定の8 kHz解析窓へ入る成分構成も変わるためである可能性が高い。

テンポ候補は持続音の振幅変動へ自己相関をかけた値で、拍の確定値ではない。各速度版の候補値は単純な回転数比に並んでいないため、速度関係の根拠には使わない。

## 版間スペクトル照合

45 RPM版の中央値Welch spectrumを48 bins/octaveの対数周波数軸へ補間し、他版を最大±80 binずらして相関が最大になる位置を求めた。

| 比較 | 推定周波数比 | ラベルからの比 | 最大相関 | shift bins |
|---|---:|---:|---:|---:|
| 16 vs 45 | 0.3800 | 0.3556 | 0.8376 | -67 |
| 33 vs 45 | 0.7384 | 0.7333 | 0.9344 | -21 |
| 78 vs 45 | 1.6818 | 1.7333 | 0.8362 | +36 |
| Repeat vs 24 Track Loop | 1.0000 | 対象外 | 0.8214 | 0 |

観測上、4つの `Graphic/Varispeed` プレビューは同じ方向の速度変換で説明できる強い共通スペクトル形状を持つ。33版が最もラベル比へ近く、相関も高い。16版と78版の差は、プレビュー範囲、EQ、トリム、デジタル化差を含みうる。

`Repeat` と `24 Track Loop` は周波数移動なしで最大相関になった。このことは同じ速度帯・素材系統を支持するが、局所ミックス差は大きい。

## 推論・仮説

### 仮説A — 速度は一つの連続パラメータではなく、身体時間の切替である

16 RPM相当では同じ出来事が長く留まり、低い帯域へ集まり、操作を差し込める時間が増える。78 RPM相当では出来事が短くなり、高域と変化密度が増える。これはpitchとdurationを独立に補正する現代的なtime-stretchとは別の関係である。

### 仮説B — 速度状態には退出方法も必要である

低速状態から原速へ戻す操作は、単に数値を45へ戻すだけでは急激な時間・音域・密度変化を起こす。Field Looperでは速度状態ごとに、cut、glide、再採取、別地面への移行を選べる必要がある。

### 仮説C — 拡張ミックスは長さの増加ではなく、判断時間の増加である

`Repeat` の全長は約3.4倍だが、プレビューの局所的な音圧・空間幅・高域分布も `24 Track Loop` と異なる。拡張とは同じ単位の反復回数を増やすことではなく、ミックス中に素材関係を変える時間を増やすことと解釈できる。

### 仮説D — 「可変する地面」は再採取によって世代を持つ

前研究の `MUTABLE_GROUND` を進めると、速度変更後の状態を再採取して次世代の地面にできる。元録音へ非破壊で戻れることと、変異した世代を独立素材として扱えることを両立させる必要がある。

## Field Looperへ採用する点

### 保存可能な速度状態

`speed = 0.36 / 0.73 / 1.0 / 1.73` の固定プリセットを移植するのではなく、任意速度を名前なしで一時保持し、その状態を地面として再採取できる構造を候補とする。

速度状態が保持するもの:

- playback rate
- pitch couplingの有無
- loop duration
- boundary位置
- filter / bandwidth
- exit behavior
- generation parent

### 元素材と変異世代の二重参照

変異後の録音を新規ファイルへ焼くだけではなく、`source -> mutation -> recapture` の系譜を保持する。undoのためだけでなく、演奏中に祖先状態へ飛び直すためである。

### 拡張ミックス用の演奏面

ループ回数を設定する画面ではなく、同じ地面に対してレベル、帯域、空間、速度、退出を継続的に変える面を検討する。操作が止まれば同じ状態へ固定されるが、自動展開はさせない。

## 採用しない点

- 16 / 33 / 45 / 78をThis Heat風プリセットとして表示すること
- pitchを保ったtime-stretchを `Varispeed` と呼ぶこと
- 30秒プレビューのテンポ候補を拍情報として実装へ入れること
- `Repeat` を「24 Track Loopを3.421倍繰り返す機能」と解釈すること
- 高速ほど明るく、低速ほど暗いというEQプリセットだけを移植すること
- 素材の自動変奏を拡張ミックスと呼ぶこと
- 全長未検証の段階で曲構成を確定すること

## 触る実装パス

今回も製品コードは変更しない。

- 追加: `research/20260906-this-heat-versions/README.md`
- 追加: `research/20260906-this-heat-versions/analyze-version-previews.py`
- 追加: `research/20260906-this-heat-versions/preview-metrics.csv`
- 追加: `research/20260906-this-heat-versions/version-comparisons.csv`

## 依存する研究

- branch only: `research/20260903-this-heat` (`149d2a56544986fc503064291a7f7fe89656217d`)
- 参照概念: `MUTABLE_GROUND`, `GROUND / INTRUSION / MUTATION / EXIT`

前研究は2026-09-06にGitHubから本文を読み戻し、`MUTABLE_GROUND` と「同一素材の別バージョン比較」の次課題を確認した。`main` には未統合なので、本研究だけで採用済みとは扱わない。

## 失効した判断

- 「速度版の違いは曲名のメタデータだけで、プレビューから検査できない」: 失効。全長比とスペクトル移動を検査できた。
- 「同じ素材なら同じミックスとみなせる」: 失効。`Repeat` と `24 Track Loop` の局所値には大きな差がある。
- 「速度はpitchとdurationの二項だけ」: 失効。帯域分布、密度、操作可能時間、退出も同時に変わる。

## 未検証事項

1. 4速度版の全長波形を同一原素材時点へ同期した差分
2. 16 RPM表記と全長・推定周波数比の約5%差の由来
3. `Repeat` 全長でのミックス操作、反復単位、構成区間
4. `24 Track Loop` のどの素材が `Repeat` のどこへ現れるか
5. pitch-coupled varispeedとpitch-preserving stretchを演奏者が区別できる最小UI
6. 速度遷移中のクリック、境界移動、バッファ長変化
7. 変異世代を保存しながら録音同意と容量上限を守る方法

## 次段階

全長音源の利用権限と取得経路が確保できた場合に限り、4速度版を原素材時刻へ整列し、波形相関、スペクトル差、トリム位置を検証する。それまでは30秒プレビューの観測を全長構成へ拡張しない。

## 解析物の扱い

取得したm4a、変換WAV、生成途中の音響データは一時解析物でありGitへ保存しない。Gitへ残すのは出典、集計値、比較結果、再現コードだけとする。
