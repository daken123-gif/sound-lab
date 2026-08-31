# James Brown / The J.B.'s 研究 — 反復を生演奏へ戻す関係エンジン

- research-id: `20260831-james-brown`
- 状態: 研究記録。製品採用・実装・実機検証は未実施
- 更新日時: 2026-08-31
- 研究対象: James Brown、James Brown Orchestra、The J.B.'s
- 現在の問い: 完成済みワンループの再生ではなく、短い反復の内部を演奏し続ける仕組みを、iPhoneのマルチタッチ楽器へどう移すか
- 触る実装パス: なし
- 依存する研究: マルチタッチ演奏、4トラック、ポリリズム、Charlie Hunter、Jeff Mills、Autechre、Aphex Twinの各研究（本文未統合）

## 0. 結論

James Brownのファンクは「同じループを長く回す音楽」ではない。短い循環を保ちながら、ドラム、ベース、ギター、ホーン、声の発音位置、休符、音価、アタック、密度、主導権をリアルタイムで更新する演奏である。

この研究から楽器へ移す対象は、JB風の音色、サンプル、プリセットではない。

> 複数声の関係を指で指揮し、その指揮自体を発音へ変えるエンジン

一般的なルーパーの工程は `録音 → 固定 → 再生 → 上乗せ` である。JB型は `演奏 → 循環 → 合図 → 内部変形 → 合流 → 再散開` になる。

## 1. 参照資料

### 演奏者本人・公的アーカイブ

1. Fred Wesley interview, American Archive of Public Broadcasting  
   https://americanarchive.org/catalog/cpb-aacip-15-w66930p811
2. Jabo Starks interview, American Archive of Public Broadcasting  
   https://americanarchive.org/catalog/cpb-aacip-15-v40js9hk6b
3. Fred Wesley interview, Red Bull Music Academy Daily  
   https://daily.redbullmusicacademy.com/2013/03/fred-wesley-interview/
4. James Brown official legacy biography  
   https://jamesbrown.com/pages/the-legacy
5. James Brown official article, “We Got To Change” / formation of The J.B.'s  
   https://jamesbrown.com/blogs/news/james-brown-x-we-got-to-change

### 音楽学・計測研究

6. Paul Ainsworth, “Microtiming in Early Funk: A Microrhythmic Analysis of Fourteen Influential Funk Grooves”  
   https://www.gmth.de/zeitschrift/artikel/1224.aspx
7. Alexander Stewart, “Funky Drummer: New Orleans, James Brown and the Rhythmic Transformation of American Popular Music”  
   https://www.jstor.org/stable/853638
8. Anne Danielsen, *Presence and Pleasure: The Funk Grooves of James Brown and Parliament*  
   https://www.weslpress.org/9780819568236/presence-and-pleasure/

## 2. 観測できた事実

### 2.1 《Cold Sweat》では各パートが別のリズムを分担する

Fred Wesleyは《Cold Sweat》について、ドラム、ベース、ギター、ホーン、声がそれぞれ異なるリズムを演奏し、それらが噛み合う対位的構造だと説明している。Clyde Stubblefieldのドラム、Jimmy Nolenのギター、Bernard Odumの簡潔なベース、ホーン、声が同じ伴奏パターンを重複していない。

Anne Danielsenの比較を参照したAinsworthの研究では、《Papa's Got a Brand New Bag》には歌が上、伴奏が下という分業が残る一方、《Cold Sweat》では声を含む全楽器が同じ階層でリズムを構成するとされる。

### 2.2 Oneは強い1拍目だけではない

Ainsworthの計測では、《Cold Sweat》の2小節周期において、ドラムの時間偏差は最初のOneから広がり、第2小節で大きくなった後、次のOneへ向けて縮む。

さらに第2小節1拍目の裏では、Bernard Odumの低いF、キック、ドラムの偏差縮小が重なる。この位置は通常の小節頭とは別の局所的な合流点、secondary Oneとして分析されている。

### 2.3 マイクロタイミングはランダムなヒューマナイズではない

《Funky Drummer》のフィルでは、次のOneへ近づくにつれて発音偏差が約56 msから約4 msへ縮む事例が計測されている。また、同様の偏差形状が別のフィルでも高い精度で反復される。

これは均等グリッドへランダム値を加える処理ではない。周期内部の構造、ほかのパート、次の着地点を反映した時間形状である。

### 2.4 ドラムブレイクは、消えたバンドを内部に保持する

Ainsworthは複数曲のドラムブレイクで、ドラム単独になった後も、直前のベース、ギター、オルガン、声が作っていたアクセント位置やsecondary Oneがドラムの強弱・発音位置に残る例を示している。

したがってブレイクは、ほかのトラックをミュートして独立したドラムループを再生する状態ではない。

### 2.5 Bootsy期には主導権が移動する

Fred Wesleyは、James BrownがBootsy Collinsへ完成済みのベースラインを渡したのではなく、発想を渡し、Bootsyが具体化したと証言している。Bootsyの演奏が強く全体を牽引し、Brown自身がそれを追う局面もあったという。

The J.B.'sは1970年、Bootsy CollinsとCatfish Collinsを核として組まれ、《Sex Machine》《Super Bad》《Soul Power》などを録音した。

### 2.6 Brownの指揮とバンドの共同制作は分けて扱う必要がある

Fred Wesleyによれば、Brownは唸りや断片的な指示で方向を示し、Jimmy Nolenをはじめとする演奏者が実際のリフへ翻訳した。この過程はドラム、ベース、ホーンにも及んだ。

同時にBrownは服装やミスに罰金を科し、長時間のセッションで演奏者を消耗させた。音楽上のリアルタイム指揮を採用することと、この労働支配を美化・再現することは別である。

## 3. 14曲から抽出する演奏文法

| 曲 | 循環／変化 | 主な抽出対象 |
| --- | --- | --- |
| Papa's Got a Brand New Bag | 歌と伴奏の分業が残る | funk化以前との境界 |
| Cold Sweat | 2小節の対位的な網 | primary / secondary One、散開と収束 |
| I Got the Feelin' | ghostを含むドラム内部運動 | 主音と影音の二層化 |
| Mother Popcorn | 声とギターの細分化 | 声を旋律ではなく打撃として扱う |
| Funky Drummer | ドラムブレイクが全体構造を保持 | 不在パートの記憶、Oneへ戻るフィル |
| Sex Machine | ベースの推進力が前面化 | Bass主導への一時移行 |
| Give It Up or Turnit a Loose (1970) | 再録音で配置が大きく変化 | 同一素材を編成関係で別物にする |
| Soul Power | Bootsy / Catfishの高エネルギー | 高密度でも役割を重複させない |
| Make It Funky | 声とWesleyの応答 | 指揮と発音を同じ入力にする |
| Doing It to Death | 生指揮、ソロ指名、下降転調 | タイムラインなしの構成編集 |
| Pass the Peas | ホーン・スタブとリズム隊 | 短い音色塊を一つの身体にする |
| The Payback | 長いヴァンプ内の重心変化 | 音を足さず意味と前景を変える |
| Mind Power | 声、間、持続 | 空白を演奏対象にする |
| Papa Don't Take No Mess | ヴァンプと複数場面 | 即興と曲形式を対立させない |

## 4. 推論・設計仮説

以下は史料から直接確認した事実ではなく、楽器設計へ移すための仮説である。

### 4.1 4トラックを4本の音声ループではなく4声として扱う

各声は以下を保持する。

```text
VOICE {
  events       発音候補
  accents      強い着地点
  ghosts       弱い発音
  gaps         意図的な空白
  timingShape  Oneから離れ、戻る時間曲線
  memory       消音中にも保持する他声との関係
  influence    他声を動かす強さ
  activity     現在の接触から得た運動量
}
```

全体は以下を保持する。

```text
ENSEMBLE {
  pulse
  primaryOne
  secondaryOnes[]
  leader
  coupling[4][4]
  tension
}
```

`coupling[4][4]` は音量関係ではなく、どの声の発音が別の声の次の発音位置・休符・アクセントを動かすかを表す。

### 4.2 発音時刻

```text
t_event = t_pulse + delta_part + delta_relation + delta_return
```

- `delta_part`: 声固有の前後位置
- `delta_relation`: 他声との押し引き
- `delta_return`: 次の合流点へ戻るための加速・減速

単一のSwing値やランダムHumanize値では、JB型の時間形状を表せない。

### 4.3 マルチタッチ操作

圧力入力は現行iPhoneの主操作として依存しない。位置、速度、移動量、接触時間、指同士の距離で成立させる。

| 操作 | 内部変更 | 発音結果 |
| --- | --- | --- |
| タップ | eventを一つ投入 | 単発音 |
| ホールド | event群のactivityを維持 | 循環が活動する |
| 左右へ動かす | 発音位置を前後へ偏らせる | 突っ込む／溜める |
| 上へ動かす | ghostを主音へ昇格 | 密度と輪郭が増す |
| 下へ動かす | 主音をgapへ移す | 音数が減る |
| 素早く弾く | 直近eventを終端へ集める | フィル |
| 指を離す | activityを減衰 | 完成ループを残さず徐々に疎になる |
| 二声を二本指で寄せる | 局所的な合流点を作る | secondary One |
| 三本以上を寄せる | 各声を最短経路で共通着地へ向かわせる | primary One |
| 指を外へ開く | 合流後の時間差を広げる | 再散開 |

### 4.4 ブレイク

声を画面外へ払うと音は消えるが、その声が作っていたアクセント位置は残った声の `memory` に残す。再接触時は保存済みループ頭から再生せず、現在の関係へ復帰する。

### 4.5 主導権移動

Bass声を大きく動かすと音量ではなく `influence` が上がる。

- DrumはBassの着地点を補強する
- GuitarはBassの空白へ移動する
- Horn / StabはBassの持続中を避ける
- GhostはBassの着地後へ集まる

入力を弱めると主導権は再び分散する。

### 4.6 状態遷移

```text
Seed -> Interlock -> Lead -> Converge -> Interlock
                    |                    ^
                    +-> Break -> Return-+
```

- `Seed`: 単発音から関係を開始
- `Interlock`: 各声が隙間を分担
- `Lead`: 一声が他声の配置を動かす
- `Break`: 音を消し、関係は保持
- `Return`: 保存位置ではなく現在関係へ戻る
- `Converge`: 各声が異なる経路でOneへ向かう

## 5. Field Looperへ採用する点

現時点の採用候補であり、統合済み・実装済みではない。

1. オーディオループではなくイベント関係を循環させる
2. primary Oneと複数のsecondary Oneを持つ
3. マイクロタイミングを周期内の時間形状として扱う
4. ブレイク中も不在パートの関係を保持する
5. 声ごとの主導権を演奏中に移動できる
6. 指揮ジェスチャーをエフェクト操作ではなく、発音配置と構成変更へ接続する
7. 手を離した後、完成済み演奏を永久維持しない
8. ノンミュージシャンには音符選択の代わりに、前後、密疎、主従、合流、散開を渡す

## 6. 採用しない点

1. JB音源・ホーン・シャウトを鳴らすだけのスタイルプリセット
2. One専用ボタン
3. 全トラックの一括頭出し
4. 固定量のSwing
5. ランダムHumanize
6. Bass主導を音量上昇だけで表すこと
7. ブレイクを単純なmute / unmuteにすること
8. Brownの罰金・服装統制・過酷な労働支配

## 7. 失効した判断

### 7.1 Oneボタン

初期案では全トラックをOneへ戻す専用ボタンを置いた。これは既存ルーパーの再同期と変わらないため失効。

現在案では、複数指の収束運動によって各声が現在地から異なる経路を通り、共通着地点へ至る。

### 7.2 4声が別々の周期を持つという一般化

JBの中心をポリメーターとして扱う案は失効。共通拍を共有しつつ、小節内部の発音位置、休符、アクセント、時間偏差を分担する設計へ修正。

### 7.3 強押し操作

圧力入力を主導権操作へ割り当てる案は、現行iPhoneで安定した主要入力として依存できないため失効。移動量、速度、保持時間で代替する。

## 8. 失敗条件

次のどれかが起きれば、JB研究を反映した設計として失敗とする。

- 手を離しても完成済み演奏が永久に回る
- 変化がランダム生成へ委ねられる
- 全声が同じクオンタイズ位置へ常時吸着する
- ジェスチャーがfilter / delay量しか変えない
- Bassを主導させても音量しか変化しない
- ブレイク後の復帰が保存済みループの頭出しになる
- Oneが専用ボタンの効果音になる
- 良い結果を出すために事前打ち込みを必要とする

## 9. 未検証事項

1. 実録音をDAWへ読み込み、14曲すべての小節・発音位置・人物を再確認する
2. 《Cold Sweat》《Funky Drummer》《Sex Machine》《Doing It to Death》の時間軸付き転記
3. secondary Oneを画面表示せず触覚と音だけで理解できるか
4. iPhoneで4本以上の指を使うときの誤接触、画面遮蔽、システムジェスチャー競合
5. `coupling[4][4]` を演奏者が学習可能な一貫性で更新できるか
6. 手を離した後の減衰時間が、演奏継続性と「垂れ流し防止」を両立するか
7. event方式と録音音声方式をどう共存させるか
8. ノンミュージシャンによる初回演奏テスト
9. Charlie Hunter / Jeff Mills研究との統合時に、JBの分散した関係が失われないか
10. 実装対象パスとテスト条件の確定

## 10. Git状態境界

このREADMEは研究記録である。以下を証明しない。

- 製品設計としての採用
- `integration/` への反映
- コード実装
- iPhone実機での動作
- 音響的な妥当性
- ユーザーによる演奏検証

