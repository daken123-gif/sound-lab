# 検証結果

最新確認: 2026-09-08 UTC。自動検査は37件通過したが、実YouTube音声取得は今回も失敗した。全体の完成判定は **QUARANTINE（実取得未達）**。最新の実行記録は末尾に追記し、以下の2026-09-07の記録を保存する。

以下の初回検証日付: 2026-09-07 UTC

## 実装・通信

- MCP SDK `1.30.0`、yt-dlp `2026.8.19`、yt-dlp-ejs `0.8.0`。
- NumPy `2.3.5`、SciPy `1.17.0`、ffmpeg `6.1.1-3ubuntu5`。
- 実際のStreamable HTTP `/mcp`でinitialize、tools/list、tools/callを実行。
- `search`、`fetch`、`acquire_audio`、`job_status`、`analyze_audio`の5 toolが返った。
- `search/fetch`のreadOnly annotationと、取得toolのwrite annotationを確認。
- 不正IDをMCP経由で拒否。
- 有効な入力でジョブIDを返し、複数回のstatus呼出しを経てterminal resultまで取得した。

初回の実通信では、FastMCPのrequest/session lifespanで共有DBを閉じてしまう不具合と、裸の`dict`型からstructuredContentが生成されない不具合を検出した。DBの寿命をサーバープロセス全体へ変更し、構造化出力を明示した後、同じMCP試験を再実行してジョブ開始・結果読取りが通った。

実行環境では別execのloopback endpointへ接続できなかったため、`smoke_mcp.py --spawn`でserverとclientを同じ実行環境に起動した。この試験はChatGPTからの接続試験ではない。

## YouTube実取得

`smoke_mcp.py --spawn --live`が実際に返したジョブ:

```json
{
  "job_id": "b82c25e799cd4134b4740669264598a6",
  "video_id": "mdhtm6qjmhU",
  "channel_id": "UCBUAlfIrcw1f0c4qGrYn3xA",
  "title": "Flutter",
  "channel": "Autechre - Topic",
  "duration_s": 600,
  "stage": "stream_url_resolved",
  "status": "failed",
  "error": "network_timeout",
  "audio_retrieved": false
}
```

このjobは一時smoke用server内で実行され、試験終了後にその一時データ領域は削除された。上記は実行出力の記録であり、現在も照会できる稼働jobとは主張しない。

YouTube音声bytes・全体decode・YouTube音源の解析は未達。MCPが動くことを音源取得成功へ読み替えない。前回の配信サーバーtimeoutはこの実行環境でも継続している。

## 自動検査

`python -m pytest -q`: **13 passed**。

- 任意URL・path・不正video IDの拒否。
- error返却から署名URLやIPを排除。
- failed jobを解析へ渡さない。
- request key再送の重複抑止と異なる入力の拒否。
- 音声bytesのない「decoded」を成功にしない。
- 実ffmpegで全体decode、破損音声と尺不一致の拒否。
- データディレクトリ二重起動の拒否。
- 再起動後のfailed保持と未終了jobのinterrupted化。
- 合成440 Hz音源を取得済みfixtureとして渡し、hash照合・共通窓解析・保存結果まで接続。
- channel IDまたはvideo IDが異なる場合はダウンロード前に停止。

合成音試験の初版では、ffmpegのsine generatorから作ったPCM16入力を理想正弦波として扱い、スペクトル重心が期待値と一致しなかった。刺激をNumPy生成のfloat32正弦波へ変更して再試験した。実音楽への精度保証に使っていない。

## 到達点

| 対象 | 状態 |
| --- | --- |
| コネクタコード | 実装・ローカル検証済み |
| MCP HTTP通信とジョブ制御 | 実呼出しで確認済み |
| ローカル合成音から共通解析 | 確認済み |
| YouTube実音声取得 | QUARANTINE: URL解決まで、bytes未取得 |
| 検索toolのYouTube実検索 | 未試験 |
| ChatGPTへのコネクタ登録 | 未実施 |
| 別hostへの配備・Secure MCP Tunnel | 未実施 |

現在の提供形態はprivateな単一利用者用サーバー。公開サービスとしての認証・多利用者分離・配備品質は検証範囲に含めない。

## 2026-09-08: アカウント分離・試験判定の修正と再実行

修正ブランチ: `research/20260908-youtube-acquisition`。基点は `bbc0b53e5cd6c773ba407acebc685d1e087c4dd6`。変更対象はこのコネクタのディレクトリ内。

### 修正した実装

- guest専用workerでCookieファイル、ブラウザ、netrc、ユーザー名・パスワードを取り込まない。既知のアカウントCookie、共通・個別リクエストのAuthorization等を送信前に拒否し、外部yt-dlpプラグインの自動読込みを無効化した。公開playerの通常のguest cookieと組込みEJS処理は利用する。
- ボット確認、ログイン要求、HTTP 403、HTTP 429と、通信タイムアウト、ローカルdecode／解析タイムアウトを分けた。終端エラーの後にアカウント認証へ切り替えない。
- 選択した形式、受信byte数、既知の診断コードを残す。署名付き配信URL・Cookie・生の外部エラー文は返さない。
- 検索・情報取得も取得／解析と同じ2枠のworker上限に含めた。256 MiB上限を転送中・decode前・成功判定時に確認し、欠落fragmentを飛ばさない。
- manifest、実音声hash・byte数・尺・video／channel IDを照合し、解析直前にも入力音声を再検査する。保存先の作成失敗は終端の失敗状態にする。
- `smoke_mcp.py --live`は取得、全体decode、同一hashの解析、解析窓の全尺被覆まで確認する。失敗・中断・証拠不足を終了コード1にし、未到達の解析を`not_requested`にする。実ジョブと機械可読reportを保持するオプションを追加した。

前のsmokeはジョブが失敗してもCLIが正常終了する欠陥を含んでいた。2026-09-07の記録は既に音声取得失敗として記載しているが、旧CLIの終了コードを取得成功の証拠に使う判断は失効する。

### 自動検査

`python -m pytest -q`: **37 passed in 3.90s**（コネクタ21件、MCP smoke判定16件）。Nodeは実測 `v24.19.0`。その他の主要依存バージョンは上記の初回記録と同じ。

既存の実ffmpegによる全体decode・破損音声検査・合成音の共通解析接続に加え、次を検査した。

- 合成の認証Cookie／ヘッダーがネットワーク送信前に拒否されること。構築後に共通ヘッダーへ追加された認証も拒否すること。
- guest処理へのボット確認応答でダウンロードへ進まないこと。
- ローカルHTTPサーバーがContent-Lengthを返さない場合でも、実yt-dlp転送が受信容量上限を越えた時点で停止し、取得成功manifestを作らないこと。
- 取得後に音声が変更された場合に解析を開始しないこと、worker枠の共有、保存先作成失敗の終端化。
- MCP smokeの取得失敗、解析失敗、hash・video・channel・尺・窓の欠落、ジョブ中断と時間切れで試験が失敗すること。CLIの終了コードも検査した。

初回のクリーンな作業ツリーではpytest一時ディレクトリの親`.data`が無くsetupが失敗した。既存データ領域に依存しない`.pytest-work`へ変更後、上記37件が通過した。

これらは実装と試験判定の検証であり、合成音やローカルHTTP転送をYouTube実音声取得の証拠には数えない。

### 実MCPからのYouTube再取得

実行: `smoke_mcp.py --spawn --live --data-dir .data/live-20260908 --report .data/live-20260908-report.json`。

| 観測 | 結果 |
| --- | --- |
| 開始／終了（UTC） | `2026-09-08T01:01:46.388640` ／ `2026-09-08T01:02:46.706731` |
| ジョブID | `88af75df56984edfbe5032f3910cb9bd` |
| video／channel | `mdhtm6qjmhU` ／ `UCBUAlfIrcw1f0c4qGrYn3xA` |
| 作品・公式表示 | Flutter / Autechre - Topic / Anti / ℗ Warp Records / 600秒 |
| MCP initialize・不正ID拒否 | 通過 |
| 取得状態 | `failed` |
| 最終段階 | `stream_url_resolved` |
| 選択形式 | `251` / WebM / Opus / HTTPS |
| 配信情報中のfilesize | `10,224,074` bytes（実受信量ではない） |
| 実受信量 | **0 bytes** |
| 認証方式 | `guest`。開始時Cookie数0、ブラウザ読込み・netrc利用なし |
| エラー／診断 | `network_timeout` ／ `["network_timeout"]` |
| 音声ファイル・decode・取得manifest | なし／未到達／なし |
| 解析 | `not_requested` |
| 試験結果／CLI終了コード | `failed` ／ **1** |

ジョブ作成は`01:01:46.442984 UTC`、`stream_url_resolved`を書いたprogressファイルのmtimeは`01:02:22.590337 UTC`。URL解決まで約36.15秒、その後、試験終端まで約24.12秒だった。この工程時間を「15秒の再試行4回」とは解釈しない。

試験後にDBとprogressを読み戻し、`received_bytes=0`、音声ファイル不在、失敗の永続化を確認した。ジョブDB・progress・reportは指定した作業データ領域に残した。サーバープロセスは終了しているため、現在稼働中のChatGPTコネクタや永続ホスティングとは主張しない。

今回の証拠で確定できる停止点は、音声URLを選択した後の転送処理。DNS、TLS、配信サーバーの応答、実行環境の通信経路のどれが根本原因かは、この試験の記録だけでは確定できない。ボット確認・HTTP 403・アカウント認証不足を今回の直接原因とは記録しない。MCPの入口が動いたこと、モデルを変更したこと、別の取得エンジンが存在することをもって解決済みとはしない。

別担当のソース確認では、`extract_info(download=False)`でもyt-dlpが形式ごとのヘッダーを計算し、選択形式のURL・ヘッダー・転送設定を返却infoへ反映することを確認した。workerはこのinfoを縮約せず同じydlの`process_info()`へ渡し、cookiejarも維持する。`retries=0`はHTTP downloaderへ渡っていた。接続と読取りのsocket timeoutは工程全体の上限ではない。この調査で新たに修正すべき転送呼出しの欠陥は特定できず、根本原因の解決とは扱わない。

有料取得サービスへの登録・決済・外部への認証情報移送は行っていない。個人アカウントを用いた追加試験、別hostへの配備、ChatGPTへの登録も未実施。実音声取得と全曲解析が未達のため、全体の完成判定は引き続きQUARANTINE。
