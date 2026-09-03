# Derrick May研究 — 反復を「発火する時間」へ変える

- status: `active`
- research-id: `20260903-derrick-may`
- started: `2026-09-03 UTC`
- last-updated: `2026-09-03 UTC`
- scope: Derrick May / Rhythim Is Rhythim / Maydayの録音、DJ由来の編集、作者関係、Sound Labへの転用候補
- authority: 研究記録。`integration/` の採用判断を変更しない
- change-boundary: 本ディレクトリのみ。製品コードと統合判断は変更しない

## 研究対象と現在の問い

Derrick Mayを「Belleville ThreeのInnovator」「Strings of Lifeの作者」という英雄的な人物紹介へ縮めず、次を分離して調べる。

1. 初期録音の反復、周期、音色、密度は実際にどう異なるか。
2. Ron HardyらChicagoのDJから受けた影響は、音色模倣でなく作曲・編集・ミックスの時間へどう入ったか。
3. Michael James、Thomas Barnett、Jay Dixonらの寄与を、May単独作者という後世の物語からどう回収するか。
4. 少数のパターンを完成済みループとして流さず、その場で発火・切断・再投入する原理をSound Labへ移せるか。

## 証拠境界

### 今回取得したもの

- Shazam接続内のApple Music Catalog検索およびAlbum取得
- 日本ストアの `Innovator - Soundtrack for the Tenth Planet`、album ID `1678920647`
- 同作7曲の曲ID、ISRC、尺、公式Preview URL
- 7曲すべての約30秒Preview音声バイト
- 校正済み `research/music-analysis/analyze_previews.py` による全断片と10秒三窓の測定
- Derrick May本人への2004年インタビューと2006年RBMA講義
- Network Recordsによる2020年再発情報
- Derrick May公式Biography
- 告発を扱ったDJ Mag、Resident Advisor、The Guardianの報道

Shazamは周囲で鳴る音を認識したのではなく、Apple Music Catalogの曲・版・Previewを取得する入口として使用した。

### 取得していないもの

- 7曲の全長音源
- オリジナル12インチと2019 remasterの音響差
- 各曲のPreview開始時刻
- マルチトラック、MIDI、ミキサー操作ログ
- Derrick MayのDJセット音源を用いた時刻付き独自分析
- `It Is What It Is`、`The Beginning`、`Icon`、`Illusion`の解析可能なPreview
- Michael James、Thomas Barnett、Jay Dixonの全証言と契約・裁判資料
- 性暴力申告について事実認定した司法判断

したがって、測定結果は未知位置の約30秒断片に限る。全曲構成、作者の意図、曲全体のBPM、DJ演奏全般をPreviewだけから断定しない。

## カタログ固定

対象はNetwork Recordsが2020年に再提示した7曲版である。同レーベルは2019年にCurvepusherでremasterしたと記している。オリジナル盤そのものではない。

| 曲 | Apple曲ID | ISRC | カタログ尺 | Preview |
|---|---:|---|---:|---|
| The Dance | `1678920651` | `GBJX31936011` | 7:13.333 | 取得済み |
| Strings Of Life | `1678920653` | `GBJX31936012` | 7:34.500 | 取得済み |
| Beyond The Dance | `1678920655` | `GBJX31936013` | 6:59.933 | 取得済み |
| Sinister | `1678920660` | `GBJX31936015` | 6:37.800 | 取得済み |
| Wiggin | `1678920663` | `GBJX31936016` | 5:31.933 | 取得済み |
| Nude Photo | `1678920667` | `GBJX31936017` | 4:41.244 | 取得済み |
| Hand Over Hand | `1678920668` | `GBJX31936018` | 8:21.135 | 取得済み |

Network RecordsのBandcamp表示では `Hand Over Hand` が13:04とされ、Apple Musicカタログ尺8:21.135と一致しない。別編集または配信メタデータ差の可能性を残し、同一版とは扱わない。

## Preview実測

測定器は各Previewを44.1 kHz stereoへdecodeし、RMS、frame RMS分布、スペクトル重心、オンセット、周期候補を出す。周期候補は拍の断定ではない。

### 約30秒断片

| 曲 | RMS dBFS | 重心 Hz | onset/s | onset間隔中央値 s | CV | 主要周期候補 BPM |
|---|---:|---:|---:|---:|---:|---|
| Beyond The Dance | -13.89 | 5044.7 | 8.019 | 0.1161 | 0.337 | 127.60 / 169.44 / 84.72 |
| Hand Over Hand | -11.01 | 4616.9 | 7.184 | 0.1103 | 0.386 | 72.79 / 56.79 / 101.33 / 127.60 |
| Nude Photo | -11.17 | 4090.9 | 7.317 | 0.1219 | 0.393 | 123.05 / 61.52 / 82.03 |
| Sinister | -10.61 | 5371.1 | 7.885 | 0.1161 | 0.410 | 132.51 / 66.26 / 106.56 |
| Strings Of Life | -13.36 | 4424.4 | 6.682 | 0.1219 | 0.460 | 121.60 / 61.16 |
| The Dance | -12.47 | 4546.1 | 7.150 | 0.1219 | 0.359 | 129.20 / 64.60 / 86.13 |
| Wiggin | -10.88 | 4154.6 | 7.451 | 0.1248 | 0.366 | 126.05 / 63.02 |

左右RMS差は全曲で絶対値0.04未満だった。この指標だけから定位の狭さ、広さ、モノ互換性は断定しない。

### 三窓で残ったもの

| 曲 | 三窓の観測 | 判定 |
|---|---|---|
| Beyond The Dance | 127.60が三窓とも第一候補。onset/s 8.095 → 7.989 → 7.949 | Preview内の安定した周期候補 |
| Nude Photo | 123.05 / 61.52 / 82.03が三窓で反復。onset/s 7.295 → 6.790 → 6.930 | Preview内の安定した複数周期候補 |
| Wiggin | 126.05 / 63.02が三窓で同順。onset/s 7.695 → 7.589 → 6.726 | Preview内の安定した主周期・半周期候補 |
| Sinister | 132.51 / 66.26 / 106.56が三窓に残るが順位が交代 | 周期は残るが前景が変わる候補 |
| The Dance | 129.20 / 64.60等が残るが、第二窓では172.27が第一候補 | 単一BPMへの平坦化を棄却 |
| Strings Of Life | 第一窓61.52、第二窓120.19、第三窓121.60 / 61.16。第三窓でRMSと重心が急上昇 | 局所的な前景・密度転換を確認 |
| Hand Over Hand | 第一窓のonset/s 5.497から第二・第三窓8.288 / 8.560へ増加。周期候補順位も変化 | Preview内に大きい密度差 |

`Strings Of Life`では第一・第二窓が約-16 dBFS台、第三窓が-10.22 dBFSへ上昇した。スペクトル重心も4091.0 / 4205.2 Hzから5292.1 Hzへ上がり、onset/sは8.395 / 8.688から6.216へ下がった。これは「音数が増えた」という意味ではない。より少ない検出オンセットで、強く明るい層が前へ出た可能性を支持する。

## 外部資料から確認できた制作関係

### Chicagoの目的関数

Mayは、Chicagoの音を真似ようとしたのでなく、Ron Hardyがプレイしたくなる曲を作りたかったと述べる。ここから確認できるのは、作曲の評価関数が楽譜やジャンル純度だけでなく、特定DJがフロアへ投入する瞬間に置かれていたことである。

この発言とPreview測定を合わせると、Mayの反復は「同じループを滑らかに維持すること」より、安定した周期の上でどの層を前景化し、どこで密度を変えるかに重心がある、という仮説が立つ。ただしDJセットの時刻分析は未実施である。

### `Strings of Life`は単独作者神話にできない

Mayの説明では、Michael Jamesが別のballad用に弾いたピアノ素材を切断・loopし、自分のピアノとorchestrationを加えた。さらにJay Dixonがテープ編集を担当し、逆方向編集やtimingを作った。May自身は、曲が単にmixされたのでなくchoreographされたと述べる。

Apple Musicの別コンピレーション版 `Innovator`（album ID `1804523507`）は `Strings of Life` のcomposerをDerrick May / Michael Jamesと表示する一方、今回測定したNetwork版はDerrick Mayのみと表示する。カタログ表示が一致しないため、単一配信欄を作者関係の最終証拠にしない。

2006年講義では、Mayは録音していたオーケストラ素材をEnsoniq Mirageへ入れ、鍵盤でprogressionを演奏したと説明する。2004年インタビューでは他人のレコードをsamplingすることを否定しつつ、Michael Jamesのピアノ断片をchop / loopしたと説明している。ここでは次を分ける。

- 既存商用録音の無断サンプリングを避けるというMayの自己定義
- 自分たちが録音した素材をサンプラー／シーケンサーで再配置する制作
- Michael Jamesの演奏とJay Dixonの編集を含む共同的な成立

### `Nude Photo`も寄与関係が争われる

Derrick May公式Biographyは `Nude Photo` をThomas Barnettとの作品とする。2026年にApple Musicへ提示されている別 `Innovator` 版もcomposerをDerrick May / Thomas Barnettと表示する。一方、Mayの2004年インタビューは、Barnettの持参した素材を退け、自分が一晩で曲を作ったという説明である。Barnett側には、自分がsequencerへ複数patternを入力し曲を書いたという証言がある。

今回、契約、セッション資料、裁判資料までは取得していない。したがってMay単独作ともBarnett単独作とも確定しない。確認できる最低線は、公式Biographyと一部カタログが共同名義を保持し、成立過程について当事者説明が衝突していることである。

## 中心仮説

Derrick Mayの初期録音の特徴は、テクノへ情緒的なstringsやpianoを足したことだけではない。

**安定した周期を床として残しながら、前景となる周期、密度、音量、帯域を手作業で交代させ、反復を「再生中の物」から「いま発火した出来事」へ変える。**

この仮説は三層に分ける。

1. `FLOOR` — 三窓を通じて残る主周期／半周期。身体を切らさない。
2. `IGNITION` — 音量、明度、オンセット密度、フレーズの投入で現在を変える。
3. `CHOREOGRAPHY` — ミュート、テープ編集、逆回転、パンチイン／アウトで出来事順を決める。

`FLOOR`を自動ループ、`IGNITION`を装飾、`CHOREOGRAPHY`を事後編集へ固定しない。Mayの制作ではこの三者が演奏中に相互作用していた可能性がある。

## Jeff Mills研究との接続

Jeff Mills研究の暫定仮説は、複数の不安定な時間層を途切れさせず、位相差や事故を次の構造へ変換する精度にある。

Derrick May側から得られる対照候補は次の通り。

| 軸 | Derrick May | Jeff Mills |
|---|---|---|
| 維持するもの | soul / emotionを含む周期床 | 高速な連続性と複数層 |
| 破断の主手段 | edit、mute、前景交代、和音・stringsの発火 | deck交代、909、位相差、即時回復 |
| 事故との関係 | 現時点ではDJ実測不足 | Liquid Room等で回復単位を検証中 |
| Sound Labへの問い | 感情的事件を音色presetなしで起こせるか | ずれを消さず連続性へ戻せるか |

両者を「Detroit techno的即興」という一語へ潰さない。Mayの録音編集とMillsのlive operationが同型かどうかは未検証である。

## Sound Labへの転用候補

以下は `candidate` であり、採用判断・実装指示ではない。

### 1. ループではなく床を保持する

4トラック全体を同一長で一周させず、短い周期要素だけを `FLOOR` として維持する。長い音、手動打音、帯域変化、ミュート履歴は同時リセットしない。

### 2. 前景周期を指で交代させる

複数周期を常時鳴らすのではなく、接触した位置／運動によって、現在知覚される周期を変える。BPMを切り替えるのでなく、同じ素材内の主周期・半周期・細分周期のどれを前へ出すかを演奏する。

### 3. ミュートを空の停止ボタンにしない

mute解除時に常に小節頭へ戻さず、現在位相、直前の離し方、残響、短い逆行またはpickupを候補として保持する。Mayのテープ編集をエフェクト名で模倣せず、入口のtimingを演奏可能にする。

### 4. `Contact Performance Take`に前景交代を残す

現行候補のPerformance Takeへ、音符列だけでなく次を記録できるか検証する。

- track mute / unmute時刻
- 前景帯域
- density gate
- entry phase
- decay / cutoffの運動

これは実装済みではない。既存Take形式との整合、保存量、再現性は未検証である。

### 5. strings presetを採らない

May研究から得るものを「Detroit strings」「Strings of Lifeコード」「1987 drum kit」という音色presetへ閉じない。共同演奏・編集・発火の時間構造を抽出対象にする。

## 採用しない短絡

- Belleville ThreeだけでDetroit techno全体を説明する。
- Derrick May一人を `Strings of Life` / `Nude Photo` の唯一の創作者として記録する。
- Previewの第一周期候補を曲全体のBPMと呼ぶ。
- 30秒の密度差から全曲の展開を断定する。
- strings、piano、古いdrum machineの音色だけを模倣する。
- 7曲の測定をそのまま7 presetまたは7機能へ変換する。
- 本研究だけで4トラック、Skulptur主演奏面、独立ドラムの既存方針を変更する。
- MayのDJ発言を、未取得のDJセット実測の代わりにする。

## バイアス監査

| バイアス | 現在の対処 |
|---|---|
| hero bias | Michael James、Thomas Barnett、Jay Dixon、Ron Hardyの具体的寄与を分離する |
| famous-track bias | `Strings of Life`だけでなく同一7曲版を取得・測定する |
| famous-device bias | Mirage、Roland、Korgを機能要求に変えず、操作関係を見る |
| feature accumulation | 転用候補を実装・採用へ昇格しない |
| automation bias | 前景交代を自動arrangementにせず、演奏可能な判断として残す |
| DAW-convergence bias | 波形編集機能の増殖でなく、リアルタイムの入口・切断・再投入を見る |
| catalog-authority bias | 配信composer欄の矛盾を保持し、契約上の最終権威にしない |

## ガバナンス境界

- ユーザーは研究の継続とGit保存を指示した。
- 本更新は研究記録、版固定、測定値、転用候補だけを保存する。
- 製品コード、`integration/DIRECTION.md`、`integration/DECISIONS.md` は変更しない。
- commitと通常pushまでが今回の保存範囲。PR作成、merge、採用、実装、配備は行わない。

## 性暴力申告と人物評価の境界

2020年以降、DJ MagおよびResident Advisorは複数女性による性暴力・性的嫌がらせの申告を報道した。Mayは否定した。出演中止も報道されている。

今回取得した範囲では、申告を事実認定または虚偽認定した司法判断を取得していない。このため有罪判決があったとも、申告が虚偽だったとも記録しない。音楽的影響の研究は申告の消去にならず、申告の存在は個別作品の信号測定値を変更しない。両方を別の証拠軸として保持する。

## 依存する研究

- `research/music-analysis/` — Preview取得後の測定・推定・解釈境界
- `research/20260902-jeff-mills/` — 演奏中の持続／破断／回復との比較候補
- Underground Resistance研究 — Detroit technoの英雄史観、共同体、匿名性との比較候補。本文未取得
- `integration/DIRECTION.md` — 4トラック、明示録音、Skulptur型主演奏面、独立ドラムの現在境界
- `integration/DECISIONS.md` — 機材研究を機能カタログへしない既存判断

## 反証条件

- 別Preview位置または全長測定で、三窓に残った周期／密度関係が局所的例外と判明する。
- オリジナル12インチと2019 remasterで、今回の密度・帯域差が大きく変わる。
- DJセットの時刻分析で、前景交代より長時間の滑らかなblendが支配的と確認される。
- Michael James、Thomas Barnett、Jay Dixonの一次資料が、現在保持した寄与関係を訂正する。
- Sound Lab試作で前景周期の手動交代が、非音楽家の即興余地を増やさず操作負担だけを増やす。

## 未検証事項

1. 7曲Previewの開始位置と、各曲全長内での代表性。
2. 1987–1991 original masterと2019 remasterの差。
3. `It Is What It Is`等を含む初期作品全体の版固定と測定。
4. DJセット三本程度のmute、entry、blend、事故、回復の時刻ログ。
5. Michael James / Thomas Barnett / Jay Dixonの一次証言、credits、権利資料の突合。
6. 前景周期交代を3点以下のmultitouchで演奏できる最小実験。

## 次の研究サイクル

1. `It Is What It Is`、`The Beginning`、`Icon`、`Illusion`の正規版をカタログ固定する。
2. original single版とNetwork remaster版を同曲で取得できる場合、Previewの一致箇所とmaster差を調べる。
3. DJセットを一つ固定し、曲名表より先にentry / mute / overlap / recoveryを時刻記録する。
4. Jeff Mills研究の持続／破断／回復記法と同じ表へ載せ、共通点と非共通点を反証する。
5. 製品採用とは別に、`FLOOR / IGNITION / CHOREOGRAPHY`の最小演奏実験案を作る。

## 主要資料

### 公式／一次資料

- Derrick May official biography: https://derrickmay.com/biography/
- Derrick May, Red Bull Music Academy lecture, Melbourne 2006: https://www.redbullmusicacademy.com/lectures/derrick-may-it-is-what-it-isnt/
- Bill Brewster / Frank Broughton interview with Derrick May, published by RBMA Daily: https://daily.redbullmusicacademy.com/2017/05/interview-derrick-may/
- Network Records, `Innovator - Soundtrack For The Tenth Planet`: https://networkrecords.bandcamp.com/album/innovator-soundtrack-for-the-tenth-planet
- Apple Music Japan catalog album `1678920647`: https://music.apple.com/jp/album/innovator-soundtrack-for-the-tenth-planet/1678920647

### 寄与関係の補助資料

- Thomas Barnett interview: https://iumag.co.uk/thomas-barnett-authentic-detroit-techno-pioneer/

### 独立報道

- DJ Mag investigation, 2020-11-12: https://djmag.com/longreads/multiple-women-report-sexual-assault-and-harassment-derrick-may
- Resident Advisor investigation, 2021-01-29: https://ra.co/features/3828
- The Guardian report including May's denial, 2020-11-12: https://www.theguardian.com/music/2020/nov/12/techno-dj-derrick-may-accused-of-sexual-assault-by-four-women

## 触る実装パス

- なし（research-only）

## 失効した判断

- 前回会話内の「Mayの本質はDJの身体的な時間操作を作曲へ持ち込んだこと」という断定は、DJセットの独自時刻分析前には強すぎた。現在は、本人発言、制作工程、7曲Preview測定が支持する中心仮説として保持し、DJ実測を反証条件にする。
- 前回会話内で `The Dance`、`It Is What It Is`、`Beyond the Dance`の音楽構造を直接聴取したように書いた箇所は、その時点で解析可能音源を取得していなかった。本記録では取得・測定済み7曲と未取得曲を分離し、未取得の `It Is What It Is` は分析対象から外した。

## 変更履歴

### 2026-09-03

- 研究記録を開始
- 既存のShazam / Apple Music Preview取得経路を適用
- Network Records 7曲版をID / ISRC / 尺で固定
- 7 Previewの音声バイトを取得し、全断片と三窓を測定
- 作者寄与の衝突、中心仮説、反証条件、Sound Lab転用候補を記録
- 製品コードと統合判断は変更していない
