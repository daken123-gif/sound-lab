# Autechre研究更新 — 2026-09-28

対象branch: `research/20260831-autechre`  
取得base: `75341b7c638d552a951a33b402a4707fb1836a55`  
確認時刻: 2026-09-28 JST

この更新は、公式catalogの再同定、公式preview配信資産の時点差監査、公開面の更新確認、並行研究本文の再読を行った。音源本体はGitへ保存しない。製品コード、`integration/`、`main`、並行研究branchは変更しない。

## 1. 取得事実 — catalog identityは維持、GB Antiのpreview資産だけが交代

Shazam接続内のApple Music Catalogから、`Flutter`の三つのcatalog identityを再取得した。

| storefront / release | song ID | ISRC | catalog duration | default preview URL |
| --- | ---: | --- | ---: | --- |
| GB / `Anti - EP` | `292743285` | `GBBPW9400118` | `597733 ms` | `AudioPreview221/.../mzaf_1987220487659465521.plus.aac.p.m4a` |
| GB / `EPs 1991 - 2002` | `420210312` | `GBBPW9400118` | `599680 ms` | 前回と同じ `AudioPreview125/.../mzaf_14897457753820961134.plus.aac.p.m4a` |
| JP / `Anti - EP` | `314910098` | `GBBPW9400118` | `597733 ms` | 前回と同じ `AudioPreview211/.../mzaf_13802220145402762989.plus.aac.p.m4a` |

GB `Anti - EP`だけが、2026-09-14に記録した`AudioPreview125`のURLから`AudioPreview221`のURLへ変わった。曲名、artist、album、song ID、ISRC、catalog durationは変わっていない。

現行GB `Anti - EP` previewを二回取得し、二回とも同じ`1028853 bytes`、SHA-256 `96f0c35012443d6eb55648ebd8d01dd037d3f8615b03b96284bb7c9de2cf9d7f`だった。旧30秒URLと旧90秒URLも再取得でき、既存hashと一致した。従って旧資産が取得不能になったのではなく、catalogが返す既定30秒資産が交代した状態である。

| asset | bytes | container duration | SHA-256 | 今回の状態 |
| --- | ---: | ---: | --- | --- |
| GB Anti 現行30秒 | `1028853` | `30.000000 s` | `96f0c35012443d6eb55648ebd8d01dd037d3f8615b03b96284bb7c9de2cf9d7f` | 2回取得、byte一致 |
| GB Anti 旧30秒 | `1125118` | `29.976961 s` | `7bd4c736c5649cbd25c15712643391427d9bd9f43df398599438a12c1fe448ab` | 旧hash一致 |
| GB Anti 旧90秒 | `3122487` | `89.977324 s` | `4132908b22a6407d5d30b42c3618ecafa8817beeb7dc65b4609354d5aeb5cc89` | 旧hash一致 |
| GB EPs 現行30秒 | `1097746` | `29.976961 s` | `b2f6727ed9efe09da82dbc468570d2fc0663addcbc0eb24fafd8263c9c5ca9b0` | 旧hash一致 |
| JP Anti 現行30秒 | `996146` | `30.012993 s` | `1ab386168365c5d575bc7607464d33b298198070272950f8e6327dc12324d004` | 旧hash一致 |

## 2. 分析 — container hashの変化と音楽内容の変化を分離

全資産を`ffmpeg`でmono／22,050 Hz／float32へ全区間decodeした。現行GB Anti 30秒は`660960 sample`、旧30秒は`659936 sample`で、現行版が`1024 sample`、約`46.44 ms`長い。

現行30秒を旧30秒と先頭から比較するとPearson相関`0.999968095`、旧90秒の先頭30秒と比較すると`0.999968132`だった。両方とも最良offsetは`0.000 s`である。現行30秒は旧90秒の先頭と同じ内容を約46 ms長く含む。平均絶対差は約`0.0001734`で、PCM byte hashは一致しない。

この観測は次を支持する。

- default previewのURL、container hash、容量が変わっても、同じcatalog identityと同じ音楽区間を配る場合がある。
- SHA-256は取得資産の再現性には必要だが、それだけで音楽内容の連続性や交代を判定できない。
- 既存のGB Anti preview測定は、現行default previewにも内容上ほぼ同じ区間の分析として保持できる。ただし現行資産のcontainer／PCMと旧資産を同一と呼ばない。
- 2026-09-14の「GB Anti 30秒の旧hashが現行取得と一致」という時点記述は、2026-09-28のdefault previewには失効した。旧hashと旧測定自体は履歴証拠として有効である。

今後のsource manifestでは、次の四層を分離する候補を採る。

```text
PREVIEW_EVIDENCE {
  catalog_identity
  delivery_asset_url_hash_time
  decoded_signal_hash_format
  content_alignment_reference_offset_similarity
}
```

これは研究記録の設計候補であり、製品コードや`integration/`への採用判断ではない。

## 3. 新しい公開面

- AE_STOREの公開検索面では`elseq 1-5`が2026-10-02発売予定、21 clips、5CDとして引き続き表示された。直接ページは今回もHTTP 403で本文を読めなかったため、検索面以上の説明、収録音源、master差は確認済みにしない。
- Apple Music GBで`Autechre elseq 1-5`をalbum検索した結果は、2016年の`elseq 1`一件だった。これは2026年物理boxがApple Music上に存在しないことの網羅的証明ではなく、今回の検索結果に新しいcatalog identityが現れなかったという記録である。
- 公式Bandcampの`AE_2022－`は19公演、2024-12-03 release、`all rights reserved`を維持していた。upcoming shows欄は2026-09-28時点のWrocław以降へ進んだが、新録音、新set、音源公開の証拠には使わない。

今週の新しい音源上の公開変化は、GB Antiのdefault preview delivery asset交代である。新しい本人インタビュー、公式`AE_LIVE`音源bundle、解析可能なAutechre全曲sourceは確認できなかった。

## 4. AE_LIVEと全曲取得の境界

公式Bandcampの19公演catalogは確認したが、音源本体を取得していないため公演間の反復・状態遷移を新たに測定していない。短いLondon A／Bだけを取得可能性の代表群へ昇格させない。

YouTube Topic `Flutter`は前回の0 bytes／decode未到達を保持する。取得connector headと公開経路に変更を確認できず、今回は同じ転送失敗を成功扱いする再試験をしていない。従って以下はすべて未取得である。

- 全曲音声bytesとSHA-256
- full-track decodeと機械解析
- 三previewの全曲内絶対offset
- preview／full一致度
- 版間1.947秒差の原因

Apple Music previewの既存約195.05秒相対鎖と限定区間分析を、全曲結果で置換していない。

## 5. 並行研究本文を直接読んだ結果

5 branchのhead、対象README／code blobは2026-09-21 checkpointから変わっていなかった。名称や過去要約ではなく、各refの本文と対象codeを再読した。

- Jeff Mills: 36章の非連続previewには速度族、発音密度、明るさの独立候補があるが、章境界のentry／exit／overlapは未測定。Autechreの遷移へ移せるのは「単一強度軸へ潰さない」という検査方針まで。
- Charlie Hunter: 合成couplingは複数voiceへ役割別の異なる変化を返す因果topologyを検査する。Hunter録音、MIDI、onset、奏法数値、聴感評価を含まない。
- J Dilla: 合成time-fieldと匿名WAV packは一括swingと声部別関係の差を機械的に作る。Dilla実音源のonset測定、参加者回答、歴史的再現は未取得。
- Aphex Twin: 公式Bandcampの3曲はfull streamのhashと信号測定を持つ。取得経路と権利面が異なるため、Autechre全曲の取得許可や版同一性の代替証拠にはしない。
- 独立DRUM: `globalTick`を共有しながらvoice別の局所長、rotation、決定的chance、manual recordingを使う。次eventを現在・過去・他voiceの状態から変える履歴因果はなく、Autechreの状態遷移を実装済みとは扱わない。

## 6. 取得・分析・未検証・設計候補

| 区分 | 今回の結論 |
| --- | --- |
| 取得事実 | 三catalog identityを再確認。GB Anti default 30秒assetだけ交代。現旧previewを取得しhash・decodeを固定 |
| 分析 | 現GB Antiは旧30秒／90秒先頭とoffset 0、相関約0.999968。同一区間の再エンコード／再包装が最も整合的 |
| 未検証 | 全曲、絶対offset、bar境界、反復melody、全bar非同一性、生成因果、AE_LIVE同条件比較 |
| 設計候補 | catalog／delivery asset／decoded signal／content alignmentの四層manifest。製品未採用 |

## 7. 保存境界

Gitへ保存するのは本報告、source manifest、数値監査、checkpoint manifest、README追補だけである。一時取得したM4Aとdecoded PCMはGitへ追加しない。

