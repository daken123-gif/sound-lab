# Autechre研究 — 反復・因果・ライブシステム

- research-id: `20260831-autechre`
- 状態: `active`
- 研究区分: `long-term`
- 研究対象: Autechre（Sean Booth / Rob Brown）の反復、生成過程、ライブシステム、身体操作
- 現在の問い: 固定ループの垂れ流しを避けながら、ノンミュージシャンがiPhone上でリアルタイムに構造を演奏できる原理として何を抽出できるか
- 更新日時: 2026-09-02 UTC
- 基点: `sound-lab/main` commit `95030a185aed933bf5595fc694194563399ca5dd`

## 長期研究指定

2026-09-02、ユーザー指定によりAutechreを長期研究とした。`active`は現在の進行状態、`long-term`は一回の調査で閉じず継続更新する研究区分を表す。長期指定だけでは、設計候補の製品採用、実装、`integration/`への反映を意味しない。

継続軸は次の四つとする。

1. 作品ごとの反復、局所周期、空白、長期密度の聴取・実測。
2. 複数の`AE_LIVE`で、共通する系と公演ごとの差を分離する比較。
3. 固定ループを避ける因果エンジンとマルチタッチ演奏の設計研究。
4. Jeff Mills、Charlie Hunter、J Dilla、Aphex Twin、独立DRUM研究との接続。ただし他研究の本文を取得せず、名称や要約だけから内容を補わない。

## この記録の証拠境界

この研究は、本人インタビュー、公式ディスコグラフィー、および一次資料を引用する記事を中心にした文献研究である。AutechreのMaxパッチ、ライブシステム、マルチトラック素材、内部パラメータは取得していない。曲ごとの波形・イベント列・テンポ・スペクトルの実測もまだ行っていない。

以下を分離する。

- **本人発言／公開事実**: 取得したインタビューまたは公式公開面で確認できる内容。
- **分析**: 本人発言と公開作品史から、この研究で行う解釈。
- **設計候補**: Sound Labへ移す可能性のある構造。製品採用ではない。
- **非採用**: Autechreを参照しても、この楽器には移さないもの。
- **未検証**: 音源実測、実装、ブラウザ、iPhone、聴感で確認していないもの。

## 現在の結論

Autechreから移すべき中心は、グリッチ音、金属的FM音、ランダムなドラム、Max/MSPという製品名ではない。

移す候補は、次の三つである。

1. **固定された音列ではなく、音同士の関係と変化条件を演奏する。**
2. **反復を消さず、同一内容の再生から、複数時間尺度の再帰へ変える。**
3. **システムを自動作曲者にせず、演奏者へ予想外の結果を返す応答相手にする。**

この三点から、Autechreの方法を暫定的に**開放された因果ファンク**と呼ぶ。これは本人たちの用語ではなく、本研究の分析語である。

## 1. 出発点はヒップホップとエレクトロ

### 本人発言／公開事実

- AutechreはSean BoothとRob BrownによるデュオとしてWarpから作品を発表している。
- Seanは2023年のインタビューで、自分たちは「前衛」とダンスフロアを跨いできたのではなく、エレクトロが発展し続けたら何になるかを追ってきたと説明している。
- 同じインタビューで、初期UK bleepの乾いた音、矩形波、高低音の組合せ、街路的な出自について具体的に語っている。
- 2010年のインタビューでも、本人が聴く中心としてヒップホップを挙げ、BDP、Ultramagnetic MC's、Terror Danjahなどへ言及している。

### 分析

Autechreの複雑化は、ダンス音楽から現代音楽へ逃げた歴史ではない。スクラッチ、ブレイク、ドラムマシン、初期エレクトロが持つ身体的な切断と反復を、通常の小節と曲構造を越えて発展させた歴史として読むほうが、本人発言と整合する。

したがってSound Labで参照すべきなのは「難解さ」ではなく、身体が掴める力を残したまま、拍の予測だけを不安定にする方法である。

## 2. 反復の変遷

### 本人発言／公開事実

Seanは2023年のインタビューで、後期作品は突然アルゴリズム音楽になったのではなく、全音楽はもともと命令列としてアルゴリズム的だと述べている。通常の曲にも「この音を順番に鳴らす」「一定回数反復する」「一部を変える」という規則がある。後期に変わったのは、その規則がよりopen-endedになったことと、反復の扱いである。

本人による回顧は、おおよそ次の系列を示す。

| 作品期 | 本人が回顧した問い |
| --- | --- |
| `Tri Repetae` | ループを通常より長く、許容限界近くまで続ける |
| `Chiastic Slide` | 何をループできるか、ループへ何を行えるか |
| `LP5` | ループ中心の方法へ通常のsongwritingをどう取り込むか |
| `Confield`以降 | ループ構造への拘束を弱め、別の音楽的な考えを試す |
| 後期ライブ | より開いた規則をリアルタイムで扱う |

`Anti EP`の`Flutter`は、同一のbeatを持つbarがないようプログラムされたと盤の警告文で説明された。これは後期のシステムと同一ではないが、反復の法的定義を音楽構造で攪乱した初期例である。

### 分析

反復と非反復を二択にしないことが重要である。

`Flutter`的な「異なる小節を大量に連結する」方法だけでは、固定列が長くなっただけで、十分長い尺度では再び一つの巨大ループになる。後期のopen-endedな方法では、次のイベントが現在状態、過去イベント、演奏操作、別声部の状態によって変化できる。

必要なのは**ループをなくすことではなく、同一性を保つ層と変化する層を分離すること**である。

- 音色族、密度域、重心、拍の気配は残す。
- 発音位置、休止、因果順序、別声部への波及は固定しない。
- 短期では変化し、長期では同じ生物に聞こえるようにする。

## 3. process、parameter、compositionは別の方法

### 本人発言／公開事実

2005年のSean Boothインタビューには、`Confield`期だけでも異なる三種類の作り方が示されている。

1. `VI Scose Poise`: Maxで作ったMIDI sequencerを走らせ、counterが変化を起動する。問題があれば変数を直して再実行するhands-offなprocess。
2. `Uviol`: 設定したfader parameterに応じて生成内容が変わるsequencerを作り、後からリアルタイムに演奏する。
3. `Draft 7.30`: real-time inputが少なく、ほぼcomposedな方法。

同じAutechre作品でも、生成、パラメータ演奏、細密作曲は排他的な流派ではなく、曲ごとに選ばれている。

### 分析

「Autechre = generative」という一語では方法差を失う。Sound Labでも、少なくとも次を別状態として扱う必要がある。

| 状態 | 人間の位置 | システムの位置 |
| --- | --- | --- |
| process audition | 規則を作り、結果を聴き、規則を直す | 自走する |
| parameter performance | 方向、強度、遷移をリアルタイムに動かす | 制約内で詳細を返す |
| direct composition | イベントを直接決める | 記録・再生・編集を担う |

このプロジェクトの主演奏経路へ適する中心候補は`parameter performance`である。process auditionを前面へ置くと自動作曲機へ寄り、direct compositionだけにするとDAWやstep sequencerへ寄る。

ただし、三者を一つの隠れたモードで切り替えさせない。どの状態にいるかが演奏者から判別できなければならない。

## 4. timelineを消す意味

### 本人発言／公開事実

Seanは2005年、画面上のtimelineを見せないsequencerのほうが、適切なpaceを持つ音楽を作りやすく、Autechreの良い仕事の多くはnon-timeline sequencerで作られたと述べている。audio editingにはtimelineを使うが、MIDI制作では停滞を招く場合があるとも述べている。

また、Nord Leadについて音色だけでなくinterfaceを高く評価し、mouseで画面上のknobを動かすより、物理的に触れて聴くことを好むと話している。

### 分析

timelineを消すことは、時間を消すことではない。時間を「左から右へ配置された物体」から「現在の操作に応じて進む状態」へ変えることである。

Sound Labでは、録音済み4トラックの実波形と再生位置は隠してはならない。一方、Autechre由来の演奏層をピアノロールやstep gridとして追加する必要もない。

候補となる分離は次の通り。

- **録音層**: 実波形、録音状態、再生位置を明示する。
- **演奏層**: 現在の因果状態へ触れる。未来の全イベントをtimelineへ固定しない。
- **Performance Take**: 操作と結果を記録するが、記録開始は人間が明示する。

## 5. “the system”とライブ

### 本人発言／公開事実

- 2018年のインタビューで、二人はsoftware patchを交換し、互いの作業を反復的に変形している。
- sequencerが一種類のsequenceしか作れない場合、それはtechnologyなのかmusicなのか、境界が曖昧になると話している。
- `Exai`は、後のライブシステムが曲間遷移まで安定する前に行った個別のtrial runを編集したものだと、Seanが2023年に説明している。
- システム安定後は全公演を録音し、会場の形、観客、二人がその瞬間にしたことによって公演ごとの差が生じたと説明している。
- Robは、ツアーで毎日演奏することで、互いとシステムから学び、失敗したら巻き戻さず先へ進むと述べている。
- Seanは、観客よりRobへ応答して演奏することが多く、視覚的な演技より音そのものを重視すると話している。

### 分析

ライブシステムは完成曲を吐く自動生成器ではない。二人の操作、直前の出力、相手の判断、会場の音響が循環するため、システムは第三の応答相手として働く。

重要なのは、予想外の出力そのものではなく、予想外の出力へ次の演奏で応答できることだ。事故をrandomizeボタンで起こすだけでは即興にならない。

## 6. Sound Lab向け因果エンジン候補

以下はAutechreの内部システムを再現したものではない。本研究が抽出した設計候補である。

### 6.1 各声部が持つ状態

独立ドラムの各voice、または録音素材へ作用する各modulation agentは、最低限次を持つ。

| 状態 | 役割 |
| --- | --- |
| `phase` | 現在どの周期位置にいるか |
| `rate` | 局所周期。master tempoと同一でなくてよい |
| `energy` | 発音または変形の強さ |
| `density` | 単位時間内のイベント傾向 |
| `refractory` | 直後の再発を抑える時間 |
| `memory` | 最近のイベント族、間隔、強度 |
| `materialFamily` | 同一性を保つ音素材の範囲 |
| `coupling` | 別voiceから受ける影響 |
| `gestureBias` | 現在の接触操作が与える方向 |

### 6.2 イベント決定

単純な`probability per step`ではなく、イベント候補の発生しやすさを現在状態から計算する。

```text
event tendency
  = base tendency
  + current gesture bias
  + coupled events from other voices
  - recent repetition penalty
  - refractory suppression
```

これは確率を入れること自体が目的ではない。

- 同じ操作には同じ傾向が返る。
- 直前の履歴が異なれば、細部は異なる。
- 演奏者が方向を戻せば、音楽的な領域も戻せる。
- 完全再現が必要なときは、seedだけでなく操作と状態遷移をPerformance Takeへ記録する。

### 6.3 因果結合の例

- kick候補が休止したとき、その空白がbass変形の発生可能性を上げる。
- hat密度が上限へ近づくと、snareを増やさず、snare前後の空白を広げる。
- 録音トラック2のtransientが一定域を越えたときだけ、独立ドラムの局所位相を一時的に引く。
- 一つの声部が同じmaterial familyを続けたら、別声部の音色ではなく因果の向きを反転する。

音量、filter、delayを同時に動かすmacroだけでは、音色変化は起きても出来事の因果は変わらない。Autechre研究から移すべきなのは後者である。

## 7. マルチタッチへの翻訳

### 設計候補

指一本をparameter一個へ固定すると、画面は仮想knobの集合になる。代わりに、接触を因果場への介入として扱う。

- **接触点**: どの素材領域／声部関係へ介入するか。
- **移動**: 現在状態をどちらへ押すか。
- **速度**: 変化量ではなく、遷移の切迫度へ影響させる候補。
- **複数接触間の距離と向き**: 二領域のcouplingを一時的に強める／弱める候補。
- **release**: effectを切るだけでなく、介入後の慣性を残す候補。

これは最終mappingではない。`integration/DIRECTION.md`が固定している通り、`pressure` / `contactArea`はiPhone実機検証前に音響へ割り当てない。また深い階層、隠れたモード、同時押し必須を中心にしない。

トリプルタッチを上限として設計する根拠も、現時点ではない。重要なのは認識可能な最大指数ではなく、一つの接触が関係へどこまで作用できるかである。

## 8. 現行Sound Labとの接続境界

現在のGit判断を優先する。

### 既存判断

- `D-001`: 4トラックを録音の中心にする。
- `D-002`: IDM／Autechre方向のドラム演奏系を4トラックから分離する。
- `D-004`: 録音開始は人間が決める。
- `D-006`: 有名機材・作家を機能カタログとして模倣しない。
- `D-007`: 録音後の主演奏面はSkulptur型を中心にする。
- `D-008`: KAOSS中心階層を復活させない。
- `D-009`: 操作経路は短くするが、強制横画面や旧UIを継承しない。

### 接続候補

```text
4トラック録音（手動開始・実波形）
  -> Skulptur型の素材直接演奏（主演奏面）
  -> 必要な箇所だけ因果modulation hook
  -> mix / output

独立DRUM因果エンジン
  -> 明示同期または明示音声接続
  -> mix / output
```

Autechre由来の構造は、4トラックを四つの自動生成器へ置き換えない。Skulptur型主演奏面も置き換えない。第一候補は独立DRUMの時間文法、第二候補は録音素材へ作用する限定的な因果modulationである。

この接続は`candidate`であり、`integration/DECISIONS.md`へはまだ採用判断を記録しない。

## 9. 採用候補／採用しない点

### 採用候補

- 固定patternではなく、履歴を持つevent rule。
- 全声部を一つのstep gridへ閉じ込めない局所clock / phase。
- 演奏者のgestureを、イベントの直接指定ではなく方向づけとして使う経路。
- 声部間のcouplingを演奏対象にする。
- 事故後も現在状態から進める非破壊Performance Take。
- すべての音を前面へ出さず、深度と知覚の選択性を残すmix思想。

### 採用しない点

- Autechre風の金属音、click、glitchをpreset化する。
- Max/MSPを使用すること自体を価値とする。
- randomizeボタンで複雑さを代替する。
- システムが録音開始、素材選択、曲の進行を決める。
- 4録音トラックを生成ドラムvoiceへ変える。
- Autechre専用の別画面、深い編集画面、parameter一覧を常設する。
- 暗闇ライブや視覚演出を、そのままiPhone UIの非可視性へ移す。
- 本人たちの長年のシステムを、初心者向けの数個のmacroへ縮約して再現済みと称する。

## 10. バイアス検査

- **有名作家バイアス**: Autechreの名声を採用根拠にしない。対象は反復、因果、身体操作の構造に限定した。
- **feature accumulation bias**: 新しい生成機能一式を追加しない。既存の4トラック、独立DRUM、Skulptur境界の中で候補位置を限定した。
- **DAW convergence bias**: piano roll、step grid、automation laneを中心にしていない。
- **automation bias**: システムに録音開始、素材選択、完成判断を渡していない。
- **UI inheritance bias**: Autechreの暗闇公演やMax画面を製品UIへ移していない。
- **implementation bias**: 現在は文献研究であり、code、runtime、音質、操作感を実証したとは扱わない。

## 11. 作品別の次の分析系列

次の系列は聴取・実測計画であり、今回の文献取得だけで解析済みとはしない。

| 作品 | 確認する問い |
| --- | --- |
| `Flutter` | 同一barを避けながら、何が一曲としての同一性を保つか |
| `Clipper` | 長い反復で許容限界をどう作るか |
| `Cichli` | loop内変形とloop間変形をどう分けるか |
| `Drane2` | 反復と長期構造から情動がどう生じるか |
| `VI Scose Poise` | hands-off processで形態がどう維持されるか |
| `Uviol` | fader parameter performanceが結果へどう現れるか |
| `Gantz Graf` | rhythm、timbre、gestureを同一イベントとして聴けるか |
| `bladelores` | 長い時間尺度でsystemと感情をどう両立するか |
| `pendulu hv moda` | 複数周期と空白の階層 |
| `gonk steady one` | pulseの存在と知覚上の曖昧さ |
| 複数の`AE_LIVE` | 同一toolsetから各公演の差がどこに現れるか |

実測時には、拍位置を一つのBPMへ強制せず、event interval、accent、休止、同時発音、局所period、長期密度を別々に記録する。

## 12. 反復史の再記述 — 非反復から状態遷移へ

### 証拠から分けられる四層

今回の追加調査では、Autechreの反復を「同じbarがある／ない」だけで扱わず、次の四層へ分ける。

| 層 | 固定または再帰するもの | 変化しうるもの | 研究上の問い |
| --- | --- | --- | --- |
| event sequence | 発音イベントの並び | 各barの打点 | 同一barを避けても、長い固定列になっていないか |
| relation | 声部、音色族、密度域、重心の関係 | 個々の発音位置、休止、accent | イベントが変わっても何が同じ曲として残るか |
| state transition | 現在状態から次状態へ移る条件 | 条件分岐、履歴、他声部の入力 | 何が次の出来事を可能／不可能にするか |
| performance trajectory | 同じtoolsetと可動範囲 | 演奏者の操作、公演ごとの経路 | 同じ系から、どこまで異なる演奏が生まれるか |

この分離により、公開資料から読める変遷は次のようになる。

1. **`Flutter`: event sequenceの同一性を崩す。** 盤面警告では、同一beatを持つbarがないようプログラムされたとされる。これは法的な「repetitive beats」を作品構造から攪乱した。ただし、公開された録音としての`Flutter`は再生ごとに同じ記録を返す。したがって、bar非反復はopen-ended generationと同義ではない。
2. **`Tri Repetae`: loopの持続を閾値まで押す。** Seanの2023年の回顧では、loopを通常より長く、許容限界近くまで持続させ、incrementalに変化させること自体が中心だった。ここでは反復を避けず、聴取の耐久と微差の知覚を作曲対象にする。
3. **`Chiastic Slide`: loopを対象から操作可能な物質へ変える。** 問いが「何をloopできるか」「loopへ何を行えるか」へ移る。固定patternへ装飾を重ねるのではなく、loopの内部、境界、変形可能性を調べる段階として読む。
4. **`Confield`: event sequenceよりprocessとparameter relationを前面化する。** 2005年のSeanの説明では、`VI Scose Poise`はcounterが変化を起動するhands-off process、`Uviol`はfaderでgeneration parameterを演奏するsequencerから作られた。一方、同じ時期の全曲を一つの生成方式へまとめられず、曲ごとにprocess、performance、細密作曲の比率が異なる。
5. **`AE_LIVE`: state transitionを二人で演奏し、trajectoryを作品化する。** 2015年のSeanの説明では、note sequencingの多くは毎回異なる一方、各trackの全体的な“flavor”と可能範囲は保たれ、結果の多くはconditionalsで決まる。二人はdataを共有し、相互のsystemが無視するか反応するかを操作できる。ここでは単発の生成結果ではなく、同じ系を各公演でどう通過したかが記録になる。

### 現在の修正結論

Autechreの進展を「反復が減り、ランダムが増えた」とは記述しない。より正確には、**反復の正本が、音声列から関係、状態遷移、演奏経路へ順に移動した**と仮定する。

これは作品の波形・イベント列を測定した確定結果ではない。本人発言と公開資料から立てた歴史モデルであり、`Flutter`、`Clipper`、`Cichli`、`VI Scose Poise`、`Uviol`、複数の`AE_LIVE`を同じEVENT / RELATION / TRANSITION記法で測って反証する。

## 13. Git上の並行研究本文との接続

### 取得した研究実体

| 研究 | 取得ref | README blob | 証拠状態 |
| --- | --- | --- | --- |
| Charlie Hunter | `research/20260902-charlie-hunter@6d0a0c053c94a3e3f14dc58583880f7ee26c240d` | `080c91224ccbf2fbc224ac8cb40790c6c122797f` | `researching`。同一身体に拘束された低音／上声関係。音源測定は未実施 |
| J Dilla | `research/20260902-j-dilla@3e9249a3a3ea676d141c8ab55553f49f4d6dc3fa` | `e0e5e1b2d7f329091ddb12b483fee9c6a05f9058` | `researching`。複数clock candidateとpreview周期解析。微細timingは未確定 |
| Jeff Mills | `research/20260902-jeff-mills@06fb70d76da8020b1919e3e69ad10448a1563498` | `39b514ffcfd1c060b2112d7c6b10a7858163ebd2` | `researching / long-term`。本人資料と演奏観察。解析音源は未取得 |
| Aphex Twin | — | — | `not found in searched Git scope`。`sound-lab`の全head名、`sympathia`の`aphex` / `twin` branch名、`sympathia`の全状態PR、両repoのdefault-branch code searchを確認したが本文未取得 |

Aphex Twinは「存在しない」とは判定しない。今回検索したGit範囲で本文を取得できていないため、名称だけでAutechreとの差や共通項を補完しない。

### 接続して残る差

| 研究 | 現在形で演奏する関係 | Autechreと接続する点 | Autechreへ回収しない点 |
| --- | --- | --- | --- |
| Charlie Hunter | 同一身体に拘束された低音／上声の音価、mute、局所前後差 | 別声部が互いの次の可能性を制約するcoupling | system間data共有は、一人の手と姿勢が作る身体制約の代替にならない |
| J Dilla | 安定層を残したclock候補間の分割、位相、attack、長周期 | 単一master gridを正解にせず、関係と変化規則を保存する | open-ended generationは、Dilla固有の時間形状や録音済みtimingの証明にならない |
| Jeff Mills | 持続する床を保ちながら、cut、entry、位相事故、回復を短い判断窓で組み替える | 現在状態から事故を消去せず次の構造へ変換する | conditionalsによる自律遷移は、Millsの即時認知、手動破断、回復判断の代替にならない |
| Autechre | relation、condition、履歴、相互dataによる次イベントとtrajectory | relation自体を演奏し、同じtoolsetから非同一の結果を作る | Hunterの身体拘束、Dillaの実測timing、MillsのDJ状況判断を「生成系」で一括自動化しない |

共通項は「複雑さ」でも「ずれ」でもない。**反復中の同一性を保持する層と、現在形で更新する関係を分けること**である。ただし、保持の担い手は同じではない。

- Hunterでは身体と実行可能性。
- Dillaでは安定層と競合する時間基準。
- Millsでは床の連続性と演奏者の回復判断。
- Autechreではtoolset、可動範囲、condition、共有data。

### Sound Labへ接続する場合の候補境界

この比較から直ちに新機能は採用しない。独立DRUMの研究候補を記述するなら、一つの「Autechreモード」ではなく次を別軸として保つ。

1. `BODY_COUPLING`: 一つのgestureが複数voiceの実行可能性を拘束する。
2. `CLOCK_RELATION`: voiceごとのclock candidate、phase、再合流条件を保持する。
3. `FLOOR_AND_BREAK`: 持続層と手動破断層を分け、事故後の回復を演奏者へ残す。
4. `STATE_TRANSITION`: 履歴、別voice、gestureから次イベントの可能範囲を変える。

四軸は同時実装を意味しない。特に`STATE_TRANSITION`が他三軸を自動化すると、Hunter、Dilla、Millsから取得した身体的・時間的・判断的な差を消してしまう。Autechre研究からの第一実験は、独立DRUM内で`STATE_TRANSITION`だけを最小化し、録音開始、素材選択、4トラック、Skulptur主演奏面へ権限を広げない。

## 14. AE_LIVEの変化を四段階へ分ける

### 追加取得した事実

1. 2014/15の`AE_LIVE`について、Seanは2015年に、note sequencingの多くは毎回異なるが、各trackの全体的な“flavor”と可能範囲は保たれ、conditionalsと二人のdata共有が即時反応を可能にすると説明した。
2. Seanは2018年、2014 live setを、全要素を前面へ出したcartoon-likeなclub musicとして回顧し、その後は初聴で気づかない要素を含むdeep mixingと三次元的なsound stageへ関心が移ったと説明した。
3. 2016年11月の本人インタビューでは、2014/15系を「そのsetの行き止まり」と判断して新しいsetを作り、以前より少し遅く、soundとbeatへ焦点を移したと説明している。`elseq`は旧`AE_LIVE`と同じsetup systemから生まれ、新setは別のものと明示された。
4. 同じ2016年インタビューで、Kino Šiškaの音響と会場経験を、新setを作る際の参照にしたと両名が述べている。会場は演奏結果へ反応する外部条件であるだけでなく、set設計以前へ遡って作用していた。
5. 2023年の本人インタビューでは、2022年からのsetに少なくとも第一・第二iterationがあり、dancefloor向けに作られたsetをseated venueでも演奏したこと、会場形状、観客の参加、分単位の判断が公演録音の差へ作用したと説明している。
6. 公式公開面では、`AE_LIVE 2016/2018`は2016年5公演と2018年2公演の計7録音、`AE_2022－`は2022年から2024年までの計19録音を一つの系列として掲載している。

### 一つの「ライブ差」に潰さない

| 変化層 | 何が変わるか | 現在の証拠例 | 同一視してはいけないもの |
| --- | --- | --- | --- |
| `SYSTEM_GENERATION` | setup、sequencing、synthesis、controlの基盤 | 2014/15系を終え、2016に別setを構築 | 一夜の即興差 |
| `SET_ITERATION` | 同じ世代内の構成、可動域、会場想定 | 2022 setの第一・第二iteration | system全体の作り直し |
| `PERFORMANCE_TRAJECTORY` | conditionalsを通る経路、二人の操作、分単位の判断 | 同一tour内の公演差 | 曲またはsetの固定構造 |
| `CAPTURE_CONTEXT` | 会場形状、音響、観客の参加、収録条件 | Kino Šiška参照、2022以降の会場差 | 演奏者の操作だけで生じた差 |

したがって、複数の`AE_LIVE`を比較して共通部分が見つかっても、それを直ちに「systemの不変核」としない。公演間の共通性は、同じset iteration、似たtrajectory、venue制約、編集・収録条件からも生じうる。逆に大きな差も、system generationの変更ではなく、一夜のtrajectory差である可能性がある。

### 比較実測の設計

最初の比較は二段に分ける。

#### A. 同一世代内

- `AE_LIVE 2016/2018`から2016年の3公演を選ぶ。
- `AE_2022－`から2022年の3公演を選ぶ。
- 各組で、局所period、event density、休止、onsetの離散性、spectral depth、長期密度曲線、再帰区間を同じ方法で測る。
- wall-clockの同じ時刻を機械的に対応させず、self-similarityと知覚上の状態遷移から候補区間を作り、人手で再確認する。

#### B. 世代間

- 2014/15、2016/18、2022－から各3公演を使う。
- 世代内分散を先に求め、その範囲を越える差だけを世代差候補にする。
- 本人発言にある`upfront / deep mixing`、`slower`、`sound / beat`、会場想定を測定項目へ翻訳するが、発言へ合う結果だけを選ばない。

音源は公式公開面で再生・購入経路を確認したが、今回の更新では音声ファイルを取得していない。上記は実測済み結果ではなく、比較対象と反証方法の固定である。

### Sound Labへ返る新しい境界

deterministic replayを設計するとき、seedとgestureだけでは不足する可能性がある。研究上の候補snapshotは次になる。

```text
PERFORMANCE_RECORD {
  system_generation
  set_iteration
  initial_state
  gesture_and_control_events
  inter_system_messages
  state_transitions
  audio_clock
  venue_or_device_context
}
```

これは製品仕様ではない。特に`venue_or_device_context`を自動補正の口実にせず、何が演奏者の操作で、何がiPhone、browser、speaker、roomによる結果かを再現時に分離するための研究候補である。

## 15. 2022／2025 AMA原文による修正

### 取得範囲

- 2022年7月のSean Twitch AMA全文transcriptから、live setの設計量、柔軟性、deterministic chaos、seed、controller、live set cellに関する回答を取得した。
- 2025年4月のKEYOSC AMAは、SeanとRobが回答した約500問のtranscript本体とspreadsheetを取得し、少なくともQ22–24、Q58–65、Q67を主張単位で確認した。

AMAは本人回答だが、即時回答、記憶の留保、質問側の仮説を含む。質問文に詳細なcell番号やBPMがあっても、Seanが肯定していない細部は本人確認済み事実へ昇格させない。

### 1. 自由度は広さではなく、破綻しない可動域である

Seanは2022年、現在のlive setはalbum以上に作業量が多い場合があり、十分なflexibilityとvariationを持たせながら、off-the-cuffにも完全固定にもせず、parameterを動かしただけで悪い結果になる自由度を避ける必要があると説明した。

これにより、本研究の「open-ended」を無制限な状態空間と読む経路を修正する。

```text
PERFORMANCE_SPACE = {
  reachable_states
  guarded_transitions
  controllable_instability
  designed_failure_bounds
}
```

`guarded_transitions`と`designed_failure_bounds`は本研究の分析語であり、本人の実装名ではない。意味するのは、何でも起こせることではなく、演奏者が強く介入しても音楽として次へ進める範囲を事前に設計することである。

### 2. “random”はrandom objectと同義ではない

Seanは同じAMAで、random objectをそのまま使う方式ではなく、deterministicなchaosを制御し、特定の方法でseedできる仕組みを使うと説明した。randomに聞こえるstateへ持っていけるが、本人はそれがrandomでないことを知っているとも述べた。

したがってAutechre由来の候補を次のように訂正する。

- `randomize`: 非採用。現在状態と関係なく結果を振り直す。
- `seeded chaos`: 研究候補。初期条件と操作履歴から予測困難だが再検査可能な差を作る。
- `selection`: 必須。複数生成物から選ぶ、交配する、方向づける判断を自動生成へ渡さない。

ただし「seedがあれば公演全体を再現できる」とはまだ言えない。Seanの回答が直接支えるのは、自身のchaos機構がdeterministicでspecificにseed可能だという範囲であり、二人分のlive system、外部controller、message timing、software dependency、audio clockまで同一再生できることではない。

### 3. cellにはpreferred orderがある

2025年のSeanの回答で、現在setにcellとpreferred orderがあることが確認できた。実演では、roomでの機能に応じて次を行う。

- 一部cellを飛ばす。
- 一部を長く演奏する。
- 音をmuteし、設定を反転する。
- soundcheckで機能した部分をその夜に使う。
- cellごとの役割は固定した「Seanのbeat／Robのmelody」ではなく、局所的に一方がbeatを多く担うなど交替する。

Seanは、solo cellはないとも回答している。したがってcellを、独立曲、preset、scene、片方の完成素材とは確定しない。現段階では次の最小記述だけを採用する。

```text
CELL {
  preferred_neighbors
  variable_duration
  skippable
  mutable_settings
  shared_authorship
  local_role_balance
}
```

これは内部Max patchの復元ではなく、本人回答が許す範囲の演奏文法である。

### 4. `AE_2022－`は完成したsetではなく累積作品である

Seanは2025年、`AE_2022－`を“a sort of accumulative piece”と呼び、興味が続く限り発展させ、終了日を先に決めないと回答した。また、Lisbonでは二公演を二部構成にし、part 2をpart 1の停止地点から始めた例を挙げている。

ここから、`SET_ITERATION`は旧版を捨てて新版へ置き換えるversion番号だけでは不足すると判断する。次の三つを分ける。

- `revision`: 既存cellまたはmappingを修正する。
- `accretion`: 新しいcell、経路、役割関係を累積する。
- `continuation`: 前公演または前partの到達地点から再開する。

この区別も本研究の分析語である。どの公演がどのrevision／accretionを含むかは、今後の公演比較で確定する。

### 5. 保存されたiterationと再現可能性は同じではない

2025年の回答では、Seanはすべてのiterationを保存しており、必要なら古いmachineも残していると述べた。一方Robは、OS更新やmachine能力のため、当時と完全に同じtaskを実行できない場合があると説明した。

これはSound Labの保存モデルにも直接関係する。保存対象を一個のpresetへ縮めず、次を分離する候補が必要になる。

1. logical stateとparameter。
2. rule、cell、依存moduleのversion。
3. software／OS／browser／device dependency。
4. gesture、message、audio-clock event。
5. 再実行できた範囲と、当時環境を失った範囲。

Git commitは研究本文とcodeの保存証拠にはなるが、古いiPhone、Mobile Safari、Web Audio実装、音響出力まで再現できる証拠にはならない。

### 現在の修正結論

Autechreのlive systemを「アルゴリズムが自由に作曲し、二人がparameterを触るもの」とは記述しない。現在の証拠に近いのは、**preferred orderを持つ共同cell群と、破綻しないよう事前設計された可動域を、roomの反応を受けながら二人がskip、linger、mute、flip、role-shiftしていく累積作品**である。

## 16. 公演差の比較開始 — 順序よりも窓と滞在が変わる

### 今回使う資料の権威

公演差の実測へ進む前段として、AEPages上でEnergyIsMassiveLightとZythionが作成している`AE_2022－`のsegment timestamp表を取得した。この表は複数の公式soundboardとbootlegを聴き比べ、2022／2023を#1–35、2024を#21–51として対応づけた共同分析である。

ただし、作成者自身がtimestampはwork in progressで、演奏上の開始・終了がsegment境界へ綺麗に収まらないと明記している。したがって本研究では次の三層を混ぜない。

| 層 | 確認できること | 確認できないこと |
| --- | --- | --- |
| 公式release metadata | 公演名、日付、公開された録音尺 | 内部cell、操作、遷移理由 |
| 2025 AMA本人回答 | preferred order、skip、linger、mute、settings flip | 各録音の具体的な境界番号 |
| AEPages共同分析 | 公演間で対応すると聴取された区間と暫定timestamp | Autechre内部のcell名、patch構造、確定した区切り |

以下の`#1`–`#51`はAEPages分析上の仮番号であり、本人が呼ぶcell番号ではない。

### 1. 2022系 — 同じ入口でも滞在時間と出口が違う

共同分析では、Milan、Athens、Helsinki、London A、Bergen、Turin、Melbourneがいずれも#1から始まり、少なくとも#11まで同じ前向き順序で対応づけられている。一方、終端はMelbourneの#11からBergenの#15まで異なる。

同じsegment候補の開始timestamp差から、最初の二区間だけでも滞在時間は固定されていない。

| 公演 | #1の滞在 | #2の滞在 | 共同分析上の最終segment候補 |
| --- | ---: | ---: | ---: |
| Milan 2022 | 7:06 | 4:56 | #12 |
| Athens 2022 | 7:41 | 6:35 | #14 |
| Helsinki 2022 | 7:42 | 5:08 | #12 |
| London A 2022 | 6:12 | 3:42 | #12 |
| Bergen 2022 | 7:00 | 3:42 | #15 |
| Turin 2022 | 5:59 | 3:43 | #13 |
| Melbourne 2023 | 7:54 | 4:43 | #11 |

この対応が正しいなら、#1の滞在rangeは`1:55`、#2は`2:53`になる。同一順序候補があることと、固定再生であることは両立しない。変化は順序の全面組み換えだけでなく、**同じ領域にどれだけ留まるか**にも現れる。

### 2. 2024系 — 公演は累積列の異なる窓を開く

2024年の共同分析には、さらに明瞭な三組がある。

| 対応群 | 共通する入口 | 共通範囲 | 異なる出口 |
| --- | ---: | --- | --- |
| Brussels / Paris / Krems | #21 | #21–35 | Parisだけ#38まで延長 |
| Rennes / Barcelona / Madrid | #24 | #24–35 | Rennes #35、Barcelona #38、Madrid #39 |
| Lisbon B / Lyon | #36 | #36–48 | Lyonだけ#51まで延長 |

これは、2025 AMAの「preferred order」「一部を長くする／飛ばす」という本人回答と矛盾しない。しかし共同分析だけからskipの具体例を確定することはできない。表に見える空白は、意図的skip、別の入口、録音欠落、分析境界のいずれでもありうる。

現在もっとも弱い仮定で記述できるのは、自由なnode graphよりも次の**可変窓モデル**である。

```text
PERFORMANCE_PATH {
  entry_region
  preferred_forward_order
  variable_dwell
  local_mutation
  optional_skip       // 本人回答で存在確認、各公演の位置は未確定
  exit_or_extension
}
```

`entry_region`と`exit_or_extension`を持つため、公演は同じ長大作品の全体再生ではない。`variable_dwell`と`local_mutation`を持つため、同じ区間を通っても固定loopの再生ではない。`preferred_forward_order`を持つため、毎回任意のsceneへ飛ぶランダムplaylistでもない。

### 3. Sound Labへ移せる候補を絞る

この比較からSound Labへ移す候補は「51個のsceneを作る」ことではない。AEPagesの分節数を製品仕様へ写すのは、共同分析上の聴取ラベルをAutechreの内部実装へ誤帰属し、さらにそれをSound Labへ複製する二重の飛躍になる。

残す候補は、演奏者が次を身体的に決められる構造である。

1. 今いる因果領域へ留まり、内部関係を深く変形する。
2. preferred successorへ進む。
3. 局所領域を飛ばす。
4. その演奏をどこで閉じるか、または先へ延ばす。

ここでも自動transportを主役にしない。Autechreの公演差から得るのはscene数ではなく、**順序骨格を残したまま、滞在・変形・退出を演奏判断にする**という候補である。製品採用とtouch mappingはまだ決定していない。

### 次の音源実測で反証すること

今回の比較はcommunity timestampを計算したもので、音声ファイルの波形・onset・spectral特徴を本研究が直接測った結果ではない。次の実測では少なくとも次を確認する。

- 対応segment内のself-similarityが、公演を跨いで境界外より高いか。
- 同じ仮segmentで、event density、休止、spectral centroid、低域エネルギー、局所periodがどれだけ変わるか。
- timestampの差が単なるmastering前後の無音や録音開始位置ではなく、演奏中のdwell差か。
- 公演ごとの入口・出口候補が、本人回答にあるroom／soundcheck差とどこまで対応するか。
- 順序の逆行、分岐、再訪が本当にないのか、それとも現在の表が前向き列へ整理しているだけか。

## 17. 2025公演による修正 — 累積は一本道ではない

### 取得範囲と限界

AEPages共同分析の2025年表とperformance anomaliesを追加取得した。2025年の録音は、現時点で公式`AE_2022－`bundleへ収録されたsoundboardではなく、主にaudience recordingを基にした共同分析である。したがって以下は本人回答で確認したpreferred order／skip／extendを、非公式録音の対応表で検査する段階に留まる。

### 1. 新しい窓が増えても、古い窓は消えない

2025年8月の欧州公演は、共同分析上おおむね#36付近から#51付近までを使っている。10月の北米公演では、#49付近から始まり、新しく対応づけられた#52–63へ進む公演が多く現れる。

これだけなら「時間とともに入口が後方へ移動し、古い部分を捨てた」と読める。しかし同日二公演を分けると、その読みは崩れる。

| 同日二公演 | 前方の窓 | 後方の窓 |
| --- | --- | --- |
| Seattle 2025 | A: おおむね#49–63 | B: #36–51 |
| Los Angeles 2025 | A: おおむね#49–63 | B: #36–48 |
| New York 2025 | A: #49–62 | B: おおむね#36–48 |

新しいsegment候補が追加された後も、以前の窓は別公演で再選択されている。したがって`accretion`を、古いsetの末尾へ新素材を足し、常にその先端だけを演奏することとは定義しない。

現在の候補は、**累積した長い作品に複数のplayable windowが共存する**という構造である。

```text
ACCUMULATIVE_REPERTOIRE {
  retained_regions
  newly_added_regions
  selectable_windows
  window_specific_entry
  window_specific_exit
}
```

ここで`retained_regions`は、音が毎回同一であることを意味しない。同じ領域へ戻っても、dwell、mapping、mute、settings、二人の役割、roomによってtrajectoryは変わりうる。

### 2. preferred orderには例外と回復がある

AEPagesのanomaly注記には、前向きの連続列だけでは記述できない候補がある。

- Barcelona 2022: #7を続けて二度演奏したと分析されている。
- Rennes 2024: #29内の固有interlude後、同区間を再開したと分析されている。
- Manchester 2025: #37冒頭で停止・再開し、#46の途中で短く#40へ戻ってから通常順序へ復帰したと分析されている。
- Amsterdam 2025: #39途中で停止し、その後再開したと分析されている。

これらはAutechre本人によるcell同定ではなく、共同分析上のanomalyである。とくにManchesterのUSB切断原因はAEPagesが引用する報告に依存し、今回その原発言本文は取得できていない。ただし、録音上の停止と再開、および分析者が過去区間との一致を聴取したという主張は、単純な一方向モデルへの反証候補になる。

section 16の`preferred_forward_order`は、通常経路の記述として残すが、経路全体を尽くすものではない。次を加える。

```text
ELASTIC_SPINE {
  preferred_forward_order
  hold_or_extend
  skip_forward
  repeat_current_region
  temporary_return
  resume_after_halt
  select_another_window_next_show
}
```

`temporary_return`は自由なランダムjumpとは異なる。Manchesterの共同分析が正しければ、過去領域へ短く触れた後に元の順序へ戻っており、逸脱と復帰点が対になっている。

### 3. 「失敗しない設計」を無停止と読まない

2022 AMAから得た`designed_failure_bounds`は、機材も演奏も停止しないという意味ではなかった。2025年の中断候補は、少なくとも次の二種類を分ける必要を示す。

| 種類 | 内容 | 研究上の扱い |
| --- | --- | --- |
| musical instability | parameter操作やchaosが予想外の音楽結果を返す | 可動域内で制御・選択する |
| infrastructure failure | interface、connection、audio pathなど演奏基盤が途切れる | 音楽生成とは別の回復経路を持つ |

`designed_failure_bounds`は前者の音楽的破綻を抑える設計語であり、後者の機材障害まで防いだ証拠にはならない。Sound Labでも、因果エンジンの音楽的安定性と、iPhone／browser／audio session中断からの復帰を同じテストへ潰さない。

### 4. Sound Labへの候補

今回追加するのはscene選択UIではなく、**復帰可能な演奏状態**という研究候補である。

```text
RESUMABLE_PERFORMANCE_STATE {
  active_window
  current_region
  local_state
  preferred_successor
  return_target?
  recovery_anchor?
}
```

ただし`recovery_anchor`を一定間隔の自動checkpointと決めてはいない。自動保存がgesture、audio clock、外部入力との不整合を作る可能性があるため、何を保存すれば音楽的に「続き」になるかは未検証である。

ここまでの修正で、Autechreから移す候補は次のように絞られる。

> 固定loopを再生するのではなく、複数の可動窓を保持し、その中で滞在・前進・省略・一時回帰・中断復帰を演奏する。

これはまだSound Labの採用仕様ではない。特に「一時回帰」と「中断復帰」は操作主体、誤操作防止、復帰時の音量安全性を含めて別途設計する必要がある。

## 18. 未検証事項

- 各作品の音源を取得した波形・イベント列の分析。
- `AE_LIVE`複数公演のcommunity segmentation比較は2025年まで進めたが、音声ファイルによるtoolset、境界、公演差、anomalyの直接測定。
- 2022 Twitch AMAと2025 KEYOSC AMAの全回答を、年代、記憶留保、後続訂正まで含めて監査すること。今回取得した該当回答は上記範囲に限定する。
- Max systemの実際のstate、clock、coupling、controller mapping。
- 3本以上の同時接触を含むMobile Safari / iPhoneのtouch取得安定性。
- 因果エンジンが演奏者へ理解可能な応答を返すか。
- deterministic replayに必要なstate snapshot、seed、gesture frame、audio clockの範囲。
- 独立DRUMと4トラック間の同期を、固定BPM以外でどう成立させるか。
- 低遅延、CPU、電池、発熱、音量安全性。

## 19. 触る実装パス

今回の研究では製品コードを変更しない。

- 追加: `research/20260831-autechre/README.md`
- 未変更: `field-processor/`
- 未変更: `prototype/`
- 未変更: `integration/`

## 20. 依存する研究・判断

- `RESEARCH_WORKFLOW.md`
- `integration/DIRECTION.md`
- `integration/DECISIONS.md` の `D-001`, `D-002`, `D-004`, `D-006`, `D-007`, `D-008`, `D-009`
- `research/20260828-image-contact-bridge/` — 接触入力を同一frame列で扱う既存研究。Autechre由来のDSP mappingを定義するものではない。
- `research/20260902-charlie-hunter/` — 同一身体へ拘束された声部間関係。研究branch本文を取得。
- `research/20260902-j-dilla/` — 複数clock candidate、声部間摩擦、反復変形。研究branch本文を取得。
- `research/20260902-jeff-mills/` — 持続層、手動破断、事故からの回復。長期研究branch本文を取得。
- Skulptur研究本文 — Git上では未取得のため、この研究から内容を補完しない。

## 21. 失効した判断

- section 16の可変窓モデルを、入口から出口まで一方向にしか進まない完全モデルとして使う候補は失効。2025年までの共同分析には、同一区間の反復、停止後の再開、過去領域への一時回帰、別公演での古い窓の再選択がある。通常経路としての`preferred_forward_order`は維持し、section 17の`ELASTIC_SPINE`を後継候補とする。

今後訂正が生じた場合、古い判断を黙って削除せず、失効理由と後継判断をここへ追記する。

## 資料

### 本人インタビュー

1. [Nialler9 — Exploring the parameter space: An interview with Autechre (2023)](https://nialler9.com/autechre-conversation-music-art-funk-and-emotion-interview/)
   - electroからの連続性、dance musicの曖昧さ、反復史、open-ended algorithm、ライブシステム、会場差、深いmixについてSean BoothとRob Brownが回答。
2. [Pitchfork — Autechre on Their Epic NTS Sessions, David Lynch, and Where Code Meets Music (2018)](https://pitchfork.com/thepitch/autechre-interview-nts-sessions-david-lynch-where-code-meets-music/)
   - “the system”、patch交換、sequencerと作品の境界、NTS制作について両名が回答。
3. [Peter Hollo — Sean Booth interview (2005、保存mirror)](https://autechre.neocities.org/en/interviews/interview30)
   - `VI Scose Poise`、`Uviol`、`Draft 7.30`の方法差、non-timeline sequencer、物理interfaceについてSeanが回答。
4. [Sean Booth Speaks (2010、aepages保存transcript)](https://aepages.org/wiki/Sean_Booth_Speaks,_April_2010)
   - setupが方法を規定すること、Quaristiceのlive session、ツアーを独立projectとして扱うこと、hip-hopとの連続性。
5. [Radio Študent — Autechre interview (2016、aepages保存transcript)](https://aepages.org/wiki/R%C5%A0_INTERVJU_Autechre%2C_Radio_Student_FM89.3%2C_November_2016)
   - 2014/15 setの終了、新setの速度と焦点、旧`AE_LIVE`と`elseq`のsetup共有、Kino Šiškaを新set設計で参照したことについて両名が回答。
6. [Sean Twitch AMA, July 2022（aepages全文transcript）](https://aepages.org/wiki/Sean_Twitch_AMA,_July_2022)
   - live setの設計量とbounded flexibility、deterministic chaos、specific seed、controller、live set cellについてSeanが回答。
7. [Ask Autechre Anything Again, KEYOSC, April 2025（transcript spreadsheet）](https://docs.google.com/spreadsheets/d/1XAizLmKun4yF6oBVUhIrewYN-ZiY_9ORckmT-hF93Ho/edit?gid=447739750)
   - iteration保存、`AE_2022－`の累積性、preferred cell order、skip／linger／mute／settings flip、役割交替、roomとsoundcheckについて両名が回答。

### 公式公開面

8. [Warp — Autechre artist page](https://warp.net/artists/autechre)
9. [Autechre official Bandcamp](https://autechre.bandcamp.com/)
10. [AE_STORE — AE_LIVE 2016/2018](https://autechre.warp.net/release/310992-autechre-aelive-20162018)
   - 7公演の公式tracklist、収録日、尺を確認。
11. [Autechre official Bandcamp — AE_2022－](https://autechre.bandcamp.com/album/ae-2022)
   - 2022–2024年の19公演を含む公式bundleとtracklistを確認。

### 補助資料

12. [VICE — How the Political Warning of Autechre's Anti EP Made it a Warp Records Classic](https://www.vice.com/en/article/warp-25-autechre-anti-ep/)
   - `Anti EP`盤面警告文と`Flutter`の非同一bar設計を確認する補助資料。本人への新規インタビューではないため、盤面一次資料と同格には扱わない。
13. [Los Angeles Times — Autechre's music is the remix of a song that never existed (2015)](https://www.latimes.com/entertainment/music/la-et-ms-autechre-20151119-story.html)
   - `AE_LIVE`で毎回異なるnote sequencing、各trackの可能範囲を決めるconditionals、二人のdata共有と即時反応についてSean Boothが説明。
14. [AEPages — AE_2022－ Analysis](https://aepages.org/wiki/AE_2022%EF%BC%8D#Analysis)
   - 公式soundboardとbootlegを跨いだsegment対応、timestamp、2025年までのperformance anomalyの共同分析。work in progressであり、内部cell名や確定境界とは扱わない。
