# ノンミュージシャンとリアルタイム演奏責任

- research-id: `20260831-non-musician-performance`
- 状態: `active`
- 更新日: 2026-08-31
- 対象: 4トラック録音後のマルチタッチ主演奏面
- 製品コード変更: なし
- 統合判断: 未実施
- iPhone実機検証: 未実施

## 現在の問い

ノンミュージシャンでも、既成ループを開始して演奏しているように見せるのではなく、Charlie Hunterの低音・和音・旋律の身体的連動と、Jeff Millsの複数時間層の高速な構成判断へ即興で入れる楽器を作れるか。その際、AutechreとAphex Twinから複雑な音色プリセットを借りるのではなく、一つの操作が複数の音響関係へ波及し、安定した音型を演奏中に変形できる構造だけを抽出できるか。

## 現在ユーザー要求

- iPhoneのマルチタッチでリアルタイム演奏できること。
- 既成ループの垂れ流しや、一ループをパッドで開始しただけの行為をライブ演奏と偽装しないこと。
- ノンミュージシャンでもCharlie HunterとJeff Millsの「センス」に即興で入れること。
- その実現へAutechreとAphex Twinの構造を接続すること。
- トリプルタッチを上限として設計しないこと。
- 研究をGitへ保存しながら進めること。

ここでいう「センス」は音色、フレーズ、既成曲、本人の演奏結果の模倣ではない。各演奏者がその場で引き受けている関係と判断の種類を指す。

## 権威と証拠境界

### 外部資料で観測した事実

1. Brian Enoは1979年のLester Bangsとの対話で、当時の「musician」を指の技能を楽器へ適用する人として捉え、自分の技能は手技より`ingenuity`にあるため`nonmusician`という対抗的位置を取ったと説明した。これは音楽制作能力の欠如を意味しない。
2. Enoは後年、テープレコーダーを自分が最初に扱えた音楽道具と説明し、録音された音を絵具のように可塑的な素材として扱った。
3. John Cageは実験的行為を、後で成功／失敗として評価する試験ではなく、結果が未知の行為として記述した。同時に、何でも無関心に許すのではなく、起きているすべてへ近接した注意を要求した。
4. Scratch Orchestraは訓練済み演奏家だけでなく、芸術家、学生、事務職などの`enthusiasts`が資源を持ち寄る構造を取った。Portsmouth Sinfoniaでは初心者と熟練者の差が、通常の正確な再現では生じない結果を作った。
5. Grandmaster Flashは再生装置だったターンテーブルを、針、フェルト、ミキサー、同一盤二枚、逆回転を含む演奏系へ作り替えた。彼はライブで人間ができることをコンピュータに代行させることへ否定的で、観客が「どう行ったか」を見ることをライブの価値に含めた。
6. Charlie Hunterの多弦ギターは低音弦とギター弦を一つの楽器へ置き、低音、和音、旋律を同時演奏できる。現在の公式説明も、楽器の独自設計と同時演奏を中核に置く。
7. Jeff Millsはターンテーブルとミキサーの枠を越え、1980年代初頭からドラムマシンと三台のターンテーブルを併用していたと述べている。
8. AutechreはMax/MSPを、用意された機能の選択ではなく、自分たちで演奏セットアップを開発できる制限のない環境として使ったと説明している。
9. AppleのUIKitは、`isMultipleTouchEnabled`を有効にしたviewが同一マルチタッチ列の複数接触を受け取れることを文書化している。`UIPanGestureRecognizer`にも最小／最大接触数の設定がある。したがって三接触はUIKitの概念上の固定上限ではない。ただし対象iPhone、実装方式、Mobile Safariまたはnative runtimeで安定して受理できる実用接触数は未検証である。

### この研究の推論

- ノンミュージシャンは固定身分ではなく、既成奏法を唯一の入口にせず、音との因果関係を作り直す実践上の位置である。
- 初心者へ完成結果を与える自動伴奏は、技能障壁を下げても演奏責任まで機械へ移す可能性がある。
- 入口の容易さと演奏の深さは対立しない。音を出す最初の接触は簡単にし、複数接触間の関係を身体化するほど結果が深くなる設計が必要である。
- Charlie Hunterから抽出すべきものはギター奏法でなく、低域と上声を別々に選びながら一身体内で相互拘束する構造である。
- Jeff Millsから抽出すべきものは909や三台のデッキの外観でなく、複数の時間層を短く導入、衝突、退出させる判断密度である。
- Autechre／Aphex Twinから抽出すべきものは「ランダム」「グリッチ」という結果でなく、操作と結果の間に決定論的だが容易には予測し尽くせない連鎖を作ることである。

これらは製品採用済みの判断ではない。

## 今回の発見: 指数ではなく接触位相を演奏単位にする

三本指までを機能表へ割り当てる設計は、四本目以降を無意味にし、指を増やすたびモード暗記を要求する。逆に全接触の全組合せを音へ割り当てると、接触数`n`に対して関係数が`n(n-1)/2`へ増え、演奏者も実装も制御不能になる。

そこで接触を固定された「指1／指2／指3」として扱わず、次の動的グラフとして扱う。

- `node`: 現在画面へ触れている各接点。
- `anchor`: 各手または各接触群で最初に成立した接点。
- `edge`: anchorと、その群の各追加接点との関係。
- `cluster`: 時間的・空間的に近い接点群。左手／右手を端末が断定せず、接触のまとまりとして扱う。
- `bridge`: 二群の重心間の関係。全接点間を総当たりで結ばない。

関係数を各cluster内の星型edgeとcluster間bridgeへ限定すれば、接触数にほぼ比例して演奏情報を増やせる。四本目、五本目も独立した声部または時間層として参加できるが、組合せ爆発は避けられる。

## 演奏面の具体案 v0.1

画面を固定ボタン群へ分割せず、一枚の連続面にする。ただし接触群の開始位置によって、その群が最初に担当する関係を分ける。

- 左寄りで始まったcluster: 音程／低音／上声関係。
- 右寄りで始まったcluster: 時間／打撃／読取ヘッド関係。
- 二群のbridge: 安定度／相互変調／feedback。

左右固定は最終仕様ではない。利き手、縦横、片手演奏を実機検証するまで候補に留める。

### 音程cluster

| 接触 | 直接結果 | 自動化しないこと |
| --- | --- | --- |
| anchorを置く | 低音または基準音を一声だけ発音 | 自動コードを付けない |
| 追加nodeを置く | anchorとの距離・方向に対応する上声を一声追加 | コードネームを選ばない |
| anchorだけ動かす | 上声との関係を変えながら低音を移動 | 自動voice leadingを生成しない |
| 追加nodeだけ動かす | 低音を保持して上声を連続変形 | スケール内へ全操作を隠れて補正しない |
| cluster全体を動かす | 声部間隔を保って移調または音色移動 | 既成フレーズを再生しない |
| nodeを離す | その声部だけrelease | cluster全体を勝手に停止しない |

初期候補では、anchorの`x`を基準音高、anchorからnodeへの相対`x`を音程、相対`y`を各声部の音色または明暗へ割り当てる。絶対座標だけで全声部を決めず、相対位置で低音と上声の関係を直接つかませる。

音程量子化の有無、音律、音域、低音と上声の音源は未固定。量子化を使う場合も、隠れた自動コード生成ではなく、接触位置と実際の構成音を可視化する。

### 時間cluster

| 接触 | 直接結果 | 自動化しないこと |
| --- | --- | --- |
| anchorをtap | 一回だけ発音または現在素材へ一回cut | tap一回で一小節を開始しない |
| 二つ目のnodeを保持 | anchor-node距離を反復周期にする | 固定ステップ列を呼び出さない |
| nodeを近づける | 周期を連続的に短縮しratchetへ入る | 「IDM」プリセットを選ばない |
| nodeを離す | 周期を長くする | BPM gridだけへ強制吸着しない |
| 三つ目以降を置く | 独立周期または別の読取ヘッドを追加 | 三接触を総上限にしない |
| nodeをrelease | 対応時間層を停止または短く減衰 | 無期限に鳴らし続けない |

周期は距離から連続値へ写像する。最初の実験候補は`40ms..1200ms`。拍同期を使う場合は常時強制せず、接触中に連続周期と近傍分割の間を行き来できる方式を別検証する。

### cluster間bridge

二群の全指を一対一で結ばず、各clusterの重心、平均速度、接触面積合計、寿命を使う。

| 二群の関係 | 候補結果 |
| --- | --- |
| 重心が近づく | 時間clusterが音程clusterのtransientを細分化 |
| 重心が離れる | 相互変調を弱め、各群を独立させる |
| 相対速度が上がる | 読取位置分裂、短時間reverse、filter tiltを増やす |
| 両群が静止する | 現在状態を保持し、変異を止める |
| 一群が消える | bridgeだけをreleaseし、残った群は継続する |

一つのbridge量を複数parameterへ同率で送らない。音量、feedback、粒子密度が同時に最大化すると危険で演奏不能になる。各parameterは異なる曲線、上限、平滑化、音量安全境界を持たせる必要がある。

## 4トラックと演奏層を混同しない

現行方向では4トラック録音が中心であり、本研究はそれを廃止しない。分けるべきなのは保存媒体と演奏行為である。

```text
4トラック録音／再生
  -> 現在素材
  -> 接触clusterが追加読取ヘッド／声部／cutを生成
  -> cluster間bridgeが相互作用を生成
  -> releaseで追加関係を閉じる
```

- `PLAY`だけなら再生であり、接触演奏とは表示しない。
- 再生中という理由だけで波形や演奏エフェクトを派手に反応させない。
- 接触で生じた読取ヘッド、反復、変形は同じ`ContactGestureFrame`列と結びつける。
- 接触を離した後も残すtailは、どの接触から生じたかを追跡できるようにする。
- 既成ループを禁止して演奏者を取り締まるのではなく、再生と現在の介入を因果上・表示上で分離する。

## ランダムではなく演奏された不予測性

複雑さを作る候補は乱数ボタンではなく、次の状態依存である。

```text
現在結果 = f(
  現在接触,
  接触間関係,
  各接触の直前速度,
  直近素材,
  現在の読取位置,
  feedback内部状態
)
```

同じ初期状態と同じ接触列なら、原則として同じ結果へ戻せる。一方、feedbackと読取位置が時間とともに変わるため、演奏者は長時間後の結果を完全には先取りできない。この境界を「演奏された不予測性」の候補とする。

完全乱数を使う場合は、乱数seed、適用parameter、上限をPerformance Takeへ記録し、再演可能性と原因追跡を失わない。完全乱数の採用自体は未判断。

## 十秒の具体演奏列

1. 音程clusterのanchorを置き、低音一声を鳴らす。
2. 二つのnodeを追加し、上声二声を作る。
3. anchorだけを動かし、上声を残して低音との間隔を変える。
4. 反対側へ時間clusterのanchorをtapし、一回だけcutする。
5. nodeを追加して保持し、二点距離を反復周期にする。
6. 三つ目のnodeを置き、別周期を加える。ここで三接触を上限にしない。
7. 二clusterの重心を近づけ、低音transientを二つの周期へ流し込む。
8. 時間nodeを一つずつ離し、対応周期だけを消す。
9. 音程anchorを止めて上声だけを動かす。
10. 全接触を離し、明示されたtailだけを減衰させる。

この列には完成フレーズ、自動コード、自動展開はない。低音、上声、複数周期、ratchet、素材cut、状態依存変形はすべて現在の接触列から生じる。

## 演奏責任を検査する条件

1. **反事実依存**: 接触位置または時刻が違えば、聴いて分かる結果差が生じる。
2. **局所因果**: 一回の操作が、説明不能な完成展開を長時間生成しない。
3. **退出可能性**: 各nodeを離したとき、対応する声部または時間層だけを閉じられる。
4. **失敗可能性**: 密度過多、濁り、空白、周期衝突が実際に起こり、常時「格好よく」補正されない。
5. **回復可能性**: 失敗しても全停止以外に、node単位のrelease、cluster分離、feedback低下で戻れる。
6. **可聴因果**: 画面を見なくても、現在の動作が何を変えたかある程度聴き分けられる。
7. **表示の正直さ**: 再生、自動処理、現在接触、記録済みTake再生を同じ「LIVE」表示へまとめない。
8. **熟練余地**: 初回接触から発音できるが、接触数、独立運動、周期衝突を身体化すると結果の自由度が増える。

## Field Looperへ採用する点／採用しない点

### 候補として残す

- 固定三本指mappingではなく、anchor-node-cluster-bridgeによる可変接触数。
- 低音と上声を相対位置で結ぶ音程cluster。
- 二点距離を周期へ、追加nodeを独立時間層へ変える時間cluster。
- 4トラックを保存層、接触を演奏層として分離する。
- 再生と現在介入を因果上・表示上で分ける。
- 同じ受理`ContactGestureFrame`列から音響、描画、Performance Takeを導出する。

### 採用しない

- 一タップで完成コード、完成ビート、完成展開を出す「初心者モード」。
- Autechre／Aphex Twin風ランダム生成ボタン。
- Jeff Millsの909や三台デッキを画面上に模写するUI。
- Charlie Hunterのギター外形や弦配置を模写するUI。
- 三接触を機能上限にする設計。
- すべての接触組合せを総当たりでparameterへ接続する設計。
- PLAY中の素材を接触演奏中と偽装する表示。
- 既存KAOSS型Master／XY階層の復活。

## 触る実装パス

現時点では製品コードを変更しない。

将来の候補パスは、統合判断後に別作業として固定する。本研究だけを根拠に`field-processor/`、`prototype/`、PR #44の候補実装を変更しない。

## 依存する研究

- `integration/DIRECTION.md`
- `integration/DECISIONS.md`
- `integration/STATUS.md`
- `research/20260828-image-contact-bridge/`
- Skulptur接触演奏候補: Draft PR #44。`main`未統合、実機未検証。
- Charlie Hunter演奏スタイル専用研究: 別研究として継続中／本research-idでは外部資料から必要構造だけを取得。
- Jeff Mills演奏スタイル専用研究: 別研究として継続中／本research-idでは外部資料から必要構造だけを取得。
- Autechre専用研究: 別研究として継続中。本research-idではMax/MSPの演奏系自作という境界だけを使用。
- Aphex Twin専用研究: 専用Git本文の所在未確認。本research-idでは既成音色の模倣を採らない境界だけを置く。

## 既存判断との関係

- D-001の4トラック中心を維持する。
- D-002の独立DRUMSを維持する。時間clusterを独立DRUMSへ統合済みとは扱わない。
- D-006に従い、各演奏者／機材を機能カタログ化しない。
- D-007のSkulptur型主演奏面と接続する候補だが、具体mappingの採用判断ではない。
- D-008に従い、KAOSS中心階層を復活させない。
- D-009に従い、横画面固定を前提にしない。
- D-010に従い、別島の会話内容だけで統合済み状態を作らない。

## 失効した判断

- 「ノンミュージシャン向け＝何をしても音楽的に補正される」という仮定は採用しない。
- 「複雑な演奏＝機能を三本指ジェスチャーへ割り当てる」という仮定は採用しない。
- 「ループが鳴り続けること自体を禁止すれば演奏責任が成立する」という仮定は採用しない。再生と現在介入を分離し、介入の因果を追えることを優先する。

## 未検証事項

- iPhone機種ごとの安定同時接触数。
- native UIKit、WKWebView、Mobile Safariでの接触列、cancel、capture喪失の差。
- 画面サイズで左右二clusterを両手演奏できるか。
- 利き手、片手、縦画面、横画面のcluster開始位置。
- cluster認識が演奏中に意図せず分裂／結合しない条件。
- 4本以上の接触でUIが指に隠れ、可視因果を失わないか。
- 音程clusterの音律、量子化、音域、音源。
- 時間clusterの周期範囲、拍同期、swing、phase、ratchet上限。
- bridgeが音量、feedback、密度を危険に同時増加させないmapping。
- 4トラック個別処理と共通処理のownership。
- 独立DRUMSと時間clusterの同期／迂回境界。
- Performance Takeでcluster再構成、乱数seed、内部状態を再現できるか。
- Mobile Safari／iPhoneのAudioWorklet負荷、発熱、音量安全性、実音、聴感。
- 実際のノンミュージシャンが説明なしで因果を発見できるか。
- 熟練者が自動補正の狭さを感じず、独立声部と時間層を深められるか。

## 一次資料・研究資料

- Lester Bangs, Brian Eno interview, 1979: <https://music.hyperreal.org/artists/brian_eno/interviews/musn79.html>
- Brian Eno, Tape Op interview: <https://tapeop.com/interviews/85/brian-eno>
- John Cage, “Experimental Music: Doctrine”: <https://sites.evergreen.edu/thewordintheear-fall/wp-content/uploads/sites/316/2014/09/cage3.pdf>
- Cornelius Cardew, “A Scratch Orchestra: Draft Constitution”, *The Musical Times*, 1969. 書誌と引用範囲: <https://www.jstor.org/stable/27294312>
- Cecilia Sun, “Brian Eno, Non-Musicianship, and the Experimental Tradition”: <https://research-repository.uwa.edu.au/en/publications/brian-eno-non-musicianship-and-the-experimental-tradition/>
- Grandmaster Flash interview: <https://chaoscontrol.com/grandmaster-flash/>
- Grandmaster Flashの技術史資料: <https://www.thevinylfactory.com/news/grandmaster-flash-the-birth-of-turntablism>
- Charlie Hunter公式プロフィール: <https://www.charliehunter.com/charlie-hunter>
- Charlie Hunter interview: <https://www.fretboardjournal.com/features/interview-charlie-hunter-public-domain/>
- Jeff Mills interview: <https://www.whitefungus.com/jeff-mills-human-human>
- Autechre interview: <https://www.tinymixtapes.com/features/autechre>
- Aphex Twin interview: <https://chaoscontrol.com/aphex-twin-2/>
- Apple, `UIView.isMultipleTouchEnabled`: <https://developer.apple.com/documentation/uikit/uiview/ismultipletouchenabled>
- Apple, `UIPanGestureRecognizer.maximumNumberOfTouches`: <https://developer.apple.com/documentation/uikit/uipangesturerecognizer/maximumnumberoftouches>

## 次の研究工程

1. 音程clusterの相対座標を、低音・上声の独立性を失わない最小mappingへ絞る。
2. 時間clusterの距離→周期写像を、40msから1200msの範囲で試作し、連続周期と拍同期の境界を比較する。
3. 三接触、五接触、八接触の疑似frame列を作り、cluster関係数、退出可能性、cancel復旧を構造テストする。
4. 実音の前に、同じframe列から表示、parameter event、Performance Takeが一対一で追跡できるか検査する。
5. その後にだけ、PR #44または別候補実装への統合差分を提示する。

この順序は研究計画であり、製品コード実装、PR #44更新、統合判断、実機検証を完了したことを意味しない。
