# Autechre研究追補 — 版同定の回復、ライブ比較の選択偏り、初期の因果関係

- research-id: `20260831-autechre`
- 確認日: 2026-09-14 JST（2026-09-13 UTC）
- 基点: `8ed5965e44127be540c726178ebdeb7eb9612af9`
- 区分: 取得事実／既存記録の再取得／分析／未採用候補。音源本体はGitへ保存しない。
- 対象: 研究記録のみ。製品コード、他研究、integration、mainは未変更。

## 1. FlutterのISRC未取得を部分解消

Shazam接続のApple Music Catalog `getsong`で、次の三つを現在のcatalog実体として取得した。周囲の音を聴かせた指紋認識ではない。

| storefront・版 | track ID | ISRC | catalog尺 |
| --- | --- | --- | ---: |
| GB / Anti - EP | 292743285 | GBBPW9400118 | 597733 ms |
| JP / Anti - EP | 314910098 | GBBPW9400118 | 597733 ms |
| GB / EPs 1991 - 2002 | 420210312 | GBBPW9400118 | 599680 ms |

[GB Anti](https://music.apple.com/gb/album/flutter/292743188?i=292743285)、[JP Anti](https://music.apple.com/jp/album/flutter/314910095?i=314910098)、[GB EPs](https://music.apple.com/gb/album/flutter/420210242?i=420210312)。

README section 20・25の「ISRC未取得」は、今回の三catalog項目に限って失効する。旧取得時点の記録は削除しない。旧Shazamウェブdeep linkの誤解決原因は未解明であり、今回APIが正しく返ったことをウェブ側の修理と呼ばない。

**分析:** 共通ISRCは録音同定を補強するが、同じPCM、同じマスター、同じ頭出しを保証しない。約1.947秒の尺差と、旧preview照合でのPCM相関差は残る。ISRC一致を理由に版を統合しない。

## 2. 既存previewの実バイトを再取得・検査

README section 24に固定されたGBの90秒enhanced preview 2本を、同じApple CDN URLから取得した。

| preview | bytes | SHA-256 | 今回の確認 |
| --- | ---: | --- | --- |
| GB Anti | 3122487 | 4132908b22a6407d5d30b42c3618ecafa8817beeb7dc65b4609354d5aeb5cc89 | 旧hash一致・全preview decode成功 |
| GB EPs | 3117352 | ab5d3f767f96e3d62e4abd494654e75974f2579542e113ae8fc0a20d59ebc751 | 旧hash一致・全preview decode成功 |

両方AAC／44.1 kHz／stereo、container尺89.977324秒。検査はSHA-256、ffprobe、ffmpeg `-xerror`による全previewデコードで行った。今回新しいonset／帯域測定はしていない。JP 90秒音源は今回再取得していない。

**保持する既存結果:** 三previewからなる約195.050839秒の相対鎖、各帯域・event測定、相対offsetは旧研究記録として保持する。今回の2本のhash一致はその入力の再現性を補強するが、相対鎖の相関計算を再実行した証拠ではない。全曲内offset・全曲hash・全曲との一致度はいずれも未取得。

取得URL、三catalogの返却フィールドは `sources.json`、実検査結果は `catalog-preview-audit.json`。

## 3. AE_LIVE比較には通信障害とは別の長さ制約がある

[公式AE_2022－](https://autechre.bandcamp.com/album/ae-2022)は今回も19録音を掲載。公開ページのrelease表示は2024-12-03。2025／2026録音がこのページへ追加されたことは確認していない。

### 取得事実と計算

YouTube取得研究の固定commit `0e10051483bc800a8d7b77ab3284a8fb6c36477f` の `worker.py` は、取得対象を `0 < duration <= 3600` に制限する。公式19録音の表示尺を秒へ変換してこの条件と比較すると、**17本が上限超過**、通るのはLondon A（3588秒）とLondon B（3573秒）の2本だけになる。

これは公式catalogとコードの静的突合である。19本のYouTube動画を同定・取得試験した結果ではない。Bandcampへこのworkerが対応するという意味でもない。

### 比較研究への影響 — 分析

- 2024年の8録音はすべて長さ条件の範囲外。現状で通る音源だけ集めると、長い公演だけでなく後期の比較群全体を失う。
- London A/Bの表示尺差は15秒だが、長さが近いことから経路・入口・内部状態の同一性は導けない。
- Londonの二本は同日の比較対候補として価値がある。ただしこれだけを2022年以降の代表標本にはしない。
- README section 14の「世代内分散を先に測り、世代間差と分離する」計画は、現行worker単独の条件では必要な群を揃えられない。

**未採用候補:** 長尺対応を別工程で行うなら、単に上限を外すのではなく、容量上限、全尺decode、途中欠落、解析窓の末尾被覆、区間間の特徴量連続性を保つ必要がある。最初の3600秒だけ切り出して「全公演」とはしない。本追補ではコード改修を行わない。

## 4. 新しく取得した公開記事は、1994年の発言だった

2026-08-24公開の[MusicRadar記事](https://www.musicradar.com/artists/there-isnt-one-thing-about-the-gear-that-were-using-now-that-we-dont-understand-autechre-on-their-diligent-tech-learning-ethos-and-very-first-workflow)から、2021-08-11掲載の[Future Music原インタビュー再掲](https://www.musicradar.com/news/autechre-classic-interview)へ遡った。取材年は1994年。三つの日付を分け、現行rigの証拠にはしない。

**本人発言として取得:** 当時、音素材がリズムを方向づけ、R-8でEPSを同期・シーケンスし、舞台ではSeanとRobが機器操作を分担していた。公演ごとにsetを再プログラムして変えるとも述べる。

**分析:** 因果関係の演奏はMax期に突然発生したものではない。初期には「素材の性質→リズムの選択」「機器間の同期→二人の手動操作」「公演間の再プログラム」があり、後期資料では可動域・cell内変形・手動遷移へ拡張される。ただし初期の公演間改訂を、後期の公演中のopen-ended生成と同じ仕組みとは扱わない。

README section 12の「音声列→関係→状態遷移」という歴史モデルは、関係が後から初めて生じたという直線史としては使わない。**以前からある複数層のうち、何を固定し、どこを演奏可能にしたかが変わった**という非直線的な読みを追加する。これは文献解釈であり音響実証ではない。

## 5. 並行研究の現在差を本文・コードで確認

固定commit・blobは `sources.json` に記録。以下は他研究の取得済み本文が述べる状態であり、今回その音源試験を再実行したという意味ではない。

| 対象 | 今回確認した状態 | Autechreへの接続と制限 |
| --- | --- | --- |
| Jeff Mills | headは変化したがREADME blobは前回と同じ。Liquid Room全36章preview地図 | 章数が揃うことと連続音源の被覆は別。入口・撤去・重なりの実測へ読み替えない |
| Charlie Hunter | head・README blobとも前回と同じ。合成tone比較と既知のenergy交絡 | 結合の聞き分けを本人演奏や嗜好優位の証拠にしない |
| J Dilla | head・README blobとも前回と同じ。匿名聴取パック、回答未取得 | 生成可能なタイミング差と人間が知覚する関係を区別する |
| Aphex Twin | READMEが更新。#3／4／VordhosbnのMP3 hash・全尺相当の測定記録が追加 | Autechre README section 24.6の「初版以降の音源実測更新なし」は失効 |
| 独立DRUM | head・drum-engine.js blobとも前回と同じ | global tick、voice別周期、hash条件、手動録音はある。結果event履歴による次状態の制約を実装済みとはしない |

Aphexの `r02-sources.json` と測定コードも読んだ。Autechreはmono 22.05 kHz・2048/256窓、Aphex側はstereo由来のスペクトル・2048/512窓と100ms RMSを使うため、既存数値をそのまま一つの順位表へ並べない。Aphex側の取得記録にはhashとbyte数があるが、機械取得・解析の利用条件を明示する欄はない。他研究の「取得済み」をAutechreの取得許可へ転用しない。

### 設計候補の更新

状態遷移の記録には、音の特徴だけでなく、変化の担い手を併記する候補を残す。

- 素材から生じた制約
- 演奏者のその場の操作
- 公演間の再プログラム
- 同じ規則から生じる公演内の分岐
- 取得経路が生んだ標本の欠落

最後の項目は音楽の性質ではなく観測条件である。欠測を作品の「静けさ」「短さ」「類似性」に誤変換しない。

## 6. 全曲取得の到達点と未取得境界

- 前回のYouTube試験はGit上のVALIDATION本文で再確認した。2026-09-08 UTC、URL解決後に `network_timeout`、実受信0 bytes、decode・解析未到達。
- 今回はYouTubeページのウェブ取得も失敗。前回workerのライブ試験を今回再実行したとはしない。新たなYouTube音声hashはない。
- 公式Bandcamp Antiの通常再生・購入経路は確認。取得・機械解析の許容範囲を今回確立していないため、フル音源は取得しない。購入、個人アカウント利用、認証移送は行っていない。
- AE_STOREの直接本文取得は失敗。検索表示にはelseqの2026-10-02予定が残るが、発売済み・変更なしと確定しない。
- RA 2016記事はタイトルと日付までで本文未取得。検索断片やReddit転載を代わりの本人本文にしない。
- 全曲offset、全曲内代表性、bar非同一性、AE_LIVE間の音響差は未検証。

次の有効な継続点は、許容される正規フル音源経路の確立、長尺制限の別工程での評価、版別previewと全曲の照合。今回のISRC・hash検査・長尺被覆監査はこの条件が未解決でも有効な研究更新であり、長期研究の完了を意味しない。

