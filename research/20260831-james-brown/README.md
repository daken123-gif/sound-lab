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



## 11. 四曲比較 — 反復の中で何が変わるか

> この節は音源の直接再生・波形採取ではなく、演奏者の証言、公開トランスクリプト、専門研究の記述を突き合わせた比較である。小節ごとの精密採譜と音源照合は未実施。

| 曲 | 変化の主座 | 根拠から読めること | エンジンへ移すなら |
|---|---|---|---|
| `Cold Sweat` | マイクロタイミングの周期形 | The One から偏差が広がり、次の One に向けて収束する。2小節目の beat 1 裏は副次的な収束点として働く | 音符を一様にスウィングさせず、周期内の位相に応じて各声部の遅速を拡大・収束させる |
| `Funky Drummer` | 不在声部の記憶 | ドラムだけになっても、フィルと着地が元の合奏の空間を保つ | mute を「消去」にせず、休んだ声部のアクセント予測を影として残す |
| `Sex Machine` | リーダーシップと応答 | count-off、歌と応答、bridge cue、bass/guitar/drums の噛み合わせが同じ反復を更新する | 一つの声部を一時的な leader にし、その onset・rest が他声部の選択確率を変える |
| `Doing It to Death` | 指名 cue による即時作曲 | 「誰が吹くか」「どこで構造を変えるか」が演奏中の指示で決まる | cue を装飾エフェクトでなく、役割・調的重心・密度を切り替える構造命令にする |

四曲は同じ「反復」の例ではない。少なくとも次の四つの更新機構に分かれる。

1. **MICROFORM** — 周期内部の遅速が呼吸する。
2. **MEMORY** — 休んでいる声部も、他声部の選択に痕跡を残す。
3. **LEADERSHIP** — leader の交代が合奏全体の onset と rest を再配分する。
4. **CUE** — 演奏中の短い命令が、次に成立する収束点で構造を変える。

この分解により、JB 的な生々しさを「スウィング量」「ヒューマナイズ」「シャッフル」の単一ノブへ畳む設計は棄却する。

## 12. The One の再定義

The One は毎小節の頭に置く固定アクセントではなく、直前まで分散していた関係が再び共有される**収束イベント**として扱う。

```text
spread -> tension -> viable convergence -> shared return
```

したがって、生成器は小節番号だけを見て One を鳴らさない。各声部について、直近の onset、休符、音価、リーダーへの追従度、break 中に保持した記憶を評価し、十分な声部が「戻れる」瞬間を候補にする。

```text
one_score(t) =
  agreement(t)
  + return_pressure(t)
  + remembered_accents(t)
  - collision_cost(t)
```

ここで `agreement` は全声部の同時発音率ではない。kick と bass が着地し、guitar や horn が休む場合も、役割が共有されていれば強い One になり得る。

### 副次的な One

`Cold Sweat` の2小節形から、副次的な収束点を持たせる。主 One と同じ強さのアクセントを複製するのではなく、次の主 One まで周期を保つ中間の結び目にする。

```ts
type Convergence = {
  strength: number;     // 主従
  participants: VoiceId[];
  phase: number;        // 周期内位置
  action: "land" | "leave-space" | "answer";
};
```

## 13. iPhone 演奏面の修正 — One を多指ジェスチャーに固定しない

前節の「複数指を寄せると One」という案は、象徴としては分かりやすいが、毎回の収束に3〜4本の指を要求すると演奏を止め、端末のジェスチャーとも競合する。よって必須操作としては棄却する。

代わりに、片方の親指で画面端を保持している間だけ **conductor layer** を開く。

| 状態 | 他の指の同じ動作 |
|---|---|
| 親指保持なし | 発音、休符、音価、attack を直接演奏 |
| 親指保持あり | `solo`、`break`、`return`、`downshift` など関係への cue |

重要なのはボタン数ではなく、演奏層と指揮層が同じ面に重なることだ。cue は押した瞬間に機械的に小節を切り替えず、次の `viable convergence` で実行する。親指を離せば即座に通常演奏へ戻る。

多指の「寄せる」動作は、全声部を強制的に同期させる命令ではなく、任意の強い `return_pressure` 入力として残す余地だけを持たせる。

## 14. 次のプロトタイプで反証可能にする条件

以下は史実ではなく、次段階の設計仮説である。

1. **放置劣化**  
   入力が止まったら録音ループのように同じ密度を維持せず、2〜4周期を目安に onset・attack・参加声部のいずれかが衰える。

2. **cue の遅延実行**  
   cue は必ず「次の小節頭」ではなく、関係上成立した次の収束候補で発火する。結果として実行時刻は演奏ごとに変わる。

3. **leader の波及**  
   leader 交代が音量だけでなく、少なくとも二つの従属声部の onset または rest の分布を変える。

4. **break memory**  
   mute した声部を戻したとき、録音済みループの先頭ではなく、休止中に他声部から推定した関係位置へ入る。

5. **One の非強制**  
   全声部同時発音を禁止しても One を知覚できる構成が生成される。休符も参加として記録される。

### 失敗判定

- どの曲モデルでも結果が同じ「少しヨレた16分」になる。
- cue が実質的にプリセット切替または fill ボタンになる。
- leader を替えても他声部の音量以外が変わらない。
- break 復帰が常にループ頭へスナップする。
- The One が最大ベロシティの同時発音にしかならない。

## 15. 今回の研究更新で確定したこと／未確定のこと

### 確定した設計判断

- JB の反復を四つの更新機構 `MICROFORM / MEMORY / LEADERSHIP / CUE` に分ける。
- The One を固定拍ではなく、声部関係の収束イベントとして実装候補にする。
- conductor layer は片親指保持で一時的に開き、通常の演奏面を恒久的なボタンで埋めない。
- 多指 pinch を The One の必須入力にしない。

### 未確定・次に検証すること

- 四曲それぞれの小節単位の転記と、公式音源への時刻アンカー。
- `viable convergence` の重みと閾値。
- 片親指保持が iPhone 実機で誤操作・疲労を生まないか。
- bass leader と drum leader で従属声部に生じる差の定量化。
- `downshift` を調的変化として一般化するか、曲固有 cue として限定するか。

## 16. この追記の根拠

- Patrick Ainsworth, “Microtiming in Early Funk” — `Cold Sweat` を含む初期ファンクの The One、周期内の偏差拡大と収束、副次的 One の分析。
- Fred Wesley interview (Red Bull Music Academy) — `Doing It to Death` の短時間での組み上げ、各奏者への指名 cue、対照的に長時間かかった `Papa Don't Take No Mess` の回想。
- Bootsy Collins interviews — `Sex Machine` の count-off、The One を軸にした bass、guitar の “chicken scratch”、歌と応答、bridge cue。
- John “Jabo” Starks interview (American Archive of Public Broadcasting) — Brown が一度舞台を離れても続いた Bootsy 期バンドの groove に関する証言。
- Bonedo specialist analysis — `Sex Machine` で drums / bass / guitar の共有アクセントが限定され、休符を含めて歯車状に噛み合うという補助的分析。



## 17. 訂正 — LEADERSHIP は一枚の権限ではない

前回の `LEADERSHIP` は、leader が他声部の onset / rest を直接変える一つの変数としていた。しかし、これは Brown の指揮とバンドの groove を一つの上下関係へ潰している。

Patrick Ainsworth の初期 funk のマイクロタイミング分析では、`Cold Sweat`、`Funky Drummer`、`Sex Machine`、`Super Bad` における Brown の vocal interjection は、drums のリズムを有意に攪乱していないとされる。Brown は恐るべき bandleader であると同時に、groove の内部では「バンドの一部」として振る舞う、という観察である。

一方、`Funky Drummer` では Brown が事前に lay out と return を言語で指示し、count の後に全員が抜け、drummer を残し、再度戻す。この二つは矛盾しない。**構造を決める権限と、拍を生成する権限が別だからである。**

したがって、`LEADERSHIP` を廃止せず、次の三つへ分解する。

| 権限 | 決めるもの | JB 研究上の例 | 他権限への影響 |
|---|---|---|---|
| `STRUCTURAL_AUTHORITY` | break、return、solo、modulation、区間境界 | Brown の count と指名 cue | 拍そのものを再生成しない |
| `PULSE_AUTHORITY` | 位相、周期、microtiming contour、着地可能性 | Stubblefield / Starks が維持する pocket | 構造 cue の実行可能時刻を与える |
| `PHRASE_AUTHORITY` | 局所フレーズ、fill、応答、音価 | drummer の ghost note、horn や vocal の応答 | 一時的に attention を移す |

これは固定メンバー表ではない。同じ人物・同じ声部が、ある瞬間には複数の権限を持てる。重要なのは、人ではなく**何を決める権限か**を分離することだ。

## 18. Cue は時計を奪わず、実行待ちになる

Brown 型 cue を、押した瞬間に全体を切り替える UI event として処理しない。cue はまず発行され、pulse が成立させた次の収束可能点まで待つ。

```ts
type PendingCue = {
  action: "break" | "return" | "solo" | "downshift";
  target: VoiceId | VoiceGroup;
  issuedAt: AudioTime;
  issuer: AuthorityId;
  executeAt: "next-viable-convergence";
  urgency: number;
  expiresAfterCycles: number;
};

type PulseState = {
  phase: number;
  cycle: number;
  confidence: number;
  microtimingContour: number[];
  candidateConvergences: Convergence[];
};
```

実行器は次の順序で動く。

1. `STRUCTURAL_AUTHORITY` が cue を pending queue に入れる。
2. `PULSE_AUTHORITY` は現在の groove を止めず、収束候補を更新する。
3. cue 対象の voice が、現在の note / rest を壊さず移行できるか評価する。
4. 最初の十分な候補で cue を実行する。
5. 実行後も pulse の位相は原則として連続させる。

```text
can_execute(cue, t) =
  pulse_confidence(t) >= p_min
  && convergence_score(t) >= c_min
  && transition_collision(cue, t) <= k_max
```

ここで閾値は未確定であり、史実の数値ではない。実装時に演奏感から反証する対象である。

### 強制 cue

通常 cue と、即時停止を必要とする強制 cue は分ける。JB の演奏上の cue から非常停止までを同じ仕組みにしない。

```ts
type CueMode =
  | "musical-pending"  // 関係を保って次の収束で実行
  | "hard-stop";       // 安全・明示停止。収束を待たない
```

## 19. Break memory の根拠を強める

Anne Danielsen の `Continuity and Break: James Brown's 'Funky Drummer'` は、cut によって残った drum が目立つだけでなく、消えた bass、organ、guitar、horn の層も「不在」として知覚されると論じる。break は単純なトラック削除ではなく、直前まであった関係を露出させる操作である。

この観察から、`MEMORY` は録音データの保持ではなく、予測されていた関係の保持とする。

```ts
type AbsentVoiceMemory = {
  voice: VoiceId;
  expectedOnsets: PhaseDistribution;
  expectedRests: PhaseDistribution;
  lastRelationToPulse: number;
  lastRelationToPeers: Record<VoiceId, number>;
  decay: number;
};
```

break 中、消えた voice の audio は鳴らさない。しかし、その `expectedOnsets` と `expectedRests` は残った voice の配置評価に使う。復帰時は録音ループの先頭でも、機械的な小節頭でもなく、その時点で更新された関係位置へ入る。

このため、break は subtractive mixer ではなく、**聞こえない声部を含む合奏状態**になる。

## 20. 最小シミュレーターの仕様

次の実装段階では音色を作り込まない。四声部の event だけで、権限分離が成立するかを先に試す。

### 入力

- 4 voices: `DRUM / BASS / GUITAR / HORN`
- 各 voice: onset、rest、duration、accent、phase
- 2-cycle の初期 pattern
- cue: `break / return / solo / downshift`
- authority assignment: structural / pulse / phrase

### 観測ログ

```ts
type ObservationFrame = {
  time: AudioTime;
  pulsePhase: number;
  activeVoices: VoiceId[];
  pendingCues: PendingCue[];
  executedCue?: PendingCue;
  convergenceScore: number;
  authorityMap: Record<AuthorityKind, VoiceId | "performer">;
};
```

### 合格条件

- structural cue を発行しても、その瞬間に pulse phase が飛ばない。
- pulse authority を DRUM から BASS へ移すと、収束候補の位置が変わる。
- phrase authority の solo は他声部を一律 mute せず、rest 密度を局所的に再配分する。
- break 中に absent voice memory が更新され、return が固定 loop start にならない。
- Brown 相当の structural authority が発音しなくても cue を出せる。
- Brown 相当の vocal voice が発音しても、それだけで drum microtiming が引きずられない。

### ここで棄却する実装

- `leaderId` 一つだけで timing、form、solo をすべて支配する。
- cue 受信時に sequencer position をゼロへ戻す。
- break を単なる gain = 0 として扱う。
- humanize の乱数だけで voice 間の差を作る。
- One のたびに全 voice を同時発音させる。

## 21. 追加資料

- Patrick Ainsworth, [Microtiming in Early Funk](https://www.gmth.de/zeitschrift/artikel/1224.aspx)
- Anne Danielsen, [Continuity and Break: James Brown's 'Funky Drummer'](https://www.researchgate.net/publication/334695958_Continuity_and_Break_James_Brown%27s_%27Funky_Drummer%27)
- NPR / KLCC, [The Original Funky Drummers On Life With James Brown](https://www.klcc.org/npr-music/2015-01-05/the-original-funky-drummers-on-life-with-james-brown)
- Roland, [Behind the Beat: “Funky Drummer”](https://articles.roland.com/behind-the-beat-funky-drummer-by-james-brown/)

## 22. この更新後に残る検証

- `Funky Drummer` の full take を正規に取得し、cue 発行、count、cut、return の時刻を音源から転記する。
- `Cold Sweat` の二小節 microtiming contour を一次分析表から数値化する。
- pulse authority の交代と、単なる instrument mute の聴感差を比較する。
- 最小シミュレーターを実装し、上記ログを実際に採取する。
- iPhone 実機の conductor layer は、シミュレーターが成立した後に検証する。

