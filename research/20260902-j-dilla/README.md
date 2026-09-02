# J Dilla研究 — 単一グリッドでは捉えられない演奏時間

- status: `active`
- research-id: `20260902-j-dilla`
- 研究対象: J Dillaのビート制作、特にSlum Village期から `Donuts` までのリズム設計
- 現在の問い: キック、スネア、ハイハット、サンプルが異なる時間基準を保持しながら、一つのグルーヴとして成立する条件は何か
- 更新日時: 2026-09-02
- 変更範囲: 研究記録のみ。製品コード、`integration/`、既存判断は変更しない
- 正本候補: この研究ブランチ上のREADME。mainへ統合されるまでは製品採用済みではない

## 1. 研究開始時の訂正

初期の曲別分析は、音源同定と波形検証を行う前に公開資料から推論を進めていたため、実測結果としては失効させる。

その後に行ったShazam利用は、周囲で鳴る音をマイクから認識する「音響指紋照合」ではなく、Shazam経由のApple Musicカタログ検索と公式プレビュー取得である。したがって、これを「Shazamで実録音を認識した」とは記録しない。

現在までに確認できたのは次の範囲に限る。

1. カタログ上の作品・版・曲順・プレビューの対応候補
2. 30秒AACプレビューから得た粗い周期候補
3. アルバム版とインストゥルメンタル版の周期候補の一致／不一致
4. 微細な打点偏差を測るには、フル尺かつ可能ならロスレス音源が必要であること

AACプレビューは長さが短く、非可逆圧縮で過渡成分も変形しうる。以下の数値をJ Dillaのマイクロタイミングそのものの証明には使わない。

## 2. 取得資料

### 一次資料・準一次資料

- Questlove, Red Bull Music Academy Lecture  
  https://www.redbullmusicacademy.com/lectures/questlove-new-york-2013/
- Smithsonian National Museum of African American History and Culture, J Dilla使用MPC 3000  
  https://nmaahc.si.edu/object/nmaahc_2014.139.1
- Dan Charnas interview on *Dilla Time*  
  https://maximumfun.org/transcripts/bullseye-with-jesse-thorn/transcript-bullseye-with-jesse-thorn-dan-charnas-on-his-new-book-dilla-time/
- Stones Throw, J Dilla production accounts  
  https://www.stonesthrow.com/news/the-story-behind-some-of-j-dilla-s-greatest-productions/
- Stones Throw, *Donuts* 33⅓ excerpt  
  https://www.stonesthrow.com/news/j-dilla-donuts-333-excerpt/

### 方法論資料

ユーザー提供の「音楽分析手法の体系的レビュー」を研究入力として使用した。そこから次を採用する。

- 音源同定、信号処理、音楽理論、機械学習を一つの処理へ潰さず分離する
- まず解釈可能なDSPベースラインを作る
- 音源分離は観測補助とし、最終的な発音時刻は原波形へ戻って測る
- confidence、代替候補、人手訂正履歴を保存する
- 単一の総合精度ではなく、タスクごとの評価指標を使う

## 3. カタログ同定

Shazam経由のApple Musicカタログ検索で、少なくとも次の版を区別した。

| 作品候補 | Apple Music album ID | 曲数 | 注記 |
| --- | ---: | ---: | --- |
| *Fan-Tas-Tic, Vol. 2* | `1159991240` | 20 | 2000年版として取得 |
| *Fantastic, Vol. 2.10* | `1159911337` | 36 | 追加曲・別ミックスを含む |
| *Fantastic, Vol. 2* 2023 remaster | `1707814892` | 21 | リマスター版 |
| *Fantastic, Vol. 2: Vinyl Instrumentals* | `1159985669` | — | インストゥルメンタル候補 |

同名曲でも版、尺、ミックスが異なりうる。曲名一致だけで解析対象を同一録音とみなさない。

## 4. 30秒プレビューによる初期ベースライン

短時間フーリエ変換から得たspectral fluxの周期性を用い、倍テン／半テン候補を含む粗いテンポ・クラスを比較した。値は小数第3位まで計算されたが、現段階では概算として扱う。

| 曲 | アルバム版候補 | インスト版候補 | 現在の判定 |
| --- | ---: | ---: | --- |
| Conant Gardens | 約93.96 BPM | 約93.96 BPM | 周期候補は一致 |
| Climax (Girl Shit) | 約95.26 BPM | 約95.26 BPM | 周期候補は一致 |
| Raise It Up | 約94.83 BPM | 約94.83 BPM | 周期候補は一致 |
| Hold Tight | 約96.60 BPM | 約97.05 BPM | 同じ約97 BPM帯 |
| Hold Tight（Vinyl Instrumentals候補） | 約96.60 BPM | 約102.34 BPM | 別版または誤対応候補として除外 |

最後の `Hold Tight` 候補は、カタログ上の尺もアルバム版候補と大きく異なった。したがって「インスト版だから正解」とせず、対象録音の同一性が解決するまで比較対象から外す。

### 現段階で言えること

- 約94–97 BPM帯の候補は、複数のアルバム版／インスト版プレビューで再現した。
- この一致はファイル対応と粗い周期推定の健全性を補助する。
- 30秒プレビューだけでは、小節全体の反復変異、スネアの恒常的遅延、ハイハットの局所的前進などは立証できない。
- BPM一致はグルーヴ一致を意味しない。

## 5. Dilla固有の解析モデル

### 5.1 単一グリッドを正解にしない

通常の解析では、一つのテンポと拍グリッドを先に確定し、各打点のずれを誤差として扱いやすい。本研究では複数の時間基準を候補として併存させる。

```text
CLOCK_CANDIDATE {
  source_layer
  period
  phase
  stability
  confidence
}
```

候補例:

- サンプル由来の周期
- キックが作る重心周期
- スネア／クラップが作るバックビート
- ハイハット等の細分パルス
- 声のフレーズ周期
- 小節・複数小節の反復周期

### 5.2 発音イベント

```text
ONSET_EVENT {
  onset_time
  source_origin
  clock_candidate
  offset_from_clock
  local_ioi
  subdivision_ratio
  cycle_position
  confidence
  correction
}
```

`offset_from_clock` は絶対的な「ずれ」ではなく、どの時計に対する値かを必ず保持する。同じスネアがサンプル周期には遅く、別の演奏層には整合している可能性を残す。

### 5.3 分離と計測の役割分担

音源分離は、キック、スネア、ハイハット、ベース、サンプル断片の由来を判断する補助に使う。ただし分離モデルは過渡成分をぼかしたり移動させたりする可能性がある。

そのため:

1. 分離音で発音源候補を付ける
2. 原波形でonset近傍を再確認する
3. 自動候補と人手訂正を両方保存する
4. 分離音だけからミリ秒単位の結論を出さない

## 6. 現在の仮説

以下は未検証の設計仮説であり、事実として扱わない。

### 6.1 「遅れ」ではなく時計間関係

J Dilla的な時間を、全打点へ同じswing量を加える処理としては捉えない。複数層が異なる位相・細分・安定度を持ち、その関係が周期内で保たれる可能性を検証する。

### 6.2 固定オフセットではなく時間形状

あるスネアが常に同じミリ秒だけ遅れるというモデルでは不足する可能性がある。小節内位置、直前のキック、サンプルのアタック、フレーズ終端に応じて偏差が変わるかを調べる。

### 6.3 反復同一性は全層同時回帰ではない

各層が同時にループ頭へ戻らなくても、重心、音色、声、休符の関係が一定範囲に戻れば反復として知覚されうる。この条件を曲ごとに比較する。

## 7. Field Looperへ採用する候補

ここでの採用は研究候補であり、統合済みではない。

- 一つのmaster gridではなく、複数のclock candidateを保持する
- 各声の発音を絶対時刻と関係時刻の両方で保存する
- 「Humanize」のランダム偏差ではなく、層間関係から次の発音候補を作る
- すべてを常時クオンタイズせず、再合流点だけを制約できるようにする
- 自動解析結果へconfidenceと人手訂正を持たせる
- 手を離したあと完成済み音声が永久反復する設計ではなく、関係状態を演奏中に維持する

## 8. 採用しない点

- J Dillaの音源やドラム音色を模倣しただけのプリセット
- 全声へ同じswing率を適用する「Dillaモード」
- ランダムな数ミリ秒の散布をグルーヴと呼ぶこと
- 30秒AACプレビューからマイクロタイミングを断定すること
- 分離済みstemの発音位置を原波形確認なしで正解とすること
- 一つのBPM推定値を曲の唯一の時間基準とすること

## 9. 触る実装パス

現段階ではなし。研究記録のみ。

次段階で候補とするが、実装前に既存コードとの競合を確認する。

- この研究ディレクトリ内の解析スクリプト
- この研究ディレクトリ内の派生JSON／CSV
- 製品コードは統合判断まで触らない

## 10. 依存する研究

- `20260901-music-theory`: 反復、ミクロタイミング、複数時計の記述
- James Brown研究: primary / secondary One、声部間関係との比較
- Anderson .Paak研究: 身体が保持するパルスと前景交替との比較

このREADME作成時点では、上記すべてを統合判断へ昇格していない。

## 11. 失効した判断

- 公開記事だけを根拠にした初期の曲別「実測分析」は失効。
- Shazamカタログ検索を音響指紋認識として扱う説明は失効。
- `Hold Tight` のVinyl Instrumentals候補を同一録音とみなした比較は失効。
- BPMが取れればDillaの時間が測れたとする判断は失効。

## 12. 未検証事項

1. 合法的に利用できるフル尺音源の版・ISRC・マスター同定
2. ロスレス音源でのキック、スネア、ハイハット、サンプルonsetの再計測
3. 2小節／4小節／8小節ごとの偏差形状
4. 曲内セクション間でclock candidateが入れ替わるか
5. `Conant Gardens`、`Climax (Girl Shit)`、`Raise It Up`、`Hold Tight` の比較
6. Slum Village期と `Donuts` 期で同じモデルが成立するか
7. 自動分離によるonset変位量の測定
8. 人手訂正UIと訂正履歴のデータ形式
9. multi-clockモデルをマルチタッチ操作へ移しても、単なる複雑なシーケンサーにならないか
10. ノンミュージシャンが時計間関係を視覚説明なしで演奏できるか

## 13. Git状態境界

このREADMEは研究記録である。以下を証明しない。

- J Dillaのグルーヴを再現できたこと
- フル尺音源を解析したこと
- ミリ秒単位の打点偏差が確定したこと
- Field Looperへ製品採用されたこと
- 製品コードへ実装されたこと
- 実機または人間の演奏評価で妥当性が確認されたこと

## 14. 先行研究による中心仮説の修正

### 追加取得した研究

1. Sean Peterson, *Something Real: Rap, Resistance, and the Music of the Soulquarians*, University of Oregon doctoral dissertation, 2018.
   - 書誌・要旨: https://scholarsbank.uoregon.edu/items/5b4c64fb-52b8-4c19-82fd-7289be624d66/full
   - PDF: https://scholarsbank.uoregon.edu/bitstreams/0e04faef-6878-4733-92d0-ae4cf00f9ecd/download
   - J DillaとD'Angeloの録音について、波形、スペクトログラム、タイミンググラフを用いたmicrotiming分析を報告している。

2. Daniel Akira Stadnicki, “Play like Jay: Pedagogies of drum kit performance after J Dilla,” *Journal of Popular Music Education* 1(3), 2017.
   - DOI: https://doi.org/10.1386/jpme.1.3.253_1
   - 取得範囲は書誌と要旨。全文は未取得。
   - Dillaのサンプルベースの時間感覚が、後続の生ドラム演奏と教育実践へ移されたことを扱う。

3. Loren Kajikawa, Dan Charnas, Kelley L. Carter and Robert Glasper, “Dilla Time,” *Journal of Popular Music Studies* 34(4), 2022.
   - DOI: https://doi.org/10.1525/jpms.2022.34.4.4
   - 取得範囲は公開冒頭と書誌。全文は未取得。

4. J Dilla公式Bandcamp上の *Welcome 2 Detroit – The 20th Anniversary Edition*.
   - https://jdilla.bandcamp.com/album/welcome-2-detroit-the-20th-anniversary-edition
   - 「Come Get It」について通常版、instrumental、cassette demo、alt beatが収録されていることを確認した。
   - 各版の音源内容自体はまだ取得・比較していない。

### 中心仮説の修正

Petersonの分析に従うと、Dillaの時間感覚を「遅いスネア」へ縮めることはできない。曲によって安定する声部、不安定化する声部、競合する分割が異なる。

> 暫定中心仮説: Dillaの時間感覚は、全声部を同じ方向へ遅らせる処理ではなく、安定した基準層を残したまま、キック、スネア、ハイハット、ベース、サンプルへ異なる分割・先行・遅延・周期を与えることで成立する。

これは先行研究から導いた実証対象であり、私たち自身の音源測定による確定結果ではない。

## 15. 4曲の反例コーパス

以下の観測はPetersonの博士論文が報告した内容であり、私たち自身による再測定結果ではない。

| 作品 | 先行研究上の観測 | 実証での役割 |
| --- | --- | --- |
| The Pharcyde「Runnin'」 | スネアとハイハットは安定した八分音符グリッドを作り、不規則なキックが対置される | 安定層と不規則層 |
| Slum Village「Players」 | live-likeなキックと低域要素が拍位置へ食い込む | 低域による拍の先取り |
| Slum Village「Keep It On (This Beat)」 | スネアがわずかに前進し、低域が拍位置を先取りする | 「Dilla = 遅いスネア」説の反例 |
| J Dilla「Come Get It」 | straightな十六分系キックとtripletを示唆するハイハットが競合する | 異なる分割原理の同時存在 |

この4曲を、既存の *Fan-Tas-Tic, Vol. 2* プレビュー群とは別の反例コーパスとして扱う。既存プレビュー解析を無効化せず、単一アルバム内の周期推定と、作家内で異なる時間技法を検証するコーパスの役割を分ける。

## 16. 対立仮説と反証条件

| ID | 仮説 | 主な反証条件 |
| --- | --- | --- |
| H1 | 一括humanize説 | 同じ偏差分布をランダム配置した版で知覚が保たれない |
| H2 | 固定swingテンプレート説 | 4曲間で基準声部、偏差方向、細分原理が共通しない |
| H3 | 声部間摩擦説 | 声部関係を壊して単独偏差だけ再現しても知覚が保たれる |
| H4 | 知覚的錯覚説 | snare位置を固定し、kickまたはsample側だけ変えても「遅いsnare」感が変わる |
| H5 | 音色attack説 | onset時刻を固定し、attack envelopeだけ変えて時間知覚が変化する |
| H6 | 長周期構成説 | 一小節へ短縮ループしても元の推進・弛緩が失われない |

H3を現在の有力仮説とするが、採用済みの設計原理にはしない。

## 17. 測定と変形実験

### 声部間の主変数

単独声部のグリッド偏差だけでなく、次の声部間差を保持する。

    Δkick-snare(n) = tkick(n) - tsnare(n)
    Δbass-kick(n) = tbass(n) - tkick(n)
    Δhat-grid(n) = that(n) - tgrid(n)

各onsetには次を保存する。

- absolute time
- bar、beat、subdivision
- 参照したclock candidate
- clockからの偏差
- onset confidence
- attack rise time
- loudnessまたはpeak
- 分離モデル
- 原mixでの再確認
- 人手訂正

### 周期

- 1、2、4、8、16、20小節候補でパターン相関を見る
- 同じ小節内位置の偏差分布を比較する
- 完全反復、変奏、長周期シーケンスを分ける
- ループ素材自体のtempo driftと追加ドラムの偏差を分ける

### 最低限生成する変形版

1. 原音
2. 全声部クオンタイズ
3. kickのみクオンタイズ
4. snareのみクオンタイズ
5. hi-hatのみ同一swing化
6. bassのみグリッドへ戻す
7. 元の偏差を声部間で交換
8. 偏差の符号を反転
9. 偏差量を保ったまま小節内位置をシャッフル
10. 同じ分布によるランダムhumanize

原音と変形版はラウドネスを揃え、タイトルと処理条件を隠した聴取比較を行う。

## 18. 他の音楽研究との接続

### research/music-analysis

音源同一性、二重分離、BPM信頼度、phase/onset分析の基盤として参照する。ただし汎用解析結果だけでDillaの作家性を断定しない。

### Charlie Hunter研究

複数声部が異なる役割と時間を同じ身体で保持する仕組みを、マルチタッチの指ごとの役割分担へ接続する。Charlie Hunter研究本文はこの更新ではGitHubから全文取得していないため、具体的な演奏規則はまだ取り込まない。

### Jeff Mills長期研究

基準層を維持しながら別の時間層へ即時介入し、解除する操作へ接続する。Jeff Mills研究本文はこの更新ではGitHubから全文取得していないため、長期研究の採用状態は変更しない。

### Autechre / Aphex Twin研究

複数時間原理、周期変形、再演可能な生成状態へ接続する。両研究本文はこの更新ではGitHubから全文取得していない。

### Field Looperへの暫定写像

| 研究上の関係 | 操作候補 |
| --- | --- |
| 安定した時間層 | 一つの指が基準を保持する |
| 先行・遅延する別層 | 別の指が小節位置ごとの偏差を操作する |
| binary / triplet競合 | 三本目の指が細分比を移動する |
| 層間摩擦 | 指同士の距離でcouplingを操作する |
| 長周期変形 | 指の保持時間でmemory lengthを変える |
| 層の解除 | 指を離すとその層だけ基準へ戻る |

この写像は設計仮説であり、実装許可でも製品採用でもない。

## 19. 追加された未検証事項

- 4曲の正規音源ファイル取得とhash固定
- 「Runnin'」「Players」「Keep It On」「Come Get It」の各16小節以上の声部別onset測定
- Petersonの図表と私たちの測定値の再現性
- 「Come Get It」の通常版、instrumental、cassette demo、alt beat比較
- ランダムhumanizeと構造化偏差のブラインド聴取差
- onset時刻とattack envelopeの寄与分離
- Charlie Hunter、Jeff Mills、Autechre、Aphex Twin各研究本文のremote由来取得と接続監査
- iPhone実機上での複数時間層操作の遅延と演奏可能性

## 20. GitHub実体を取得した研究との接続

取得日: 2026-09-02

### 取得できた実体

| research-id | 取得ref | 取得ファイル | blob SHA | 状態 |
| --- | --- | --- | --- | --- |
| 20260831-james-brown | research/20260831-james-brown | research/20260831-james-brown/README.md | 947ba74bbab1da7e0632929d6f188914076b7c81 | PRIMARY_ARTIFACTとして本文取得 |
| 20260831-anderson-paak | research/20260831-anderson-paak | research/20260831-anderson-paak/README.md | b3798491a5e88d1680920516b901a9548adb16cb | PRIMARY_ARTIFACTとして本文取得 |
| 20260901-music-theory | research/20260901-music-theory | research/20260901-music-theory/README.md | 59b775936eb5bad4e8b0f9416cd2f5a6b787b17d | PRIMARY_ARTIFACTとして本文取得 |

検索結果に対する汚染scannerはCLEANだった。これは制御文や現在クエリの自己反響を検出しなかったことだけを意味し、各研究の仮説が真であることや製品採用を証明しない。

### James Brown研究との接続

取得したJames Brown研究は、共通拍を共有する複数声部が、休符、アクセント、microtiming、primary / secondary One、主導権を分担すると記述する。特に次の点がJ Dilla研究と直接接続する。

- microtimingをランダムHumanizeではなく、周期内の時間形状として扱う
- 4トラックを完成音声ではなく相互に影響する4声として扱う
- couplingを音量関係ではなく、別声部の次の発音位置や休符を動かす関係として扱う
- ブレイク中にも不在声部との関係を保持する

ただし、James Brown研究では「4声が別々の周期を持つ」という一般化が失効し、共通拍の内部で発音位置を分担するモデルへ修正されている。したがって、J Dillaのmulti-clock仮説をJames Brownへ逆流させない。

比較軸は次のように分ける。

| 軸 | James Brown研究 | J Dilla研究 |
| --- | --- | --- |
| 基準 | 共通拍とprimary / secondary One | 複数clock candidateの併存可能性 |
| 差異 | 共通拍内部の声部別timing shape | straight / swing、sample / drum等の時計間摩擦 |
| 回帰 | Oneへ収束 | 同期回帰するか自体を未検証 |
| 反復 | 生演奏関係の循環 | sample / sequence内の長周期を含む |
| 共通禁止 | 固定Swing、ランダムHumanize、完成ループの垂れ流し | 同左 |

### Anderson .Paak研究との接続

取得したAnderson .Paak研究では、「一定」と「同一」を分けている。

- 一定: pulse、重心、反復周期を保つ
- 同一: 前小節と同じ打点、強度、音色を再生する

この区別をJ Dilla研究へ接続すると、clock candidateの安定は、同じイベント列の再生を意味しない。安定したsnare / hi-hat層を保持しながら、kickやbassのイベント列を変化させられる。

また.Paak研究の前景交替と負荷階層は、J Dillaの複数時間層を人間が演奏可能にする際の制約になる。

| .Paak研究の要素 | J Dilla研究への接続 |
| --- | --- |
| 半自動のpulse保持 | 一つのclock candidateを身体側で維持 |
| 意図的なkick / snare決定 | 別clockとの位相関係へ介入 |
| 反射的なghost / fill | timing shapeを局所変形 |
| foreground role | 操作対象の時間層を交替 |
| 指の追加・離脱 | clock層の介入・解除 |

.Paak研究本文内のCharlie Hunter / Jeff Mills接続は、そのREADMEの推論である。Charlie Hunter / Jeff Mills各研究本文の代替にはしない。

### 楽理研究との接続

取得した楽理研究は、演奏イベントを次の組で扱う。

    E = (t, Δt, p, c, a, r, μ)

- t: 発音位置
- Δt: 想定グリッドからの変位
- p: 音高関係
- c: 音色
- a: 強度・包絡
- r: 他音との役割関係
- μ: 次の反復で何が変わるか

J Dilla研究では、Δtを単一グリッドに対する値へ固定せず、参照clockを追加する。

    E_dilla = (t, clock_id, Δt_clock, p, c, a, r, μ)

ここで重要なのは、clock_idを増やすこと自体ではない。

- rは、どの声部が安定層、不安定化層、前景、回帰点を担うかを保持する
- μは、次の反復で偏差、密度、声部間couplingの何が変わるかを保持する
- cとaは、物理onsetを変えずに時間知覚を変えるattack仮説の検証に使う
- Δt_clockは、どの時計に対する偏差かを失わない

これにより、楽理研究の第一命題「同一性を保ちながら差異を生成する周期構造」を、J Dillaの具体的な反証実験へ落とせる。

### 取得不能の研究

次の語でbranch検索を二波行った。

- Charlie Hunter: charlie-hunter / hunter
- Jeff Mills: jeff-mills / mills
- Autechre: autechre / autech
- Aphex Twin: aphex / aphex-twin

対応ブランチは取得できなかった。したがって現時点では以下の状態を維持する。

| 研究 | 状態 |
| --- | --- |
| Charlie Hunter | referenced only。本文未取得 |
| Jeff Mills | referenced only。本文未取得 |
| Autechre | referenced only。本文未取得 |
| Aphex Twin | referenced only。本文未取得 |

過去会話の要約や、別研究README内の短い説明を各研究の正本本文へ昇格させない。

## 21. 接続後に更新された実証焦点

三研究を接続したことで、J Dillaの実証は「打点が何msずれたか」だけでは不足する。

1. clock: 何が時間基準を作るか
2. relation: どの声部が別声部の発音可能性を制約するか
3. mutation: 次の反復で何が保持・変形されるか
4. foreground: どの時間層を演奏者が現在操作しているか
5. return: 共通着地点へ戻るのか、摩擦を維持するのか
6. embodiment: ノンミュージシャンが説明なしに関係を演奏できるか

これらを、既存music-analysisのonset / phase計測と、4曲の変形聴取へ同時に記録する。

## 20. 再現可能なプレビュー周期解析

研究ディレクトリ内に、30秒WAVから粗い周期候補を求める最小実装を追加した。

- `tools/analyze_preview_periodicity.py`
- `tests/test_analyze_preview_periodicity.py`
- `data/preview-periodicity-v1.json`

処理は次の順序で固定した。

1. PCM WAVをmonoの浮動小数点波形へ正規化
2. STFT（frame 2048、hop 256）
3. log magnitudeの正方向spectral flux
4. unbiased autocorrelation
5. 70–130 BPM範囲の局所ピーク
6. parabolic interpolationによるサブフレーム周期候補
7. 入力WAVのSHA-256、長さ、サンプルレート、方法パラメータをJSONへ保存

合成96 BPMクリック列に対する単体試験は成功した。9本のプレビューWAVを再解析し、保存済みJSONとのbyte単位比較も一致した。これは実装の再実行可能性だけを示し、音楽的正解やマイクロタイミング妥当性を証明しない。

### v1の第一候補

| ファイル | BPM候補 | autocorrelation score |
| --- | ---: | ---: |
| conant_album_preview.wav | 94.040944 | 0.625253 |
| conant_instrumental_preview.wav | 94.006832 | 0.717590 |
| climax_album_preview.wav | 95.336879 | 0.279008 |
| climax_instrumental_preview.wav | 95.414627 | 0.303532 |
| raise_album_preview.wav | 95.012745 | 0.411676 |
| raise_it_up_instrumental_preview.wav | 94.880350 | 0.751613 |
| hold_tight_album_preview.wav | 96.871095 | 0.288505 |
| hold_tight_instrumental_preview.wav | 97.064079 | 0.706373 |
| hold_tight_vinyl_instrumental_preview.wav | 102.211309 | 0.663320 |

初期READMEの丸め値との差は、方法パラメータとピーク補間を固定していなかったために生じた。以後、再現値としては `preview-periodicity-v1.json` を使う。ただし、短いAAC由来WAVという証拠限界は変わらない。

この追加により、Section 9の「現段階では実装パスなし」は失効した。製品コードは依然として変更していない。

## 21. 他研究から取得した差分

以下は各研究ブランチのREADME本文を取得して比較した結果であり、`main`へ統合済みという意味ではない。

### 楽理研究との接続

楽理研究は演奏イベントを `E = (t, Δt, p, c, a, r, μ)` と置き、反復時の変化規則 `μ` まで演奏対象にする。J Dilla研究はこのうち `Δt` を単一グリッドからの誤差にせず、`clock_candidate` と声部間差へ分解する。

したがって接続後の候補は次になる。

```text
E_dilla = (
  onset_time,
  clock_candidate,
  offset_from_clock,
  source_role,
  relation_deltas,
  attack,
  repeat_transform
)
```

### James Brown研究との差

James Brown研究では、共通拍を共有したまま各声が小節内部の発音位置、休符、アクセントを分担する。別々の周期を持つという一般化は同研究内ですでに失効している。

Dilla研究でも「複数時計」を即座にポリメーターとみなさない。比較単位は次のように分ける。

- JB: 共通拍の内部で、声部がOneから離れ、別経路で戻る
- Dilla: 安定層を残し、別声部の分割、位相、attack、長周期を競合させる可能性
- 共通点: 固定swingやランダムhumanizeではなく、声部間関係を保存する

### Anderson .Paak研究との差

Anderson .Paak研究は「一定」と「同一」を分け、身体がパルスを維持しながら前景と局所変化を現在形で生成すると記述する。

Dilla研究との接続では、完成音声を再生するのでなく次を演奏状態として保持する。

- 基準層を保持する接触
- 別層の先行／遅延または細分を動かす接触
- 層間couplingを変える接触
- 指を離したとき、その層だけ基準へ戻す規則

ここで重要なのは、Dillaの録音結果を固定テンプレート化することではない。.Paak研究の身体的維持と接続し、時間関係そのものを演奏者が現在形で作り続けることにある。

## 22. 次の実証境界

プレビュー周期解析の次に必要なのは、より高性能なBPM推定器ではない。

1. フル尺・同一マスターを固定する
2. 原mixと分離補助から声部候補を付ける
3. 原mixでonsetを再確認する
4. attack envelopeとonset timeを分離する
5. 声部間差 `Δkick-snare`、`Δbass-kick`、`Δhat-grid` を小節位置ごとに保存する
6. 量子化、符号反転、声部間交換、ランダムhumanizeの変形版を比較する

フル尺音源がない現状態では、この境界を越えた数値を作らない。

