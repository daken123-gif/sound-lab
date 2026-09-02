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

## 12. 未検証事項

- 各作品の音源を取得した波形・イベント列の分析。
- `AE_LIVE`複数公演で共通するtoolsetと公演差の比較。
- Autechre本人の2022 Twitch AMAおよび2025 KEYOSC AMAの該当回答の原文取得。
- Max systemの実際のstate、clock、coupling、controller mapping。
- 3本以上の同時接触を含むMobile Safari / iPhoneのtouch取得安定性。
- 因果エンジンが演奏者へ理解可能な応答を返すか。
- deterministic replayに必要なstate snapshot、seed、gesture frame、audio clockの範囲。
- 独立DRUMと4トラック間の同期を、固定BPM以外でどう成立させるか。
- 低遅延、CPU、電池、発熱、音量安全性。

## 13. 触る実装パス

今回の研究では製品コードを変更しない。

- 追加: `research/20260831-autechre/README.md`
- 未変更: `field-processor/`
- 未変更: `prototype/`
- 未変更: `integration/`

## 14. 依存する研究・判断

- `RESEARCH_WORKFLOW.md`
- `integration/DIRECTION.md`
- `integration/DECISIONS.md` の `D-001`, `D-002`, `D-004`, `D-006`, `D-007`, `D-008`, `D-009`
- `research/20260828-image-contact-bridge/` — 接触入力を同一frame列で扱う既存研究。Autechre由来のDSP mappingを定義するものではない。
- Skulptur研究本文 — Git上では未取得のため、この研究から内容を補完しない。

## 15. 失効した判断

- なし。

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

### 公式公開面

5. [Warp — Autechre artist page](https://warp.net/artists/autechre)
6. [Autechre official Bandcamp](https://autechre.bandcamp.com/)

### 補助資料

7. [VICE — How the Political Warning of Autechre's Anti EP Made it a Warp Records Classic](https://www.vice.com/en/article/warp-25-autechre-anti-ep/)
   - `Anti EP`盤面警告文と`Flutter`の非同一bar設計を確認する補助資料。本人への新規インタビューではないため、盤面一次資料と同格には扱わない。
