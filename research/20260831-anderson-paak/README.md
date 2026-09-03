# Anderson .Paak研究

- status: `active`
- research-id: `20260831-anderson-paak`
- 研究対象: Anderson .Paak、The Free Nationals、NxWorries
- 現在の問い: 「Come Down」の反復が、なぜワンループの垂れ流しにならないのか。その演奏原理を、iPhoneのマルチタッチ楽器へどう移せるか
- 更新日時: 2026-09-03
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


## 13. 2026-09-02追補 — 声が反復を出来事へ変える

### 追加資料

1. [Modern Drummer: Anderson .Paak (August 2019 PDF)](https://www.moderndrummer.com/wp-content/uploads/2019/06/1908_MD_August_477c.pdf)  
   .Paak本人が、キット上では演奏を明確に見せ、前へ出たときはフロントマンとして明確に振る舞う、という役割分離を語っている。
2. [GQ: The Real-Life Diet of Anderson .Paak](https://www.gq.com/story/real-life-diet-anderson-paak)  
   .Paak本人が、観客をショーの一部にすること、ショーの流れのどこで観客を参加させるかを常に考えると説明している。
3. [The FADER: Considering The Wonderful And Incomplete Arrival Of Anderson .Paak](https://www.thefader.com/2016/02/05/anderson-paak-new-york-sobs-show)  
   ライブ評。反復される “Yes, lawd!” が、曲中の歓喜の句読点として機能したことを記録している。
4. [XXL: Anderson .Paak Gets Into His Groove at First New York City Show](https://www.xxlmag.com/anderson-paak-new-york-show-recap/)  
   ライブ評。.Paakがコール＆レスポンスと身体動作で観客を指揮したことを記録している。

### 追加事実と観測

- .Paakは、ドラム／シンガーという複合能力を曖昧に見せるのではなく、「キット上の演奏」と「前へ出たフロントマン」の双方をはっきり成立させる課題として引き受けている。
- .Paak本人にとって観客参加は偶発的な盛り上がりではなく、ショー全体の流れの中で配置する設計対象である。
- ライブ評では “Yes, lawd!” が同じ語の反復でありながら、曲の内部で句読点、肯定、観客への合図として複数の役割を持つ。
- コール＆レスポンスは声を追加するだけではない。誰が次の時間を担当するかを、演奏者から観客へ一時的に移す。

最後の二点は演奏記録に基づく現在の分析であり、本人が同じ語で理論化した事実ではない。

### イベント文法としての“Come Down”

固定ビートの上でも、出来事は新しいコードや新しいループを追加せずに作れる。必要なのは、反復内部の役割と時間責任を切り替えることである。

```text
TIME_KEEPER  = 周期と重心を維持する
CALL         = 次の発音主体へ空間を渡す
RESPONSE     = 渡された空間を別主体が引き受ける
CUT          = 複数層を同時に止め、次の打点を未決定にする
REENTRY      = 骨格を新しいアタックで現在へ戻す
PUNCTUATION  = 掛け声や短い打点で区切りを作る
```

これは六つの独立音色ではない。一つの反復の中で、接触や声が担う役割である。

```text
TIME_KEEPER
  -> CALL
  -> RESPONSE
  -> CUT
  -> REENTRY
  -> TIME_KEEPER
```

遷移順は固定しない。ただし `REENTRY` は自動タイマーだけで起こさない。停止後に演奏者または別の参加者が、新しい入力で時間を引き受ける必要がある。

### 一身体の中の前景交換

.Paakの重要点は「歌いながら複雑なドラムを全部叩く」ことだけではない。

- 低負荷の運動層が時間を保持する
- 声が意味の前景を取る
- 短いフィルや掛け声が句読点を置く
- 必要な瞬間だけフロントマン／指揮者の役割が前へ出る
- 観客へ渡した時間を、再突入でバンドへ戻す

したがって楽器側も、全指へ同じ重さの音符入力を割り当てるべきではない。一方の手がパルスを保持し、もう一方が `CALL`、`CUT`、`REENTRY` を指揮できる非対称性が必要になる。

### Sound Labへの更新仮説（未採用）

#### 1. パッドではなく役割を触る

```text
TOUCH_ROLE = {
  time_keeper,
  call,
  response,
  cut,
  reentry,
  punctuation
}
```

同じ場所への接触でも、直前の空白、他の指の保持、接触速度によって役割が変わる。固定された「キック・パッド」「声ネタ・パッド」の集合へ戻さない。

#### 2. コール＆レスポンスを自動演出にしない

システムが常に気の利いた返答を自動生成すると、観客参加を模倣しただけになる。

- `CALL` は応答可能な空白を作る
- `RESPONSE` は別の接触、別人の接触、または明示的に取得した声を必要とする
- 応答がなければ空白を保持する
- システム自身の補完は、安全用の最小骨格に限定する

応答しない自由を残すことで、コールは本当に他者へ開かれる。

#### 3. カットを一音のミュートにしない

`CUT` は複数層の共有イベントとして扱う。

```text
CUT_SCOPE = {
  pulse_layer,
  bass_layer,
  vocal_capture,
  visual_motion
}
```

すべてを必ず止める必要はない。ただし一つの層だけが無関係に消えるのではなく、バンド全体が同じ境界を知覚できる必要がある。

#### 4. 再突入は保存ループの再開ではなく再発音にする

`REENTRY` で戻すのは周期情報と重心であり、直前の完成音声ではない。

- 最初のアタックは現在のジェスチャーから生成する
- 密度は骨格から始める
- 以前の装飾は自動復元しない
- 他者の `RESPONSE` があれば、それを新しい前景へ昇格できる

これにより「止めたふりをして同じループを再生する」挙動を避ける。

#### 5. 小節ではなくイベント窓で状態を変える

観客の応答や掛け声は小節線ちょうどに返るとは限らない。変化を次小節まで待たせず、次の安全な着地点までの短い窓で受け取る。

```text
EVENT_WINDOW = {
  opened_by,
  acceptable_roles,
  latest_safe_entry,
  fallback: silence | skeleton
}
```

クオンタイズは入力を消すためではなく、複数人が同じ再突入を共有するために使う。

### 更新後の設計命題

固定ビートを「演奏らしく揺らす」だけでは足りない。

**反復の内部で、誰が時間を保持し、誰が呼び、誰が応え、誰が止め、誰が戻すかを現在の行為で移し替える。**

.Paakの声はループ上の追加トラックではなく、この役割移譲を観客にも読める形にするインターフェースとして働く。Sound Labへ移すべきなのは声ネタそのものではなく、反復を社会的な出来事へ変えるこの構造である。

### 追加した未検証事項

- Tiny Desk版“Come Down”の `CALL / RESPONSE / CUT / REENTRY` 発生時刻の採譜
- 各イベント前後でハイハット、キック、ベースのどの層が残るか
- “Yes, lawd!” の反復位置と、バンド／観客の応答形式の曲別比較
- iPhoneを二人で触る場合の所有権、誤接触、再突入競合
- 自動応答なしでも初心者がコール＆レスポンスを成立させられるか
- 小節クオンタイズとイベント窓方式の演奏感比較


## 14. 2026-09-02追補 — パルスを委譲しても演奏は手放さない

### 今回の比較資料

1. [NME: Anderson .Paak live in Birmingham](https://www.nme.com/reviews/anderson-paak-leaves-it-all-on-the-stage-as-he-delivers-a-high-energy-masterclass-in-birmingham-2541008)  
   “Come Down”のインストゥルメンタル上で.Paakがステージ左、右、中央の順に観客へジャンプを要求し、その後キットへ戻って次曲へ進んだと記録している。
2. [808sandjazzbreaks: Best Teef in the Game Tour review](https://www.808sandjazzbreaks.com/concert-reviews/3w4ghykwm6f2lo47wk2pu333r1grmp)  
   “Heart Don’t Stand a Chance”をキット上で終えたあと、.Paakがキットを離れ、“Come Down”ではステージと客席を移動しながら観客を動かしたと記録している。
3. [The Line of Best Fit: Anderson .Paak live in London](https://www.thelineofbestfit.com/reviews/live-reviews/anderson-paak-the-forum-london)  
   “Come Down”冒頭のベースラインと、観客の応答を.Paakが引き出す公演構造を記録している。
4. [Austin Chronicle: ACL Review — Anderson .Paak](https://www.austinchronicle.com/music/acl-review-anderson-paak-12096736/)  
   “Come Down”を冒頭曲に置き、.Paakがドラムを行き来しながらバンド全体のまとめ役を担ったことを記録している。
5. [NPR Music Tiny Desk Concert](https://www.youtube.com/watch?v=ferZnZ0_rSM)  
   “Come Down”を.Paak自身がキット上で歌いながら演奏する比較対象。

### 前章への修正

前章までの「一方の手がパルスを保持し、もう一方が `CALL / CUT / REENTRY` を指揮する」という設計は、Tiny Desk型の**身体内分担**には有効である。しかし“Come Down”一般の中心原理ではない。

別公演では.Paakがキットを離れても曲は成立している。その間、周期の実音はバンドまたはインストゥルメンタルへ委譲され、.Paakは観客の区分、煽り、応答要求、次の曲への遷移へ身体を使う。

したがって次の二つを分ける必要がある。

- **時間源**: 誰／何がパルスを実際に鳴らすか
- **出来事の決定権**: 誰が次の停止、応答、再突入、遷移を決めるか

.Paakは時間源を委譲できるが、出来事の決定権まで無関係な自動進行へ渡してはいない。これが現在の比較から得られる中心差である。

### 二軸モデル

```text
TIME_SOURCE =
  FIXED_BEAT
  | PAAK_BODY
  | BAND_MEMBER
  | SHARED_BODY

EVENT_AUTHORITY =
  FRONT_PERSON
  | BAND
  | CROWD
  | SHARED
  | SYSTEM
```

この二軸は一致しなくてよい。

| 公演構造 | 時間源 | 出来事の決定権 |
|---|---|---|
| スタジオ版 | Hi-Tekの固定ビート | 録音された声と編曲 |
| Tiny Desk版 | .PaakとThe Free Nationals | .Paakとバンド |
| Birmingham評に記録された“Come Down” | インストゥルメンタル／バンド | 観客を区分し指揮する.Paak |
| 観客の応答中 | バンドが骨格を保持 | .Paakから観客へ一時移譲 |

厳密な時間源の内訳は各公演の音源分離をしていないため未確定である。表は取得資料で判別できる責任配置だけを示す。

### 委譲と放棄を分ける

#### 委譲

- 委譲先が明示される
- 何を維持するかが限定される
- 元の演奏者が状態を聴き続ける
- 合図によって停止、変形、回収できる
- 委譲中に別の現在行為が前景化する

#### 放棄

- 完成ループが無期限に進む
- 誰も次の境界を引き受けない
- 観客入力が音楽状態へ影響しない
- 回収が再生停止ボタンだけになる
- 演奏者が何もしなくても同じ展開へ到達する

ループの使用自体ではなく、この差が「垂れ流し」かどうかを決める。

### Sound Labへの更新仮説（未採用）

#### 1. `DELEGATE_PULSE` を独立操作にする

保持していたパルスを離指と同時に消すか、永久再生へ移すかの二択にしない。

```text
DELEGATE_PULSE = {
  target,
  retained_skeleton,
  max_unattended_cycles,
  reclaim_window,
  audible_owner
}
```

委譲後も、どの層が誰に預けられているかを触覚または画面上の運動で判別できる必要がある。

#### 2. システムへ二軸を同時に渡さない

システムが時間源を担当する局面は許容する。しかし同時に次の出来事まで自動決定させると、演奏者は観客になる。

暫定制約:

```text
if TIME_SOURCE == SYSTEM:
    EVENT_AUTHORITY != SYSTEM
```

自動伴奏中でも、密度、停止、呼びかけ、応答受付、再突入の少なくとも一つは現在入力に残す。

#### 3. 空間への呼びかけを音高パッドへ還元しない

Birmingham公演で記録された左・右・中央への呼びかけは、三つのサンプルを鳴らす操作ではない。観客を一時的な演奏群へ分け、同じ要求を別々に通す操作である。

```text
ADDRESS_GROUP = {
  region,
  requested_action,
  response_window,
  accepted_energy
}
```

iPhone一台でも、画面領域を固定音色へ割り当てるのでなく、「今は誰へ時間を渡しているか」を示す空間として使える。

#### 4. 委譲中の前景を必須にする

パルスを預けたあと、演奏者が次に何を担うかを選ぶ。

- `ADDRESS_GROUP`: 参加者を指名する
- `REQUEST_RESPONSE`: 応答窓を開く
- `SHAPE_DENSITY`: バンドの密度を動かす
- `CUT`: 共有境界を作る
- `RECLAIM_PULSE`: 時間源を身体へ戻す

何も選ばれない周期が一定数続けば、安全な骨格へ痩せる。完成アレンジへ自動発展させない。

#### 5. 回収を演奏可能にする

委譲したパルスを身体へ戻すとき、単なるモード切替にしない。

```text
RECLAIM_PULSE requires:
  cue_gesture
  + entry_attack
  + accepted_phase_window
```

現在の打撃または接触が次の重心を作り、システム側の骨格はその位相へ追従する。演奏者がループへ戻るのではなく、ループが演奏者の新しい打点へ戻る。

### 更新後の中心命題

.Paakの“Come Down”は、ライブ・ドラムがある公演だけで成立する曲ではない。固定ビート、ライブ・バンド、キット上の身体、ステージ前方の身体の間を移動できる。

その可搬性を支えるのは、音色や担当楽器の固定ではなく、

**時間源を他者へ預けながら、出来事の決定権を現在の身体と場のあいだで移し続けられること**

である。

Sound Labで目指すべきなのも、全音を一人で生成する純粋性ではない。必要な層を委譲して別の行為へ出ながら、再び時間を身体へ回収できる演奏構造である。

### 追加した未検証事項

- Birmingham公演の“Come Down”で時間源を担う各パートの実音確認
- キットを離れる直前と戻る直前の合図、フィル、視線の採譜
- 左・右・中央への要求が同一か、段階的に強度を変えているか
- 観客応答中にバンドが保持する最小骨格
- `max_unattended_cycles` が演奏支援から自動再生へ変質する境界
- `DELEGATE_PULSE` の所有表示を視覚、触覚、音のどれで伝えるべきか


## 15. 2026-09-02追補 — James Brownから受け継ぐ「未完成な指示」

### 参照境界

既存のJames Brown研究ブランチは横断取得できたが、現在の検索語との自己反響が強く、逆流防止検査で隔離された。その本文の主張はこの追補の証拠として使用していない。

過去READMEからは一次資料の所在だけを取り出し、以下の公開本文を直接取得し直した。

1. [Fred Wesley interview — Red Bull Music Academy Daily](https://daily.redbullmusicacademy.com/2013/03/fred-wesley-interview/)
2. [Fred Wesley interview — American Archive of Public Broadcasting](https://americanarchive.org/catalog/cpb-aacip-15-w66930p811)
3. [Pitchfork: Anderson .Paak “Come Down” track review](https://pitchfork.com/reviews/tracks/17909-andersonpaak-come-down/)
4. [Pitchfork: The 100 Best Songs of 2016 — “Come Down”](https://pitchfork.com/features/lists-and-guides/9981-the-100-best-songs-of-2016/?page=6)
5. [NME: Anderson .Paak live in Birmingham](https://www.nme.com/reviews/anderson-paak-leaves-it-all-on-the-stage-as-he-delivers-a-high-energy-masterclass-in-birmingham-2541008)

### 取得した事実

- Fred Wesleyによれば、James Brownは完成した譜面を各奏者へ渡すだけでなく、発想、唸り、短い声を提示し、Jimmy Nolenをはじめとする奏者がそれをリフへ翻訳した。
- Brownは奏者が作った具体形を聴き、望む形へ至るまで修正させ、採用の判断を行った。
- “Doing It to Death”では、Brownが演奏中に奏者名と短い発話でソロを指名し、録音自体が短時間の共同生成として成立したとWesleyは説明している。
- 同じ証言には、服装、生活、演奏ミスへの過剰な統制や罰金も含まれる。音楽上の短い合図と、労働上の支配は分離して評価する必要がある。
- “Come Down”についてPitchforkは、Hi-Tekの空間のある固定ビート上で.Paakが複数の人格と想像上の群衆を作り、James Brown的な “get down” の身振りを現代ヒップホップへ接続したと評している。
- Birmingham公演では、.Paakが固定された一人の応答者を指名するのでなく、会場を左、右、中央へ分け、同じ要求を別々の群へ投げている。

### 継承されるもの

#### 1. 指示は完成した音ではない

Brownの唸りや短い発想は、最終的なギター・リフ、ベース・ライン、ホーン譜そのものではない。奏者が解釈しなければ音楽にならない。

.Paakの観客への要求も同様に、観客の声量、タイミング、身体運動を事前録音として決めていない。呼びかけは応答可能性を開くが、応答の実体はその場の人間が作る。

共通するのは次の形である。

```text
INCOMPLETE_CUE
  -> HUMAN_INTERPRETATION
  -> AUDIBLE_RESPONSE
  -> ACCEPT | MODIFY | REDIRECT
```

#### 2. 声が構成操作と発音を兼ねる

Brownの短い呼びかけは、それ自体が曲中の音でありながら、次のソロやパート配置を変更する。

.Paakの掛け声も、声ネタとして上へ追加されるだけでなく、観客の参加、バンドの密度、場面の境界を変える。

したがって声入力を「録音してループへ載せるトラック」だけとして扱うと、この二重機能を失う。

#### 3. バンドは命令の再生装置ではない

Brownが強い最終決定権を持っていても、具体的なリフは各奏者の翻訳能力から生まれた。入力と出力の間には演奏者固有の差がある。

.Paakの場合、その翻訳主体はThe Free Nationalsだけでなく、観客の群、固定ビート上の複数人格、.Paak自身のドラム／声の切替へ広がる。

### 変わったもの

| 層 | James Brownの証言から確認できる構造 | “Come Down”で見える展開 |
|---|---|---|
| 合図の主対象 | 熟練したバンド奏者 | バンド、固定ビート上の人格、観客群 |
| 合図の主機能 | リフ生成、ソロ指名、構成変更 | 群の指名、応答要求、エネルギー配分、再突入 |
| 翻訳単位 | 個々の楽器パート | 楽器、声、身体運動、群衆の反応 |
| 時間源 | 主にライブ・バンド | 固定ビートとライブ・バンドを横断 |
| 権力構造 | Brownへ決定権が集中し、労働統制と結合 | 少なくとも取得した公演記録では、参加を観客へ分配 |
| 不変点 | 短い合図が現在の演奏を変える | 短い合図が現在の場を変える |

最後の「参加を観客へ分配」は公演記録からの観測であり、.Paakの全運営・全労働関係を民主的だと断定するものではない。

### `EVENT_AUTHORITY` の再分解

前章の一変数では、Brown型の指示と奏者の翻訳、.Paakの呼びかけと観客の応答を区別できない。

```text
EVENT_AUTHORITY = {
  proposal_authority,
  realization_authority,
  acceptance_authority,
  veto_authority,
  reclaim_authority
}
```

- `proposal_authority`: 次に何を起こしたいか提示する
- `realization_authority`: 実際の音・身体運動へ翻訳する
- `acceptance_authority`: 応答を採用し次へ進める
- `veto_authority`: 応答を拒否または止める
- `reclaim_authority`: 委譲した時間を自分へ戻す

これらを一人またはシステムへ自動集中させない。

### Sound Labへの更新仮説（未採用）

#### 1. `CUE_PACKET` は意図的に未完成にする

```text
CUE_PACKET = {
  target_role,
  desired_change,
  response_window,
  hard_constraints,
  open_dimensions,
  recall_gesture
}
```

`hard_constraints` は安全な着地点や衝突回避だけを指定する。`open_dimensions` には音高、細部のリズム、強度、音色、応答人数など、翻訳者へ残す自由を明示する。

#### 2. 合図から完成フレーズを自動生成しない

初心者支援のために全フレーズをシステムが完成させると、合図はプリセット選択になる。

システムが担ってよいもの:

- 位相衝突を避ける
- 音域の危険な重複を警告する
- 応答可能な空白を確保する
- 戻れる着地点を提示する

現在入力へ残すもの:

- いつ応答するか
- どの輪郭を選ぶか
- 応答しないか
- どこで止めるか
- どの応答を次の骨格へ残すか

#### 3. 翻訳量を測る

```text
TRANSLATION_DISTANCE =
  difference(cue_constraints, performed_response)
```

差がゼロなら、参加者は命令を再生しただけである。差が大きすぎて共通骨格が失われれば、合図が届いていない。

狙うのは一定値ではなく、演奏中にこの距離を広げたり狭めたりできること。初心者には制約を多く、慣れるほど `open_dimensions` を増やす。

#### 4. 応答しない権利を残す

Brown型の罰金・服装統制・過酷な拘束を、リアルタイム指揮の必要条件として持ち込まない。

```text
response = PERFORM | TRANSFORM | DECLINE | SILENCE
```

観客または共同演奏者が応答しない場合、システムは勝手に参加したことにしない。空白を出来事として残す。

#### 5. 貢献の由来を消さない

合図を出した人と、実際のフレーズを作った人を分けて保持する。

```text
EVENT_PROVENANCE = {
  proposed_by,
  realized_by,
  transformed_from,
  accepted_by
}
```

これは権利処理をこの研究だけで解決するものではない。少なくともUIと内部状態で、フロント役が全応答の作者だったことにしないための条件である。

### 更新後の中心命題

James Brownから.Paakへ継承されるのは、声質、ホーン、Oneの強調だけではない。

**短い未完成の合図を出し、他者がそれを音へ翻訳し、その結果を現在の構成へ戻すこと。**

.Paakはこの構造を、ライブ・バンドだけでなく、Hi-Tekの固定ビート、複数の声の人格、会場を分けた観客応答へ拡張する。

Sound Labでは、指揮する人が全音を事前所有する構造にも、システムが全応答を代作する構造にも戻さない。合図と実現の間に、別の身体が本当に音楽へ入れる距離を残す。

### 追加した未検証事項

- “Come Down”各公演で、.Paakの合図がバンドの具体的リフを変更しているか
- 観客応答の採用／再要求／拒否を示す身体合図
- The Free Nationals側が.Paakの非言語合図をどう分類しているか
- 初心者に必要な `hard_constraints` と自由を奪う過剰制約の境界
- `TRANSLATION_DISTANCE` を音高差だけでなくリズム、音色、密度、沈黙で測れるか
- 複数参加者の `EVENT_PROVENANCE` を演奏中に負担なく表示できるか


## 16. 2026-09-03追補 — 音ではなく「応答の空席」を保存する

### 追加資料

1. [Issue Magazine: Anderson .Paak interview by Talib Kweli](https://www.issuemagazine.com/anderson-paak/)  
   .Paak本人が、声をビート内の「もう一つの楽器」として捉えること、Hi-TekやKnxwledgeのように余白を使うプロデューサーを好むことを説明している。
2. [Pitchfork: The 100 Best Songs of 2016 — “Come Down”](https://pitchfork.com/features/lists-and-guides/9981-the-100-best-songs-of-2016/?page=6)  
   固定ビートの空間を、想像上の群衆と複数の人格で満たす構造として“Come Down”を記述している。
3. [NPR Illinois: “Come Down” live at SXSW 2016](https://www.nprillinois.org/the-x/2016-03-19/anderson-paak-the-free-nationals-come-down-live-at-sxsw-2016)  
   .Paakが客席前へ入り、複数の声によるチャントが実際のライブ空間を形成する記録。
4. [Complex: “Come Down” video premiere](https://www.complex.com/music/a/edwin-ortiz/anderson-paak-come-down-video-premiere)  
   .Paakが演奏者だけでなく複数の登場人物を演じ、Ernie Barnes《Sugar Shack》の群衆空間を映像として展開したことを記録している。
5. [NME: Anderson .Paak live in Birmingham](https://www.nme.com/reviews/anderson-paak-leaves-it-all-on-the-stage-as-he-delivers-a-high-energy-masterclass-in-birmingham-2541008)  
   会場の左・右・中央を別々の応答群として指揮する公演記録。

### 証拠から確認できる範囲

- .Paakは歌詞をビートから独立した情報層として置くのではなく、音色、旋律、cadenceを含む一つの楽器としてビートへ参加させる。
- .Paakは、情報を詰め込むトラックより、声が入る余白を残す制作を明確に評価している。
- Pitchforkの批評では、“Come Down”の声は単一の語り手に閉じず、主人公、煽る群衆、複数の人格が同じ空間にいるように配置される。
- SXSWやBirminghamの公演では、録音上の群衆的役割を、実際の観客の声や身体運動が占める。
- 公式映像では、.Paak一人が複数の人物を演じることで、一人の声／身体と一つの社会的役割を固定しない。

ただし、スタジオ版の個別stem、全ヴォーカル・テイク、各声の演唱者は未取得である。「録音内のすべての群衆声を.Paak一人が多重録音した」とは断定しない。

### スタジオ版が保存したもの

スタジオ版には実在のライブ観客はいない。それでも、呼ぶ側、拒む側、煽る側、返す側の位置関係が聞こえる。

ここで保存されているのは応答音声だけではない。次の声または身体が入りうる**役割の空席**である。

```text
ROLE_SLOT = {
  requested_role,
  opened_at,
  response_window,
  expected_energy,
  relation_to_pulse,
  current_occupant,
  vacancy_tension
}
```

- `requested_role`: 呼応、否定、煽り、合唱、句読点など
- `response_window`: いつ入れるか
- `relation_to_pulse`: One、裏拍、語尾、ブレイク後などの関係
- `current_occupant`: 録音声、演奏者、観客、無人
- `vacancy_tension`: 埋まらない状態が作る緊張

`current_occupant = NONE` でもslotは消えない。空白そのものが次の行為を要求する。

### スタジオからライブへの置換

```text
STUDIO:
  fixed beat
  + recorded protagonist
  + recorded / imagined response roles

LIVE:
  live or delegated beat
  + current protagonist
  + band / audience response roles
```

重要なのは、ライブでスタジオ音源を忠実再生することではない。録音で作られた役割関係を保持しつつ、その占有者を現在の身体へ交換できることにある。

```text
ROLE_CONTINUITY != AUDIO_CONTINUITY
```

- 音声が変わっても役割関係が続けば、曲の社会的骨格は保たれる
- 同じ音声を再生しても、誰も応答を引き受けていなければ、現在の出来事にはならない

### 一人と複数人を対立させない

“Come Down”には二方向の変換がある。

1. 一人の身体が複数の役割へ分かれる  
   .Paakが歌、ラップ、掛け声、人物演技を切り替える。
2. 一つの役割を複数の身体が共有する  
   群衆が同じチャントや運動を引き受ける。

したがって、楽器の「一人用」と「複数人用」を別モードへ分断する必要はない。

```text
ONE_BODY -> MANY_ROLES
MANY_BODIES -> ONE_ROLE
```

同じ `ROLE_SLOT` に対して、占有者の数と同一性だけを変えられる構造が必要になる。

### Sound Labへの更新仮説（未採用）

#### 1. ループではなくrole memoryを残す

```text
ROLE_MEMORY = {
  role_type,
  phase_relation,
  response_duration,
  last_energy,
  previous_occupants,
  unresolved_call
}
```

保存対象から完成音声を必須にしない。前周期で「どこに、どの種類の応答が求められたか」を残し、次周期の音は現在入力から作る。

#### 2. 空席を知覚できるようにする

画面へ「RESPONSEを入力してください」と説明文を出すのではなく、音と触覚で入口を示す。

候補:

- 呼びかけ後に特定帯域だけを空ける
- 次の着地点へ向かう弱い触覚パルスを残す
- 入力可能な領域が呼吸するように拡縮する
- 応答期限をカウント表示せず、音の減衰で感じさせる
- 誰も入らなければ空白を閉じず、緊張として次周期へ持ち越す

これはアフォーダンス候補であり、実機で直感的に理解されるかは未検証。

#### 3. 指を音色ではなく役割占有へ使う

```text
touch.begin  -> occupy(role_slot)
touch.move   -> shape(role_energy)
touch.split  -> divide_one_role_across_bodies
touch.join   -> merge_roles_into_chorus
touch.end    -> vacate_without_deleting_role
```

離指時に録音音声を永久再生しない。同時に、離指した瞬間に役割関係まで削除しない。

#### 4. 仮想応答を実在の応答へ差し替える

一人演奏時にシステムが最小応答を担うことは許容する。ただし、別人の接触、マイク入力、明示的な第二ジェスチャーが入った時点で、仮想応答は前景を譲る。

```text
if human_response_detected:
    virtual_response -> SKELETON | SILENCE
    human_response   -> FOREGROUND
```

人間の応答へシステム音を重ねて「盛った結果」を成功扱いしない。参加者の強度が小さくても、その差を保持する。

#### 5. 不在を自動修復しない

応答slotが埋まらない場合も有効な演奏結果とする。

```text
VACANCY_OUTCOME =
  SUSPEND
  | CARRY_TENSION
  | REDIRECT_CALL
  | CLOSE_WITHOUT_RESPONSE
```

自動フィル、歓声音源、生成ヴォーカルで穴を隠すと、呼びかけと応答の関係が偽装される。

### 最小プロトタイプ試験

#### 試験A — 一人で複数役割

- 一本目の接触で時間骨格を保持する
- 二本目で応答slotを開く
- 三本目または声で別役を占有する
- 同じ音色を使っても役割交代が知覚できるか確認する

#### 試験B — 二人で一役

- 一人目がcallを開く
- 二人目が同じ画面の別接触でresponseへ入る
- システムが二人目の音を完成ループへ吸収しないことを確認する

#### 試験C — 応答なし

- call後に誰も触らない
- 自動応答を出さない
- 空白が故障ではなく演奏上の未解決として知覚されるか確認する

#### 試験D — 仮想から実在へ

- 仮想応答が最小骨格を担う
- 実際の声または第二演奏者が入る
- 位相を壊さず仮想層が退き、人間の差異が前景化するか確認する

### 更新後の中心命題

“Come Down”が強いのは、一つのループの上へ声をたくさん重ねたからではない。

**固定ビートの余白に、異なる主体が入れる役割を作り、スタジオでは声の人格が、ライブではバンドと観客が、その空席を現在形で占有できるからである。**

Sound Labで保存すべきものも、前回鳴った応答そのものだけではない。次の誰かが別の仕方で入れる、時間上の空席である。

### 追加した未検証事項

- スタジオ版のヴォーカルstemと各演唱者
- 主人公声、群衆声、掛け声の正確な定位・音量・処理
- スタジオ版のrole slotとSXSW／Tiny Desk版の観客応答位置の対応
- 空席を説明文なしに触覚と音だけで理解できるか
- 無応答を初心者が故障と誤認する率
- 一台のiPhoneへ二人が触れる際の画面遮蔽と所有競合
- role memoryを保持しながら音声履歴を捨てる場合の曲同一性


## 17. 2026-09-03追補 — Shazamプレビュー実音検証の取得境界

### 今回確認できたもの

1. [Shazam: “Come Down”](https://www.shazam.com/en-us/song/1065681770/come-down)  
   Anderson .Paakの“Come Down”、曲ID `1065681770`、`BPM 98` を表示している。
2. 同ページの `Popular Segments` は、取得時点の `Past 7 Days` で `00:35–00:40` が最も頻繁に認識された区間だと表示している。
3. Shazamから同じ曲IDの[Apple Musicページ](https://music.apple.com/us/album/come-down/1065681363?i=1065681770)へ遷移でき、同ページには `Preview` 表示がある。

### 取得できなかったもの

今回の実行経路では、プレビュー音声のasset URLと音声バイト列を取得できなかった。

- Shazam／Apple Musicの公開テキスト面には `Preview` 表示があるが、音声URLは露出しなかった。
- Appleの公開lookup endpointへの直接取得は、この実行環境のネットワーク境界で完了しなかった。
- ブラウザ操作用runtimeもこのセッションでは利用できず、再生要素のnetwork requestを検査できなかった。

したがって、今回は次を**実施していない**。

- 音源を聴いたという報告
- 波形、スペクトル、onset、低域反復の計測
- 35–40秒区間の声、ドラム、ベースの実音判定
- スタジオ版とTiny Desk版の小節単位比較

プレビューが存在する表示と、プレビュー音声を取得・測定した事実は分ける。

### 98 BPMから計算できる範囲

以下は音声測定ではなく、Shazam表示値 `98 BPM` に基づく算術である。

```text
beat_duration = 60 / 98
              = 0.612244... seconds

4/4_bar_duration = 4 * beat_duration
                 = 2.448979... seconds

5_second_window = 5 / beat_duration
                = 8.1666... beats
                = 2.0416... bars
```

よって `00:35–00:40` は、98 BPMを前提にすれば約8.17拍、4/4なら約2.04小節ぶんに相当する。ただし、35秒地点が小節頭だとは確認していない。実音なしにこの窓を「二小節のフック」と確定しない。

### 認識窓と応答窓を分ける

前章の `ROLE_SLOT.response_window` は、曲中で誰かが応答できる時間を表す。一方、Shazamの `Popular Segments` は、利用者がその付近で曲を認識させた頻度の集計である。

```text
RECOGNITION_WINDOW != RESPONSE_WINDOW
```

```text
RECOGNITION_WINDOW = {
  observed_range,
  aggregation_period,
  recognition_frequency,
  track_identity,
  retrieval_epoch
}
```

- `RECOGNITION_WINDOW`: 外部の認識行動が集中した場所
- `RESPONSE_WINDOW`: 曲内で声・身体・観客が入れる場所

両者が重なる可能性はあるが、現在は未検証である。35–40秒が人気なのは、フック、音色、声、低域反復、動画上の出来事、利用状況など複数理由がありうる。人気認識区間だけから原因を一つへ固定しない。

また `Past 7 Days` は変動する観測値である。曲そのものの不変構造として保存せず、取得日とともに扱う。

### 次回の実音検証手順

合法かつ取得可能な同一プレビューが得られた場合、次の順で検証する。

1. **同一性固定**  
   track ID、取得URL、取得日時、duration、codec、sample rate、channels、ファイルSHA-256を記録する。
2. **時間軸固定**  
   プレビューが曲全体のどこから始まるかを確認する。プレビュー内の0秒を曲本体の0秒と誤認しない。
3. **テンポを独立推定**  
   onset envelopeからtempo候補を推定し、Shazamの98 BPMを強制入力しない。49／98／196 BPMの倍半テンポ候補を並べる。
4. **人気区間を比較**  
   曲本体の30–35秒、35–40秒、40–45秒で、低域energy、spectral flux、onset密度、反復自己相関を比較する。
5. **応答窓を注釈**  
   声のcall、response、休止、重なりを人手で時刻注釈し、機械推定と分離する。stem未取得なら話者同定を断定しない。
6. **小節位相を検査**  
   推定downbeatに対して35秒と40秒がどの位相にあるかを確認し、窓の境界を小節境界と同一視しない。
7. **ライブ版と別測定**  
   Tiny Desk版は独立音源として同じ項目を測り、スタジオ版の時間軸へ無理に整列させない。

### Sound Labへの更新仮説（未採用）

人気区間を、そのまま自動フック検出や自動ループ範囲へ使わない。外部の認識行動は、演奏者が触るべき場所を決める命令ではない。

候補となるのは、二つの窓を別レイヤーで表示すること。

```text
external_attention -> RECOGNITION_WINDOW
performable_opening -> RESPONSE_WINDOW
```

両者が一致したときだけ強調するのでなく、ずれを演奏材料にする。

- 認識が集中するが応答余地が小さい場所
- 認識は少ないが現在入力が大きく曲を変えられる場所
- 何度も認識される固定的特徴
- ライブでのみ開く応答位置

これにより「有名な五秒を再生する」設計と、「曲の時間へ現在の身体が入る」設計を区別できる。

### 今回の結論

Shazamから得られたのは、実音分析結果ではなく、**98 BPMという曲メタデータと、直近7日の認識行動が35–40秒へ集中したという外部観測**である。

この二つは、前章の `ROLE_SLOT` を直接証明しない。しかし、曲の内部構造と曲を取り巻く認識行動を分ける必要を明確にした。

次の実音研究では、35–40秒を「答え」として聴くのではなく、隣接区間と比較し、何が認識を集中させているか、そこに本当に応答可能な空席があるかを別々に測る。

### 追加した未検証事項

- Shazam／Apple Musicプレビュー音声の再取得
- プレビューが曲本体のどの時間範囲を含むか
- 35–40秒の拍位相、低域反復、onset密度、声の役割
- 人気区間が週ごとにどの程度変動するか
- `RECOGNITION_WINDOW` と `RESPONSE_WINDOW` の一致／不一致
- 49／98／196 BPMの倍半テンポ候補を実音からどう棄却するか
