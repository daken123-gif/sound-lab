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

