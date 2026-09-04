# This Heat研究 — 可変する地面としての録音

- research-id: `20260903-this-heat`
- status: `active`
- 更新日時: 2026-09-04 UTC
- 対象: This Heat（1976–1982）の集団演奏、録音、テープ操作、構成
- 現在の問い: Field LooperはThis Heatの方法から何を採り、何を模倣しないべきか
- 起点: `main` (`565419000568005d1e0969070a0b4b05fb653007`)

## 結論

This Heatから採るべき核心は、テープ・ループ風の音色ではない。

**集団の遭遇を録音し、断片を選び、その断片を次の演奏の「地面」として戻し、現在の演奏でもう一度変形する**という循環である。本研究ではこれを `MUTABLE_GROUND`（可変する地面）と呼ぶ。

録音物は完成済みの伴奏でも、演奏を代行する自動装置でもない。過去の演奏が現在へ異物として侵入し、現在の演奏によって意味を変える。その関係がThis Heatの実践を、単なるルーパー、エフェクト・プリセット、ジャンル再現から分けている。

Field Looperへの採用候補は次の4動作である。

1. `GROUND`: いま鳴っている関係を短く固定する
2. `INTRUSION`: 固定した断片を現在へ再侵入させる
3. `MUTATION`: 速度、方向、帯域、密度、配置を演奏中に変える
4. `EXIT`: ループを作品の恒久的な土台にせず、消す・抜ける・別の地面へ渡す

## 調査範囲と証拠境界

### 取得した資料

- バンド公式Bandcampの作品説明と曲情報
- Charles Hayward / Charles Bullenの発言を含むインタビュー
- Apple Musicが配布する6曲の30秒プレビューをPCMへ変換した機械計測
- リポジトリ内の関連研究（Conny Plank、Holger Czukay、Dub、Autechre、non-musician performance）

### 今回できていないこと

- 全曲・全長音源の聴取比較
- マルチトラック、ステム、セッション・テープの確認
- 実機テープ、Harmonizer、可変速ターンテーブルでの再演
- 本人資料による全ライブ構成の曲別照合
- プレビューを人間の耳で直接試聴した評価

以下の数値は30秒プレビューの局所値であり、曲全体の確定的特徴ではない。テンポ候補は倍・半分取りを含みうる。数値は音楽的意味の証明ではなく、比較観測の補助として扱う。

## 一次資料・近接資料から確認できた事実

### 1. バンドは「録音すること」を活動の外側に置かなかった

Charles BullenはCold Storageで週50時間以上を過ごし、演奏を大量に録音し、あとから使える断片を探してメンバーへ戻したと説明している。録音アーカイブはスタジオ制作だけでなくライブにも用いられた。[Fact Magazine interview](https://www.factmag.com/2016/01/23/this-heat-interview/)

Charles Haywardは、最初からレコードを作っているつもりで、行ったことをすべて録音していたと述べる。正式スタジオで録ったミックスにも、リハーサルやライブの録音を編集して組み込んだ。[It's Psychedelic Baby interview](https://www.psychedelicbabymag.com/2019/03/this-heat-interview-charles-hayward.html)

したがって「演奏→あとで記録」ではなく、録音、聴き返し、選択、再投入までが演奏実践の一部だった。

### 2. テープは背景素材ではなく、ライブ上の行為者だった

The Quietusの取材は、テープ作曲と自由即興の組合せ、およびライブ中に録音テープを操作するエンジニアの役割を記述している。BBC側が「すべてライブであるべき」と考え、バンドがテープをライブで使うことを理解しにくかったというBullenの回想も載る。[The Quietus](https://thequietus.com/interviews/strange-world-of/this-heat-interview/)

これは再生を「ライブではない」と切り捨てる単純な二分法を崩す。ただし、ファイルを再生するだけでライブになるのではない。再生物が現在の判断、身体、音響関係に開かれていることが条件になる。

### 3. 役割の非対称性を消さず、集団として等価にした

Haywardはドラマー、Bullenはギター奏者として技量を持っていた一方、Gareth Williamsは当初「non-musician」と説明される。HaywardはWilliamsの質問や「間違い」から学び、過剰な技巧を引いて純粋な音を前面に出そうとしたと語る。[It's Psychedelic Baby interview](https://www.psychedelicbabymag.com/2019/03/this-heat-interview-charles-hayward.html)

同時にBullenは、全員が等しく、すべての役割が同じだけ重要な集団だったと説明する。[Loud And Quiet](https://www.loudandquiet.com/interview/this-heat/)

ここでの等価性は、全員が同じ技能・同じ操作を持つことではない。異なる能力、問い、失敗の仕方が、構成へ同じ強度で寄与できることである。

### 4. 「全チャンネルを開く」が形式の前提だった

Haywardは、歌、ミュジーク・コンクレート、電子音、自由即興、サウンドアート、ロックのいずれかに限定せず、それら全部に開いた集団だったと説明する。[Loud And Quiet](https://www.loudandquiet.com/interview/this-heat/)

これは何でも混ぜる雑食性ではなく、素材の種類に先立って固定された階層を置かない態度と読める。

### 5. 「24 Track Loop」は短い採取物を長い制作判断へ変えた

The Quietusは、サウンドチェック末尾のわずかなフレーズから最良の2小節を選び、マルチトラックをループし、長時間ミックスして形へ編集したという制作過程を紹介している。ループしたドラムにはHarmonizer処理が加えられた。[The Quietus](https://thequietus.com/interviews/strange-world-of/this-heat-interview/)

公式Bandcampは「Repeat」を、1978年の「24 Track Loop」の拡張ミックスと説明する。[This Heat Bandcamp — Repeat](https://thisheat.bandcamp.com/track/repeat)

重要なのは短いループそのものより、採取後の選択、重ね方、処理、編集に長い判断時間をかけた点である。

### 6. 速度は補正値ではなく、作品の複数の存在様式だった

公式Bandcampによれば「Graphic/Varispeed」の保持されたオルガン音は、あらゆるターンテーブル速度で再生することを意図し、16 / 33 / 45 / 78 RPM相当の版がある。[This Heat Bandcamp — Health and Efficiency](https://thisheat.bandcamp.com/album/health-and-efficiency)

速度変更は「原音へ戻す」ための一時的加工ではない。同一素材が異なる時間、音域、質量を持つ複数の正当な状態になる。

### 7. 異なる録音粒度の接合を隠さなかった

Haywardは、家庭制作や放送の音が異なる技術的な粒度・音響へ飛び、その接続を聞き手が作る状態をThis Heatのレコードに重ねて説明した。[The Guardian](https://www.theguardian.com/music/2020/sep/22/fiery-chaotic-and-full-of-emotion-this-heat-interview)

Fact Magazineは「Horizontal Hold」が初期版の断片から始まり、「Fall of Saigon」では半速化した打楽器ジャムのテープと一緒に演奏したと記す。[Fact Magazine interview](https://www.factmag.com/2016/01/23/this-heat-interview/)

したがって、異質な録音を同じ音質へ均すことより、継ぎ目を時間構造として生かす方法が中心にある。

## 30秒プレビューの機械観測

解析値は [preview-metrics.csv](./preview-metrics.csv) に保存した。再現コードは [analyze-previews.py](./analyze-previews.py)。入力は22.05 kHz、stereo、PCM WAVを想定する。

| 曲 | tempo候補 BPM | pulse confidence | RMS dBFS | crest dB | stereo corr | side/mid dB | centroid Hz |
|---|---:|---:|---:|---:|---:|---:|---:|
| 24 Track Loop | 68.0 | 0.40 | -21.2 | 21.0 | 0.95 | -13.9 | 1960 |
| Graphic/Varispeed (45 RPM) | 78.3 | 0.11 | -22.8 | 12.5 | 0.99 | -23.9 | 1455 |
| Health and Efficiency | 184.6 | 0.57 | -10.8 | 10.8 | 0.86 | -11.3 | 2252 |
| Paper Hats | 215.3 | 0.47 | -15.8 | 15.0 | 0.89 | -12.5 | 2161 |
| Makeshift Swahili | 103.4 | 0.38 | -15.0 | 15.0 | 0.88 | -11.9 | 1550 |
| A New Kind of Water | 41.0 | 0.65 | -16.1 | 15.8 | 0.92 | -13.6 | 1493 |

### 区間別の補助値

| 曲 | RMS thirds dBFS | centroid thirds Hz |
|---|---|---|
| 24 Track Loop | -24.3 / -23.9 / -24.1 | 1875 / 1828 / 1912 |
| Graphic/Varispeed (45 RPM) | -23.5 / -23.0 / -22.3 | 1302 / 1499 / 1515 |
| Health and Efficiency | -12.2 / -12.0 / -9.7 | 2134 / 2346 / 2480 |
| Paper Hats | -18.6 / -16.0 / -15.0 | 2186 / 2387 / 2097 |
| Makeshift Swahili | -16.4 / -14.6 / -17.0 | 1652 / 1606 / 1639 |
| A New Kind of Water | -17.4 / -16.4 / -16.1 | 1572 / 1529 / 1872 |

### 数値から言える範囲

- `Graphic/Varispeed` は今回の断片ではステレオ相関が最も高く、side/mid比が最も小さい。保持音の集中した像という公式説明と矛盾しない。ただし全長の空間設計は判断できない。
- `Health and Efficiency` は今回の断片で最大のRMS、比較的高いcentroid、後半へ向かうRMS上昇を示した。公式説明の「relentless and muscular」という記述を局所的に補助するが、数値だけで形式を説明するものではない。
- `24 Track Loop` はcrestが最大で、RMS三分割は比較的安定していた。反復する地面の上に鋭い出来事が置かれる可能性と整合するが、30秒だけから配置原理を確定しない。
- 曲間のtempo候補は広い。Field Looperで「This Heat BPM」を単一値にする根拠はない。

## 推論・仮説

ここからは資料の直接記述ではなく、本研究の推論である。

### 仮説A — 録音は記憶ではなく、時間差を持つメンバーである

録音断片は過去の保存物だが、再投入された瞬間に現在の演奏へ制約と提案を返す。この意味で録音は固定伴奏ではなく、時間差を持つ第四の演奏者として機能する。

検証条件: 演奏者が再生開始後も素材を切る、ずらす、速度変更する、応答して弾き方を変える余地があること。

### 仮説B — 反復の価値は同一性ではなく、差異を露出することにある

同じ断片が戻ると、現在側のわずかなズレ、部屋、入力、身体の変化が比較可能になる。ループは時間を止めるのでなく、変化を読む定規になる。

### 仮説C — 編集と即興は対立しない

This Heatでは即興から断片を選ぶ編集と、編集済み断片へ応答する即興が循環する。Field Looperも「録音モード」と「演奏モード」を完全分離すると、この循環を失う。

### 仮説D — 失敗はランダム生成ではなく、役割の境界を開く

Williamsの「間違い」が有効だったのは、無作為だからではなく、既存技能が当然とした問いを開いたからだ。製品上のランダマイズを「non-musician」代理と呼ぶのは誤りである。

## 関連研究との接続

### Conny Plank

共通点は、スタジオを透明な記録装置でなく演奏環境として扱うこと。差は、This Heatでは自前の長時間記録と集団内の再投入が強く、プロデューサー個人の署名へ還元しにくい点にある。

### Holger Czukay

共通点は、録音済み素材を現在へ接続し直すこと。Czukay研究の「ラジオ／偶発的受信」とThis Heatの「集団自身の過去」は入力源が異なる。Field Looperでは外部侵入と自己記憶を別ルートに保つ価値がある。

### Dub

共通点は、ミックス、ミュート、空間、反復が演奏行為になること。Dubの引き算と空間的送りに対し、This Heatでは録音粒度や編集痕跡の衝突も前面に出る。共通マクロへ潰さず、`EXIT` と `INTRUSION` を分ける。

### Autechre

共通点は、固定作品より生成・変形する関係を重視できること。差は、This Heatの循環が人間の集団即興と物理的録音の履歴に強く根差す点。アルゴリズム自律性をそのまま移植しない。

### non-musician performance

Williamsの例は、簡単操作だけを与える設計を支持しない。初心者を結果保証付きの観客にせず、音の質感、選択、拒否、タイミングへ実質的な決定権を渡す設計を支持する。

## Field Looperへ採用する点

### 1. 可変する地面

単一の「録音→再生」ボタンではなく、現在の関係を固定し、その後の侵入・変異・退出を独立して演奏できる状態モデルを採用候補とする。

```text
EMPTY -> GROUND -> INTRUSION -> MUTATION -> EXIT
             ^                         |
             +-------------------------+
```

これは厳密な一方向ステートマシンではない。`MUTATION` 中の状態を新しい `GROUND` として採取できる循環が必要である。

### 2. 明示的な録音

常時録音を既定にしない。ユーザーが取得開始を明示し、保存範囲を認識できること。This Heatの「すべて録音した」は彼らの選択であり、製品が利用者へ無断適用してよい規範ではない。

### 3. 継ぎ目を消さない選択肢

クロスフェードで全境界を自動的に滑らかにしない。クリック回避の最小安全処理と、編集点の音響的存在感を残すモードを分ける。

### 4. 速度を独立した作品状態として扱う

速度変更を一時エフェクトではなく、保存・呼び出し可能な状態にする。テンポ同期の正解へ吸着させず、連続速度と離散速度の両方を候補にする。

### 5. 操作履歴を音へ戻せること

undo履歴だけでなく、直前の状態を新しい入力として再採取できる構造を検討する。履歴は管理情報ではなく次の演奏素材になりうる。

### 6. 等価だが同一でない役割

入力、断片選択、変形、退出を複数人で分担できる。ただし全員へ同じUIを配る必要はない。異なる役割が最終音へ同程度の決定力を持つことを目標にする。

## 採用しない点

- 「This Heat」名義のジャンル・プリセット
- テープ・ワウ、ピッチ揺れ、歪みだけを束ねた表層的な再現
- 自動録音、無断の常時バッファ保存
- ループ再生だけをライブ演奏とみなす説明
- ランダマイズをnon-musicianの創造性の代替にする設計
- 音楽家の技能を罰し、初心者操作だけを道徳的に優位にする設計
- すべてを一つのKAOSS型master FXへ通す復活案
- 解析した6断片の平均BPM、音圧、centroidを「This Heatらしさ」として固定すること

## UI / 実装候補（未採用）

| 操作 | 最小UI | 音響上の責任 | 失敗条件 |
|---|---|---|---|
| GROUND | hold-to-capture | 開始・終了を本人が決める | 無断取得、範囲不明 |
| INTRUSION | momentary / latch | いつ過去を現在へ入れるか | 自動伴奏化 |
| MUTATION | speed / direction / band / density | 変化を演奏可能にする | preset一発で固定 |
| EXIT | fade / cut / shed | 反復から離脱できる | 永久に居座るloop |

候補イベント名:

```text
ground.capture.start
ground.capture.commit
ground.intrude
ground.mutate
ground.exit
ground.recapture
```

これらは実装仕様ではない。統合島で採否を判断し、既存の録音・ループ状態モデルとの競合を監査する必要がある。

## 触る実装パス

今回の研究では製品コードを変更しない。

- 追加: `research/20260903-this-heat/README.md`
- 追加: `research/20260903-this-heat/preview-metrics.csv`
- 追加: `research/20260903-this-heat/analyze-previews.py`

## 依存する研究

- `research/20260831-conny-plank/`
- `research/20260902-holger-czukay/`
- `research/20260831-dub-performance-grammar/`
- `research/20260831-autechre/`
- `research/20260831-non-musician-performance/`

依存は参照関係であり、本研究だけで各研究の統合状態を変更しない。

## 失効した判断

- 「ループは同じ音を維持する機能である」: 失効。差異を露出し、別状態へ渡るための地面として再定義する。
- 「過去素材の再生はライブではない」: 失効。現在の判断へ開かれた再生はライブ行為になりうる。
- 「This Heatらしさはテープ劣化の音色で移植できる」: 失効。核心は素材と現在の相互作用にある。
- 「non-musician向けには決定を減らせばよい」: 失効。操作量ではなく決定の実質を設計する。

## 未検証事項

1. 同一曲のスタジオ版、Peel Session、Live 80/81で、固定地面と現在演奏の関係がどう変わるか
2. `Graphic/Varispeed` の16 / 33 / 45 / 78 RPM版を同一指標で比較したとき、速度が形式認知へ与える差
3. 30秒プレビュー外でのダイナミクス、定位、反復周期
4. エンジニアを含むライブ上の役割分担を曲別に確認できる一次資料
5. Field Looper既存状態モデルへ `GROUND / INTRUSION / MUTATION / EXIT` を写像した場合の競合
6. クリックを安全に抑えつつ編集点の存在を失わない最小クロスフェード
7. 録音同意、保存期間、破棄を演奏の流れから外さず提示するUI

## 次の研究

次は「同一素材の別バージョン比較」を独立研究として行う。

- `Graphic/Varispeed` の複数速度版
- `24 Track Loop` と `Repeat`
- スタジオ版とライブ／Peel版

比較単位は音色の近さではなく、`固定された地面 / 現在の侵入 / 変異 / 退出` の4軸とする。

## 参照

- [This Heat — official Bandcamp](https://thisheat.bandcamp.com/)
- [24 Track Loop — official Bandcamp](https://thisheat.bandcamp.com/track/24-track-loop)
- [Health and Efficiency — official Bandcamp](https://thisheat.bandcamp.com/album/health-and-efficiency)
- [Repeat — official Bandcamp](https://thisheat.bandcamp.com/track/repeat)
- [Interview: This Heat — Fact Magazine, 2016](https://www.factmag.com/2016/01/23/this-heat-interview/)
- [Three Men in a Fridge — Loud And Quiet, 2016](https://www.loudandquiet.com/interview/this-heat/)
- [The Strange World Of… This Heat — The Quietus, 2016](https://thequietus.com/interviews/strange-world-of/this-heat-interview/)
- [This Heat: the band who came in from the cold — The Irish Times, 2018](https://www.irishtimes.com/culture/music/this-heat-the-band-who-came-in-from-the-cold-1.3399065)
- [This Heat interview: Charles Hayward — It's Psychedelic Baby, 2019](https://www.psychedelicbabymag.com/2019/03/this-heat-interview-charles-hayward.html)
- [This Heat, the band who tried to change everything — The Guardian, 2020](https://www.theguardian.com/music/2020/sep/22/fiery-chaotic-and-full-of-emotion-this-heat-interview)

## 証拠ファイルについて

プレビュー音源および生成したスペクトログラムは著作物・一時解析物なのでGitへ保存しない。Gitには出典、集計値、再現コードだけを残す。
