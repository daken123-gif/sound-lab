# Anderson .Paak研究

- status: `active`
- research-id: `20260831-anderson-paak`
- 研究対象: Anderson .Paak、The Free Nationals、NxWorries
- 現在の問い: 「Come Down」の反復が、なぜワンループの垂れ流しにならないのか。その演奏原理を、iPhoneのマルチタッチ楽器へどう移せるか
- 更新日時: 2026-09-02
- 正本候補: この研究ブランチ上のREADME。mainへ統合されるまでは製品採用済みではない

## 1. 一次資料

1. [Anderson .Paak & The Free Nationals: NPR Music Tiny Desk Concert](https://www.youtube.com/watch?v=ferZnZ0_rSM)  
   演奏曲: “Come Down”, “Heart Don’t Stand a Chance”, “Put Me Thru”, “Suede”
2. [Interview: Anderson .Paak — “Right now, there’s not a lot of people that are giving you soul”](https://songsforwhoever.com/2016/03/18/interview-anderson-paak-right-now-theres-not-a-lot-of-people-that-are-giving-you-soul/)  
   `Malibu`におけるドラム、ベース、ヴォーカルの役割についての本人発言
3. [Vanity Fair: “I Was Doing God’s Work”](https://www.vanityfair.com/style/2019/03/anderson-paak-new-album)  
   教会でのドラム経験についての本人インタビュー
4. [Modern Drummer: Anderson .Paak](https://www.moderndrummer.com/article/august-2019-anderson-paak/)  
   ドラマー／シンガーとしての位置づけ
5. [Stones Throw: NxWorries](https://www.stonesthrow.com/artist/nxworries/)  
   Anderson .PaakとKnxwledgeによるNxWorriesの公式記録
6. [Stones Throw: “Where I Go”](https://www.stonesthrow.com/news/nx22/)  
   Knxwledgeが送ったビートへ.Paakが“Suede”を返した経緯

## 2. 資料から確認できた事実

- .Paak本人は、`Malibu`でドラムとベースを大きな基礎とし、一定するドラム・グルーヴの上でベースが旋律を担い、ヴォーカルを可変要素として置く考えを説明している。
- Tiny Deskでは.Paak自身がドラムを演奏しながら、歌、ラップ、掛け声、観客との交信を同時に行っている。
- Tiny Deskの“Come Down”は、反復するベース・リフとドラムを中心に成立している。
- .Paakは教会でのドラム経験を自身にとって重要な教育だったと述べている。
- NxWorriesでは、Knxwledgeが作るサンプル中心のビートへ.Paakがヴォーカルを載せる分業が成立している。
- `Why Lawd?`は`Yes Lawd!`から8年後に発表されたNxWorriesの作品である。

## 3. “Come Down”の演奏観測

以下はTiny Desk映像に対する現在の観測。正確な波形解析や採譜は未実施。

### 3.1 不変骨格

曲の同一性を支えているのは、主に次の三点。

- 反復するベース・リフ
- バックビートの着地点
- ハイハットが維持する細分パルス

コード進行や新しい旋律素材を次々追加して曲を進めるのではない。少数の骨格を長く保持している。

### 3.2 毎小節変わるもの

骨格を維持したまま、次の要素が局所的に変化する。

- ハイハットのアクセント位置と開閉
- スネア周辺の弱いゴーストノート
- キックの密度とベース・リフへの追従度
- 声の語尾のあとに置かれる短いフィル
- バンド全体の停止、再突入、音量
- 掛け声による次の出来事の予告
- フレーズ末尾の空白

したがって反復しているのは完成済みの音声ではなく、演奏者が保ち続けている骨格である。

### 3.3 ドラムと声

.Paakはドラムを完成させてから、その上へ独立した歌を載せているようには聴こえない。

- 声が密な場所では、ドラムの情報を骨格へ戻す
- 声の語尾や空白へ、ゴーストや短いフィルを入れる
- ラップ、歌、叫びの切替と、ドラムの打点密度が連動する
- 声が観客へ向く瞬間も、ハイハットが時間の連続性を保持する

声とドラムは二つのトラックではなく、一つの身体の中で前景を交換している。

### 3.4 ベースとの関係

キックはベース・リフの全音をなぞらない。完全同期を避けることで、ベースには旋律として動く余地が残り、キックは身体の重心だけを指定する。

これは「ベース・トラック」と「ドラム・トラック」を別々に完成させる設計と異なる。両者は独立しているが、互いの次の発音可能性を制約する。

## 4. 現在の推論

### 4.1 反復単位は音列ではなく状態

Tiny Desk版で演奏者が維持しているものを、スタジオ版の制作構造と分けて記述する。スタジオ版の土台はHi-Tekが構築した固定ビートであり、「Come Down」全体を固定音列ではないとする以前の記述は不正確だった。

```text
LIVE_GROOVE_STATE = {
  pulse,
  backbeat,
  bass_ostinato,
  current_density,
  accent_bias,
  foreground_role,
  break_tension
}
```

Tiny Deskの演奏中はこの状態が継続し、各打点はその時点の身体運動とバンドの応答から生成される。一方、スタジオ版ではHi-Tekの固定ビートが先にあり、.Paakはその空間へ声、複数の人格、掛け合いを配置した。

### 4.2 「一定」と「同一」は違う

- 一定: パルス、重心、反復周期を保つ
- 同一: 前の小節と同じ打点、強度、音色を再生する

.Paakが保つのは前者であり、後者ではない。この分離が、ループを垂れ流しにしない中心条件だと考える。

### 4.3 演奏の負荷には階層がある

すべてを同じ意識密度で操作すると、歌いながら演奏できない。

- 半自動の身体運動: ハイハットなどのパルス保持
- 意図的な決定: キック、スネア、停止、再突入
- 反射的な装飾: ゴースト、短いフィル
- 意味の操作: 歌、ラップ、掛け声、観客への指示

ノンミュージシャン向け楽器でも、全パラメータを同列に露出するのではなく、この負荷階層を設計する必要がある。

## 5. Field Looperへ採用する点

ここでいう採用は研究上の候補であり、製品統合済みを意味しない。

### 5.1 保持ジェスチャーと発話ジェスチャーを分ける

- 一本の接触でパルス状態を維持する
- 別の指でキック／低音の重心を打つ
- 別の指でバックビートとゴーストを発生させる
- さらに別の指で停止、再突入、全層の密度変化を指揮する

三点タッチを上限にしない。四本目以降は「音を一個追加する指」ではなく、演奏全体の時間を変える指として使う。

### 5.2 キックとベースを相互拘束する

- キック入力が次のベース発音候補を狭める
- ベースの移動方向が次のキックの強度または省略可能性へ影響する
- 同時発音だけでなく、意図的な先行／遅延を演奏できる
- 完全追従モードは作らない、または一時的な状態に限定する

### 5.3 変化をランダム化で代用しない

「Humanize」の乱数で打点を散らしても、声、身体、場への応答にはならない。

変化は次の取得可能なジェスチャーから作る。

- 接触位置
- 移動方向
- 移動速度
- タップ間隔
- 接触の追加／離脱
- 複数指の距離
- 直前の打点からの継続時間

### 5.4 前景を交代させる

全層を常に派手にしない。

```text
DRUM_FOREGROUND
BASS_FOREGROUND
VOICE_OR_GESTURE_FOREGROUND
BREAK_FOREGROUND
```

前景が移動すると、他の層は消えずに骨格へ退く。この「退く」動作が、歌いながら叩く.Paakの構造に近い。

## 6. 採用しない点

- Anderson .Paakのドラム・パターンそのものの模倣
- 16ステップ・シーケンサーへゴーストノートを追加しただけの実装
- 一小節録音後の自動再生を「Paakモード」と呼ぶこと
- ランダムなタイミングずれをグルーヴと扱うこと
- ドラム、ベース、声を完全独立した完成トラックとして積層すること
- ヴィンテージなドラム音色だけを本質と見なすこと

## 7. Charlie Hunter／Jeff Millsとの接続

### Charlie Hunter

低音、和音、旋律が独立トラックではなく、一身体の中で相互に演奏可能性を制約する。

### Jeff Mills

複数の時間層を保持しながら、どの層を前景化するかをリアルタイムに変える。

### Anderson .Paak

身体がパルスを維持し、その上で声、ドラム、観客操作の前景を交換する。

三者の接続点は「複数パートを一人で鳴らすこと」ではない。複数層を固定再生せず、互いに制約させながら現在形で維持することにある。

## 8. 触る実装パス

現段階ではなし。研究記録のみ。

## 9. 依存する研究

現時点ではリポジトリ本文を未取得のため、以下は `referenced only`。

- Charlie Hunter研究
- Jeff Mills研究
- James Brown研究
- D’Angelo “Spanish Joint”研究
- J Dilla研究
- KNOWER／Louis Cole研究

## 10. 失効した判断

### 失効: 「Come Down」で保存されているのは固定音列ではない

以前の記述はTiny Desk版の演奏観測を、スタジオ版の制作構造へ拡張していたため失効する。スタジオ版の土台はHi-Tekによるベースラインと刻んだドラムから作られた固定ビートである。

現在有効な区別は次のとおり。

- スタジオ版: 固定ビートを制約として、.Paakが声の時間と場面を作る。
- Tiny Desk版: 固定ビートの骨格をバンドが再演奏し、各打点と前景交代を現在の身体へ戻す。

「反復はすべて悪い」「ループを使わない」という判断にはしていない。問題にしているのは、演奏者の現在の行為から切断された完成音列の垂れ流しである。

## 11. 未検証事項

- “Come Down”のスタジオ版とTiny Desk版の小節単位比較
- ハイハット、スネア、キックの正確な採譜
- 各打点のマイクロタイミングと強度分布
- 声のフレーズ境界とフィル開始位置の対応
- ベースとキックの先行／遅延関係
- 四本以上の指を使ったiPhone実機での誤接触率
- 接触保持を固定パターン再生に落とさず、身体運動として維持する音生成方式
- `Come Down`以外でも同じ原理が保持されるか


## 12. 2026-09-02追補 — 固定ビートを身体へ取り戻す

### 追加資料

1. [DJBooth: Hi-Tek “Beat Break” interview](https://djbooth.net/features/2017-09-22-hi-tek-interview-beat-break/)  
   Hi-Tek本人による“Come Down”制作経緯。
2. [Issue Magazine: Anderson .Paak interview](https://www.issuemagazine.com/anderson-paak/)  
   .Paak本人によるHi-Tekのビート、曲の完成時期、空間を使うプロデューサーについての説明。
3. [Shazam: “Come Down” credits](https://www.shazam.com/en-us/song/1065681770/come-down)  
   Hi-Tekのproducer credit、演奏者credit。
4. [Pitchfork: “Come Down” track review](https://pitchfork.com/reviews/tracks/17909-andersonpaak-come-down/)  
   スタジオ版をshuffling drum loopと空間のあるHi-Tek productionとして記述。
5. [NPR Music Tiny Desk Concert](https://www.youtube.com/watch?v=ferZnZ0_rSM)  
   .PaakとThe Free Nationalsによるライブ再演奏。

### 追加事実

- Hi-Tek本人によれば、ベースラインの着想は第二作目のReflection Eternal制作期に録音していたが、適切なドラムを長く決められなかった。
- 2015年にドラムを刻んで配置し、以前のベースラインへ結合した。Hi-Tekは完成版を約98 BPMと説明している。
- .Paak本人はHi-Tekから送られたビートを当初寝かせており、“Come Down”はアルバムのmastering直前に加えた曲の一つだと説明している。
- .PaakはHi-TekとKnxwledgeについて、空間を使うproducerとして評価している。
- スタジオ版のproducer creditはHi-Tekであり、Tiny Deskでは.Paak自身がドラムを演奏する。

### 二つの“Come Down”

| 層 | スタジオ版 | Tiny Desk版 |
|---|---|---|
| 時間の土台 | Hi-Tekが構築した固定ビート | .Paakとバンドがその場で維持する |
| .Paakの主な現在行為 | 声、ラップ、掛け合い、人格交代 | 声に加えて打点、音価、フィル、停止 |
| 反復の変化 | 主に声と編曲上の配置 | 打点、強度、音価、前景が演奏中に変わる |
| ループの位置 | 完成音源を成立させる制約 | 再演奏される骨格または記憶 |
| 時間への責任 | producerのビートとvocal phrasingに分散 | .Paakとバンドの身体へ戻る |

ここから得られるのは「ループを使えば垂れ流し、使わなければ演奏」という二分ではない。

スタジオ版では、固定ビートが動かなくても.Paakの声が空間を演奏している。Tiny Deskでは、その固定ビート自体を身体へ戻し、ドラムと声の両側から再編している。二版の関係は、loop versus liveではなく、**固定された時間へ何を現在行為として残すか**の違いである。

### Sound Labへの更新仮説（未採用）

#### 1. ループを録音物ではなく譜面として扱う

保存した一小節をそのまま鳴らし続けるのではなく、次の周期で守る骨格だけを抽出する。

```text
BEAT_OBJECT = {
  cycle_length,
  invariant_accents,
  bass_contour,
  backbeat_slots,
  silence_slots
}
```

演奏時には、この骨格から各打点を現在入力で再発音する。元音声を鳴らす場合も、演奏の主役ではなく参照層に留める。

#### 2. 保持だけでは完全な周期を再生させない

一本の指を置いたままにするだけでハイハット、キック、スネアが完成し続けるなら、それは接触を再生ボタンへ置き換えただけである。

- 移動
- 再打
- 離指
- 指の追加
- 指同士の距離変化
- 周期直前の選択

のいずれかが次周期へ残る必要がある。何も入力されなければ、音を消す、骨格だけへ痩せる、未決定打点を休符にする等の挙動が候補になる。

#### 3. 「現在行為率」を設計評価に使う

```text
CURRENT_ACTION_RATIO =
  current_gesture_derived_events
  / audible_structural_events
```

これは音楽的価値を一数値へ還元する指標ではない。ループが演奏支援から自動再生へ変質していないかを検査するための診断値である。

比率を100%へ固定する必要はない。スタジオ版“Come Down”のように、固定ビートの上で声が時間を演奏する構造もある。重要なのは、どの層を現在の演奏者が引き受けているかが見えることである。

#### 4. BeatからBandへの連続変形を作る

```text
FIXED_BEAT
  -> GESTURE_MODULATED_BEAT
  -> PARTIALLY_REARTICULATED_BEAT
  -> FULLY_REEMBODIED_BAND
```

モード切替ではなく連続量として扱う。指が増えるほど単純に音数を増やすのではなく、固定ビート側に残っていた時間責任を演奏者側へ引き取る。

### 更新後の中心命題

.Paakから移すべきものは、ライブ・ドラムの見た目でも、Hi-Tekの一小節でもない。

**固定ビートを受け取り、声で占有し、必要なら身体へ取り戻して別の現在形へ変える能力**である。

これは、既成ループを禁止する設計より厳しい。ループを使っても、使わなくても、現在の演奏者が時間へ何をしたかが音に残らなければならない。
