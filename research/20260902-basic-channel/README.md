# Basic Channel研究

- research-id: `20260902-basic-channel`
- 研究対象: Basic Channel、Maurizio、Rhythm & Sound、Chain Reaction
- 現在の問い: 固定ループの再生ではなく、反復素材の内部状態をリアルタイム演奏する原理を抽出できるか
- 版: 初期研究記録
- 更新日時: 2026-09-02
- 実装変更: なし
- 製品採用状態: 未統合

## 1. この記録の証拠境界

この段階で取得したのは、Basic Channel公式カタログとMoritz von Oswald本人の講演記録である。対象曲の音源ファイルを取得して信号解析した状態ではない。

したがって以下を分離する。

- **資料で確認済み**: 公式カタログ上の作品、年代、本人が説明した制作方法
- **文献からの推論**: その制作方法を状態空間、演奏、UIへ翻訳した仮説
- **未検証**: 各曲のBPM、周波数、残響時間、反復周期、音圧、ステレオ相関などの数値
- **ユーザーの評価**: この記録では新しい実機評価を取得していない

前段階で提示した個別曲の聴感記述は、音源を直接取得して解析した観測ではない。本記録では確定的な音源分析として扱わない。

## 2. 一次資料

### 公式カタログ

- Basic Channel公式: https://basicchannel.com/label/Basic%2BChannel
- BCD公式曲目: https://basicchannel.com/item/BCD
- M-Series公式: https://basicchannel.com/label/M-Series
- Rhythm & Sound公式: https://basicchannel.com/label/Rhythm%2BSound
- Chain Reaction公式: https://basicchannel.com/label/Chain%2BReaction

公式カタログでは、Basic Channel系列は1993年のBC-01 `Enforcement`から1994年のBC-09 `Phylyps Trak II`までの9枚の12インチが核になり、1995年のCD `BCD`が複数曲のeditを収録する。

### Moritz von Oswald本人の講演

- Red Bull Music Academy, Barcelona 2008:
  https://www.redbullmusicacademy.com/lectures/moritz-von-oswald-early-morning-freestyles/

講演本文から確認できる要点:

1. Wackies作品について、声、低域、打楽器、エフェクトのための空間があり、要素数が多すぎないことを評価している。
2. 伝統的なダブのステレオへのライブ・ミックスを推奨し、その操作を直観的で再現不能なものとしている。
3. `Mango Drive`は完全なライブ・ミックスで制作され、短期間ではなく数週間かけて残す要素を決めたと説明している。
4. Basic ChannelとMaurizioで、エフェクトを音楽へ統合し、輪郭の定まりきらないパターンが互いに作用しながら絶えず変化する方法を使ったと説明している。
5. リズムは動いているが、全体はポラロイド写真のように静止している状態として語っている。
6. 出来事が次々に生じる「vertical」な見方より、「horizontal」な見方を好むと述べている。
7. Basic ChannelとMaurizioのレコードはデトロイトでカッティングされ、米国で製造されたと述べている。

## 3. 系列を別々の作動モードとして捉える

これは公式分類ではなく、本研究上の整理である。

| 系列 | 作動モードとしての仮説 | 検証状態 |
|---|---|---|
| Maurizio | テクノの推進力を少数要素へ還元する | 資料＋要音源解析 |
| Basic Channel | 反復パターンをエフェクト回路内の変動体へ変える | 資料＋要音源解析 |
| Rhythm & Sound | 声、ベース、空間を前景化し、ダブの構造へ近づく | 資料＋要音源解析 |
| Chain Reaction | 同じ原理が他作家にどう分岐したかを見る比較群 | 公式カタログ確認、内容未解析 |

「Basic Channelがダブ・テクノを発明した」という一文で閉じない。調査すべき対象はジャンル名ではなく、同じ制作チームが別名義・別レーベル間で何を保持し、何を変更したかである。

## 4. 中核仮説: ループではなく状態軌道を演奏する

入力パターンを `u(t)`、ディレイ／残響／フィルター内部の記憶を `x(t)`、演奏操作を `theta(t)`、出力を `y(t)` とする。

```text
x(t+1) = A(theta(t)) x(t) + B(theta(t)) u(t)
y(t)   = C(theta(t)) x(t) + D(theta(t)) u(t)
```

通常のルーパーでは、演奏の主要単位は保存された音声 `u(t)` の追加、削除、再生開始である。ここで抽出するBasic Channel仮説では、素材 `u(t)` を少数に留め、演奏の主要単位を内部状態 `x(t)` と経路 `theta(t)` の変化へ移す。

その結果、同じ入力が繰り返されても、直前まで回路に残ったエネルギーによって毎回異なる出力になる。

これは「ランダムに音を変える」こととは違う。現在の出力が過去の操作に依存する、履歴依存の演奏である。

## 5. 音源解析で検証する仮説

### 対象候補

- BC-02: `Phylyps Trak`, `Phylyps Base`, `Axis`
- BC-05: `Inversion`, `Presence`
- BC-06: `Quadrant Dub I`, `Quadrant Dub II`
- BC-08: `Radiance I`, `Radiance II`, `Radiance III`
- BC-09: `Phylyps Trak II/I`, `Phylyps Trak II/II`
- BCD収録editとの比較
- 比較群: Maurizio M-Series、Rhythm & Sound、初期Chain Reaction

### H1: 入力パターンの反復性より、音響状態の非反復性が高い

検証:

- onset strengthとtempogramで拍節周期を推定
- self-similarity matrixで小節単位の反復を検出
- 同じ位相の反復窓同士で、スペクトル包絡・残響尾・ステレオ相関を比較
- イベント列は反復しているのに残差成分が反復しないか確認

### H2: 変化点はノート追加より、帯域・密度・残響比の移動として現れる

検証:

- spectral centroid / rolloff / flatness
- band別RMS
- transient-to-residual比
- change-point detection
- 変化点前後のonset数と残響残差を分離して比較

### H3: ディレイ／残響の尾が独立したリズム層を作る

検証:

- HPSSまたは音源分離結果だけを根拠にせず、元ミックスとの照合を残す
- onset後の減衰包絡から反復ピークを探索
- 主拍との位相差分布を計測
- 反復ピークが固定グリッドか、時間とともに揺れるかを比較

### H4: 「horizontal」は無変化ではなく、低いイベント新規性と高い音色変動の同居である

検証:

- event novelty
- timbral flux
- section boundary density
- 長時間窓と短時間窓の両方で計測し、平均値だけで平坦化しない

### H5: 名義間の違いは音色だけでなく、状態変数の配分に現れる

暫定的な比較軸:

- 低域がノートとして分離するか、全体の圧力として働くか
- ドライ音／残響音の占有率
- 声の有無と空間の確保
- キックが推進力を独占する割合
- ミックス内の空白時間
- 変化を担う帯域

## 6. 解析工程

既存の `research/music-analysis/` に依存する。ただし、既存分析器の出力をそのまま音楽的事実に変換しない。

1. 正規に利用できる同一マスターの音源を用意する
2. ファイルID、版、サンプルレート、長さ、入手経路をmanifestへ固定
3. ラウドネス正規化前後を別々に保持
4. 全曲集計の前に、複数の短区間を人間が注釈
5. onset、tempogram、recurrence、spectral、stereo、残響残差を抽出
6. edit／別version間を同じ位相へ整列
7. 数値結果と聴取注釈が一致しない箇所を失敗例として保存
8. 音源タイトルを隠した比較を行い、Basic Channelらしさを後付けしない
9. 復号後に名義・年代・マスター差を検討
10. 分析限界をREADMEへ残す

## 7. 製品へ採用する候補

まだ統合決定ではない。

### 7.1 タッチは音源ではなく経路を掴む

| ジェスチャー | 候補となる状態操作 |
|---|---|
| 接触開始 | 選択した音を場へ注入 |
| X位置 | フィルター中心／遅延時間の連続移動 |
| Y位置 | dryからstate-memoryへの深度 |
| 接触面積 | feedbackへ送るエネルギー |
| 移動速度 | パラメータ追従速度と慣性 |
| 長押し | 状態を保持するが固定しない |
| 指を離す | 入力停止。残留状態は自然減衰 |
| 複数指 | 別音源追加ではなく、複数経路の同時操作 |

圧力はiPhone機種・API上で安定した入力として取得できるとは限らないため、設計の必須条件にしない。接触面積、速度、滞在時間などで代替可能か実機検証する。

### 7.2 フィードバック安全境界

演奏性を殺さず、発散だけを抑える。

- ループ内DC blocker
- 周波数依存のsoft saturation
- feedback係数の単純な固定上限だけに依存しない
- 出力limiterは最後の防壁とし、常時潰さない
- 内部エネルギー量を可視化
- 接触を離しても減衰しない異常状態にpanic gestureを用意
- スピーカー／マイクの音響フィードバックと内部delay feedbackを区別

### 7.3 四トラックを四つの完成ループにしない

四トラックを独立した録音物の積み重ねとして固定すると、ユーザーが拒否しているワンループ垂れ流しへ戻る。

候補:

- track = 音声ファイルではなく励起源
- 各trackに独立state memory
- track間sendで他トラックの過去状態を励起
- 全トラックの録音／再生ボタンを中心に置かない
- 現在鳴っている素材数より、現在生きている状態数を表示する

## 8. 採用しない点

- 「ダブ・コード」プリセット一個でBasic Channelを代表させる
- テープノイズやローファイ処理を表面上追加するだけの模倣
- 既成のXYパッドへdelayとfilterを固定割当するだけのUI
- 変化がないことをミニマルと呼ぶ
- ランダム変調を手動ミックスの代用品にする
- フィードバックを危険回避のため完全に消す
- Basic Channel、Maurizio、Rhythm & Soundを同じ音色プリセットとして扱う

## 9. 依存する研究

- 取得済み: `research/music-analysis/`
- 名称のみ参照、本文未取得: Dub、Jeff Mills、Autechre、Aphex Twin、Charlie Hunterの各研究
- 製品側で接続が必要: マルチタッチ、四トラック、リアルタイム演奏、内部フィードバック、iPhoneマイク

本文未取得の研究内容は、この記録で補完していない。

## 10. 失効した判断

- 前段階の個別曲に関する聴感記述を、直接音源解析済みの観測として扱う経路は失効。
- 「Basic Channel = ダブ・テクノの定型音色」という扱いは採用しない。
- ループが固定なら演奏も固定になる、という前提は採用しない。検証対象は入力の固定性と状態軌道の可変性の分離である。

## 11. 未検証事項

- 対象音源ファイルの取得と版の同定
- 各曲の数値解析
- 手動ミックスの操作履歴を音源からどこまで推定できるか
- カッティング／マスタリングとミックス由来の質感の分離
- iPhoneでの複数feedback networkのCPU負荷
- 接触面積の端末差
- 内蔵スピーカー使用時のハウリング制御
- Basic Channel型の水平性が、即興演奏時にも退屈へ落ちない条件
- 他研究との接続後に残る固有性

## 12. 次の研究工程

次は音源を取得したときに、まず `Quadrant Dub I/II`、`Presence`、`Radiance I-III`の三群を同じ方法で解析する。曲名を見た印象で説明を作らず、反復窓の一致度、残響残差、帯域別変動、変化点を先に出す。その後でMoritz本人の「horizontal」「patterns constantly changing」という説明と照合する。


## 13. 継続研究: 音源到達性と概念の発生順序

### 13.1 音源到達性の実測

2026-09-02の最初の到達試験では、SoundCloudとApple Musicの再生面までは確認したが、音声ファイルを解析器へ渡せなかった。Spotify検索も試したが、これは本研究群で決めた正式取得経路ではない。

2026-09-03にユーザーの訂正を受け、正式経路をShazam／Apple Music Catalog APIへ戻した。Shazam検索から曲ID、ISRC、全曲尺、30秒Preview URLを取得し、6ファイルを解析器へ入力できた。測定結果は第15節に記録する。

| 経路 | 現在の位置づけ | 信号解析への使用 |
|---|---|---|
| Shazam／Apple Music Catalog API | 本研究群の正式取得経路 | 12-inch版と`BCD`版、計6 Previewを取得・解析 |
| Basic Channel公式SoundCloud | 公式公開名義と曲ページの確認 | 音声取得には未使用 |
| Apple Musicのブラウザ再生面 | 表示・再生の補助確認 | 音声取得には未使用 |
| Spotify | 誤って使用した経路。正式な取得・解析証拠から除外 | 未使用 |

参照:

- https://soundcloud.com/basicchannelofficial/quadrant-dub-i
- https://soundcloud.com/basicchannelofficial/radiance-i
- https://soundcloud.com/basicchannelofficial
- https://music.apple.com/us/song/quadrant-dub-i/276360114

Spotifyで得た存在確認を、以後の音源取得、版同定、信号測定の証拠には使わない。

### 13.2 「dub techno」という完成概念から逆算しない

Moritz von Oswaldへのインタビューでは、次の順序が説明されている。

1. 先に音楽を作る
2. その音が作品のconceptを決める
3. その後でartwork、label、公開方法を決める
4. Basic Channelは「dub technoを作る」という企画から始まったものではない

同じインタビューで、minimal technoは冷たいという聞き手の規定をMoritzは否定し、warm、emotional、deepとしている。また、長尺作品はクラブで聴く環境が重要だと述べている。

参照:

- Andrew Parks, “A QUICK TALK WITH … Moritz Von Oswald”
  https://www.self-titledmag.com/a-quick-talk-with-moritz-von-oswald-about-getting-deep-with-dubstep-the-richness-of-the-next-moritz-von-oswald-trio-record-and-why-minimal-techno-isnt-as-cold-as-you-think/

証拠上の注意: 取得時点の同ページには本文と無関係な不正・スパム的リンク列が混入していた。インタビュー本文は検索結果とページ本文で一致したが、サイト全体の現在の完全性は保証できない。このため、この資料単独で新しい歴史的断定を作らず、Moritz本人のRBMA講演および公式カタログと整合する範囲で使う。

### 13.3 三層モデルへの更新

前節の状態空間モデルだけでは、再生媒体と部屋を外部条件へ追い出しすぎていた。Basic Channel研究では次を分ける。

```text
u(t)      : 少数の励起素材
x(t)      : delay / reverb / filter内の履歴
theta(t)  : 手動ミックスと演奏操作
M         : vinyl、デジタル、スピーカー等の媒体条件
E         : club、部屋、ヘッドホン等の聴取環境

y_mix(t)  = StateNetwork(u, x, theta)
y_heard(t)= Environment(E, Medium(M, y_mix))
```

重要なのは、`M`と`E`を音色プリセットとして偽装しないことである。クラブ感をreverbで足すのではなく、低域の再生可能性、残響のマスキング、モノ／ステレオ、内蔵スピーカーとヘッドホンの差を実測条件として扱う。

### 13.4 Dubplates & Masteringを音色神話へ使わない

Robert Henkeは、Basic Channelが1995年にDubplates & Masteringを設立し、自身が1996〜1998年にmastering engineer／vinyl cutterとして働いたと記している。Rashad Beckerとの対話では、masteringを媒体や部屋など特定目的へ作品を仕上げる工程として説明し、周波数・振幅・位相、mid/side、EQ、compression、distortion、vinylの物理条件を論じている。

参照:

- Robert Henke / Rashad Becker, “Mastering”
  https://roberthenke.com/interviews/mastering.html

ただしこの対話は2008年のRashad Beckerの実務についての資料であり、1993〜1994年のBasic Channel各盤の実際のsignal chainを証明しない。「Basic Channelの音はtube compressorで作られた」などの機材断定には使わない。

ここから採るのは、作品、mastering、媒体、再生環境を一つに潰さず、それぞれを比較する必要があるという方法だけである。

### 13.5 製品設計への新しい接続

#### 音からUIを決める

先に「dub画面」「宇宙的な見た目」「霧状のvisual」を作り、そこへ音を従わせない。

1. 履歴依存feedback networkを実装する
2. 指で操作して、身体的に区別できる状態を採取する
3. その状態差を最小の表示へ写す
4. 操作を説明する名前ではなく、挙動から名前を決める

これは名称研究・affordance研究との接続候補だが、当該研究本文をこのブランチではまだ取得していないため、統合判断にはしない。

#### 長尺を「長いループ」にしない

長尺の必要性を、同じ素材を長く回す免罪符にしない。長い時間でだけ知覚できる状態変化を設計する。

- 数秒: touchと音の因果が分かる
- 数十秒: feedback履歴が別のリズムを作る
- 数分: 同じ素材の役割が前景／背景間を移る
- 演奏全体: scene切替なしでも不可逆な履歴が残る

#### 環境を演奏条件へ戻す

最低でも次の三条件を別々に試す。

- ヘッドホン
- iPhone内蔵スピーカー
- マイク入力を開いたスピーカー再生

同じparameter mappingを共用しても、feedback上限、low-end補償、state表示を同じにしない。環境差を自動で「補正して消す」だけでなく、演奏者がその差を利用できる余地を残す。

### 13.6 更新された中核判断

Basic Channelから採る対象は「ダブ・テクノの音」ではない。

- studioをinstrumentとして扱う
- 手動mixを再現不能なperformanceとして残す
- 少数要素の関係を長時間変化させる
- 媒体と聴取環境を作品の外へ捨てない
- 音がconceptとsurfaceを決める順序を守る

したがって製品側の問いは、「どうすればBasic Channel風に聞こえるか」ではなく、**固定された少数素材から、演奏者の履歴と環境によって同じ状態へ戻れない楽器をどう作るか**へ更新する。

### 13.7 次の未完了工程

- 正規に解析可能な音源ファイルまたは明示的に利用可能なpreview fileの取得
- `Quadrant Dub I`の90秒previewが曲中のどの区間かの同定
- original 12-inch、`BCD` edit、デジタル再発の版差固定
- 既存`research/music-analysis/`へ渡すmanifest作成
- 名称研究／affordance研究の本文取得後、sound-firstの順序と照合


## 14. 継続研究: versionは短縮版ではなく、別の状態軌道である

### 14.1 公式カタログが示す二つの編集方針

公式カタログ上で、1995年の`BCD`と2008年の`BCD-2`は役割が異なる。

- `BCD`: `Quadrant Dub I Edit`、`Radiance II Edit`、`Lyot Remix Edit`、`Presence Edit`、`Q1.1 Edit`、`Radiance III Edit`など、editを明示した曲を多く含む
- `BCD-2`: 公式説明で、1993〜1995年にvinylで発表した6曲の`full length versions`を収録するとされる

参照:

- https://basicchannel.com/item/BCD
- https://basicchannel.com/item/BCD-2
- https://basicchannel.com/label/Basic%2BChannel

両CDに同じ曲の短尺版と長尺版が一対一で並んでいるわけではない。したがって、`BCD`対`BCD-2`を直接の版違い比較にはしない。

比較単位は次のように固定する。

| 比較群 | 対象 | 調べること |
|---|---|---|
| edit群 | 元12-inch版 ↔ `BCD`の同名`Edit` | どの時間帯を切ったかではなく、どの状態遷移を残したか |
| full-length群 | 元12-inch版 ↔ `BCD-2`収録版 | 同一尺でもmastering／媒体差があるか。未確認の同一マスター扱いをしない |
| 表記非Edit群 | `BCD`で`Edit`表記のない`Radiance I`、`Q1.2`等 | 表記が実際の尺・版差と一致するか。`Radiance I`は第15節で別尺・別ISRCと判明 |

### 14.2 一つの長さではなく、三つの時間を分ける

Moritz von OswaldのRBMA講演では、以下が同時に語られている。

1. 制作は、少数要素の何を残すか決めるために数日ではなく数週間かかり得る
2. 最終的なdub／mixはライブで行われ、直観的で再現できない
3. 反復作品は途中で切らず、grooveへ入り、少数要素がどう扱われるかを時間をかけて聴く

参照:

- https://www.redbullmusicacademy.com/lectures/moritz-von-oswald-early-morning-freestyles/

ここから、単一の「長尺性」ではなく三つの時間を区別する。

| 時間 | 内容 | 製品側で混同すると起きること |
|---|---|---|
| 選別時間 | 素材を走らせ、残す要素を判断する制作期間 | 長く悩んだこと自体を演奏の深さと誤認する |
| 操作時間 | live mixで一回だけ生じるフェーダー／send／effect操作 | automation再生を即興と呼んでしまう |
| 知覚時間 | 聴き手が反復内の微細な役割変化を知覚する時間 | 同じループを長く流すだけで水平性が生まれると誤認する |

この分離により、「制作に時間をかける」「長く再生する」「ライブで操作する」は互いの代用品ではないと判断する。

### 14.3 versionは原曲の修正版ではない

Moritzは、version／dubについて、instrumentalから別の展開を作り、mixを変え、以前の仕事の別のlevelへ入る方法として説明している。また、小さな失敗を全て除去するより、vibeが成立したtakeを残す判断も述べている。

この資料から採る仮説は次である。

```text
source material
   ├─ trajectory A -> captured version A
   ├─ trajectory B -> captured version B
   └─ trajectory C -> discarded / later source
```

versionは「正本を少し修正したもの」ではなく、同じ素材から別の操作履歴を通って捕獲された兄弟関係として扱う。どれか一つを完成版へ昇格させた後も、他を失敗版として自動的に降格しない。

ただし、全takeを保存すればよいという結論ではない。資料で確認できるのは、結果を聴き、残すものを選び、成立した瞬間を捕獲するという往復である。

### 14.4 音源解析へ追加する仮説

#### H6: editは均等な時間短縮ではなく、状態軌道の編集である

検証方法:

1. 元12-inch版と`BCD Edit`を波形類似だけでなく、onset／帯域包絡／残響残差で局所整列する
2. editで残った区間と除かれた区間を同定する
3. 変化点、feedback蓄積、前景／背景交代の直前直後が保存されたか測る
4. 単なる尺比率と、状態変化の保存率を分ける

編集後も曲の性格が保たれるなら、保持されたのは全時間の縮小コピーではなく、状態軌道の節点である可能性がある。

#### H7: full-lengthでしか観測できない遅い変数がある

候補:

- 数十秒を越えて蓄積する残響エネルギー
- 帯域の重心が数分単位で移る傾向
- 同じ要素の前景／背景比率
- listenerが予測を固定した後にだけ知覚できる微差
- 一度減衰した状態が同じ形では戻らない履歴

短いpreviewはH7の検証には不十分である。previewから取得できる局所特徴と、全長が必要な遅い特徴を解析表で別欄にする。

### 14.5 楽器設計への接続候補

四トラックを音声loopの容器ではなく、状態軌道の分岐元として扱う。

- `capture`: 出力音声だけでなく、操作履歴とstate snapshotを一緒に捕獲する
- `continue`: 捕獲後も現在状態をresetせず演奏を続ける
- `fork`: 過去のsnapshotを再生するのではなく、その状態から別軌道を開始する
- `compare`: 音量差を揃えた上で、二つの軌道がどこから別れたか聴けるようにする
- `discard`: 失敗を自動修正せず、演奏者がtake単位で捨てる

これは実装決定ではない。まず内部feedback networkが同じsnapshotから再開可能か、また再開時の完全再現が演奏を固定化しないかを検証する。

### 14.6 現在の設計判断

Basic Channel研究から抽出する「反復」は、次の三つを同時に満たす必要がある。

1. 入力素材は反復できる
2. 内部状態は操作履歴により変化し続ける
3. 捕獲されたversionは、元素材ではなくその一回の軌道を記録する

したがって、ルーパーの代替案は「ループを賢く変形する装置」では足りない。必要なのは、**同じ素材から複数の成立した演奏史を分岐させ、それぞれをversionとして捕獲できる楽器**である。

### 14.7 次の未完了工程

- 12-inch版と`BCD Edit`の正規音源を同一曲単位で揃える
- 版ごとのduration、catalog number、媒体、mastering表記をmanifestへ固定
- edit位置を自動推定した後、人間の聴取で状態遷移を注釈
- full-length仮説を90秒previewで検証したと誤認しない
- snapshot／forkを既存四トラック設計へ持ち込む前に、CPU・メモリ・再現性を測る


## 15. Shazam Previewによる初回信号解析

### 15.1 取得経路と版同定

ShazamのApple Music Catalog検索から、`Quadrant Dub I`、`Radiance I`、`Presence`について、1994年の12-inch収録版と1995年の`BCD`収録版を取得した。

| 短縮名 | Apple曲ID | album | 全曲尺 | ISRC | Preview SHA-256 |
|---|---:|---|---:|---|---|
| Quadrant 12 | 276360114 | Quadrant Dub | 936.017秒 | DEW259400126 | `084cc6378ac59674bc3862e442c64c5ff798274a20611e05f8de1d4ed6b2c266` |
| Quadrant BCD | 47296248 | BCD | 416.960秒 | DEW259500104 | `bdc8747b5001245ebaf54cf6d15c911d53c377c2b17e520479dad56e43520dcf` |
| Radiance 12 | 276508664 | Radiance | 811.138秒 | DEW259400130 | `9923083261c4714992cfa14acca66721d333763c25e7ce844c4e4818ef91e86a` |
| Radiance BCD | 47297098 | BCD | 477.867秒 | DEW259500110 | `fd53863bb76ed9b89883eb502a48ce17b81422d418b653288e77063ce925a9c1` |
| Presence 12 | 276503162 | Inversion | 1239.951秒 | DEW259400125 | `9785b5d9f19fcd2f9e3f64bd851e238b497459b212cbb0cfbd1f8d38bcb1ecaf` |
| Presence BCD | 47296710 | BCD | 497.493秒 | DEW259500107 | `5b693ae345dd1d2721a61e7712f4406de18e031183700183ccea18b9af624dec` |

全PreviewはAAC、44.1kHz、stereo、取得ファイル尺29.976961秒、復号後有効音声約29.9291秒だった。Preview本体はGitへ保存しない。

重要な訂正: Apple Music上の`BCD`版`Radiance I`は曲名に`Edit`が表示されないが、1994年版と全曲尺もISRCも異なる。曲名だけでは版を同定できない。

### 15.2 共通解析器の使用

独自の解析器を先に作る経路は採用しなかった。GitHub `main`の`research/music-analysis/`から次を取得して使用した。

- `calibrate_analyzer.py`
- `analyze_previews.py`
- `reliability_audit.py`

合成信号による校正は12/12項目で成功した。窓別信頼性監査には`Essentia 2.1b6.dev1389`を使用した。

### 15.3 校正済み基本測定

以下は開始位置不明の約30秒区間に対する測定であり、全曲値ではない。

| Preview | RMS dBFS | spectral centroid | onset/s | 周期候補 |
|---|---:|---:|---:|---|
| Quadrant 12 | -12.83 | 1359.4 Hz | 4.076 | 61.89 / 124.53 / 83.35 |
| Quadrant BCD | -18.44 | 995.5 Hz | 4.444 | 61.89 / 124.53ほか |
| Radiance 12 | -16.80 | 2904.2 Hz | 7.217 | 175.19 / 53.83 |
| Radiance BCD | -21.17 | 2188.9 Hz | 5.714 | 175.19 |
| Presence 12 | -24.19 | 1122.5 Hz | 9.188 | 63.80 / 61.52 |
| Presence BCD | -25.76 | 920.0 Hz | 9.322 | 63.80 / 62.64 / 61.52 |

RMS差をmasteringの音圧差とは断定しない。Previewの開始位置、Catalog側の処理、元の状態差を分離できていないためである。周期候補も音楽上のBPMそのものではない。

### 15.4 10秒×3窓の信頼性監査

| Preview | 窓BPM推定 | 判定 | 信頼度上の扱い |
|---|---|---|---|
| Quadrant 12 | 124.05 / 123.99 / 123.56 | 直接安定 | 約124 BPMの局所pulse候補を保持 |
| Quadrant BCD | 96.12 / 123.39 / 123.66 | 不安定 | 単一BPMを棄却 |
| Radiance 12 | 172.27 / 172.27 / 166.19 | 数値上は直接安定 | 全体信頼度0.791、方式差4.65%のため単一BPMを棄却 |
| Radiance BCD | 71.89 / 106.72 / 165.76 | 不安定 | 単一BPMを棄却 |
| Presence 12 | 62.96 / 62.27 / 62.35 | 直接安定 | 約62.5 BPMの局所pulse候補を保持 |
| Presence BCD | 62.43 / 62.60 / 61.87 | 直接安定 | 約62.5 BPMの局所pulse候補を保持 |

調推定は、3窓一致した`Radiance 12`の`C# minor`だけが既存採用規則を通過した。ただし、これもPreview区間の推定であり、全曲の調性や作曲意図へ拡張しない。

### 15.5 ここから言えること

#### Presenceは版を越えて局所pulseが残る

`Presence`の両Previewは、全曲尺が約20分40秒と約8分17秒で大きく異なる。一方、Preview内では両方とも約62.5 BPM候補が3窓で安定し、onset rateも9.188／9.322と近い。

これは、edit後も局所的なpulse familyが保持されたという仮説を支持する。ただし、両Previewが原曲上の対応区間かは未同定であり、「状態軌道の節点を保存した」というH6までは証明しない。

#### Quadrantでは同じ周期候補と窓不安定が同居する

`Quadrant`両版の基本解析には61.89／124.53 BPM近傍が現れた。しかし`BCD`版の最初の10秒窓だけ96.12 BPMへ外れた。

ここで単一BPMへ平均化すると、区間内でオンセット検出の手掛かりが変わった事実を消す。Basic Channel型の反復を調べる際は、pulseの存続と、表面上のイベント密度の変化を別変数にする必要がある。

#### Radianceは単一BPM推定が最も壊れやすい

`Radiance 12`は高いspectral centroidとonset rateを示したが、BPM信頼度が低く二方式も不一致だった。`BCD`版は3窓が71.89／106.72／165.76 BPMへ分裂した。

これはテンポが実際に変化した証明ではない。残響、連続音、帯域変化、Preview位置によって、beat trackerが異なる層をpulseとして掴んだ競合仮説を残す。ここでは「正しいBPMを決める」より、どの音響層が周期推定を支配したかが研究対象になる。

### 15.6 製品設計への更新

初回解析から、状態表示を一つのtempo値へ従属させない。

- `pulse`: 複数窓で残る周期候補
- `event density`: onset rateとその時間変化
- `spectral field`: 帯域重心と広がり
- `confidence`: 解析器同士・時間窓同士の一致
- `ambiguity`: 複数の層が別の周期を示す状態

演奏画面で曖昧さをエラーとして消すのではなく、安定したpulseの周囲で別の層が動いていることを表示できる可能性がある。これは実装決定ではなく、Basic Channelの反復を一つのBPMへ平坦化しないための設計候補である。

### 15.7 未完了

- Preview開始位置の同定
- 12-inch版と`BCD`版の対応区間整列
- `Quadrant Dub II`、`Radiance II/III`、`Inversion`への標本拡張
- 原ミックスと推定stemを照合した周期層の分離
- 30秒を越えるH6／H7の検証
