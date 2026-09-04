# Dub演奏文法研究

- 状態: `active`
- research-id: `20260831-dub-performance-grammar`
- 更新日時: 2026-09-03
- 研究対象: Jamaican dubの成立、コンソール演奏、反復の再構成、4トラック・マルチタッチ楽器への変換
- 現在の問い: 固定ループを垂れ流さず、録音済み4トラックを毎瞬再作曲するために、Dubから何を操作文法として抽出できるか

## 0. 結論

Dubから採るべきものは、スプリングリヴァーブやテープエコーの音色ではない。

採るべき核は、録音済み素材について次の四つをリアルタイムに分離して演奏する構造である。

1. 原音が現在存在するか
2. どの瞬間だけ時間系へ投げるか
3. 投げた過去がいつまで帰還するか
4. 何を消した空白へ、どの断片を戻すか

同じリズムを反復していても、聴覚上の編成、距離、因果、前景が固定されなければ、ループは完成品ではなく演奏材料として残る。

この研究ではDub層をSkulptur型主演奏面の代替にしない。4本の元音声を保持し、そこから明示的に接続する一基の共有Dub send/returnを候補とする。共有returnは第五トラック、第五ルーパー、常時master effectにしない。

## 1. 権威と証拠境界

### 1.1 一次証言として扱う資料

- Scientist, Tape Op interview
  - https://tapeop.com/interviews/136/hopeton-overton-brown-scientist
  - engineerがcomposer / artistになること、surprise、patternの保持と切替、4-track環境、high-pass filter、controlled bleedについての本人証言。
- Mad Professor, Tape Op interview
  - https://tapeop.com/interviews/144/mad-professor
  - Dubをtechnical musicとして捉えること、素材をstrip downしてput togetherする方法、Massive Attackへの適用についての本人証言。
- Adrian Sherwood interview, Red Bull Music Academy Daily
  - https://daily.redbullmusicacademy.com/2019/01/adrian-sherwood-interview/
  - reggae以外のfolk、jazz、industrial、funkにも、unclutteredな同一のmixing approachを適用した本人証言。
- Moritz von Oswald lecture, Red Bull Music Academy
  - https://www.redbullmusicacademy.com/lectures/moritz-von-oswald-early-morning-freestyles/
  - Basic Channel / Rhythm & Soundと、Wackiesを含むDub接続についての本人講演。

### 1.2 歴史整理として参照する資料

- The Roots of Dub, Red Bull Music Academy Daily
  - https://daily.redbullmusicacademy.com/2018/08/the-roots-of-dub/
  - 7-inchのversion、12-inch discomix、soundsystemとdubplateの流通構造。
- Lee “Scratch” Perry, Tape Op
  - https://tapeop.com/interviews/136/lee-scratch-perry
  - 本人発話に加え、Black Ark、`Super Ape`、console / pan / mute / volume rideを演奏として扱う編集部記述を含む。編集部記述と本人証言を分ける。

### 1.3 未取得・未検証

- 当時のKing Tubby本人による体系的な技法説明は未取得。
- Ruddy Redwoodとversion起源をめぐる複数の発明譚は、当事者間の証言差を比較していないため確定しない。
- 各盤のオリジナル盤面、matrix、正確なmix creditは本研究で照合していない。
- 実機コンソール、spring reverb、tape echoの測定値は取得していない。
- iPhone / Mobile Safariでのfeedback delay、tail、同時タッチ数、AudioContext schedulingは未検証。

## 2. 観測できた事実

### 2.1 Dubはエフェクトの集合ではなく再作曲である

ScientistはDubを、engineerがcomposerとartistになる電子音楽として説明している。また、ひとつのpatternへ聴き手を引き込んだ後、そのpatternを切り替えるsurpriseを中核に置く。

この証言から確認できるのは、Dubの主体が「録音を正しく再現するengineer」から「録音済み関係を組み替えるperformer」へ移ることである。

### 2.2 versionは完成曲を開いた材料へ戻した

1970年代半ばには、歌入りA面に対するversionが7-inchの裏面へ広く置かれ、sound systemで歌入りからversionを続けて演奏できた。12-inch discomixでは歌入りからDubへの移行自体が一続きの時間構造になった。

したがってversionは単なるinstrumental mixではない。selector、DJ / toaster、sound system、観客が既存曲へ再介入するためのsurfaceだった。

### 2.3 限られたトラック数が決定を演奏へ戻した

ScientistはKing Tubby周辺の4-track環境と、短時間で録音からmixまで進めた制作条件を説明している。多数のstemを後から無限に修正するのではなく、少数のまとまった要素を一回のpassで出し入れするため、mix decisionが演奏時間へ露出する。

### 2.4 聞こえる回路名と実際の回路は一致しない

Scientistによれば、phase shifterと受け取られた効果の一部はhigh-pass filterだった。よって「Dubらしい音」を現代のpreset名から逆算すると、歴史上の操作を誤同定する。

### 2.5 分離の不完全さは欠陥とは限らない

Scientistはmic bleedを排除し切るとdrumがstiffになり、周波数ごとにcontrolled bleedを構成して大きなdrum imageを作ったと説明している。RAW素材を完全分離した後にだけDub処理を足す設計では、この相互汚染の身体性を失う可能性がある。

### 2.6 Dubの方法はレゲエ以外へ移植できる

Adrian Sherwoodはfolk、jazz、industrial、funkにも、素材を詰め込まず同じmixing approachを適用したと述べる。Mad ProfessorもMassive Attackを通常のDubと同様にstrip downして再構成したと説明する。

したがってDubを採ることは、製品をreggae accompaniment machineへすることではない。

## 3. 人物ごとの差

ここは単一の「Dubらしさ」へ均さない。

| 系列 | 中心操作 | 空間の性格 | この楽器へ与える示唆 |
| --- | --- | --- | --- |
| King Tubby | 減算、出現、消失、filter、短い断片 | 空白を彫る | muteとreturnを別操作にする |
| Lee Perry / Black Ark | overdub、飽和、漏れ、堆積、異物 | 録音物を発酵させる | 非破壊RAWと変質層を分離する |
| Scientist | 高速なfocus移動、surprise、high-pass、劇的return | sceneが次々切り替わる | 一操作一effectでなく、事件単位のgestureを設計する |
| Errol Thompson / Mighty Two | rhythm sectionを保つ空間移動 | dance floorの推進を維持 | BODYを壊さず上物だけ投げる経路を許す |
| Prince Jammy | 整理された空間、digital rhythmへの移行 | 簡潔で強い | 音源方式とDub文法を分離する |
| Adrian Sherwood | collage、industrial、異種素材への移植 | 混成的 | genre presetではなくrouting grammarとして持つ |
| Mad Professor | 歌の中心を残す分解と再構築 | 情緒を保持 | 抽象化してもsource identityを消し切らない |
| Basic Channel / Rhythm & Sound | 個々の投擲を持続状態へ変換 | delayとnoiseが地形になる | event型Dubとstate型Dubを分ける |

人物差のうちKing Tubby、Perry、Errol Thompson、Prince Jammyに関する詳細は、本人一次証言と盤面creditの追加取得が必要であり、この表を歴史的最終判定にしない。

## 4. 固定ループとDubの差

| 固定ループ | Dub演奏 |
| --- | --- |
| 反復単位の内部関係が固定される | 同じ素材でも編成と遠近が毎回変わる |
| layer追加が主な発展になる | 出す、消す、投げる、帰還を切るが同格 |
| 過去の録音が現在を拘束する | 現在の操作が録音された過去の意味を変える |
| effectは素材に付属する | effect returnが次の出来事を起こす |
| 密度が不可逆に増えやすい | 空白へ戻る経路を常時持つ |
| playback中の演奏責任が小さい | mix decisionを演奏者が引き受け続ける |

Dubは反復を拒否しない。反復物へ演奏の決定権を渡さない。

## 5. 抽出する演奏文法

### 5.1 CUT

原音を止める。tailまで同時に止める操作とは分離する。

音楽的意味:

- 空白を作る
- 次のreturnへ注意を集中させる
- rhythm sectionだけを露出する

### 5.2 THROW

連続send量を設定するのではなく、選択した瞬間の短い音片を共有時間系へ投げる。

音楽的意味:

- 過去の一音を未来へ送る
- 現在のsourceを消した後も、その残像だけを残す
- 同じphraseの全体ではなく、語尾、snare、horn stabだけを事件化する

### 5.3 REVEAL

消えていたsourceを一時的に前景へ戻す。

音楽的意味:

- loop playbackでは予測可能だった素材を、出現時刻によって再び意外にする
- 原曲のidentityを短時間だけ回復する

### 5.4 VACUUM

BODY以外、または明示選択した複数sourceのdryを一度に落とす。ただしtailは残せる。

音楽的意味:

- arrangementを骨格へ戻す
- 蓄積をリセットする
- 次の小さな音を大きな事件にする

### 5.5 TAIL CHOKE

共有returnを切る。source muteとは別である。

音楽的意味:

- feedbackの自律運動を人間が終わらせる
- silenceを偶然でなく演奏決定にする
- runaway feedback時の音量安全操作を兼ねる

### 5.6 FILTER VANISH

音量を下げるのでなく、帯域を狭めて身体を失わせる。

音楽的意味:

- sourceを存在／不在の二値にせず、身体から幽霊へ連続変化させる
- high-pass sweepをphase presetの代用品にしない

### 5.7 ANCHOR

4本のRAW playback、dry level、共有returnを、破壊的undoではなく演奏上の基準状態へ戻す。

音楽的意味:

- Dub passを終えて原曲関係へ戻る
- もう一度別のDub passを開始できる

## 6. 候補信号構造

```text
Track 1 RAW -> Track playback -> Skulptur candidate -> dry bus ----+
Track 2 RAW -> Track playback -> Skulptur candidate -> dry bus ----+--> output
Track 3 RAW -> Track playback -> Skulptur candidate -> dry bus ----+
Track 4 RAW -> Track playback -> Skulptur candidate -> dry bus ----+
                               |                                 ^
                               +-> explicit Dub send -> shared tail --+
```

### 固定する境界

- RAWは書き換えない。
- 4トラックを4本とも元音声として保持する。
- shared tailはトラック数へ数えない。
- shared tailを録音ループとして自動保存しない。
- tailをsourceへ戻すresampleは、行うなら別の明示録音操作にする。
- Dub sendを常時master insertにしない。
- Skulptur型主演奏面をDub UIで置き換えない。

### まだ固定しないもの

- Skulpturの前からsendするか、後からsendするか
- delay head数
- delay timeをfree、tempo-relative、両対応のどれにするか
- spring / tape / digitalの音響model
- saturation位置
- per-track sendの同時数
- tailの最大長
- feedback limiterの方式

## 7. 状態モデル候補

各トラック `i` は最低限、次を独立状態として持つ。

```text
TrackDubState[i] = {
  dryPresence,
  filterState,
  throwGate,
  throwAmount,
  foreground
}

SharedTailState = {
  returnPresence,
  feedback,
  delayTime,
  tone,
  safetyGain
}
```

ここで `throwGate` は通常のsend knobと異なる。指が通過した瞬間のaudio sliceだけをsendへ渡し、離した後のsource全体を流し続けない候補である。

一つの連続パラメータへすべてを畳み込まない。特に次は別状態にする。

- source dry mute
- send input gate
- return mute
- feedback clear

これらを一個のXY位置へ隠すと、演奏者が「原音だけ消した」「過去だけ残した」「過去も切った」を選べなくなる。

## 8. マルチタッチへの変換候補

### 8.1 同時押しを前提にしない

既存方向では、隠れたmode、深い階層、同時押しを中心に置かない。したがって二本指、三本指のchord gestureだけにDub操作を割り当てない。

複数接触は同時に複数sourceを演奏するために使い、機能呼出しの暗号には使わない。

### 8.2 接触の役割候補

| 接触 | 候補イベント | 判定境界 |
| --- | --- | --- |
| source面へ触れる | REVEAL / foreground | Skulptur接触との競合を検証する |
| source面からDub send境界へ払う | THROW | 誤投擲と到達距離を実機確認する |
| source面から外へ離脱 | CUT候補 | Pointer離脱をrelease捏造に使わない |
| tail面を短く触る | return reveal | hidden modeにしない |
| tail面を明示的に切る | TAIL CHOKE | 音量安全操作として常時到達可能にする |
| anchorへ触る | ANCHOR | undo / data restoreと混同しない |

これらは候補であり、UI採用ではない。

### 8.3 多点接触の目的

多点接触数を機能数として競わない。狙うのは次の独立性である。

- 一本の指でBODYを保持する
- 別の指でVOICEを瞬間的にREVEALする
- 第三の指でCUTまたはFILTER VANISHする
- 投げたtailは手を離した後も鳴る
- 必要な瞬間に別接触でTAIL CHOKEする

これはCharlie Hunterの独立声部、Jeff Millsの複数装置の機能分担、Dubのconsole improvisationを同一画面で接続する仮説である。三者の実演比較は別研究で行う。

## 9. 時間設計

### 9.1 小節ではなく事件時刻を記録する

THROW、CUT、REVEAL、TAIL CHOKEは、loop positionだけでなくaudio clock上のeventとして記録する候補とする。

```text
DubEvent = {
  audioTime,
  loopPhase,
  trackId,
  action,
  value,
  contactId
}
```

`loopPhase`だけでは、異なる周回で同じgestureを反復したように見える。`audioTime`を保持することで、何周目のどの瞬間に過去を投げたかをPerformance Takeとして再生できる。

### 9.2 quantizeを自動前提にしない

Dubの意外性はbar boundaryだけで起きない。voiceの語尾、snare直後、off-beat guitarの一打を投げるため、非quantizeを基準候補にする。

quantizeを設ける場合も演奏者が明示選択し、録音開始やinput detectionから自動適用しない。

### 9.3 tailは別時間層である

現在のsource playbackと、過去にTHROWされたtailは異なる時計上の因果を持つ。UIはsourceの現在位置だけでなく、tailがまだ自律運動中であることを示す必要がある。

ただし詳細なecho波形を常時描いて画面をDAW化しない。必要なのは「まだ帰還が生きている」「chokeできる」という因果の可視性である。

## 10. 採用候補

- `candidate`: dry mute、send input、return mute、feedback clearを分離する。
- `candidate`: 4トラックから一基の共有時間メモリへ明示THROWする。
- `candidate`: THROWを連続send knobではなく短いeventとして扱う。
- `candidate`: TAIL CHOKEを常時到達可能な安全操作にする。
- `candidate`: Dub操作をContact Performance Takeの同じaudio-clock event列へ記録する。
- `candidate`: source playbackとtail activityの因果だけを簡潔に可視化する。
- `candidate`: 非quantizeを基準とし、quantizeは明示選択にする。

## 11. 採用しない点

- `rejected`: Dubをspring reverb presetの名称として採用する。
- `rejected`: 4本目をGHOST専用トラックにする。
  - 理由: `D-001` と `integration/DIRECTION.md` は4本の元音声を中心に固定している。
- `rejected`: shared tailを第五ルーパーとして扱う。
- `rejected`: 全トラックへ常時同量のdelay / reverbをかける。
- `rejected`: KAOSS型master XYをDubの名で復活させる。
- `rejected`: 操作しないと自動変調が音楽を作る仕組みを、反復回避の中心にする。
- `rejected`: 同時押しの本数をhidden commandとして使う。
- `rejected`: historical hardwareの回路名だけを借り、実測なしにKing Tubby / Black Ark再現を名乗る。

## 12. 失効した判断

### S-001 4本目をGHOST trackにする

- 状態: `superseded`
- 由来: 2026-08-31の会話内初期研究案
- 旧判断: 4トラックをBODY / CUT / VOICE / GHOSTへ固定する。
- 失効理由: Git正本の現行方向では、4本の元音声を保持し、時間メモリは明示sendによる後段候補として分離している。
- 現在候補: 4本すべてをsource trackとして保持し、一基の共有Dub send/returnを接続する。

## 13. Field Looperへ採る点／採らない点

### 採る点

- 録音済み素材を完成品ではなく、存在、不在、距離、帰還を演奏する材料として扱う。
- 追加録音だけでなく減算を主要演奏にする。
- 原音を消した後もtailだけを残せる。
- tailを演奏者が明示的に終わらせられる。
- 少数のsourceと共有処理により、routingを身体で把握できるようにする。

### 採らない点

- reggae固有のone-drop、skank、bass音色を製品の既定styleにすること。
- vintage機材の外観模倣。
- 盤のdub mixを自動生成すること。
- AIが変化量やdrop時刻を決めること。
- 画面上のtrackを増殖させてDubを表現すること。

## 14. 触る実装パス

この保存では実装を変更しない。

将来の候補パスは、最新の統合監査とPR競合確認後に決める。現時点で既存製品コードの具体pathを推定して固定しない。

## 15. 依存する研究・判断

- `integration/DIRECTION.md`
- `integration/DECISIONS.md`
- `D-001`: 4トラックを製品の中心にする
- `D-002`: ドラムをルーパーから分離する
- `D-004`: 自動録音を既定にしない
- `D-007`: Skulptur型を録音後の主演奏面にする
- `D-008`: KAOSS中心階層を退役させる
- `D-009`: 一画面原則を強制横画面から分離する
- `D-010`: Git未収載の研究を統合済みにしない
- Contact Performance Take / Audio-clock候補
- Dedalus型共有時間メモリ候補
- BattleFX型rhythmic-tail候補

## 16. 未検証事項

1. Skulptur接触とTHROW gestureが同じsurfaceで衝突しないか。
2. source dry、send input、return、feedback clearの四状態を一画面で理解できるか。
3. iPhoneで何点の同時接触を安定して取得・audio scheduleできるか。
4. Touch / Pointerから同一gesture event列を生成できるか。
5. non-quantized THROWをAudioContext時計へ十分な精度でscheduleできるか。
6. shared tailが四つのsource identityを混濁させすぎないか。
7. feedback runawayを防ぎながら、自己発振直前の演奏域を残せるか。
8. tail activityの表示を増やしてもDAW的監視画面にならないか。
9. spring、tape、digital delayのどれが必要か。複数modelを搭載する必要が本当にあるか。
10. Charlie Hunter、Jeff Mills、Scientistの実演を同一時間軸で比較したとき、独立声部、機能分担、console gestureの共通単位が成立するか。

## 17. 次工程

次は製品実装ではなく、代表的Dub mixの時間分析を行う。

- vocal originalとdub versionを対にする。
- 8小節ごとではなく、CUT / THROW / REVEAL / VACUUM / TAIL CHOKEの事件時刻を記録する。
- source数、同時発音数、tail継続、空白長を観測する。
- King Tubby、Lee Perry、Scientistで同じ事件語彙が通用するか、差異を潰さず比較する。
- その結果から、gesture数を増やさずに必要なprimitiveを絞る。

この時間分析とiPhone実機検証が終わるまで、Dub層のUI、DSP、製品採用は確定しない。

## 18. 2026-09-02訂正: Shazamプレビューによる実信号取得

### 18.1 経路訂正

直前の更新でSpotify検索をコーパス取得経路として採用したのは誤りだった。依頼されていた手順は、Shazam検索が返すApple Music catalogのpreviewを取得し、その実音を研究対象にする流れである。

Spotify由来のURI、再生可能表示、尺は本研究の証拠から撤回する。以下はShazamの検索結果と曲取得結果から再確定した。Apple Musicの曲ページはcatalog項目の参照先であり、preview本体はShazamが返した`previews[].url`から取得した。

### 18.2 取得したプレビュー

| pair | 役割 | 曲・版 | Apple Music ID | ISRC | catalog尺 | 取得preview |
| --- | --- | --- | --- | --- | ---: | ---: |
| A | vocal original | Jacob Miller — [Baby I Love You So](https://music.apple.com/us/album/baby-i-love-you-so/1060638661?i=1060639199) | `1060639199` | `GBBZV9201384` | 150.840秒 | 29.977秒 |
| A | Dub | Augustus Pablo — [King Tubby Meets Rockers Uptown](https://music.apple.com/us/album/king-tubby-meets-rockers-uptown/1060638661?i=1060639201) | `1060639201` | `GBBZV9201260` | 148.373秒 | 29.977秒 |
| B | vocal original | Michael Prophet — [You Are a No Good](https://music.apple.com/us/album/you-are-a-no-good/1101800620?i=1101802290) | `1101802290` | `GBBZV8004722` | 199.427秒 | 30.004秒 |
| B | Dub | Roots Radics — [Dance of the Vampires](https://music.apple.com/us/album/dance-of-the-vampires/1101800620?i=1101802077) | `1101802077` | `GBBZV1555866` | 205.787秒 | 30.004秒 |

pair Aは両曲とも`Who Say Jah No Dread: The Classic Augustus Pablo Sessions`、pair Bは両曲とも`Junjo Presents: The Evil Curse of the Vampires`に収録されたcatalog版である。

取得ファイルのSHA-256:

- `Baby I Love You So`: `34252808861763eb2e317491c4c2f7ac075d2072cffc61fbddfd1d58fb61077a`
- `King Tubby Meets Rockers Uptown`: `e2f9af4ca52f0c75bd4539d507dd9f76ecdce919e07391e127f3e30476cd238d`
- `You Are a No Good`: `2af34400c4239368afdc5c4ba0b6417bd1f2b9408107932c44c163a11159c849`
- `Dance of the Vampires`: `cb2aa36e8d8f102d5db94bc548a7e7652164fe5128229939dff1256b5f8911e1`

preview音源そのものはGitへ保存しない。解析手順は[`analyze_dub_previews.py`](./analyze_dub_previews.py)、測定結果は[`preview-analysis.json`](./preview-analysis.json)に保存する。

### 18.3 解析経路の再訂正

2026-09-03に、Dub専用の`analyze_dub_previews.py`を新設して先に数値化した経路を失効させた。理由は、`main/research/music-analysis`に校正済みの共通解析器が既に存在しており、個別研究ごとに異なる特徴定義を追加すると比較可能性が壊れるためである。

現在の解析権威:

- `main:research/music-analysis/calibrate_analyzer.py`
  - blob: `314db6380f63c12017b52dcd3dd2dfcaff94a539`
- `main:research/music-analysis/analyze_previews.py`
  - blob: `4e36a19c5760cc1f3a7cf4b80ad3e9ad6e3baa47`

GitHubから取得した上記ソースをそのままメモリ上で実行した。合成校正は12件中12件成功した。現行の測定結果は[`preview-analysis-standard.json`](./preview-analysis-standard.json)に保存する。

旧[`analyze_dub_previews.py`](./analyze_dub_previews.py)は実行停止するtombstoneへ変更した。旧[`preview-analysis.json`](./preview-analysis.json)は履歴を消さず`superseded`へ変更した。

### 18.4 共通解析器による測定

| 曲 | RMS dBFS | frame RMS p10 / p50 / p90 | centroid | onset/s | onset interval median | onset interval CV |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| Baby I Love You So | -11.91 | -17.91 / -12.77 / -8.93 | 2590.5 Hz | 8.320 | 0.1103秒 | 0.364 |
| King Tubby Meets Rockers Uptown | -12.75 | -24.11 / -14.15 / -9.05 | 2605.4 Hz | 7.685 | 0.1161秒 | 0.474 |
| You Are a No Good | -11.74 | -19.14 / -12.01 / -9.01 | 3560.1 Hz | 8.207 | 0.1103秒 | 0.375 |
| Dance of the Vampires | -13.93 | -30.33 / -14.12 / -10.52 | 3094.1 Hz | 7.439 | 0.1103秒 | 0.438 |

周期候補:

| pair | vocal original | Dub | 観測 |
| --- | --- | --- | --- |
| A | 134.23 / 66.26 / 88.34 | 134.23 / 88.34 / 65.83 / 53.28 | 134.23が一致し、二次候補も同じ周期族にある |
| B | 137.81 / 68.91 / 91.47 / 54.69 | 68.00 / 137.81 / 91.47 / 54.40 | 137.81とhalf/double候補を共有するが順位が異なる |

これらは周期候補であり、検証済みのbeatまたはBPMではない。

### 18.5 再現した差

二つのpairで同方向に再現したのは次である。

- Dub版のonset密度が低い。
  - pair A: 8.320/s → 7.685/s
  - pair B: 8.207/s → 7.439/s
- Dub版のframe RMS p10が大きく下がる。
  - pair A: -17.91 dBFS → -24.11 dBFS
  - pair B: -19.14 dBFS → -30.33 dBFS
- Dub版のframe RMS p50も下がる。
  - pair A: -12.77 dBFS → -14.15 dBFS
  - pair B: -12.01 dBFS → -14.12 dBFS
- 周期候補の族は原曲とDub版で保たれる。

30秒preview内では、Dub版は周期的な骨格候補を保ちながら、発音候補の密度を下げ、静かな側の振幅領域を深くしている。この関係は「基礎リズムを保持したまま、編成と空白を再構成する」という仮説を補強する。

ただしonset detectorは声、打楽器、ギター、echo returnを区別しない。onset減少をそのままsource mute数、`CUT`数、演奏者の意図へ変換しない。

### 18.6 反証と撤回

旧Dub専用解析では「両pairのDub版でmedian spectral centroidが低下した」と記録した。しかし共通解析器では次になった。

- pair A: 2590.5 Hz → 2605.4 Hz（Dub版が14.9 Hz高い）
- pair B: 3560.1 Hz → 3094.1 Hz（Dub版が466.0 Hz低い）

したがって「Dub版では一貫してスペクトル重心が低下する」という主張は撤回する。旧方式はエネルギー帯域比とframe中央値に基づき、共通方式は全区間FFT magnitudeの重心を使う。定義が異なる値を同じ指標名で比較したことが誤りである。

現時点で直接証拠にできるのは取得previewの信号測定までである。この実行環境では音声を聴覚入力として受け取れないため、「聴いた」とは記述しない。次は人間の時間位置つき知覚記録が必要であり、それ以前に`CUT`、`THROW`、`REVEAL`、`VACUUM`、`TAIL CHOKE`の事件時刻を確定しない。

### 18.7 10秒窓による区間安定性

30秒全体の差が一部区間だけで生じた可能性を調べるため、各previewを0–10秒、10–20秒、20–終端の三窓へ分け、同じ共通解析器で再測定した。結果全文は[`preview-window-analysis-standard.json`](./preview-window-analysis-standard.json)に保存する。

Dub版が原曲版より低い窓数:

| 指標 | Rockers pair | Vampires pair | 合計 |
| --- | ---: | ---: | ---: |
| onset/s | 2/3 | 2/3 | 4/6 |
| frame RMS p10 | 3/3 | 3/3 | 6/6 |
| frame RMS p50 | 3/3 | 3/3 | 6/6 |
| frame RMS p90 | 2/3 | 3/3 | 5/6 |
| spectral centroid | 1/3 | 3/3 | 4/6 |

この分割で、30秒全体のonset密度低下は全区間へ一様に広がる特徴ではないと分かった。一方、frame RMS p10とp50の低下は6窓すべてで再現した。

Rockers pairではp10の差が-6.74、-8.29、-4.02 dBであるのに対し、p90の差は+0.15、-0.25、-0.27 dBだった。このpreviewでは大きい瞬間の水準がほぼ同じまま、振幅分布の静かな側が深くなっている。

Vampires pairではp10の差が-13.62、-10.78、-9.76 dB、p90の差も-1.44、-1.45、-1.68 dBだった。こちらは静かな側の拡大に加え、大きい側も全窓で低い。

したがって二組に共通する直接測定は「発音数が常に少ない」ではなく、**preview内の各10秒窓で振幅分布の低い側と中央値が下がる**ことである。これを聴覚上の無音、source mute、空間の深さと同一視するには、時間位置つき聴取がまだ必要である。

## 18.8 official Demucsによるdrums / no-drums二次監査

前節の「振幅分布の静かな側が下がる」という差が、ドラム骨格の弱化なのか、ドラム以外の推定層の減算なのかを分けるため、mainの既存Linux CPU監査手順を同じ4 Previewへ適用した。新しいDub専用分離法は作っていない。

使用した共有権威:

- `main:research/music-analysis/run_linux_demucs_audit.sh`
  - blob: `2d2af511d136f2ae09d48dd7bb33e1bfe9bb667b`
- `main:research/music-analysis/demucs_cpuinfo_compat.py`
  - blob: `a6235124714f3b31ef9c4d0cfefe5ba57ba99480`
- `main:research/music-analysis/calibrate_analyzer.py`
  - blob: `314db6380f63c12017b52dcd3dd2dfcaff94a539`
- `main:research/music-analysis/analyze_previews.py`
  - blob: `4e36a19c5760cc1f3a7cf4b80ad3e9ad6e3baa47`

分離条件はofficial Demucs 4.0.1、`htdemucs`、PyTorch CPU、`--shifts 1 --overlap 0.25 --two-stems drums`、seed 0。4本の入力SHA-256は18.2の保存値と全一致した。共通解析器の合成校正は再度12/12件成功した。数値全文は[`preview-demucs-audit-standard.json`](./preview-demucs-audit-standard.json)へ保存する。

30秒全体の推定stem:

| pair | stem | RMS Dub−original | p50 Dub−original | onset/s Dub−original |
| --- | --- | ---: | ---: | ---: |
| A | drums | +0.95 dB | +2.79 dB | +0.300 |
| A | no_drums | -1.26 dB | -2.07 dB | -1.303 |
| B | drums | +0.88 dB | +5.91 dB | +0.334 |
| B | no_drums | -3.39 dB | -4.80 dB | -2.536 |

10秒窓の方向再現:

| 判定 | Rockers pair | Vampires pair | 合計 |
| --- | ---: | ---: | ---: |
| Dub drumsのp50が高い | 3/3 | 3/3 | 6/6 |
| Dub drumsのonset/sが低くない | 3/3 | 3/3 | 6/6 |
| Dub no_drumsのp10が低い | 3/3 | 3/3 | 6/6 |
| Dub no_drumsのp50が低い | 3/3 | 3/3 | 6/6 |
| Dub no_drumsのonset/sが低い | 3/3 | 3/3 | 6/6 |

推定drumsの周期候補は、6窓すべてで原曲版とDub版が同じ約132–140 BPM族を共有した。half-time候補が首位になる窓はあるため、単独BPMとは呼ばない。

この二次監査では、二組に共通する静かな側の低下は**推定ドラム骨格の弱化には現れず、主に`no_drums`推定層へ現れた**。したがって現段階の解釈は、「周期骨格を維持しながら、声・ギター・鍵盤・残響などを含む非ドラム側の密度と存在量を減らす」である。

ただしDemucs出力は派生推定であり、実multitrackではない。drums + no_drumsの再構成残差は原mix RMS比で0.0456–0.0573あり、分離漏れやartifactを含む。また`no_drums`は声、楽器、returnを区別しない。この結果から`CUT`、`THROW`、source mute、mixing意図を確定しない。時間位置つき聴取が必要という18.6–18.7の境界は維持する。

## 19. 時間分析の記録形式

### 19.1 一行を一事件にする

```text
DubObservation = {
  pairId,
  versionId,
  evidenceClass,
  tAbsolute,
  tNormalized,
  loopOrPhraseIndex,
  sourceClass,
  action,
  tailEnd,
  confidence,
  note
}
```

### 19.2 証拠区分

| 値 | 意味 |
| --- | --- |
| `METADATA` | 曲名、版、尺、credit等、取得した外部記録 |
| `DIRECT_AUDIO` | 実際に取得した音声から直接聴取・測定した観測 |
| `INFERENCE` | `DIRECT_AUDIO`をもとにした信号経路・演奏意図の推論 |
| `UNRESOLVED` | 複数解釈が残り確定できない箇所 |

catalog metadataやpreview URLの存在だけを`DIRECT_AUDIO`へ昇格させない。取得したpreviewの直接測定または聴取だけをこの区分へ入れる。

### 19.3 action語彙

既存の七語をそのまま押しつけず、聴取時には次の観測語へ分ける。

| 観測語 | 判定 |
| --- | --- |
| `DRY_EXIT` | dry sourceが知覚上退場する |
| `DRY_ENTRY` | dry sourceが知覚上再登場する |
| `SEND_EVENT` | 特定の音片だけが時間／空間系へ投げられる |
| `RETURN_ONLY` | 原音不在でreturnだけが残る |
| `RETURN_CUT` | 継続中のreturnが知覚上切られる |
| `FILTER_NARROW` | sourceの帯域が狭まり身体性が減る |
| `FILTER_OPEN` | 狭まった帯域が戻る |
| `MASS_DROP` | 複数sourceが短時間に退場する |
| `FULL_OR_PARTIAL_RESET` | 基準編成へ戻る |

分析後にだけ、`DRY_EXIT -> RETURN_ONLY`を`CUT + THROW`候補へ、`MASS_DROP`を`VACUUM`候補へ写像する。先に七語へ押し込んで人物差を消さない。

### 19.4 時刻

- `tAbsolute`: 取得音源の先頭からの秒。
- `tNormalized`: `tAbsolute / duration`。再発版の無音余白や速度差があるため補助値として使う。
- `loopOrPhraseIndex`: 小節数を断定できる場合だけ記入する。不明なら空欄。
- 版の先頭無音、fade、速度差を確認せず、秒数だけで原曲とDub版を機械的に対応させない。

### 19.5 tailの因果

tailを単に「echoあり」と数えない。

1. 親になったsource eventを特定する。
2. dry sourceが残るか消えるかを分ける。
3. tailが次のphrase境界を越えるか記録する。
4. 新しいsource entryと衝突するか、空白を占有するか記録する。
5. returnが自然減衰したか、演奏者に切られたように聞こえるかを分ける。

親eventを特定できないreturnは`UNRESOLVED`にする。

## 20. 比較指標候補

指標は優劣評価ではなく、人物ごとの演奏文法の差を見つけるために使う。

### 20.1 介入密度

```text
interventionDensity = DIRECT_AUDIO事件数 / 分
```

同じ長さでも、ScientistがTubbyより多いと決めつけず、実測後に比較する。

### 20.2 dry不在率

```text
dryAbsenceRatio(source) = sourceが知覚上不在の時間 / 全時間
```

stem分離なしの聴感判定になる場合は、confidenceを必ず付ける。

### 20.3 tail自律率

```text
tailAutonomyRatio = RETURN_ONLY時間 / return総時間
```

値が高いほど優れているのではない。原音を消した後、過去がどれだけ独立声部として働くかを見る。

### 20.4 編成状態数

同時に知覚できるsource classの組をstateとして数える。ただし細かな音色差を別stateへ水増ししない。

例:

```text
{bass, drums, vocal}
{bass, drums, vocalTail}
{drums, hornTail}
{bass, drums}
```

### 20.5 予測破り

定量値へ急いで落とさず、次の二条件を満たす事件を注記する。

- 直前まで成立していた反復規則が破られる。
- 破った後もrhythmまたは別の因果が残り、曲が単に停止しない。

Scientistのいうsurpriseを、effect数やランダム性へ置換しないための観測欄である。

## 21. コーパスから設計へ戻すゲート

一曲で見つかったgestureを直ちに製品機能へしない。次を通ったものだけ設計候補として残す。

1. 二人以上のmixer、または同一mixerの三曲以上で再観測される。
2. sourceの音色に依存せず、存在・不在・時間・距離の操作として抽出できる。
3. 既存のSkulptur主演奏面を置換しない。
4. 第五trackを作らない。
5. hidden multi-touch commandを要求しない。
6. 演奏者が発生時刻と終了時刻を引き受けられる。
7. iPhone実機で入力因果と音量安全性を検証できる。

現在このゲートを通過済みのDub機能はない。七つの演奏文法も`candidate`のままである。

## 22. 次の未完了工程

- Corpus AとBの30秒previewは取得済み。次は権利と取得経路を保ったままfull-length版を確保する。
- 取得した版のcontent identity、duration、先頭無音を固定する。
- 最初は自動stem分離を使わず、原曲／Dub版を交互に聴いて事件表を人手で作る。
- 次に必要な箇所だけ波形、spectrogram、loudness、band energyで観測を補助する。
- 自動解析結果を聴取事実へ置き換えない。
- Corpus AとBで語彙が安定した後、Lee Perryの別系統を追加する。
