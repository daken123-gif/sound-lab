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


## 13. 追補: 短曲・切断・場面交換――編集を演奏として読む

### 13.1 「短いビート」と「短い曲」は同じではない

`Madvillainy` の最初期デモ系列は12曲36分だった。完成盤は22曲約46分であり、単純にデモを引き伸ばしたのではなく、より多くの曲・インタールード・引用音声へ細分化されている。Stones Throwの同時代記事は、コーラスを置かず、短いインタールードで全曲を連結した構造を記録している。

ここから次を区別する。

- **ビートの短さ**: 生成を早く止め、次の素材へ移る
- **曲の短さ**: ラップまたは場面の役割が終われば、慣例的な二番やコーラスを待たず終了する
- **アルバムの長さ**: 短い単位を多数接続し、個々の未展開を全体の流れへ変える

Madlibの断片は「完成できなかったループ」ではなく、次の断片が続くことを前提にした場面単位として読める。ただし、これは作品構造からの分析であり、Madlib本人がこの用語で説明した事実ではない。

### 13.2 ミクロの固定とマクロの可変

Madlibの形式には、同時に反対方向の二つの運動がある。

| 層 | 運動 | 効果 |
|---|---|---|
| ループ内部 | 同じ断片を固定する | 解決しない期待、ラップのための狭い空間 |
| 曲・場面間 | 断片を早く交換する | 音色、時代、人物、場所の急転換 |
| アルバム全体 | 声片やインタールードで接続する | 切断を隠さず、切断そのものを連続性へ変える |

したがってMadlibの音楽を「反復中心」とだけ呼ぶと半分を落とす。内部では反復を強く固定する一方、外部ではその反復を長く育てず交換する。

`Beat Konducta Vol. 1–2` は公式説明で35個の短いソウル断片、スペース・ジャズのループ、音声編集を連続した流れへ置き、ビートCDと架空映画のサウンドトラックの中間として提示された。ここでは各ビートの起承転結より、「いまどの場面にいるか分からなくなること」が作品の形式になっている。

### 13.3 完成条件を「展開量」から「役割終了」へ変える

通常の曲作りでは、素材を次のように完成へ近づける。

```text
ループ
  → Aメロ
  → コーラス
  → 二番
  → ブリッジ
  → 終止
```

Madlib型では、別の完成条件を仮定できる。

```text
断片が固有の空間を作る
  → 声または演奏がその空間へ入る
  → 役割が終わる
  → 断片を説明し尽くす前に切る
  → 次の場面が前の意味を変える
```

ここで重要なのは、短くすること自体ではない。「もう一展開できるか」ではなく、「この断片が担当した役割は終わったか」で切ることにある。

### 13.4 初稿・完成盤・私的リミックスは固定された正解系列ではない

`Madvillainy` には次の異なる構成が存在する。

- 2002年の初期デモ系列: 12曲、36分
- 2004年の完成盤: 22曲、約46分
- 2008年の `Madvillainy 2: The Madlib Remix`: 25曲
- ボーカルを除いた公式インストゥルメンタル盤

2008年版は、Madlibが私的鑑賞用に再構成したものと公式に説明されている。これは完成盤を唯一の不動な配列とせず、同じ声や素材が別の場面関係を持ち得ることを示す。

研究上は、次の三軸を分ける。

1. **素材生成**: ビート、声、引用音声、演奏を作る
2. **局所構成**: 一つの声とビートを曲として結びつける
3. **再配列**: 同じ素材群から別のアルバム時間を作る

第三軸は単なる再発や別ミックスではなく、編集者が同じ出来事を別の順番で再演する工程として扱う。

### 13.5 Medicine Showは作品群そのものを編集単位にする

Medicine Showは当初、Madlib Invazionから毎月一枚を出す挑戦として始まり、事前にシリーズ全体の形を固定せず、最終的に13作へ拡張された。公式総括は、ヒップホップ、ビートテープ、リミックス、ジャズ、DJミックスを同一系列に含めている。

ここでは編集単位が曲からアルバムへ拡大する。

- ラッパーとのアルバム
- インストゥルメンタル・ビート集
- 地域／ジャンルを横断するDJミックス
- リミックス集
- ジャズ／電子音楽的な派生作

これらを別々の活動として整理せず、一つの連続した「Show」として出す。Madlibの変名が演奏主体を分ける装置なら、Medicine Showは公開形式を分けながら制作時間を連続させる装置である。

### 13.6 リアルタイム楽器へ接続する編集演算

以下は製品採用済み仕様ではなく、研究から導く操作候補である。

| 編集演算 | 動作 | Madlib研究との接続 |
|---|---|---|
| 捕獲 | 演奏途中の短い区間を即座に保持する | 完成した小節だけを素材にしない |
| 固定 | 断片内部を反復させる | Loop Lock |
| 切断 | 小節頭を待たず現在の場面を終了する | 役割終了による短曲化 |
| 交換 | 別断片へ即時遷移する | Montage Time |
| 持越し | 低音、声、残響など一層だけ次場面へ残す | 切断を連続性へ変える |
| 再登場 | 以前の断片を短く戻す | リプライズ、記憶化 |
| 退避 | 現在の演奏を自己生成クレートへ残す | Selection Time |
| 再配列 | 同じ素材群から別の進行を演奏する | 私的リミックス |

ここで自動クロスフェードを常用すると、異質な場面同士の衝突を丸めてしまう。滑らかさだけでなく、切断面を残すモードが必要になる。

### 13.7 「ループ垂れ流し」との分岐

既製ループを再生し続ける設計とMadlib型の反復は同じではない。

- 既製ループは、演奏前に外形と反復長が完成している
- Madlib型の断片は、その場で捕獲・短縮・交換・再配置される
- 反復は安定した伴奏を保証するためではなく、次の切断を効かせるために一時固定される
- 演奏者の仕事はループの上へ音を足すことだけでなく、ループの寿命を判断することになる

したがって、リアルタイム楽器で必要なのは「何トラック重ねられるか」だけではない。いま鳴っている断片を、壊さずに終わらせ、何を持ち越し、何を捨てるかを身体で決められることが中心になる。

### 13.8 他研究との接続

- **DJ Shadow**: 長尺サンプル構成との比較。Shadowが曲内で積層と回収を行う場合、Madlibは回収前に別場面へ移る傾向を検証する
- **J Dilla**: 一拍内部の時間設計と、Madlibの場面間編集を同一の「ヨレ」へ統合しない
- **Can / Conny Plank**: 長時間演奏から作品を切り出す編集と、大量の短断片を連結する編集を比較する
- **Miles Davis後期**: Teo Maceroの録音後編集と、Madlib／Hebdenの素材庫編集における作者性を比較する
- **Jeff Mills**: 素材交換をステージ上の即時判断として行う方法へ接続する
- **Autechre**: イベント生成規則の変形と、場面単位の交換を分けて設計する

### 13.9 次の検証課題

- `Madvillainy` 初期デモ、完成盤、2008年リミックスで同じ声／素材がどの位置へ再配置されたかを対応表にする
- 各版の曲長分布、無音、音声ブリッジ、ハードカット、持越し音を実測する
- `Beat Konducta Vol. 1–2` の35断片について、局所反復長と場面遷移の種類を符号化する
- Medicine Show全13作を、ビート集／ラップ作／DJミックス／ジャズ・電子音楽の公開形式で分類し、系列順が聴取に与える意味を検討する
- Field Looper試作では、固定小節境界あり／なし、自動クロスフェードあり／なしで切断の演奏性を比較する
- 著作権上適切に取得できる音源がない限り、音響実測を完了扱いにしない

### 13.10 追加資料

- Stones Throw, “Madvillainy Demo Tape”
  - https://www.stonesthrow.com/store/madvillainy-demo-tape/
- Stones Throw, “Mad Genius”
  - https://www.stonesthrow.com/news/mad-genius/
- Stones Throw, “Beat Konducta Vol. 1–2”
  - https://www.stonesthrow.com/news/beat-konducta-vol-1-2-1/
- Stones Throw, “Madvillainy 2: The Box”
  - https://www.stonesthrow.com/news/madvillainy-2-box/
- Stones Throw, “Madvillainy 2: The Madlib Remix”
  - https://store.stonesthrow.com/products/madvillainy-2-the-madlib-remix
- Stones Throw, “Madlib: All 12”
  - https://www.stonesthrow.com/news/madlib-all-12/
- Stones Throw, “Madlib Medicine Show: The Aftermath”
  - https://www.stonesthrow.com/news/madlib-medicine-show-the-aftermath/


## 14. 追補: `Madvillainy` の版間比較――完成は追加だけでなく圧縮で起きる

### 14.1 「デモ版」は一つではない

前節では2008年に公式化されたデモ・カセットを基準に「12曲、36分」と記した。この記述は当該カセットについては維持するが、`Madvillainy Demos` 全体の固定仕様としては使わない。

2025年1月31日に公式Bandcampで公開された `Madvillainy Demos` は14曲である。2008年版の公式曲目にはなかった `Do Not Fire! (demo)` と `Bistro (demo)` が冒頭に入り、末尾には `One False Move (“Great Day” demo - instrumental)` が置かれている。

以後は次のように版を明記する。

| 呼称 | 収録単位 | 本研究での扱い |
|---|---:|---|
| 2002年初期シーケンス | 流出時の並び。現物差異は未照合 | 制作途中の歴史的状態 |
| 2008年公式デモ・カセット | 12曲、公式説明では36分 | 最初に商品化されたデモ版 |
| 2025年公式 `Madvillainy Demos` | 14曲 | 現在公式に取得できる拡張デモ版 |
| 2004年完成盤 | 22曲 | 正規アルバム構成 |
| 2008年 `Madvillainy 2` | 25曲 | Madlibによる私的再編集の公開版 |

2002年の流出物、2008年のカセット、2025年の拡張版を、同じ曲数・同じ配列の「原版」として混同しない。

### 14.2 2025年デモ版と2004年完成盤の同名／改題対応

以下は公式Bandcampに表示された曲名と時間を比較したもの。音源波形を照合した結果ではなく、同名曲と公式に改題関係が示された曲の書誌的対応である。

| 2025年デモ版 | デモ時間 | 2004年完成盤 | 完成盤時間 | 増減 |
|---|---:|---|---:|---:|
| Do Not Fire! (demo) | 0:52 | Do Not Fire! | 0:52 | 0秒 |
| Bistro (demo) | 1:08 | Bistro | 1:07 | −1秒 |
| One False Move | 2:12 | Great Day | 2:16 | ＋4秒 |
| America’s Most Blunted (demo) | 3:53 | America’s Most Blunted | 3:54 | ＋1秒 |
| Operation Lifesaver (demo) | 1:25 | Operation Lifesaver | 1:30 | ＋5秒 |
| Figaro (demo) | 2:33 | Figaro | 2:25 | −8秒 |
| Rainbows (demo) | 3:02 | Rainbows | 2:51 | −11秒 |
| Just for Kicks | 2:46 | Meat Grinder | 2:11 | −35秒 |
| Fancy Clown (demo) | 3:30 | Fancy Clown | 1:55 | −95秒 |
| Shadows of Tomorrow (demo) | 4:02 | Shadows of Tomorrow | 2:36 | −86秒 |
| Money Folder (demo) | 3:16 | Money Folder | 3:02 | −14秒 |
| Stakes | 1:18 | Supervillain Theme | 0:52 | −26秒 |
| All Caps (demo) | 2:20 | All Caps | 2:10 | −10秒 |

この13対応の表示時間を合計すると、デモ版は32分17秒、完成盤側は27分41秒で、完成盤は4分36秒短い。中央値も10秒の短縮になる。

ただし平均値だけでは編集の性格を捉えられない。ほぼ同じ長さを維持する曲と、大幅に圧縮する曲が同居している。

- **ほぼ保存**: `Do Not Fire!`、`Bistro`、`America’s Most Blunted`
- **軽い圧縮**: `Figaro`、`Rainbows`、`Money Folder`、`All Caps`
- **大幅な圧縮**: `Meat Grinder`、`Fancy Clown`、`Shadows of Tomorrow`、`Supervillain Theme`

これはMadlibの短曲性が一律の尺制限ではないことを示す。素材ごとに「残すべき時間」の判定が異なる。

### 14.3 完成盤はデモを磨いただけではない

完成盤22曲のうち、2025年デモ版に同名または公式な改題対応がない曲目は次の九つである。

- The Illest Villains
- Accordion
- Raid
- Sickfit
- Curls
- Hardcore Hustle
- Strange Ways
- Eye
- Rhinestone Cowboy

これは九曲すべてが流出後に新規制作されたことを証明しない。公式曲目から確認できるのは、2025年デモ版と完成盤の構成差だけである。

Pitchforkの制作史では、初期版流出後にDOOMが全ボーカルを録り直し、より低く、落ち着いた声へ変えたこと、歌詞の一部を修正したこと、`Accordion` と `Bistro` を追加したことが、Peanut Butter WolfとJeff Jankの証言として記録されている。ここから完成工程を三種類に分ける。

1. **圧縮**: 既存曲から時間を削る
2. **再身体化**: 同じ歌詞でも声の高さ、速度感、拍への沈み方を録り直す
3. **再構成**: 新しい曲・インタールードを加えて全体の順序を作り直す

完成とは、情報や展開を足すことだけではない。長いデモを削り、声を録り直し、別の短い断片を間へ入れることで、アルバム全体の密度を上げている。

### 14.4 声の録り直しはビート編集でもある

DOOMのボーカル変更を「ラッパー側の仕上げ」として分離すると、Madlibとの時間関係を落とす。

同じビートでも、声が高く前へ飛び出すか、低く拍の内側へ沈むかで、聴こえる重心が変わる。制作史の証言どおり全ボーカルが録り直されたなら、完成盤ではビート素材を大きく変えなくても、声によって時間構造全体を再設計できる。

したがってMadlib研究では、ビート単体のオンセットだけでなく、次を同時に測る必要がある。

- 声の音節開始とキック／スネアの距離
- 行末が小節線を越える位置
- デモと完成盤の発話速度
- 同じ歌詞で休符が増減した場所
- ボーカル削除後にも残るビート側の時間感覚
- 声を戻したときに生じる重心の変化

これを行わず、完成盤の低い声をMadlibの「ヨレ」へ誤帰属しない。

### 14.5 2008年リミックスは「別ミックス」より再作曲に近い

公式Bandcampは `Madvillainy 2: The Madlib Remix` を、Madlibが完成盤全体を発売約四年後に私的鑑賞用としてリミックスした作品と説明している。全25曲には、同名曲を並べた通常のリミックス盤ではなく、`No Brain`、`Pearls`、`Boulder Holder`、`Butter King Jewels`、`Cold One` など別タイトルが付けられている。

このため、曲名だけから完成盤との一対一対応を断定できない。正確な対応には音源または公式ライナーノーツが必要であり、現段階では未検証とする。

それでも構造上、次は確認できる。

- 完成盤22曲に対し、再編集版は25曲
- 20秒、44秒、45秒のインタールード／リプライズを含む
- `No Brain` を二曲続けて置く
- 最終曲 `Cold One` の直後に45秒のリプライズを置く
- Madlib自身が完成盤を終点とせず、私的な別配列を作った

ここでは「完成作品を保存し、素材関係だけを再演する」ことが起きている。原版を上書きせず、別の時間系列を成立させる。

### 14.6 Field Looperへ接続する版管理

製品採用済みではない。研究からの設計候補として、次を置く。

1. 捕獲した演奏を破壊編集せず、原テイクとして残す
2. 原テイクから短縮版を複数作れる
3. 同じ断片へ別の声・別のタッチ演奏を録り直せる
4. 曲名やスロット名ではなく、素材の由来関係を保持する
5. 一つの「完成ループ」で終了せず、同じ素材群から別の演奏系列を呼び出す
6. 版の差をエフェクト設定だけでなく、尺、順序、持越し層、声の位置として保存する

```text
原テイク
  ├─ 圧縮版A
  ├─ 圧縮版B
  ├─ 別ボーカル版
  └─ 別シーケンス版
```

Madlibから引くべきなのは「たくさん保存する機能」ではない。原テイク、圧縮、再身体化、再配列を同じ素材の系譜として演奏中に扱えることにある。

### 14.7 今回の認知更新

前節の「12曲36分の初期デモ」という記述は、2008年公式カセットの仕様へ限定した。2025年公式版を含めたデモ史全体の曲数としては失効する。

新しい中心仮説は次である。

> Madlibの完成度は、ループを発展させた量ではなく、素材ごとに必要な時間だけを残し、声と配列を別の身体でやり直せることから生まれる。

この仮説のうち、曲長差と版の曲目差は公式表示から確認済み。具体的にどの小節、声、サンプルが削られたかは音響照合前の未検証事項である。

### 14.8 追加資料

- Madvillain Bandcamp, `Madvillainy Demos`
  - https://madvillain.bandcamp.com/album/madvillainy-demos
- Madvillain Bandcamp, `Madvillainy`
  - https://madvillain.bandcamp.com/album/madvillainy
- Madvillain Bandcamp, `Madvillainy 2: The Madlib Remix`
  - https://madvillain.bandcamp.com/album/madvillainy-2-the-madlib-remix
- Stones Throw, “20 Years of Madvillainy: Demos & Audiophile Edition on Vinyl”
  - https://www.stonesthrow.com/news/madvillainy-demos-audiophile-edition-vinyl/
- Pitchfork, “Searching for Tomorrow: The Story of Madlib and DOOM’s Madvillainy”
  - https://pitchfork.com/features/article/9478-searching-for-tomorrow-the-story-of-madlib-and-dooms-madvillainy/


## 15. 追補: Shazamプレビュー取得経路の実測

### 15.1 今回実行したこと

ShazamのApple Musicカタログ検索を使い、前節で大幅な尺の圧縮が確認された三組を日本ストアで検索した。

- `Fancy Clown (demo)` / `Fancy Clown`
- `Shadows of Tomorrow (demo)` / `Shadows of Tomorrow`
- `Just for Kicks (“Meat Grinder” demo)` / `Meat Grinder`

検索後、候補名だけで判断せず、曲IDを指定して曲情報を再取得した。六曲すべてについて、アルバム名、曲名、Apple Music曲ID、ISRC、ミリ秒単位の曲尺、プレビューURLの存在を確認した。

### 15.2 特定できた六曲

| 版 | 曲名 | Apple Music曲ID | ISRC | カタログ曲尺 | プレビュー |
|---|---|---:|---|---:|---|
| デモ | Fancy Clown (demo) | 1785333006 | US2S70465038 | 210,432 ms | URLあり |
| 完成盤 | Fancy Clown (feat. Viktor Vaughn) | 887699529 | US2S70465017 | 115,827 ms | URLあり |
| デモ | Shadows of Tomorrow (demo) | 1785333007 | US2S70465039 | 242,769 ms | URLあり |
| 完成盤 | Shadows of Tomorrow (feat. Quasimoto) | 887699521 | US2S70465012 | 156,187 ms | URLあり |
| デモ | Just for Kicks (“Meat Grinder” demo) | 1785332998 | US2S70465037 | 166,017 ms | URLあり |
| 完成盤 | Meat Grinder | 887699512 | US2S70465003 | 131,867 ms | URLあり |

安定した参照先として、変動し得る音声CDNのURLではなくApple Music曲ページを記録する。

- https://music.apple.com/jp/album/fancy-clown-demo/1785332878?i=1785333006
- https://music.apple.com/jp/album/fancy-clown-feat-viktor-vaughn/887699504?i=887699529
- https://music.apple.com/jp/album/shadows-of-tomorrow-demo/1785332878?i=1785333007
- https://music.apple.com/jp/album/shadows-of-tomorrow-feat-quasimoto/887699504?i=887699521
- https://music.apple.com/jp/album/just-for-kicks-meat-grinder-demo/1785332878?i=1785332998
- https://music.apple.com/jp/album/meat-grinder/887699504?i=887699512

### 15.3 取得できたことと、取得できなかったこと

今回のShazam経路で取得できたのは、カタログ情報と各曲のプレビューURLである。プレビュー音声のバイト列や再生音は、この実行環境の分析面へ渡っていない。音声CDNへの直接取得も許可されず、実行できなかった。

したがって現在の状態を分ける。

| 工程 | 状態 |
|---|---|
| 対象曲の検索 | 実施済み |
| デモ／完成盤の候補分離 | 実施済み |
| 曲ID・ISRCによる再同定 | 実施済み |
| プレビューURLの存在確認 | 実施済み |
| プレビュー音声の取得 | 未実施 |
| 音声の聴取 | 未実施 |
| 波形・オンセット解析 | 未実施 |
| デモ／完成盤の音響比較 | 未実施 |

「プレビューURLがある」を「プレビューを聴いた」へ変換しない。この境界は、他の音楽研究でShazamを使う場合にも維持する。

### 15.4 カタログメタデータの注意点

Apple Musicカタログでは `Madvillainy Demos` のレコードレーベル表記と著作権年は2025年だが、各曲の `releaseDate` は完成盤と同じ2004年3月23日として返る。

一方、公式Bandcampはデジタル版 `Madvillainy Demos` の公開日を2025年1月31日とする。

したがってApple Music APIの `releaseDate` を、その版が一般公開された日付として単独使用しない。次を分ける必要がある。

- 録音／作品に付与された原日付
- そのマスターまたは再発版の著作権年
- その版が実際に公開・発売された日付
- カタログへ登録された日付

これは曲名、尺、ISRCの同定には直ちに影響しないが、版の制作史を復元する際には重要である。

### 15.5 ここまでで強化された点

前節の曲尺比較は、Bandcampの秒表示だけでなく、Shazam経由で取得したApple Musicのミリ秒値でも再確認できた。

| 曲 | 前節の秒表示による短縮 | Apple Music値による短縮 |
|---|---:|---:|
| Fancy Clown | 約95秒 | 94,605 ms |
| Shadows of Tomorrow | 約86秒 | 86,582 ms |
| Just for Kicks / Meat Grinder | 約35秒 | 34,150 ms |

二つのカタログで大幅短縮の順位は一致する。

1. Fancy Clown
2. Shadows of Tomorrow
3. Just for Kicks / Meat Grinder

ただし、短くなった箇所がイントロ、声、反復、アウトロのどこかはまだ分からない。曲尺一致は編集位置の証拠にならない。

### 15.6 音響分析へ進むための必要条件

次の工程では、合法的に取得でき、解析環境へ実際の音声バイト列として渡せる素材が必要になる。

最低条件は次の通り。

1. デモ版と完成盤の両方について、同じ長さの試聴区間または正規入手音源がある
2. 音声ファイルの由来、版、曲IDを保持できる
3. 実際に取得したファイルの長さ、形式、ハッシュを確認できる
4. 波形を読み込み、オンセット、無音、声区間、反復境界を測れる
5. 解析結果を曲全体へ無断で一般化しない

この条件が揃うまでは、音響分析を完了扱いにしない。

### 15.7 今回の研究上の意味

今回の進展は音そのものの分析ではなく、音響分析へ入る前の対象同定と証拠境界の確定である。

Shazamは「どの商用録音を指しているか」「プレビューが存在するか」の解決には使えた。しかし現状の実行経路では、Shazamの検索成功だけでは聴取研究にならない。

これにより、従来の音楽研究にあり得た次の混同を切り離せる。

- 曲を検索した
- カタログ情報を取得した
- プレビューURLを得た
- 音源を取得した
- 音を聴いた
- 音響特徴を測った

この六段階は別工程である。
