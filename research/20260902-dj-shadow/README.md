# DJ Shadow研究 — サンプルを完成ループではなく、場面と役割へ変える

- status: `active`
- research-id: `20260902-dj-shadow`
- 研究対象: DJ Shadow（Josh Davis）のサンプリング、長尺構成、録音空間、DJ／ライブ、制作技術の変化
- 現在の問い: 反復素材を固定伴奏として垂れ流さず、演奏中に役割、前景、場面、回帰条件を変える原理として何を抽出できるか
- 更新日時: 2026-09-02 UTC
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
