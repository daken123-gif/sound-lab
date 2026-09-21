# Autechre研究更新 — 反復の三軸化と全曲取得境界の再検証

更新日: 2026-09-21 JST

状態: active / 研究記録。製品未採用、音源本体なし

基点: `024d36c32a25fa57e42a7ee37bbc826a2822272b`

対象: `research/20260831-autechre`

## 1. 今回の取得事実

### Autechre本線

remoteの研究branchを取得した時点で、2026-09-14のREADME追補以後に二つのcheckpointが追加されていた。

- 2026-09-16: 1994年の本人発言を基に、発音時刻だけでなく、音価、重なり、音高、複数音の関係を分けて検査する研究ノート。
- 2026-09-20: 同一の250 ms発音列へ50 ms／300 msの音価と220 Hz固定／220・440 Hz交互を組み合わせた合成対照実験。

README本体はこの二件をまだ統合していなかった。今回、保存済みスクリプトを再実行し、環境version文字列を除く科学ペイロードが保存済み`results.json`と完全一致することを確認した。三つの既存ファイルのSHA-256も`CHECKPOINT.json`と一致した。

### 本人発言と新しい公開記事の年代

The Independentの1994-07-19記事では、Sean Boothが`Flutter`について、可能な限り異なるbarを作って連結し、beatを変化させる一方、単純で反復的なmelodyを位置の手掛かりにしたと説明している。

MusicRadarの2021-08-11全文再掲では、Rob Brownは少数のsoundがrhythmを導くと述べ、Seanはnoteを異なる長さ・音高で鳴らすsoundとしてrhythm内で扱うと説明している。同媒体の2026-08-24記事はこの1994年取材の再紹介であり、2026年の新規インタビューではない。

これらは本人の制作説明である。ただし、`Flutter`全barの非同一性や、現在の測定器がbarを正しく分節できることを証明する音響測定ではない。

### 公式公開面

2026-09-21にAutechre公式Bandcampの`AE_2022－`を再取得した。表示は19公演、releaseは2024-12-03、licenseは`all rights reserved`のまま。表示尺が1時間を超える公演は17件、1時間以内はLondon A／Bの2件である。streaming／購入表示を、音源bytesの取得・機械解析許可へ読み替えない。

同ページのshows欄には2026-09-24から2026-10-24までの日程が表示されるが、日程から新set、録音、cell構造を補完しない。`elseq 1–5`の公式storeページは今回403で本文を再取得できず、前回保存した2026-10-02予定という状態を更新しない。

## 2. 合成対照から得た新しい分析

同じ発音時刻を共有する条件でも、短音は占有20%・重複0%、長音は占有100%・重複20%になった。それにもかかわらず、220／440 Hz交互条件で短音と長音の正のスペクトルフラックス相関は`0.9988477088`だった。短音の固定音高／交互音高も`0.9998724523`だった。

この値が示すのは、立ち上がり中心の一変量へ畳むと、隙間から重なりへの変化や、変化した周波数位置を見失えることである。相関値を「音楽が99.9%同じ」「知覚上同じ」「同じ反復」と読むことはできない。

今後、作品内の反復を少なくとも次の三軸に分ける。

```text
REPETITION_VECTOR {
  onset_axis       // 発音時刻・局所周期
  occupancy_axis   // 音価、空白、重なり、残響
  frequency_axis   // 音高ではなく、まず周波数分布とその遷移
}
```

これは`Flutter`実音源から三軸を測り終えた結果ではない。以前のpreview測定は削除・上書きせず、onset／band-energyを観測した限定結果として保持する。次に既存のFlutter測定コードと入力を回収できた場合、同じ合成対照をその分析器へ通し、どの軸を捨てるかを先に検査する。

## 3. 因果・状態遷移への接続

一つの高い相関やevent密度を一つの状態名へ変換する設計は弱い。状態は、各軸の値だけでなく、どの軸が保持され、どの軸が動いたかを持つ必要がある。

```text
TRANSITION_CANDIDATE {
  invariant_axes
  changed_axes
  source_state
  destination_state
  trigger_or_intervention
  evidence_window
}
```

`Flutter`について現在観測済みなのは、全曲内offset不明のpreview鎖における短周期候補、帯域状態、event候補の局所変化までである。反復するmelody、全barの非同一性、生成規則、因果方向は未検証。

`AE_LIVE`へは同じ軸を公演間比較に使えるが、19公演の音声を取得しておらず、短い2公演だけを代表群にしない。公演ごとの入口、滞在、回帰、停止、回復という既存の記述は、共同分析と本人発言に基づく候補であり、今回の音響実測で確定したものではない。

## 4. 並行研究本文の再取得

Jeff Mills、Charlie Hunter、J Dilla、Aphex Twin、独立DRUMのremote headと本文／code blobを再取得した。2026-09-14 checkpointに記録されたhead・blobから変更はなかった。

- Jeff Mills: 36章preview地図は、床を保った密度の変化候補を持つ。ただし非連続previewであり、実際のentry／exit／overlapは未測定。
- Charlie Hunter: 合成couplingは同一gestureが役割別に異なる結果を返すことを検査する。Hunter録音の測定、本人の奏法再現、聴感評価ではない。
- J Dilla: 合成time-field／blind packは一括swingと声部別関係を分ける。Dilla実音源のonset測定、参加者回答は未取得。
- Aphex Twin: 公式Bandcamp公開stream 3曲のhash固定と信号測定を持つ。この取得事実をAutechre音源の取得許可へ転用しない。
- 独立DRUM: 四voiceの局所長、決定的hash条件、手動recordingを持つが、全voiceは一つのglobal tickでscheduleされる。Autechre研究の履歴state、voice間因果、可動域遷移が実装済みとは扱わない。

これらは名称や要約からの補完ではなく、`sources.json`に固定したremote branch headとblob本文を読んだ結果である。

## 5. YouTube公式Topicの実取得再試験

2026-09-21 UTC、remoteのYouTube取得branch `0e10051483bc800a8d7b77ab3284a8fb6c36477f`をdetached worktreeへ取り出し、同branchが固定する`mcp 1.30.0`、`yt-dlp 2026.8.19`、`numpy 2.3.5`、`scipy 1.17.0`でlive smokeを再実行した。個人account、browser cookie、netrc、proxy、購入、外部serviceは使用していない。

| 項目 | 観測 |
| --- | --- |
| video / channel | `mdhtm6qjmhU` / `UCBUAlfIrcw1f0c4qGrYn3xA` |
| metadata | Flutter / Autechre - Topic / Anti / 600秒 / ℗ Warp Records |
| 認証 | guest |
| 解決形式 | format 251 / WebM / Opus / HTTPS |
| 表示filesize | 10,224,074 bytes |
| 最終stage | `stream_url_resolved` |
| error | `network_timeout` |
| 実受信 | **0 bytes** |
| decode / audio hash / manifest | 未到達 / なし / なし |
| analysis | `not_requested` |

作品metadataとstream URLの解決は、音源取得ではない。全曲音声、全曲hash、previewの全曲内offset、一致度は引き続き未取得。従って既存のApple Music preview hashと約195.05秒の相対鎖は保持し、全曲結果で上書きしない。

## 6. 未検証と次の継続点

- `Flutter`三previewの全曲内絶対offset、full-track一致度、版間1.947秒差の原因。
- 全曲の発音時刻、音価／空白／重なり、周波数分布を同じ時間軸で測った`REPETITION_VECTOR`。
- 本人説明の「異なるbar」と音響的bar分節の一致。
- `AE_LIVE`複数公演を同じ取得・解析条件で比較した状態遷移。
- 合成対照の複合音、位相、残響、非整数周期、音量統制、人間の聴取に対する一般性。
- YouTube転送が0 bytesで停止する根本原因。watch page取得成功だけではaudio CDNの転送成功を意味しない。

## 7. 変更境界

- 変更: Autechre研究READMEと、このcheckpointの研究記録。
- 未変更: Apple Music previewの既存hash・測定値。
- 未保存: 音源本体、preview本体、署名付き配信URL、cookie。
- 未変更: `field-processor/`、`prototype/`、`integration/`、`main`、並行研究branch。
- 未判断: 製品採用、integration採用、UI mapping。
