# Bandcamp共通取得経路とYouTube取得診断

検証日: 2026-09-07 UTC

## Bandcamp: 取得・全体decode・共通窓測定を確認

- 入力: https://autechre.bandcamp.com/album/anti のAutechre「Flutter」。公開playerの`mp3-128`。
- Bandcamp track ID: `3691941194`。
- 取得bytes: `9,564,577`。MP3、44,100 Hz、stereo。
- SHA-256: `0e348e91e3ed3d7c911506c82dfe529c73e59d4917ea70ff8d7bda38e2b09f1e`。この会話の前回取得hashと一致。
- ページの内部metadata: `597.733 s`。
- `ffmpeg 6.1.1-3ubuntu5`、`-xerror`付きの全体decode成功。16 kHz検査PCMは`597.733375 s`、44.1 kHz解析PCMは`597.7333333333333 s`。
- 共通校正済み特徴による30秒窓19個＋最後の27.733333秒窓1個、合計20窓。先頭0秒から末尾まで隙間・重複なし。
- 最初の30秒をfloat32 WAVに取り出して既存`analyze_previews.py`でも測定し、新しい窓処理の全10出力指標と表示桁で一致することを確認。比較からfile名と旧scope文だけを除外した。

同じbytesでも前回応答のデコード尺`597.7349375 s`とは約1.6 ms違う。今回の実行条件と測定値をmanifestに固定し、前回値を再現したとは主張しない。音声同一性は元bytesのhash一致により判定した。

記録:

- `bandcamp-flutter-manifest-20260907.json`: 取得実体、版、hash、codec、実測尺。
- `bandcamp-flutter-windows-20260907.json`: 全20窓、指標、解析コードhash、依存version。
- `acquire_bandcamp.py`: 公開stream取得、artist/title照合、全体decode、manifest生成。
- `analyze_source_windows.py`: hash・尺照合、連続窓による既存特徴測定。

この実行は全Bandcampカタログの可用性、元masterの忠実再現、Apple previewと同一masterであることを証明しない。Apple previewの絶対offset照合は未実施。以前のAutechre研究内のevent候補は別定義のため、今回の共通特徴値と直接比較しない。

全曲化で検出した解釈上の注意: 最終570–597.733秒窓はRMS `-70.93 dBFS`だが、既存の相対正規化されたonset検出は226 event候補を返す。微小残響・ノイズまで正規化して候補化する可能性があるため、この末尾値を「演奏が高密度へ戻った」と解釈しない。最初の30秒で既存値と一致することは、ほぼ無音の末尾に対する音楽的妥当性を保証しない。全曲適用での低レベル区間の信頼性校正は未完了として保持する。

## YouTube Topic: 配信URL解決済み、音声bytes未取得

- 入力: https://www.youtube.com/watch?v=mdhtm6qjmhU
- 取得metadata: `Flutter`、`Autechre - Topic`、channel `UCBUAlfIrcw1f0c4qGrYn3xA`、表示600秒。
- 環境: `yt-dlp 2026.8.19`、`yt-dlp-ejs 0.8.0`、Nodeを有効化。
- 最初の試行は同梱certifiの証明書ストアでTLS検証に失敗。
- `--compat-options no-certifi`により実行環境の信頼ストアへ切替え、TLS検証を有効にしたままplayer metadata取得に成功。
- 通常の抽出経路はvisionOS player応答からAAC/Opusの署名付き配信URLを解決。選択したformat 251はOpus、metadata上のfile sizeは`10,224,074 bytes`。このサイズは取得bytesではない。
- `manifest.googlevideo.com`のHLS情報取得は20秒read timeout。
- `rr2---sn-oguesn6k.googlevideo.com`の音声取得は20秒read timeout、1回再試行後も失敗。
- 標準urllibで`Range: bytes=0-65535`を指定した独立試験もread timeout。経過約47.25秒、音声bytes未取得。
- URLの失効時刻は当日19:46:47 UTC、検査は13:51 UTC台であり、この失敗をURL期限切れとは判定しない。
- 追加のWeb player経路はページtimeoutとVisitor Data不足の警告を返し、選択可能な音声formatを得られなかった。

到達状態は `stream-url-resolved / audio-not-retrieved`。YouTubeからの全曲取得は未解決。小さいRangeでも失敗したため転送量だけでは説明できないが、ネットワーク制約、配信側応答、経路障害のどれが根本原因かは未確定。モデル名の変更をネットワーク到達性の証拠にしない。

再試行用の通常コマンド（依存はGit外に導入）:

```bash
python -m yt_dlp --ignore-config --no-cache-dir \
  --compat-options no-certifi --js-runtimes node \
  --no-playlist --socket-timeout 20 --retries 1 --extractor-retries 1 \
  -f bestaudio --no-progress \
  -o 'research/music-analysis/.source-work/%(id)s.%(ext)s' \
  'https://www.youtube.com/watch?v=mdhtm6qjmhU'
```

`no-certifi`はこの環境の信頼ストアに合わせた設定であり、証明書検証無効化ではない。他環境では必要性を確認する。配信URLはstableなvideo URLから再解決する。今回のURL、IP、署名parameter、player応答全体は公開Gitへ載せない。

公式実装資料:

- https://github.com/yt-dlp/yt-dlp
- https://github.com/yt-dlp/yt-dlp/wiki/EJS

## 次に残る検証

1. 取得済みBandcamp全曲とApple previewを照合し、全曲内位置・版差を測る。
2. 別アーティストの公式Bandcampでも同じ取得器を適用し、非公開track、部分試聴、版違いは対象ごとの結果として記録する。
3. YouTubeは配信サーバーへの通常接続が成立した時点で実bytes、hash、全体decodeを検証する。未取得を全曲観測へ昇格させない。
