# DJ Shadow研究 — サンプルを完成ループではなく、場面と役割へ変える

- status: `active`
- research-id: `20260902-dj-shadow`
- 研究対象: DJ Shadow（Josh Davis）のサンプリング、長尺構成、録音空間、DJ／ライブ、制作技術の変化
- 現在の問い: 反復素材を固定伴奏として垂れ流さず、演奏中に役割、前景、場面、回帰条件を変える原理として何を抽出できるか
- 更新日時: 2026-09-04 UTC
- 起点: `sound-lab/main@f5c694e47f9ed115e9c2de6433dbd6976847a2e4`
- 変更範囲: 研究記録のみ。製品コード、`integration/`、既存判断は変更しない
- 保存境界: この研究ブランチは研究本文の保存先。main統合、PR作成、製品採用、実装を意味しない

## 0. 今回固定する結論

DJ Shadowを「大量のレコードから珍しいネタを探す人」または「暗いインストゥルメンタル・ヒップホップ」へ縮めない。

現在の中心仮説は次である。

> Shadowの作曲単位は、完成した一小節ループではなく、録音断片が現在担っている役割と、曲中でその役割が変わる事件である。

同じ断片でも、導入では環境、次の局面では拍の基準、別の局面では記憶、最後には崩壊の残骸として機能しうる。曲はコード進行や同一ビートの継続だけで進まず、次の変化で進む。

- 新しい断片が入る
- 既存断片が消える
- 前景と背景が交換される
- 同じ断片の機能が変わる
- 別の録音空間へ移る
- 一度使った断片が別の意味で戻る
- 局所的な回帰を作り、全要素は同時に初期化しない

この仮説は文献、本人発言、公開録音の聴感から導いた。フル尺PCMの波形測定、ステム分離、サンプル単位のアラインメントは未実施である。

## 1. 前回提示からの証拠境界

前回の会話では、次を研究の入口として提示した。

- 過去の録音を使い、存在しなかった演奏空間を構築する
- MPC60の短いサンプリング時間が選択と確定を要求した
- “Stem / Long Stem”や“Napalm Brain / Scatter Brain”を長尺構成として読む
- ドラム、持続する情景、記憶断片、場面転換を分ける

これらは研究仮説または聴感分析であり、当時も今回も音源ファイルの信号解析結果ではない。本記録では、本人が工程を説明した“Mutual Slump”、本人が完成判断を説明した“Six Days”、本人が初期構成を回顧した“Midnight in a Perfect World”を証拠の固定点に加える。

## 2. 取得資料

### 本人発言を含む主要資料

1. DJ Shadow / Song Exploder, “Mutual Slump,” Episode 91 transcript
   https://songexploder.net/transcripts/dj-shadow-transcript.pdf
2. Josh Davis and James Lavelle, “How we made DJ Shadow's Endtroducing,” *The Guardian*, 2022
   https://www.theguardian.com/culture/2022/jun/27/inadvertently-invented-trip-hop-how-we-made-dj-shadow-endtroducing-pink-floyd-beethoven
3. Eric Stenman, “DJ Shadow: Samplers, Turntables, & Downtime,” *Tape Op* No. 11, 1998
   https://tapeop.com/interviews/11/dj-shadow
4. Bill Brewster, “The Vinyl-Hunting Exploits of DJ Shadow,” Red Bull Music Academy Daily archive
   https://daily.redbullmusicacademy.com/2018/04/dj-shadow-interview/
5. DJ Shadow interview, “The Shadows of Tomorrow,” Bonafide, 2016
   https://www.bonafidemag.com/the-shadows-of-tomorrow/
6. “DJ Shadow's Reconstructed: An Oral History,” *The Quietus*, 2012
   https://thequietus.com/interviews/dj-shadow-reconstructed-best-of-interview/
7. “DJ Shadow on the Music That Made Him,” *Pitchfork*, 2020
   https://pitchfork.com/features/5-10-15-20/dj-shadow-on-the-music-that-made-him/
8. DJ Shadow, *Action Adventure* album update and release statements, 2023
   https://djshadow.com/blogs/album-update/new-album-update
   https://djshadow.com/blogs/news/my-new-full-length-album-action-adventure-is-released-today
9. DJ Shadow interview, KCRW, 2023
   https://www.kcrw.com/shows/morning-becomes-eclectic/stories/dj-shadow-2023-album-action-adventure-interview
10. DJ Shadow reader interview, *The Guardian*, 2026
    https://www.theguardian.com/music/2026/apr/16/dj-shadow-josh-davis-interview-kraftwerk-touchstone-of-my-career

### 資料の限界

- 制作年代の異なる発言を、同じ制作環境の説明として混ぜない。
- 本人が現在回顧した初期工程と、制作当時のインタビューを区別する。
- サンプル元データベースの曲名一致だけで、使用区間、加工、権利状態を確定しない。
- “trip-hop”は流通・批評上の語として記録するが、Shadow本人の制作原理の正本にはしない。
- 本人の意図説明は工程の一次資料だが、聴覚効果や信号特性の測定結果ではない。

## 3. 制作方法の変化

### 3.1 MPC以前: 四トラック上の「貧者のサンプリング」

Shadow本人は、サンプラーを買えなかった時期に、レコードを四トラック・カセットへ直接キュー出ししてサンプリングに似た制作を行ったと回顧している。

ここで重要なのは機材不足の美談ではない。Shadowの制作は最初から、演奏を一から打ち込むより、既存録音の入口と出口を手で決め、別の時間へ置き直すことから始まっている。

### 3.2 MPC60: 保持量の不足が、役割の決定を強制する

本人の2022年の説明では、MPC60は一度に約2.5秒のステレオ素材をサンプルでき、合計保持量は約13秒だった。ビート、旋律、打楽器を組み、Dan the Automatorの環境でマルチトラック化した。

2016年の別インタビューでも、`Endtroducing.....`を特徴づけた条件として13秒のステレオ・サンプリング時間を挙げ、作品が主にループとチョップで構成されたと説明している。

したがって、MPC60の価値を「古い機材特有の音」だけに置かない。構成上の作用は次にある。

1. 何を保持するかを早期に決める
2. 一つの断片に複数の役割を背負わせる
3. 全素材を可逆状態で抱えず、バウンスして次の局面へ進む
4. 音色の微調整より、断片の出入りと順序を判断する
5. 曲を完成素材の並列ではなく、確定判断の履歴として作る

### 3.3 MPC3000とUNKLE: 小机上の制作から大規模ミックスへ

1998年の`Tape Op`で、ShadowはUNKLE制作の中心機材をMPC3000と説明している。`Endtroducing.....`はADATへ録音し、UNKLEは2インチ・アナログ・テープへマルチトラック録音した。Pro Toolsは主にアルバム編集とシーケンス、UNKLEではノイズの多いサンプルのde-clickにも使った。

これは「サンプラーだけで全部作った」という純粋性からの転落ではない。短い断片を作曲核にする工程と、ゲスト、歌、2インチ・テープ、エンジニアリングを組み合わせる段階への移行である。

### 3.4 `The Private Press`: サンプリングによる第二の声明

Shadowは後年、最初の二枚をサンプリングについて声明を出す作品だったと説明している。`The Private Press`は`Endtroducing.....`の同じ雰囲気を反復するのでなく、私的録音、声、長尺の物語、強いセクション差を拡張した作品として調べる。

本人は“Six Days”について、制作中の多数の判断のどれも変更したくないと初めて感じた曲だと回顧している。ここでの完成は、素材数の多さではなく、配置、パン、構成、ミックスを含む判断系列が閉じた状態である。

### 3.5 MPC中心主義からの離脱

ShadowはMPCの硬直性に疲れ、より柔軟なPro Tools／DAW中心の工程へ移ったと説明している。また2026年の回答では、サンプル・クリアランスと権利持分の問題、制作方法を新しく保つ欲求の両方を理由に挙げた。

したがって次を分ける。

- サンプリングという作曲思想
- MPCという特定操作系
- 既存録音の権利処理
- 自分で演奏・録音した素材の再サンプリング
- DAW上の編集、合成、演奏家との共同制作

Shadow研究から「MPCを再現すればよい」という結論は出ない。

### 3.6 `Action Adventure`: 全音響空間を本人が引き受ける

2023年の公式説明では、ゲスト、コラボレーション、フィーチャーを置かず、本人が全構成を占有する作品として`Action Adventure`を作った。別の公式更新では、ボーカリスト用の余白を作らず、利用可能な音響空間を自分で埋めることを課題にしたと述べている。

KCRWでは、コロナ期に入手した1980年代のミックステープ群が音楽へ戻る橋になったと説明した。またノスタルジーだけに閉じず、同時代に可能なこととの均衡を取る必要を語っている。

これは`Endtroducing.....`への回帰ではない。本人も後のインタビューで、共通点はインストゥルメンタルでゲストがいないことまでで、現在の作曲・工学的知識を捨てて過去へ戻ったわけではないと区別している。

## 4. “Mutual Slump”から取得できる制作事実

Song Exploderの本人解説は、Shadowの抽象的な「コラージュ」ではなく、一曲の意思決定を追える重要資料である。

### 4.1 レコード店は素材庫ではなく、行き詰まりを解除する外部系だった

`Endtroducing.....`のジャケットに写るRecordsは、制作中に行き詰まると週一、二回通う場所だった。完成形を検索語で探したのではなく、聴取中の偶然が制作上の詰まりを解除した。

この関係を次のように記述する。

```text
current composition state
  -> unresolved need
  -> unindexed encounter
  -> fragment acquires a role
  -> composition state changes
```

重要なのは巨大ライブラリではなく、現在の曲が何を必要としているかによって、同じレコードの意味が変わることにある。

### 4.2 ドラムはブレイク全体の引用と、個別イベントの再構成を分ける

本人は、Pugh Rogefeldtの録音から、ノイジーな導入のフィルとギター・フィードバックは比較的そのまま残し、それ以外のドラムは切り分けて組み替えたと説明している。

一小節のブレイクをそのままループするのでなく、元録音に含まれる複数のキックとスネアから強いものを三、四種類ずつ選び、同じ音を機械的に連打せず交替させた。本人はこれを、元の演奏を再構成した「super version」と説明している。

したがって同一曲内に次の二種類が共存する。

- 録音された出来事全体を保持する引用
- 元の演奏を部品へ分け、新しい時間へ再配置する演奏

すべてを細かく切るわけでも、すべてを長いループのまま使うわけでもない。

### 4.3 明白なサンプルは、隠すべき失敗ではなかった

Björk“Possibly Maybe”の使用について、Shadowは当時の聴き手が気づくような明白な引用を意図的に置き、他のネタを探す聴取を攪乱する働きも与えたと説明している。

これは希少性競争だけでは説明できない。認識できる断片と認識できない断片を混ぜ、聴き手の注意そのものを構成する。

### 4.4 声は既成音源だけでなく、私的録音から作られた

曲中の話し声は当時のパートナーLisaをDan the Automatorのスタジオで録音し、指示を詰めずに話してもらったものから選ばれた。声は歌詞を説明するナレーションではなく、断片を選ぶことで曲内の人物と空間を作る。

ここから、Shadowのサンプリングを「他人のレコードだけで作る方法」と定義しない。自分たちで録音した現在も、直後に切断・選択され、記憶素材へ変わる。

### 4.5 ピッチ変更は音色処理と調律を兼ねる

Björkの断片は大幅に速度を落とし、既にあったドラムの感情へ接続した。終盤では、元から同じ音構造を持たないヴィブラフォンをフルートへ合うように曲げたと説明している。

ここでは速度、ピッチ、長さを別ノブとして扱えない。速度変更が、音高、音価、質感、情動、録音空間を同時に変える。その変化後の素材を別素材と調律し、一つのsceneへ置く。

### 4.6 インスト曲は「ラッパー待ちのビート」ではない

Shadowは、ボーカリストを必要とする未完成ビートではなく、インストゥルメンタルだけで注意を保ち、発展するarrangementを作ること自体を課題にしたと説明している。

“Mutual Slump”では、四小節または八小節ごとの変化、bridge、抽象化する区間、拍子変化を置いた。終盤のサックスでは針を持ち上げ、ほぼランダムな位置へ落とす操作も使った。ここから、scene transitionは整然としたクリップ切替だけでなく、制御された構成の中へ局所的な不確定操作を入れることも含む。

## 5. 作曲を記述する五つの役割

サンプル元のジャンルではなく、曲中での働きを記録する。

```text
FRAGMENT_ROLE = {
  PULSE,
  FRAME,
  BODY,
  VOICE,
  RUPTURE
}
```

### PULSE

拍、細分、歩行速度、反復の重心を作る。ドラムだけに限定しない。ベースや反復音型もPULSEになりうる。

### FRAME

曲が存在する場所、年代、空気、遠近を作る。ノイズ、残響、持続音、語りの背景を含む。

### BODY

一回性のある演奏身体を残す。ドラムフィル、ベースの滑り、声の息、ギターのアタックなど、完全に部品化すると失われる運動を保持する。

### VOICE

言葉の意味、発音、人物、引用元の認識によって、曲内に視点を作る。歌声、インタビュー、私的録音、カウントを含む。

### RUPTURE

現在の反復を破り、別の局面へ移す。クラッシュ、停止、別ブレイク、極端な帯域変化、認識可能な引用など。

一つの断片は曲中で役割を変更できる。分析では`source_id`と`role`を別フィールドにする。

## 6. Shadow固有の時間構造

### 6.1 Loop time

短い反復が現在の場を固定する。ただし完成伴奏として最後まで放置しない。

### 6.2 Scene time

断片の追加、除去、役割変更によって局面が進む。小節数より、何が前景を引き受けたかを記録する。

### 6.3 Excavation time

異なる年代、地域、媒体の録音が同時に鳴ることで、一つの現在に複数の過去が残る。単なるヴィンテージ音色ではなく、録音ごとの空間差を保持する。

### 6.4 Decision time

制約下でバウンスと確定を繰り返した制作判断の履歴。聴き手には直接見えないが、曲が過剰な可逆編集へ溶けず、局面ごとに形を持つ条件になる。

### 6.5 Return time

以前の断片が戻っても、曲全体は初期状態へ戻らない。戻った断片は、途中の出来事を経た後の記憶として聞こえる可能性がある。

## 7. 曲別分析コーパス

現段階では音源測定前の構成仮説である。次の順序で版と音源を固定する。

| 優先 | 曲 | 調べる中心 | 主な反証対象 |
| --- | --- | --- | --- |
| A | “Mutual Slump” | 同一断片の引用／再構成、私的声、認識可能性 | 素材列挙だけで構成を説明できるか |
| A | “Stem / Long Stem” | 長尺局面、前景交替、回帰 | 単一ループへのオーバーダブだけか |
| A | “Napalm Brain / Scatter Brain” | 密度、速度感、崩壊 | BPM変化だけで知覚を説明できるか |
| A | “Midnight in a Perfect World” | loop、beat、声、遠近、情動 | 単一主旋律中心の曲か |
| A | “Six Days” | 完成判断、循環、曲中の視点 | 通常のverse／chorusだけか |
| B | “Building Steam with a Grain of Salt” | 固定frame上の役割追加・除去 | 単純な累積構成か |
| B | “The Number Song” | 複数ブレイク、カウント、速度知覚 | ブレイクのメドレーに留まるか |
| B | “Organ Donor” | 最小素材とDJ身体 | 長尺作品と別原理か |
| B | “Monosylabik” | 一素材の極端な変形可能性 | 素材量と複雑さが比例するか |
| B | “Blood on the Motorway” | 声、事故、長尺物語、セクション境界 | 音色変化だけの組曲か |
| C | “Nobody Speak” | MCのための余白とプロデューサー構成 | Shadow単独の全空間占有との差 |
| C | “Ozone Scraper” | 現代的音響と移動感 | 初期作の手法へ回帰しているだけか |

### “Midnight in a Perfect World”の固定点

本人の回顧では、主サンプルをMPC所有初期に発見し、ビートを本人自身でも再現できない方法で反転・加工し、後にループとビートを結合した。ここから、完成音をレシピへ還元できない点も記録する。

Sound Labへ移す場合も、操作結果をプリセット名へ固定するのでなく、演奏履歴からしか到達できない状態を許す必要がある。ただし再現不能を不具合と混同しないため、状態記録と音声記録を分ける。

### “Six Days”の固定点

本人は、曲の開始から終了まで多数の判断が連鎖し、配置やミックスを一つも変更したくない状態へ初めて到達したと説明する。

これは「AIが自動的に最適化する完成度」ではない。作者が各判断を引き受け、止める時点を選ぶことが中心にある。

## 8. 音源分析モデル

`research/20260902-parallel-music-analysis`のSOURCE / EVENT / RELATIONを、Shadow用に次へ拡張する。

### 8.1 Source fragment

```text
SHADOW_FRAGMENT = (
  source_id,
  recording_identity,
  edition_or_master,
  source_interval,
  acquisition_route,
  source_space,
  source_noise,
  recognition_level,
  processing_hypothesis,
  rights_boundary,
  confidence
)
```

`recognition_level`は、聴き手に引用元が分かることを失敗とせず、構成上の変数として扱う。

### 8.2 Role event

```text
ROLE_EVENT = (
  absolute_time,
  fragment_id,
  role,
  foreground_level,
  rhythmic_function,
  spatial_function,
  entry_type,
  exit_type,
  transform,
  return_reference,
  confidence
)
```

### 8.3 Scene transition

```text
SCENE_TRANSITION = (
  from_scene,
  to_scene,
  retained_roles,
  removed_roles,
  new_roles,
  reassigned_fragments,
  transition_duration,
  clock_continuity,
  spatial_continuity,
  return_condition
)
```

## 9. 測定計画

### 9.1 版の固定

- アルバム、シングル、リミックス、デラックス版、リマスターを分ける
- source ID、取得経路、尺、sample rate、hashを保存する
- 30秒プレビューはフル尺構成の証拠にしない
- 著作権音源本体をGitへ保存しない

### 9.2 構成境界

- novelty curve
- spectral flux
- self-similarity matrix
- loudness envelope
- low／mid／high帯域の前景交替
- speech／voice区間
- drum density
- stereo widthと左右相関

自動境界は候補として保存し、人手でrole eventとscene transitionを注釈する。

### 9.3 サンプル整列

合法的に比較可能な原音がある場合だけ、次を使う。

- chroma／MFCCによる粗い候補
- tempo／pitch変形を許したsubsequence alignment
- onset列と包絡の局所照合
- 聴取による開始・終了の再確認

音源同定データベースの記述だけから、加工率や使用区間を捏造しない。

### 9.4 反証用変形版

1. scene境界を保ち、断片だけ交換
2. 断片を保ち、scene境界を均等化
3. 全sceneを同じ一小節頭へ回帰
4. 前景交替をなくし、全層を常時鳴らす
5. RUPTUREを削除
6. FRAMEのノイズと残響だけ削除
7. BODY断片を個別ワンショットへ分解
8. 認識可能な引用だけ匿名断片へ交換
9. 断片の役割変更を禁止
10. 元のscene順を保ち、transition durationだけ短縮

同じ素材があってもShadow的構成が失われる条件を調べる。似た音を作ることより、仮説を壊すことを優先する。

## 10. 他研究本文との接続

今回、Gitから次の本文を取得した。

| 研究 | ref | blob SHA | 接続状態 |
| --- | --- | --- | --- |
| J Dilla | `origin/research/20260902-j-dilla` | `fb32ed2b1eb7d6c485e7e3261b29449ea1f48f71` | 本文取得 |
| Madlib | `origin/research/20260902-madlib` | `c43fef90388f86766e4862f6f678ed238928f540` | 本文取得 |
| Portishead | `origin/research/20260902-portishead` | `36116426fb096bbd9f599574eb9bd54c4d296c1f` | 本文取得 |
| Autechre | `origin/research/20260831-autechre` | `c57156415879d6ce6ee49511b9586182b26e55d0` | 本文取得 |
| 並行音楽分析 | `origin/research/20260902-parallel-music-analysis` | `a4416da621020d7f32eb41197f8f1ede40572587` | 本文取得 |

blob SHAは取得内容の同一性だけを表し、仮説の正しさやmain統合を証明しない。

### J Dillaとの差

J Dilla研究は、安定層を残しながらキック、スネア、ハイハット、ベース、サンプルが異なる細分・位相・周期を持つ可能性を中心に置く。

Shadowは、一拍内部のtiming shapeだけでなく、複数小節から曲全体にわたるroleとsceneの交替を中心に置く。

```text
Dilla: voices disagree inside time
Shadow: recorded worlds change roles across time
```

この対比は排他的ではない。Shadowのドラムにも声部間差があり、Dillaにも場面転換がある。主解析変数を区別するための仮説である。

### Madlibとの差

Madlib研究はHuman Time、Loop Lock、Montage Time、Selection Timeを分け、短い未解決ループ、制作速度、場面交換、仮想演奏者を扱う。

Shadowとの近接点は、異なる録音時間の接続と、レコード探索が作曲に組み込まれる点にある。差は現在次のように仮定する。

| Madlib | DJ Shadow |
| --- | --- |
| 初回性と速度を残す | 多数の判断を長尺構成へ固定する |
| 短い未解決ループを保持する | ループの役割を曲中で変える |
| 人格・名義・架空バンドを増殖させる | 一つの作者が異なる録音世界を構成する |
| 場面交換の縫い目を残しうる | transition自体を劇的な事件として設計する |

この差は音源比較前の仮説である。

### Portisheadとの差

Portishead研究は、自分たちの演奏を録音し、媒体化し、摩耗・切断・反復した上で、Beth Gibbonsの不可逆な現在と対置する構造を中心に置く。

Shadowも私的録音や自作素材をサンプル化するが、現在の中心は歌手の身体との対立ではなく、断片間の役割交替と場面構成にある。

- Portishead: 演奏を架空の過去へ加工し、現在の声と衝突させる
- Shadow: 異なる過去と現在の録音を同一曲内の複数役割へ再配置する

### Autechreとの差

Autechre研究では、反復の正本が音声列から関係、状態遷移、演奏経路へ移る仮説を立てている。

Shadowの公開録音は再生ごとに同じ構成を返す。その意味ではopen-ended systemではない。ただし作曲工程では、断片の役割とscene transitionを連続判断している。

Sound Labへ移す場合、Shadowの完成録音を模倣せず、role reassignmentとscene transitionを現在形の演奏操作へ変換できるかが接点になる。

### DJ Premierとの接続境界

この更新時点で、`sound-lab`のremote branchからDJ Premier専用研究本文は取得できなかった。したがって「MCの句読点」「硬質なチョップ」等の一般的比較をGit正本の結論として取り込まない。専用研究本文が保存された後、同じサンプル断片がMCのための空白と長尺sceneでどう異なるかを比較する。

## 11. Sound Labへの研究候補

以下は製品採用済みではない。既存の4トラック、Skulptur、明示録音、独立DRUMの判断を変更しない。

### 11.1 Role reassignment

録音断片をトラックへ固定せず、同じ素材の役割を演奏中に切り替える。

- PULSE: 拍の基準
- FRAME: 空間と持続
- BODY: 一回性のある動き
- VOICE: 視点と句読
- RUPTURE: 局面転換

役割変更は音色プリセットの切替ではない。再生方法、前景、密度、空間、回帰条件をまとめて変える事件である。

### 11.2 Scene memory

完成ループを保存する代わりに、現在のsceneを次の関係として保持する。

```text
SCENE = {
  active_fragments,
  roles,
  foreground,
  clock_relations,
  spatial_relations,
  return_references
}
```

次sceneへ移るとき、全状態を入れ替えず、保持する関係と変更する関係を演奏者が選ぶ。

### 11.3 Gesture transition

三点以上のマルチタッチを「同時に多数ノブを動かす」ために使わない。

- 一本目: 現在sceneを保持
- 二本目: 一つの断片を前景へ引き出す
- 三本目: その断片の役割変更または新sceneへの移行を準備
- 指を離す: 全体停止ではなく、局所回帰またはtransition確定

これはmapping候補であり、iPhone実機の遮蔽、誤接触、遅延を未検証である。

### 11.4 Destructive decision without destructive audio

Shadowの制約から、判断を確定する速度を移す。ただしRAW音声を破壊しない。

- 元音声は保持する
- 演奏状態では使用候補を意図的に限定する
- scene確定後、無限undoで判断を溶かさない
- Performance Takeには判断履歴を保存する
- 後でRAWへ戻れることと、演奏中に決断することを両立させる

### 11.5 Unindexed self-crate

既成サンプル集を選ぶのではなく、自分が直前に録音した音から短い候補を残す。

ただし自動で「最良ループ」を選び完成伴奏を作らない。

- 候補は少数
- 音源名より、録音時刻と状況を残す
- 演奏者が現在の不足に応じて役割を与える
- 一度採用した断片も別役割へ再発見できる

### 11.6 Recognizable fragment

既知の素材を使うことそのものは製品機能にしない。自作素材の中で、すでに聴き手が覚えた断片を再登場させることで、認識可能性を構成変数にする。

これは外部著作物の無許諾収録を必要としない。

## 12. 採用しない点

- “DJ Shadow mode”という音色プリセット
- レコードノイズ、低いBPM、短調ピアノを組み合わせたジャンル模倣
- 希少盤の所有量を創造性の指標にすること
- 長い完成ループを自動生成し、演奏者がミュートするだけの構造
- MPC60の量子化、ビット深度、フィルターだけを模倣してShadow的と呼ぶこと
- 全素材を常時鳴らし、足し算だけで展開を作ること
- scene切替を既製のfillボタンにすること
- AIが「最良のサンプル」と「最良の構成」を自動選択すること
- サンプル・クリアランス問題を、発見されにくい音源を使うことで回避する設計
- 著作権音源を研究リポジトリへ保存すること
- Shadow研究だけを根拠に、Skulptur主演奏面や4トラック中心を置き換えること

## 13. バイアス検査

### `Endtroducing.....`中心主義

代表作を入口にするが、それ以後を劣化または逸脱として扱わない。MPC中心からDAW、演奏家、MC、全インスト構成へ移る変化自体を研究対象にする。

### レア盤フェティシズム

希少性は発見経路の一部であって、曲中の機能を保証しない。認識可能なBjörkの断片を意図的に使った事例は「希少であるほど良い」という説明への反例になる。

### 機材決定論

13秒制約は重要だが、同じMPC60を使えば同じ長尺構成になるわけではない。機材、判断、素材、録音、編集、権利条件を分ける。

### シネマティックという空語

「映画的」で説明を止めない。scene境界、視点、前景交替、transition duration、再登場、空間差として測定可能な仮説へ分解する。

### trip-hopという外部分類

Shadow本人はヒップホップを自分があらゆる音楽を見る基準として説明している。同時に一ジャンルへ自分を制限しないとも述べる。分類名を消さないが、作曲原理の代わりにしない。

### 完成作品からの逆算

完成録音の精密さから、制作中にすべてを先に設計していたと推定しない。“Mutual Slump”の記録店での偶然や、私的録音からの選択を残す。

## 14. ガバナンス境界

- 本研究は調査・分析記録であり、製品仕様の承認ではない。
- ユーザーの「gitに保存しながら」は、この研究本文のcommitと通常pushを許可する。PR作成、merge、`main`反映は含まない。
- 製品コードと`integration/`は変更しない。
- 公開資料からの短い引用は必要最小限とし、本文は要約と分析で記録する。
- 音源本体をGitへ保存しない。
- 音源分析を行う場合、版、取得経路、区間、hash、合法的利用境界を記録する。
- 聴感、本人発言、外部記事、信号測定、本研究の推論を別の証拠種として保つ。
- ブランチへのpushはPR作成、merge、main統合、製品採用を意味しない。

## 15. 未検証事項

1. `Endtroducing.....`各版、シングル版、リマスター版の録音同一性。
2. “Mutual Slump”のsource alignmentとrole event注釈。
3. “Stem / Long Stem”のscene境界、retained role、return condition。
4. “Napalm Brain / Scatter Brain”の実BPM、倍テン知覚、密度変化の寄与分離。
5. “Midnight in a Perfect World”のbeat加工と本人が再現不能とした工程の観測可能範囲。
6. “Six Days”の構成判断と通常のverse／chorusモデルとの差。
7. “Monosylabik”で一素材から生成されたイベントの範囲。
8. `The Outsider`のBay Area／hyphy接続を、逸脱史観なしに一次資料から再構成すること。
9. `The Mountain Will Fall`以後のAbleton／DAW、演奏家、自作音源、サンプルの割合と役割。
10. `Action Adventure`各曲の全空間占有と、初期二作のインスト構成との差。
11. ライブでShadowが完成曲をどの程度分解し、ターンテーブル、サンプラー、映像へ再配分するか。
12. Cut Chemistとの`Brainfreeze`／`The Hard Sell`で、選曲と即時操作がスタジオ長尺構成へどう接続するか。
13. サンプル権利持分が制作判断へ与えた曲単位の影響。
14. DJ Premier専用研究本文のGit取得と主張単位比較。
15. Massive Attack、Dub、This Heat、Can／Conny Plank各研究本文との接続。
16. role reassignmentをiPhoneで説明なしに演奏できるか。
17. 三点以上の接触でscene保持、前景化、transitionを同時に扱えるか。
18. scene memoryが新しいDAWのscene launcherへ収束しないか。

## 16. 次の研究工程

1. “Mutual Slump”を最初の注釈対象として、本人解説と録音のイベントを対応させる。
2. “Stem / Long Stem”をscene transitionモデルで記述し、単純な足し算構成説を反証する。
3. “Midnight in a Perfect World”と“Six Days”を比較し、loop中心とsongwriting中心の差を取る。
4. `The Outsider`をBay Areaの地域史と本人発言から研究し、`Endtroducing.....`中心史を崩す。
5. `Action Adventure`を同じROLE / SCENE形式で注釈し、過去回帰説を検証する。
6. DJ Premier、Massive Attack、Dub、This Heat、Can／Conny PlankのGit本文を取得して接続する。
7. 実装へ進む前に、Role reassignment、Scene memory、Gesture transitionから一項目だけを試作候補として提示する。

## 17. 触る実装パス

なし。今回の変更は次の研究記録のみ。

- `research/20260902-dj-shadow/README.md`

## 18. Git状態境界

このREADMEは次を証明しない。

- DJ Shadowの全作品を分析したこと
- フル尺PCMを解析したこと
- 全サンプル元、加工法、権利状態を確定したこと
- ROLE / SCENEモデルが実証されたこと
- Sound Labへ製品採用されたこと
- 製品コードへ実装されたこと
- iPhoneで演奏可能と確認されたこと
- mainへ統合されたこと

## 19. 長尺二曲の版固定

今回の追補では、長尺構成の仮説を聴感印象のまま進めず、まず分析対象の版を分離する。

### 19.1 取得した版情報

現行Spotify表示では、次の単位になっている。

| 対象 | 表示時間 | 分析上の扱い |
| --- | ---: | --- |
| “Stem / Long Stem – Medley” | 7:47 | 主分析対象 |
| “Transmission 2” | 1:29 | 主曲から分離する |
| “Napalm Brain / Scatter Brain – Medley” | 9:21 | 主分析対象 |

一方、CD資料には“Stem / Long Stem / Transmission 2”を一つの約9分台トラックとして表示する版がある。したがって、曲長だけを比較するときも、Transmissionの結合状態を記録する。

公式20周年版`Endtrospective`の追加ディスクには、次の別形態がある。

- “Stem – Cops ’N’ Robbers Mix”
- “Napalm Brain – Original Demo Beat”

公式販売ページは収録名を確認できる。Qobuzのデラックス版メタデータでは“Napalm Brain (Demo Beat)”は0:34と表示される。現時点では、この34秒が完成版の直接の起点か、後年に選ばれた一断片かを確定しない。

### 19.2 版を混ぜないための訂正

2022年の本人回顧で、映画`Heat`のVHSを借りてサンプルしたと説明される対象は、明確に“the seven-inch mix of Stem”である。

したがって本研究では、次を分ける。

- アルバム版“Stem / Long Stem”
- 7インチ版“Stem”
- “Stem – Cops ’N’ Robbers Mix”
- “Transmission 2”の結合版／分離版

映画台詞の使用をアルバム版の事実として一般化しない。サンプル元が似ていても、版ごとの配置と役割が同じとはみなさない。

### 19.3 追補資料

11. DJ Shadow official store, `Endtroducing (20th Anniversary Endtrospective Edition)`
    https://djshadow.com/products/endtroducing-20th-anniversary-endtrospective-edition-3cd-deluxe-digipack
12. Spotify, `Endtroducing.....` album page
    https://open.spotify.com/embed/album/4tUVkNYSFrrEqqrxBQW9PN
13. Qobuz, `Endtroducing (Deluxe Edition)`
    https://www.qobuz.com/jp-ja/album/endtroducing-dj-shadow/gj94mf6b5hfgb
14. Nate Patrin, `Total Breakdown: Hidden Transmissions From The MPC Era, 1992–1996`, *Pitchfork*, 2012
    https://pitchfork.com/reviews/albums/17145-total-breakdown-hidden-transmissions-from-the-mpc-era-1992-1996/

## 20. 「長いループ」から「短い核を長い時間へ写像する」へ

前節までのROLE / SCENE仮説を、次の二段階モデルへ更新する。

### Stage A: seed

短い断片または短いビートが、局所的な同一性を作る。

```text
SEED = {pulse_candidate, timbre_signature, gesture, source_memory}
```

ここではまだ曲の長さも場面数も決まらない。seedが良いことと、長尺曲になることは同じではない。

### Stage B: temporal scaling

seedを単に長く反復せず、役割、密度、空間、前景、回帰条件を時間上で変える。

```text
LONG_FORM = map(SEED, ROLE_EVENT[], SCENE_TRANSITION[], RETURN_CONDITION[])
```

長尺化の評価対象は素材数ではなく、次の差分である。

- 同じseedが別役割へ移るか
- 新しい素材が既存sceneを強化するか、破るか
- 境界で拍の基準が変わるか
- 前景と背景が交換されるか
- 終端で全素材が同時に止まるか、残存物へ縮退するか

James Lavelleは制作依頼を回顧して、verse／chorusを心配せず音を押し進めること、Pink FloydやBeethovenのような大きなsoundscapeを考えていたと述べる。これは個々の曲の編集工程を証明しないが、長尺形式を通常の歌形式だけで測らない歴史的根拠にはなる。

Pitchforkの初期MPC資料評は、一部の短いスケッチを、興味深いループが展開せず尽きるものとして区別し、初期のドラムロールに後の“Napalm Brain / Scatter Brain”のcrescendoの予兆を読む。二次批評ではあるが、seedの存在だけでは完成長尺曲にならないという比較対象を与える。

## 21. 曲別の検証仮説

以下は音源の時刻注釈前の仮説であり、確定した構成表ではない。

### 21.1 “Stem / Long Stem”

検証する仮説は、二つの題名が二つの独立曲を機械的に連結したことではなく、保持される役割と交換される役割の組合せで連続性を作ることである。

主な問い:

1. `Stem -> Long Stem`で保持されるのはPULSE、FRAME、音色署名、空間、gestureのどれか。
2. 境界は瞬間切替か、複数要素が別々の時刻で移る分散遷移か。
3. 後半が前半の素材を再提示する場合、同じ役割で戻るか、記憶として戻るか。
4. “Transmission 2”は曲内sceneではなく、アルバム階層のframeとして分離できるか。
5. 7インチ版の映画台詞はscene境界を補強するのか、別の物語層を追加するのか。

暫定的な反証:

- 前後半で役割、前景、拍基準、空間に有意な差がない
- 境界と呼んだ箇所が単なる短いfillにすぎない
- 別mix間の差が音量または尺だけで、構成機能が変わらない

### 21.2 “Napalm Brain / Scatter Brain”

ここでは「テンポが徐々に上がる曲」という要約を出発点にしない。BPM変化、イベント密度、細分化、ドラムロール、前景交替は分けて測る。

主な問い:

1. 物理的BPMは変化するか。それとも同じ拍上で細分イベントが増え、速く感じるのか。
2. crescendoは音量、帯域占有、同時発音数、ドラム密度のどれで作られるか。
3. `Napalm -> Scatter`は素材交替か、同じ素材の役割崩壊か。
4. 終盤は新sceneへの到着か、既存sceneのterminal reductionか。
5. 34秒のdemo beatにある要素のうち、完成版でPULSEとして保持されるもの、RUPTUREへ変わるもの、消えるものは何か。

暫定的な反証:

- 知覚上の加速を測定BPMの加速と誤認している
- 密度増加がscene変化ではなく、同一scene内の装飾にとどまる
- demo beatと完成版の同一性が題名以外に確認できない

## 22. SCENE境界の注釈プロトコル

### 22.1 必須メタデータ

```yaml
ANALYSIS_SOURCE:
  title:
  edition:
  service_or_medium:
  track_duration:
  transmission_split: true | false
  acquisition_date:
  file_hash: null
  legal_basis:
```

ストリーミング聴取だけなら`file_hash`は`null`とし、PCM解析済みと書かない。

### 22.2 境界候補

境界時刻`t`で、前後8秒を比較する。次のうち二項目以上が変化した場合だけ、scene候補にする。

| 変数 | 観測 |
| --- | --- |
| `pulse_source` | 拍の基準となる音の交替 |
| `foreground_role` | 前景役割の交替 |
| `event_density` | 単位時間当たりの主要イベント数 |
| `spectral_occupancy` | 低・中・高域の占有変化 |
| `space_signature` | 残響、距離、モノ／ステレオ感の不連続 |
| `motif_state` | 導入、継続、欠落、変形、回帰 |
| `rupture` | cut、drop、roll、scrub、無音など |

### 22.3 瞬間境界と分散境界

`SCENE_TRANSITION`へ次を追加する。

```yaml
transition_shape: hard | overlap | dissolve | distributed
onset_first_change:
onset_last_change:
transition_duration:
retained_roles: []
reassigned_roles: []
```

一つのタイムスタンプへ無理に圧縮しない。たとえばPULSEが先に変わり、FRAMEが残り、VOICEが後から入るなら`distributed`として開始と終了を持つ。

### 22.4 独立注釈

最初の試行では、二名が曲名以外の事前説明を共有せず境界候補を付ける。

- 境界時刻が±2秒以内で一致: 強い候補
- 2秒を超えてずれるが同じ変数群を指す: 分散遷移候補
- 一方だけが指す: 弱い候補
- 題名上の`/`位置を先に教えない

一致率を高く見せるために許容幅を後から変更しない。

## 23. 長尺構成の測定値

単なるscene数ではなく、次を曲ごとに記録する。

```text
retention_ratio = 境界をまたいで保持された役割数 / 境界前の役割数
reassignment_count = 同一断片が別役割へ移った回数
return_distance = 断片の消失から再登場までの時間
transition_spread = 最初の変化から最後の変化までの秒数
terminal_reduction = 終盤で残る役割数 / 最大同時役割数
```

これらはShadowらしさの点数ではない。二曲の長尺化が同じ方法か、別方法かを比較するための記述量である。

予測:

- “Stem / Long Stem”は`retention_ratio`と`transition_spread`が主要差分になる可能性がある。
- “Napalm Brain / Scatter Brain”は`event_density`、`reassignment_count`、`terminal_reduction`が主要差分になる可能性がある。

この予測は実測前なので、逆の結果でも失敗ではない。逆ならROLE / SCENEモデルの曲別適用を狭める。

## 24. Sound Labへの限定的含意

今回の追補から新しいエフェクトや“DJ Shadowモード”は採用しない。候補を一つに絞るなら、`transition spread`を演奏可能にすることが先である。

### Transition Spread Gesture

一つのgestureで全要素をscene Bへ切り替えず、役割ごとに遷移時刻をずらす。

```yaml
GESTURE:
  source_scene: A
  target_scene: B
  spread: 0.0..1.0
  retained_roles: [FRAME]
  early_roles: [PULSE]
  late_roles: [VOICE]
  rupture_policy: manual
```

設計条件:

- `spread = 0`ではhard cut
- 値を上げると、PULSE、BODY、VOICEなどが異なる時刻で移る
- FRAMEを保持する選択がある
- いつでも現在状態をsceneとして採取できる
- AIは移行先や最適な順序を自動決定しない
- iPhoneで一つの連続gestureとして扱えることを、実装前に紙上／低忠実度で検証する

これは既存の`Gesture transition`を精密化する研究候補であり、製品仕様の承認ではない。

## 25. 更新後の未解決事項

1. 公式20周年版の各別形態と分析対象版を同一取得条件で聴取できていない。
2. “Napalm Brain – Original Demo Beat”と完成版の系譜は題名以外未確認。
3. “Stem / Long Stem”の題名境界と音響上の境界が一致するか未確認。
4. 二曲の物理BPM、拍知覚、イベント密度を分離測定していない。
5. `transition_spread`の変数が実際の聴取境界を十分説明するか未検証。
6. 二名独立注釈を実施していない。
7. 音源版のhashを取得していない。
8. Sound Lab上のgesture試作、iPhone操作検証、製品採用は行っていない。

## 26. 次の研究工程

1. 合法的に取得可能な同一版を固定し、曲長、媒体、Transmission分離、hashを記録する。
2. “Stem / Long Stem”を二名で独立注釈し、hard／distributed境界を比較する。
3. “Napalm Brain / Scatter Brain”でBPM、イベント密度、音量、帯域占有を分離する。
4. 34秒demo beatと完成版の共通イベントを、題名に依存せず照合する。
5. 結果がROLE / SCENE仮説を支持しない場合、その曲への適用を撤回または限定する。
6. 研究結果が揃うまで製品コードと`integration/`を変更しない。

## 27. 今回の証拠状態

- 文献探索: 実施
- 本人発言による版限定: 確認
- 公式20周年版の別形態収録: 確認
- 現行配信上の曲分割と表示時間: 確認
- フル尺音源取得: 未実施
- 音響信号測定: 未実施
- scene時刻注釈: 未実施
- 仮説の実証: 未完了
- 製品実装: 未実施
- PR作成／main統合: 対象外

## 28. Shazam経由の実信号取得

### 28.1 以前の未実施状態を更新する

前節までの「フル尺音源取得／音響信号測定／scene時刻注釈は未実施」は、フル尺とscene注釈については現在も有効である。ただし、Shazamが返すApple Musicカタログの公式previewについて、音声バイト取得と30秒断片の測定を実施したため、「音響信号測定は全面的に未実施」という状態は失効した。

使用した経路は、Dub、Jeff Mills、Curtis Mayfield各研究で確立済みの次の経路である。

`Shazam searchmusic -> getsong / getalbum -> Apple Music公式preview URL -> AAC取得 -> 断片測定`

周囲で鳴っている音を認識する`recognizemusic`は使用していない。Shazamは曲名、版、Apple Music ID、ISRC、カタログ尺、preview URLの取得面であり、以下の音響特徴をShazamが解析したわけではない。

### 28.2 固定した版

| 役割 | 曲／版 | Apple Music song ID | ISRC | カタログ尺 |
| --- | --- | ---: | --- | ---: |
| 主対象 | “Stem / Long Stem (Medley)” — `Endtroducing.....` | `1660486400` | `GBAQH9600069` | 467.373秒 |
| 主対象 | “Napalm Brain / Scatter Brain (Medley)” — `Endtroducing.....` | `1660486425` | `GBAQH9600072` | 561.360秒 |
| 比較 | “Stem (Cops 'n' Robbers)” — Deluxe Edition | `1660367654` | `GBAQH9601074` | 228.640秒 |
| 比較 | “Napalm Brain (Demo Beat)” — Deluxe Edition | `1660368000` | `GBAQH0500006` | 34.800秒 |
| 版照合 | “Stem / Long Stem / Transmission 2” — Deluxe Edition | `1660367323` | `GBAQH0500010` | 562.253秒 |
| 版照合 | “Napalm Brain / Scatter Brain (Medley)” — Deluxe Edition | `1660367643` | `GBAQH9600072` | 563.827秒 |

Apple Music JP:

- https://music.apple.com/jp/album/stem-long-stem-medley/1660485817?i=1660486400
- https://music.apple.com/jp/album/napalm-brain-scatter-brain-medley/1660485817?i=1660486425
- https://music.apple.com/jp/album/stem-cops-n-robbers/1660367299?i=1660367654
- https://music.apple.com/jp/album/napalm-brain-demo-beat/1660367299?i=1660368000
- https://music.apple.com/jp/album/stem-long-stem-transmission-2/1660367299?i=1660367323
- https://music.apple.com/jp/album/napalm-brain-scatter-brain-medley/1660367299?i=1660367643

現行版とDeluxe版の“Napalm Brain / Scatter Brain”は同一ISRCだが、カタログ尺には2.467秒差がある。同一ISRCを同一ファイルまたは同一masterの証明にはしない。

### 28.3 取得音声

六版のApple Music公式previewからAACを取得した。全ファイルは44.1 kHz、stereo。長尺五版のcontainer尺は30.000秒、34.800秒のdemo曲から返ったpreviewは30.017秒だった。音源ファイルそのものはGitへ保存しない。

| 断片 | SHA-256 |
| --- | --- |
| Stem / Long Stem | `12f10578146558fd2e15d8342314b8f1a155481522ec514e40887c77d00264a7` |
| Napalm Brain / Scatter Brain | `ba0146f68a8c7b607099ea9fd14e357c5adadcee40cd4caff839f7dad985f0d6` |
| Stem (Cops 'n' Robbers) | `317551ae1ad70813f818fbe1ae7c7a4e101cf36c3ef1980e88444f916d3f9b29` |
| Napalm Brain (Demo Beat) | `569081e4baf04d428a4ac4874c45ce5e74c0487177d9022b3260af430c3604d5` |
| Stem / Long Stem / Transmission 2 — Deluxe | `1d35fb8cf78b41d9bd2f1163f38c1925fe46dfd86eaf29a22d891092da3ed1c2` |
| Napalm Brain / Scatter Brain — Deluxe | `36f63de0f650f59473547aac5fe59dcc671c7d22926204575ffb8e5a31be3dc2` |

長尺曲のpreview開始位置はカタログ応答に含まれない。したがって以下の測定を、導入、曲中盤、題名上の境界、終盤の代表として扱わない。

### 28.4 校正済み抽出器による30秒断片測定

Jeff Mills研究で使用した抽出器と校正器を同じ条件で実行した。合成信号による校正は12項目中12項目が通過した。周期候補は人間の聴く拍を自動確定せず、倍／半分を含む候補列として残す。

| 断片 | RMS | centroid | onset/s | median IOI | 強い周期候補 |
| --- | ---: | ---: | ---: | ---: | --- |
| Stem / Long Stem | -19.64 dBFS | 2796.1 Hz | 8.340 | 0.1045秒 | 108.80, 191.41, 219.91, 145.58 |
| Stem (Cops 'n' Robbers) | -17.22 dBFS | 2336.1 Hz | 8.540 | 0.1103秒 | 161.50, 191.41, 109.96, 106.56 |
| Stem / Long Stem / Transmission 2 — Deluxe | -18.73 dBFS | 2582.1 Hz | 8.507 | 0.1103秒 | 105.47, 108.80, 219.91, 191.41 |
| Napalm Brain / Scatter Brain | -14.49 dBFS | 2613.0 Hz | 4.971 | 0.1219秒 | 71.78, 143.55 |
| Napalm Brain (Demo Beat) | -14.59 dBFS | 2532.6 Hz | 7.373 | 0.1103秒 | 73.30, 145.58, 58.07, 98.44 |
| Napalm Brain / Scatter Brain — Deluxe | -13.79 dBFS | 2571.2 Hz | 5.271 | 0.1161秒 | 71.78, 143.55 |

ここでの`onset/s`は同じ抽出器内の比較量であり、打音数、ノート数、演奏密度そのものではない。

### 28.5 現行版previewとDeluxe版previewの照合

未知位置のpreview同士を±2秒で整列し、onset包絡、RMS包絡、周期profile、四帯域profileを比較した。

| 曲 | onset相関 | RMS相関 | 周期profile cosine | 帯域profile cosine |
| --- | ---: | ---: | ---: | ---: |
| Stem現行分離版 vs Deluxe結合版 | 0.9752 | 0.9986 | 0.9999 | 0.9999 |
| Napalm現行版 vs Deluxe版 | 0.9844 | 0.9961 | 0.9999 | 0.9997 |

二組ともpreview内ではほぼ同じ局所素材を返している。これは比較対象のpreview位置が大きくずれていないことを補強する。ただし、曲全体のmaster同一性、Transmission部分、2.467秒の尺差の原因は確定しない。

### 28.6 短縮版／demoとの探索的比較

次の比較量は校正済みの同一性判定器ではなく、競合仮説を絞る探索量である。

| 比較 | onset整列相関 | RMS整列相関 | 周期profile cosine | 帯域profile cosine |
| --- | ---: | ---: | ---: | ---: |
| Stem album vs Cops 'n' Robbers | 0.4175 | 0.5964 | 0.7424 | 0.9973 |
| Napalm final vs Demo Beat | 0.1323 | 0.3153 | 0.7829 | 0.8893 |

“Stem”の二版は30秒全体の帯域比が非常に近い一方、個々のonsetとRMS包絡は同一時系列としては中程度しか整列しない。少なくとも「同じ30秒ファイルを音量だけ変えた」とは扱えない。しかし、別の曲位置、別mix、編集差、codec差の寄与は分離していない。

“Napalm”完成版とdemoは、周期profileと大域帯域profileには類似が残るが、個々のイベント時系列は整列しない。この結果は「短いseedと完成版に粗い周期族が共有される可能性」には整合するが、demoが完成版の直接祖先であること、同じbreakであること、同じsceneを切り出したことは証明しない。

### 28.7 10秒窓で見えた局所変化

探索的な別抽出器で30秒を三つの約10秒窓へ分けた。

“Stem / Long Stem”のpreviewでは、20–150 Hzのエネルギー比が`0.4708 -> 0.0010 -> 0.0005`、150–1000 Hzが`0.5137 -> 0.9880 -> 0.9873`へ移った。RMSも`-14.07 -> -18.86 -> -18.87 dBFS`へ低下した。これは同じ30秒の内部で、低域の担い手と音量重心が大きく変わる直接測定である。原因となる楽器、sample、mix操作、曲全体のscene位置は未同定。

“Napalm Brain / Scatter Brain”のpreviewでは、RMSが`-15.59 -> -12.03 -> -9.31 dBFS`へ連続上昇した。一方、同じ抽出器のonset/sは`1.300 -> 2.300 -> 2.211`で、最後まで単調増加しなかった。したがって、このpreviewの強まりを「BPMが上がった」または「イベント数が増え続けた」だけで説明しない。低域比、帯域再配分、個々の打音の強度、重なりも競合説明として残る。

### 28.7.1 局所周期候補

校正済み抽出器を同じ三つの約10秒窓へ適用した。

| 断片 | 0–10秒 | 10–20秒 | 20–29.95秒 |
| --- | --- | --- | --- |
| Stem / Long Stem | 191.41, 145.58, 132.51, 161.50 | 108.80, 53.00, 70.79 | 107.67, 71.78, 53.55, 215.33 |
| Napalm Brain / Scatter Brain | 71.78, 73.30, 145.58, 156.61 | 72.79, 143.55 | 72.28, 143.55, 147.66 |

“Napalm Brain / Scatter Brain”では約72／144 BPMの周期族が三窓すべてに残る。よって、少なくとも取得した30秒内の強度上昇を、周期基準そのものが連続的に高速化した結果とは読まない。これは曲全体のBPM一定を証明せず、preview区間に限定した反証である。

“Stem / Long Stem”では、最初の窓の候補集合と後二窓の約108／54 BPM族が異なる。帯域比とRMSの大幅変化も同時にあるため、preview内部に周期役割を含む状態変化があるという候補は強まった。ただし曲名上の`Stem / Long Stem`境界との一致は未取得。

2秒窓、0.5秒hopでRMS、onset率、四帯域比の変化量を探索すると、最大候補は“Stem”でpreview内3.5秒、“Napalm”で4.5秒だった。この検出器は校正済みのscene認識器ではないため、時刻をscene境界として確定せず、再聴取用の弱い候補としてJSONにだけ残す。

### 28.8 ROLE / SCENE仮説の更新

実信号取得後、中心仮説を次のように狭める。

> Shadowの長尺化は、短いseedの単純延長ではない。ただし変化を直ちにscene数やテンポ上昇へ変換せず、まず帯域を担う役割、音量包絡、周期族、イベント時系列が別々に変わるものとして記述する。

今回の30秒断片は、二つの異なる変化型を示した。

- “Stem / Long Stem”: preview内部で低域占有とRMSが大きく落ち、別の帯域役割へ移る。
- “Napalm Brain / Scatter Brain”: preview内部でRMSは強まるが、onset率は最後まで増え続けない。

したがって`transition_spread`は「複数トラックが順番に切り替わる時間」だけでなく、`energy_role`、`pulse_role`、`foreground_role`が異なる時刻で変わる幅として定義し直す。

```yaml
transition_spread:
  first_changed_dimension:
  last_changed_dimension:
  energy_role_change:
  pulse_role_change:
  foreground_role_change:
  event_timeline_change:
```

### 28.9 保存物と未取得

Gitへ保存する:

- `preview-analysis-20260903.json` — カタログ、hash、全測定値、比較値、限界
- `tools/calibrate_analyzer.py` — 校正器
- `tools/analyze_previews.py` — 校正済み断片抽出器
- `tools/compare_shadow_previews.py` — 10秒窓と探索的版間比較

Gitへ保存しない:

- preview AAC本体
- デコードしたPCM
- Apple Music以外から取得した音源

現在も未取得:

- フル尺波形
- previewの曲内開始時刻
- “Stem / Long Stem”の題名境界
- “Napalm / Scatter”の題名境界
- 曲全体のtempo map
- 二名独立scene注釈
- sample単位の同一性
- 製品実装とiPhone実機検証

## 29. 次の研究工程

1. preview範囲の探索的境界候補は抽出済み。次は3.5秒／4.5秒候補の前後を別特徴量と聴取で検証する。
2. “Stem”二版の0.7314秒付近の最良lagがcodec遅延か編集差かを、波形ではなくイベント列で再検証する。
3. “Napalm”の約72／144 BPM周期族は三つの10秒窓で維持された。次は窓長変更への頑健性を調べる。
4. demoの30秒が34.8秒曲のどの部分か、preview URLだけでは解けない場合は未取得のまま保持する。
5. フル尺を取得できる権利経路が成立するまで、曲全体のscene図を確定しない。


## 30. 境界候補・周期族・版間lagの頑健性追補

### 30.1 方法

前節の2秒窓・0.5秒hopによる最大候補をscene境界とは認定せず、同じApple Music preview断片に対して次を再検証した。

- 境界窓長を1.0、1.5、2.0、3.0、4.0秒へ変更
- hopを0.25秒へ細分
- 既存候補の±1秒から局所peakを探索
- RMS、onset率、四帯域比の標準化差分を二乗し、変化量への寄与率を算出
- “Stem”二版を10秒区間ごとに別々に整列
- “Napalm”を6、8、10、12、15秒窓、50% overlapで周期候補抽出

入力AACのSHA-256は前節と照合し、三ファイルすべて一致した。校正器も再実行し、12項目中12項目が通過した。境界抽出そのものはscene認識器として校正されていない。

### 30.2 “Stem” 3.5秒候補

| 窓長 | 近傍peak | preview内順位 | percentile | 主な寄与 |
| ---: | ---: | ---: | ---: | --- |
| 1.0秒 | 3.50秒 | 7 | 94.8 | 20–150 Hz、150–1000 Hz、1000–6000 Hz |
| 1.5秒 | 3.50秒 | 6 | 95.6 | 20–150 Hz、150–1000 Hz、1000–6000 Hz |
| 2.0秒 | 3.50秒 | 2 | 99.1 | 1000–6000 Hz、6 kHz以上、20–150 Hz |
| 3.0秒 | 3.50秒 | 2 | 99.1 | onset率70.1%、1000–6000 Hz |
| 4.0秒 | 3.50秒 | 15 | 86.4 | 1000–6000 Hz、onset率、20–150 Hz |

時刻は五設定すべてで3.50秒に残ったが、強度は窓長依存であり、90 percentile以上は5設定中4設定だった。短い窓では帯域再配分、3秒窓ではonset率が支配する。よって「単一の音量cut」ではなく複数の測定次元が近接して変わる候補として保持するが、4秒窓で薄まるため強いscene境界とはまだ呼ばない。

### 30.3 “Napalm” 4.5秒候補

| 窓長 | 近傍peak | preview内順位 | percentile | 主な寄与 |
| ---: | ---: | ---: | ---: | --- |
| 1.0秒 | 4.25秒 | 1 | 100.0 | 150–1000 Hz、1000–6000 Hz、RMS |
| 1.5秒 | 3.75秒 | 1 | 100.0 | 150–1000 Hz、1000–6000 Hz |
| 2.0秒 | 4.25秒 | 1 | 100.0 | onset率、6 kHz以上、20–150 Hz |
| 3.0秒 | 5.00秒 | 5 | 96.3 | 150–1000 Hz、20–150 Hz、6 kHz以上 |
| 4.0秒 | 4.00秒 | 2 | 99.0 | 150–1000 Hz、20–150 Hz、6 kHz以上 |

五設定すべてで90 percentile以上だが、peak時刻は3.75–5.00秒へ広がり、中央値は4.25秒だった。これは瞬間境界の時刻精度ではなく、約1.25秒幅にわたる変化領域として読むべき結果である。寄与も窓長により帯域比とonset率の間で交替する。したがって、前回の「4.5秒」という一点は、`transition_spread`候補`3.75–5.00秒`へ改める。

### 30.4 “Stem”二版の0.7314秒lag

前回の30秒全体で得た+0.7314秒を固定遅延仮説として検査した。10秒区間別の最良lagは次のように一致しなかった。

| 区間 | onset包絡 | RMS包絡 |
| --- | ---: | ---: |
| 0–10秒 | +0.7314秒 | +0.7198秒 |
| 10–20秒 | -1.5209秒 | +1.2887秒 |
| 20–29.5秒 | +1.3003秒 | -1.2771秒 |

全体lagの+0.7314秒をonsetイベント列へ適用すると、album側99イベントのうち51.5%が50 ms以内、62.6%が100 ms以内でCops版イベントに近接した。ただし区間別lagは符号まで変わり、一定値を保持しない。

したがって、「同一時系列に一定のcodec遅延だけが加わった」という説明は今回の特徴列では支持されない。+0.7314秒は先頭10秒の類似が全体最適値を引いた可能性がある。編集差、異なるpreview位置、共通する局所イベントと異なる時系列の混在を残す。codec寄与を完全に否定するにはsample精度の同一波形対応が必要であり、今回は未取得である。

### 30.5 “Napalm”約72／144 BPM周期族

6、8、10、12、15秒の計23窓で検査した。

- 70–75 BPM候補を含む: 22/23窓、95.7%
- 140–150 BPM候補を含む: 20/23窓、87.0%
- どちらかを含む: 22/23窓、95.7%
- 例外: preview 0–6秒窓は97.51、76.56、215.33 BPM候補

窓長変更後も約72／144の倍半分関係は大部分で残った。したがって、取得preview内のRMS上昇を連続的な周期高速化で説明する仮説はさらに弱くなった。これは人間が感じる拍、曲全体のtempo map、`Napalm / Scatter`題名境界を確定しない。

### 30.6 仮説の更新

今回の結果から、境界を一点時刻へ圧縮する方法を狭める。

```yaml
boundary_candidate:
  time_region:
  persistence_across_window_lengths:
  dominant_dimensions_by_scale:
  periodicity_family_before_after:
  semantic_label: null
```

`semantic_label`は聴取、版内位置、独立注釈が揃うまで`null`にする。“Stem”は同一時刻に残るが長窓で弱まる候補、“Napalm”は強いが時刻幅を持つ候補であり、両者を同じhard cutとして扱わない。

### 30.7 保存物と次の工程

追加保存:

- `robustness-followup-20260903.json` — 全設定、特徴寄与、区間lag、周期候補
- `tools/robustness_followup.py` — 再現用解析

次に残る工程:

1. previewを実際に聴取できる経路で3.5秒と3.75–5.00秒を確認し、変化した前景役割を注釈する。
2. “Stem”二版の共通イベントを一対一対応へ絞り、局所的な編集単位を調べる。
3. フル尺の合法的取得経路が成立するまで題名境界と曲全体scene図は未確定に保つ。
4. preview内位置が不明のため、今回の時刻を曲頭からの時刻として転載しない。


## 31. “Stem”二版の一対一イベント対応

### 31.1 前回の問いを狭める

前節では、30秒全体の特徴包絡で得た+0.7314秒が10秒区間ごとには維持されず、一定codec遅延だけでは説明できないことを確認した。今回は、同じonset検出条件で得たalbum版99イベントとCops版98イベントを、順序を逆転させず、一つのイベントを一度だけ使う条件で照合した。

許容誤差は50 ms。イベント記述子は四帯域エネルギー比、正規化centroid、正規化RMSである。ただし対応そのものは時刻だけで決め、記述子cosineは対応後の粗い検査に限定した。

### 31.2 +0.7314秒では連続列が短い

| 指標 | 結果 |
| --- | ---: |
| 一対一対応 | 51組 |
| album側coverage | 51.5% |
| Cops側coverage | 52.0% |
| 残差中央値 | 0.0 ms |
| 残差90 percentile | 23.2 ms |
| 最長の連続event-index列 | 3イベント |
| 連続列のalbum範囲 | 7.7090–8.8468秒 |
| 連続列のCops範囲 | 8.4405–9.5898秒 |

0.0 msという中央値はsample同一を意味しない。解析hopが256 samples / 22.05 kHzで量子化され、+0.7314秒が約63 hopsに相当するためである。51組が近接しても、間に未対応イベントを挟まない連続列は最大3イベントしかない。したがって+0.7314秒を、二版を貫く一本の共通時系列とは扱わない。

### 31.3 ±2秒のlag探索

0.01秒刻みで-2.00〜+2.00秒を探索した。

| lag | 対応数 | 全対応の絶対残差合計 |
| ---: | ---: | ---: |
| +1.31秒 | 55 | 0.7760秒 |
| +1.32秒 | 55 | 1.1482秒 |
| +0.71秒 | 55 | 1.4707秒 |
| +1.30秒 | 53 | 0.5414秒 |
| +0.74秒 | 53 | 0.5990秒 |

最大対応数55を作るlagが+0.71、+1.31、+1.32秒に分かれ、唯一の整列値は得られない。前回値+0.7314秒の51対応は全401 lag中95.0 percentileだが、最大ではない。周期的で密なイベント列では異なるlagでも対応数が高くなりうるため、percentileだけで版の同一性を判定しない。

### 31.4 局所的な共通イベント列候補

残差合計が最小の最大対応lagは+1.31秒だった。この条件では55組が対応し、最長の連続event-index列は9イベントになった。

| 指標 | 結果 |
| --- | ---: |
| album範囲 | 6.1997–8.8468秒 |
| Cops範囲 | 7.5000–10.1587秒 |
| album側span | 2.6471秒 |
| 連続列の残差中央値 | 9.7 ms |
| 連続列の記述子cosine中央値 | 0.9219 |

これは「二版全体が同じ録音で1.31秒ずれている」という結果ではない。約2.65秒の局所区間に、時刻間隔と粗い帯域形状が近い9イベント列があるという候補である。反復パターン同士の偶然な整列、共通リズム素材、別編集で保持された局所単位が競合説明として残る。

5秒ごとの最良lagも+0.73、+1.30、+0.42、+1.59、-0.94秒へ動いた。よって全previewを一つのoffsetで説明する仮説は採用しない。

### 31.5 仮説更新

“Stem”二版の関係を次の三層へ分ける。

```yaml
edition_relation:
  global_constant_offset: unsupported
  local_event_sequence:
    album_preview_region: 6.1997-8.8468
    cops_preview_region: 7.5000-10.1587
    status: candidate
  sample_identity: unacquired
```

現時点の判断は、全体一致ではなく局所保持候補である。曲内位置不明のpreviewなので、この範囲を原曲の絶対時刻、`Stem / Long Stem`境界、編集元の所在へ変換しない。

### 31.6 追加保存と次の工程

追加保存:

- `event-correspondence-20260904.json` — 全lag探索、一対一対応、局所区間
- `tools/event_correspondence_followup.py` — 再現用解析

次は9イベント列について、イベント間隔列と帯域記述子を個別に比較し、周期だけで説明できる対応と、局所的な音色系列まで一致する対応を分ける。実際の聴取は今回も未実施であり、前景役割とsample同一性は未取得のまま残す。
