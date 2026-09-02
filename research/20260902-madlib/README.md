# Madlib研究

- research-id: `20260902-madlib`
- 研究対象: Madlib（Otis Jackson Jr.）の制作方法、リズム、編集、変名、共同制作
- 現在の問い: Madlibの音楽を「サンプリングの巧さ」「ローファイ」「ヨレ」へ縮めず、その時間構造をリアルタイム演奏楽器へどう接続できるか
- 状態: 継続研究中
- 更新日時: 2026-09-02
- 実装変更: なし
- 触る実装パス: なし

## 0. 現在の結論

Madlibの核心は、珍しいレコードを発見することだけではない。

レコードを採取する、短く切る、自分で楽器を演奏する、声の速度を変える、架空の演奏者を作る、大量に生成する、別の人物に選ばせる、という工程が一続きになっている。ヒップホップ、ジャズ、ソウル、レゲエ、アフリカ音楽、ブラジル音楽、クラウトロックを分類して引用するのではなく、異なる録音時間を同じ現在へ持ち込む。

Madlibのリズムは単純な「ヨレ」ではない。ひとつの正しいクロックへ全素材を従わせず、異なる時間を持つ演奏、サンプル、声、引用音声を同居させる方法として捉える。

## 1. 一次資料から確認できた事実

### 1.1 機材は制作原理ではない

2002年のRed Bull Music Academy講演で、MadlibはBOSS SP-303を示し、ヒップホップ作品の中心機材として使っていると説明した。SP-1200やMPCも使うが、主にSP-303を使い、「どんな音楽でも作れる」「安い」と話している。

同じ講演では、Madvillain初期音源をSP-303と小型デジタル卓で録音したこと、家庭で落ち着いた状態で制作していることも確認できる。

2016年の講演では、Kanye Westへ渡したビートの一つをiPadで作ったと話している。後年の `Bandana` についてもiPad制作を表明している。

ここから確認できるのは特定機材への忠誠ではなく、安価で小型の機材でも生成を止めないこと。SP-303の音色を模倣するだけではMadlibの制作原理を再現したことにならない。

### 1.2 human time

MadlibはYesterdays New Quintet系列について、次の手順を説明している。

1. 最初にドラムを録る。
2. その後は必要な演奏を重ねる。
3. ドラム録音では外部メトロノームではなく、頭の中の拍を使う。
4. オフビートになった部分も自分の好みとして残す。
5. ドラムを録った後、別トラックへベースを録る方法を `human time` と呼ぶ。
6. ライブ演奏とシーケンスを場合によって使い分ける。
7. 基本録音には小型8トラック、アナログ／デジタル双方を使用し、ドラムをワンマイクで録る場合がある。

重要なのは、各パートが共通メトロノームへ個別に同期するのではなく、先に録音された自分の演奏を次の自分が聴いて反応する点である。

### 1.3 速度と初回性

Madlibは制作を「freestyle approach」と呼び、多くが自発的で、ひとつのトラックを何日も練り続ける方法は取らないと話している。別のインタビューでは、最初のテイクを残し、短時間で次の音楽へ移ると説明している。

ただし、これは作品全体が無編集という意味ではない。Peanut Butter Wolfなど別の人物が大量の素材から選び、アルバムとして配列する工程が存在する。Madlibの高速生成と、第三者による選択・編集は分けて考える必要がある。

### 1.4 Quasimotoの声と人格

Quasimotoは、Madlibが通常の自分のラップ声を好まなかったことから生まれた。テープを遅くした状態でゆっくりラップを録音し、再生速度を戻して高い声を作った。単なる後処理のピッチ変更ではなく、録音時の発声速度と身体運動を変えている。

Quasimotoは当初、自分と身近な仲間だけで聴く私的なビートテープのために作られた。Peanut Butter Wolfがその録音を聴き、`The Unseen` としての発売を促した。

### 1.5 変名と架空バンド

初期Yesterday’s New Quintetでは複数の演奏者名が設定され、Madlib自身がドラム、ベース、鍵盤などを多重録音している。2002年の講演で、20以上の変名があり、聴き手に別人だと思わせたいと話している。

ただし、後に拡張されたYesterdays Universe全体までMadlib一人の架空名義とは扱わない。公式ガイドはKarriem Riggins、Ivan “Mamao” Conti、Todd Simon、Dan Ubickなど、Madlib圏外でも活動する実在奏者の参加と、記録されたライブ演奏を明記している。

本研究では、初期YNQの変名を作品整理用の偽名ではなく、演奏判断を変えるための仮想的な身体として扱い、拡張後の実在奏者との共演は別層として記録する。

### 1.6 Madvillainy

Stones Throwの記録では、`Madvillainy` は2002年に制作が始まり、2004年に発売された。短い曲、汚れた音、コーラス不在、初聴では明瞭でない主題が、当時の商業ヒップホップの慣例に逆行していた。

22曲を約46分へ収め、短いインタールードで連結する。Madlibの短時間・断片生成と、DOOMの慎重な作詞／録音が衝突することで成立している。Madlibの音楽だけを「即興」、作品全体を「即興」と同一視しない。

### 1.7 Freddie Gibbsとの選択型共同制作

`Piñata` ではMadlibが大量のビートCDを渡し、Freddie Gibbs側が選択した。Gibbsはこの作業を、Madlibのクレートを掘り、パズルを組むことに近いと説明している。

Madlibは、Gibbsが別の場所で声を録音した後、必要に応じてコーラスやホーンなどを追加する方法を説明している。専用ビートを逐次発注・制作する関係ではなく、先行する素材庫をラッパーが探索し、声が入った後に最小限の仕上げを行う。

後のインタビューでMadlibは、`Bandana` ではGibbsを前へ出すため、ビートをよりミニマルにしたと話している。

### 1.8 Sound Ancestors

`Sound Ancestors` の音楽素材はMadlib、編集・構成・マスタリングはKieran Hebden（Four Tet）である。

したがってこの作品は、Madlibの生成物そのものだけでなく、他者がその素材庫を聴き、アルバムへ構成した結果として研究する必要がある。

## 2. 四種類の時間構造

以下は、上記資料と作品構造から導いた分析仮説である。音源ファイルを使った信号計測はまだ行っていない。

### 2.1 Human Time

対象: Yesterday’s New Quintet、Monk Hughes周辺。

ドラムの揺れを修正せず、次のベース演奏がその揺れへ追従する。ズレは誤差ではなく、次の演奏を発生させる原因になる。

```text
頭の中の拍
  ↓
ドラムの揺れ
  ↓
ベースがドラムへ追従
  ↓
鍵盤・打楽器が前二層へ追従
```

全パートを同じグリッドへ揃える通常の多重録音とは異なり、層を重ねるたびに時間偏差が継承・変形される。

### 2.2 Loop Lock

対象: Madvillain、Quasimotoの一部。

四小節／八小節の完成した伴奏ではなく、旋律の途中や和声が解決する直前を短く閉じ込める。ループは反復するたびに続きを期待させるが、解決は来ない。ラップだけがループ外の文章時間を進める。

この方法では、トラック展開がラッパーを導くのではない。閉じた音響空間へラッパーが時間を持ち込み、声が消えた時点で曲も終了できる。

### 2.3 Montage Time

対象: Quasimoto、Beat Konducta、Medicine Show。

- ビートが成熟する前に別場面へ移る
- 映画、会話、ラジオ、レコード店などの音声が割り込む
- 本編とインタールードを分離しない
- 異なる時代・地域の録音を説明なしで接続する
- Madlib、Quasimoto、引用音声が同じ曲の語り手を奪い合う

ここでは小節内部のヨレより、場面転換そのものが拍節構造を切断することが重要になる。

### 2.4 Selection Time

対象: `Piñata`、`Bandana`、`Sound Ancestors`。

大量生成の後に選択者が入る。完成曲を一本ずつ設計するのではなく、素材庫を作り、別の耳が採掘し、関係を作る。

```text
Madlibが大量生成
  → ビート／演奏素材のプール
  → Gibbs、Hebden、Peanut Butter Wolf等が選択
  → 声・配列・追加演奏
  → アルバム
```

生成と選択を同一人物・同一時間へ閉じないこと自体が、Madlibの作品システムである。

## 3. J Dillaとの比較仮説

これは信号計測前の暫定比較であり、確定事項ではない。

| 観点 | J Dilla | Madlib |
|---|---|---|
| 主な操作対象 | 一拍内部の音の前後関係 | 異なる録音時間・場面の接続 |
| ドラム | 音ごとのタイミング網を精密に変形 | 演奏・サンプルの揺れを次層へ継承 |
| ベース | ドラムと別の微細な時間網を形成 | 先行するドラムを聴いて身体的に追従 |
| 編集 | 小節内部の時間彫刻 | 断片、時代、人物、地域の衝突 |
| 形式 | 同じ小節が内部で変形する | 閉じたループの外側で場面が交換される |

両者を「人間的なヨレ」で一括しない。Dilla研究で計測するオンセット偏差と同じ方法をMadlib作品へ適用し、差が本当に観測できるか検証する。

## 4. Field Looperへ採用する点

製品採用済みではない。以下は研究からの候補であり、統合判断と実装は別工程とする。

### 4.1 独立クロック・オーバーダブ

最初のタッチ演奏を記録するが、グリッドへ矯正しない。次の演奏層は固定BPMではなく、直前層のイベント時刻を聴覚的な基準として重なる。

### 4.2 ズレの継承

各レイヤーのイベント時刻を保存し、再生開始点だけを機械的に揃えて内部イベントを量子化する処理を避ける。必要なら「補正」ではなく、揺れの強さを後から連続制御する。

### 4.3 即時捕獲と交換

演奏が完成する前でも短い断片を捕獲できる。捕獲した断片は固定ループとして放置せず、別のタッチで交換、短縮、逆転、ミュート、再捕獲できる。

### 4.4 自己生成素材のクレート

既製ループを選ぶのではなく、直前の演奏から複数の断片を自動保持する。演奏者はその場で自分が作った素材を掘り直し、現在の演奏へ戻す。

### 4.5 Beat Switchを演奏化する

曲順編集としてのビート切替ではなく、複数断片間をタッチで瞬時に遷移する。切替時に全素材をリセットせず、声、残響、フィードバック、低音など一部の層を持ち越せるようにする。

### 4.6 仮想演奏者

同じ演奏者でも、触れる領域やジェスチャーごとに異なる時間規則を持たせる。名称やキャラクター表示を増やすのではなく、実際の応答差で別身体を作る。

例:

- 指A: ドラム断片を即時捕獲
- 指B: 先行ドラムの揺れへ追従する低音
- 指C: 場面全体を切り替える
- 長押し: 現在の演奏を素材プールへ退避

## 5. 採用しない点

- レコードノイズを足すだけの「Madlib風」
- 全体へ一律のスウィング率を適用する処理
- SP-303風の帯域劣化を制作思想そのものとして扱うこと
- 既製サンプルパックを大量に並べ、クレート感を演出すること
- 変名や宇宙的な名称だけを借りること
- 自動生成された完成ループを演奏者が選ぶだけの設計
- ユーザーの演奏を裏側で完全量子化し、「human」と表示すること

## 6. 作品系列

| 系列 | 代表作 | 研究焦点 |
|---|---|---|
| Lootpack | `Soundpieces: Da Antidote!` | MC、DJ、ビート制作が未分化だった出発点 |
| Quasimoto | `The Unseen` | 声の速度変更、私的録音、複数話者 |
| Yesterdays New Quintet | `Angles Without Edges` | 一人多重演奏、human time、架空バンド |
| Blue Note | `Shades of Blue` | アーカイブを保存対象でなく現在の演奏素材として扱う |
| Jaylib | `Champion Sound` | MadlibとJ Dillaのビート／ラップ交換 |
| Madvillain | `Madvillainy` | 短曲、フック不在、未解決ループ、断片的物語 |
| Beat Konducta | 各シリーズ | 映画、インド、アフリカ、Dilla追悼の組曲化 |
| Medicine Show | 全13巻 | ビート集、DJミックス、地域音楽研究の横断 |
| Freddie Gibbs | `Piñata` / `Bandana` | 素材庫からの選択、声の後に行う最小編集 |
| 単独名義 | `Sound Ancestors` | 他者による選択・配列と素材作者の分離 |

## 7. 最初の試聴系列

1. Quasimoto – “Microphone Mathematics”
2. Quasimoto – “Come on Feet”
3. Yesterdays New Quintet – “Uno Esta”
4. Madlib – “Slim’s Return”
5. Jaylib – “The Red”
6. Madvillain – “Accordion”
7. Madvillain – “Rhinestone Cowboy”
8. Madlib – “Movie Finale”
9. Madlib – “Two for 2 – For Dilla”
10. Freddie Gibbs & Madlib – “Crime Pays”

この順序は、声の変形、一人多重演奏、ジャズ再編集、Dillaとの交換、DOOMとの短編化、後期の統合を追うための暫定系列である。

## 8. 未検証事項

- 対象音源ファイルを取得した信号分析
- ドラム、ベース、サンプルのオンセット抽出
- 局所テンポ曲線と小節境界の推定
- Dilla作品と同条件でのタイミング偏差比較
- SP-303、iPad、8トラック録音による差の切り分け
- Beat Konducta各地域シリーズで、資料引用とMadlib固有編集を分離すること
- `Sound Ancestors` でMadlibの素材判断とKieran Hebdenの配列判断を分離すること
- Field Looper試作へ落とした際の実機マルチタッチ検証
- 著作権上適切な検証音源の取得経路

## 9. 依存する研究

- J Dilla研究: 一拍内部の時間偏差との比較
- リズム／ポリリズム研究: 共通グリッドを使わない層間関係
- DJ Shadow研究: 長尺構成とサンプル編集の対照
- Sun Ra研究: 架空宇宙と演奏主体
- Miles Davis後期研究: 録音後編集と演奏の境界
- Can／Conny Plank研究: 反復、編集、スタジオの演奏装置化
- Autechre研究: イベント時間を固定拍から解放する設計
- Jeff Mills研究: 素材切替をリアルタイム演奏として扱う方法
- Charlie Hunter研究: 一人の身体による複数役割の同時制御

## 10. 失効した判断

現時点ではなし。

今後、音源計測によってDilla比較や四種類の時間構造が支持されなかった場合、該当仮説を削除せず、ここへ失効理由と検証条件を記録する。

## 11. 参照資料

一次資料・公式資料を優先した。

- Red Bull Music Academy, “Madlib (2002)”
  - https://www.redbullmusicacademy.com/lectures/madlib-king-of-the-beats/
- Red Bull Music Academy, “Madlib (2016)”
  - https://www.redbullmusicacademy.com/lectures/madlib-2016/
- Stones Throw, “Madvillain”
  - https://www.stonesthrow.com/artist/madvillain/
- Stones Throw, “Mad Genius”
  - https://www.stonesthrow.com/news/mad-genius/
- Stones Throw, “Phantom Menace: Remix Mag Interview with Madlib and engineer Dave Cooley”
  - https://www.stonesthrow.com/news/phantom-menace-remix-mag-interview-with-madlib-and-engineer-dave-cooley/
- Stones Throw, “Quasimoto”
  - https://www.stonesthrow.com/artist/quasimoto/
- Stones Throw, “History of Lord Quas”
  - https://www.stonesthrow.com/news/history-of-lord-quas/
- Stones Throw, “A guide to Madlib’s Yesterdays New Quintet and Yesterdays Universe”
  - https://www.stonesthrow.com/news/guide-to-madlib-yesterdays-new-quintet-yesterdays-universe/
- Stones Throw, “Madlib’s Shades of Blue”
  - https://www.stonesthrow.com/news/shades-of-blue/
- Madlib Bandcamp, `Sound Ancestors`
  - https://madlib.bandcamp.com/album/sound-ancestors
- Red Bull Music Academy Daily, “Interview: Freddie Gibbs on Madlib, Young Jeezy and Gary, Indiana”
  - https://daily.redbullmusicacademy.com/2014/03/freddie-gibbs-interview/


## 12. 追補: Yesterdays New Quintetと複数身体

### 12.1 初期YNQと拡張Universeを分ける

Stones Throwの公式ガイドが示す系列は次の通り。

- 2000–2001: Yesterdays New Quintet
- 2002: Joe McDuphrey Experience
- 2003: Ahmad Miller
- 2004: Monk Hughes & The Outer Realm
- 2005: Malik Flavors
- 2007: Otis Jackson Jr. Trio
- 2007以降: Sound Directions、Young Jazz Rebels、The Last Electro-Acoustic Space Jazz & Percussion Ensembleなどを含むYesterdays Universe

初期YNQはJoe McDuphrey、Malik Flavors、Ahmad Miller、Monk Hughes、Otis Jackson Jr.という五人の名義と、Madlibのプロデューサー／編曲／録音という外枠で構成された。Madlibが全楽器を演奏した一人プロジェクトとして報じられ、本人も「周囲に誰もいないから自分でやる」「最初にドラムを演奏し、残りを加える」と説明している。

一方、Universe拡張後は実在奏者を含む。このため、次の二層を混ぜない。

| 層 | 主体 | 研究上の意味 |
|---|---|---|
| 初期YNQ | Madlibの一人多重演奏＋五つの演奏者名義 | 一人の身体を役割ごとに分割する |
| 拡張Universe | Madlibの制作・編曲＋実在奏者＋派生名義 | 私的な仮想バンドを実際の協働網へ開く |

### 12.2 「上手く全楽器を弾く」ことが目的ではない

MadlibはYNQについて、自分は大きなソロを弾くような演奏家ではなく、音の雰囲気を組み合わせ、頭の中の曲を形にすると説明している。

ここでの能力は、各楽器を独奏レベルで習得することではない。

1. 曲に必要な最小語彙を各楽器で覚える。
2. ドラム、ベース、鍵盤、打楽器へ異なる役割を与える。
3. ひとつ前の演奏を聴き、次の役割として応答する。
4. 各テイクを直し続けず、大量の録音へ進む。
5. 後で素材を選び、アルバムへ構成する。

Peanut Butter Wolfは、20枚から30枚規模のCD-R群から `Angles Without Edges` の素材を選んだと複数の同時代記事で記録されている。したがって制作単位は「完成曲」だけではなく、「異なる自分による大量の試行群」である。

### 12.3 仮想メンバーは時間規則の分割として読める

五つの名義を単なる物語設定ではなく、演奏規則の分割として仮定する。

| 仮想役割 | 担当する判断 |
|---|---|
| ドラム身体 | 曲の絶対時間を作る。外部グリッドへ戻らない |
| ベース身体 | ドラムの局所的な前後へ追従し、重心を作る |
| 鍵盤身体 | 和声を説明しすぎず、色と反復を置く |
| 打楽器身体 | 拍を補強するのでなく、別の周期を持ち込む |
| 編曲身体 | 個別演奏から距離を取り、残す断片を選ぶ |

これは史料上の各名義と楽器を厳密に同定した表ではない。Field Looperへ移すための設計仮説である。

重要なのは、同じ人間がすべてを操作しても、全レイヤーが同じ判断癖を持たないようにすること。Charlie Hunter型の同時分担とは異なり、Madlib型は時間をずらして別の身体へ入り直す。

### 12.4 human timeの最小モデル

通常の量子化ルーパーは、入力イベントを共通格子 `G` へ吸着させる。

```text
入力イベント → 最寄りのG → 全レイヤー共通の正しい拍
```

Madlib型では、最初のドラム層 `D` 自体を時間基準にする。

```text
D = {d1, d2, d3 ...}        最初のドラム
B = {d(i) + ΔB(i)}          ドラムを聴いたベース
K = {b(j) + ΔK(j)}          ドラム＋ベースを聴いた鍵盤
P = 独立周期または局所追従  打楽器
```

`Δ` はランダムなヒューマナイズ値ではない。演奏者が先行層を聴いて生じた応答時間である。ソフト側が後から乱数を加える方法では代替できない。

実装候補では次を保存する。

- 各入力イベントの生時刻
- イベント間隔
- どのレイヤーを聴きながら録音したか
- 録音開始時の親レイヤー位置
- 量子化前のタッチ圧、位置、移動速度
- レイヤーごとの反復長

これにより、全層を同じ小節長へ切り揃えず、親子関係を持つ時間を再生できる。

### 12.5 マルチタッチ楽器への最小操作

画面上の三本指を「三つのパラメータ」ではなく、「三つの演奏主体」として扱う。

- 第一接触: 現在の音を捕獲し、基準層を作る
- 第二接触: 基準層を聴きながら別の音域／音色を重ねる
- 第三接触: 現在の層を壊さず、別断片へ場面転換する
- 接触の移動: タイミング補正ではなく、層間の追従度を変える
- 長押し: 直前の演奏状態を自己生成クレートへ残す
- 三点同時接触: 全層同期ではなく、現在の時間関係を一時固定する

ここで三本指は上限ではない。最小の身体分割として置く。OSとブラウザが何点まで安定取得できるかは実機検証事項として残す。

### 12.6 試作時の判定条件

今後の試作は、音が「Madlibっぽい」かではなく次で判定する。

1. 意図的に不均等な最初の演奏が、再生時に均されていないか。
2. 後続層が親層と異なるタイミング輪郭を保持しているか。
3. 反復の途中で断片を交換しても、すべての層が小節頭へ戻らないか。
4. 演奏ミスを削除だけで処理せず、別断片として退避できるか。
5. 既製ループを使わず、直前の演奏だけで素材庫が成長するか。
6. 同じ指の操作を繰り返しても、役割の違いによって異なる結果が生じるか。
7. 画面説明を読まなくても、触ることで捕獲・追従・転換の差が分かるか。

### 12.7 今回の認知更新

以前の記述には、初期YNQの一人多重録音と、拡張後のYesterdays Universeを連続した架空名義群として読める余地があった。

今回の資料確認により、次のように限定する。

- 初期YNQ: Madlibの一人多重録音と仮想メンバーの研究対象
- 拡張Universe: 実在奏者を含む協働ネットワーク
- 共通項: Madlibがプロデューサー／編曲者として異なる演奏主体を一つの宇宙へ配置すること

この限定により、「仮想メンバー」という面白さを残しながら、実在奏者の寄与をMadlib一人へ誤帰属しない。

### 12.8 追加資料

- Stones Throw, “A guide to Madlib’s Yesterdays New Quintet and Yesterdays Universe”
  - https://www.stonesthrow.com/news/guide-to-madlib-yesterdays-new-quintet-yesterdays-universe/
- Stones Throw, “Madlib’s Yesterdays New Quintet”
  - https://www.stonesthrow.com/news/phases-madlib-yesterdays-new-quintet/
- Stones Throw, “Angles Without Edges”
  - https://store.stonesthrow.com/products/angles-without-edges
- Stones Throw, “Beyond Hip Hop”
  - https://www.stonesthrow.com/news/beyond-hip-hop/
- Stones Throw, “Diary of the Mad Man”
  - https://www.stonesthrow.com/news/diary-of-the-mad-man/
- Stones Throw, “A Tribute To Brother Weldon”
  - https://www.stonesthrow.com/store/a-tribute-to-brother-weldon/
