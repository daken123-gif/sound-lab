# YouTube音源研究コネクタ

ChatGPTから動画検索・動画情報取得・音声取得・全体decode・共通解析を呼び出す、画面を持たないMCPサーバー。Python MCP SDKのFastMCPを使う。OpenAIのtool-onlyサーバー／search・fetch仕様に合わせ、既存のNumPy／SciPy解析器を後段へ接続した。

## 呼び出し

| Tool | 役割 | 結果 |
| --- | --- | --- |
| `search(query)` | YouTube候補を最大5件検索 | `id / title / url`。公式性は別判定 |
| `fetch(id)` | 1動画のchannel ID・尺・説明を取得 | 標準`id / title / text / url / metadata`。音声取得ではない |
| `acquire_audio(video_id, expected_channel_id, request_key)` | 公開音声を取得し全体decode | ジョブID。channel相違、取得・decode失敗は成功にしない |
| `job_status(job_id)` | 進捗・結果を読む | `queued / running / succeeded / failed / interrupted`、段階、manifestまたは解析結果 |
| `analyze_audio(source_job_id, request_key)` | 検証済み音源を共通30秒窓で測定 | 解析ジョブID。hash・尺確認を再実行 |

同一`request_key`・同一入力の再送は同じジョブを返す。失敗後に再試行する場合は新しいkeyを使う。異なる入力でkeyを再使用するとエラー。同時workerは2、未終了ジョブは最大8。音源は最大1時間・取得器の上限256 MiB。workerは180秒でprocess groupごと終了する。長時間音源はこの期限で取得できない場合がある。

取得音声はサーバー側の`.data/`に残り、ChatGPTへ返すのはmetadataと測定値。音声本体や署名付き配信URLはtool出力・Gitに含めない。データディレクトリの二重起動は拒否し、再起動時の未終了ジョブは`interrupted`へ変更する。成功と偽って復帰させない。単一利用者のprivate server用であり、複数利用者のtenant分離・公開サービス用OAuthは実装していない。

## 起動

Python 3.12、ffmpeg/ffprobe、Node 22以上を用意し、リポジトリ内のこのディレクトリで実行する。既存の共通解析コードを参照するため、このディレクトリだけを切り離さない。

```bash
python -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python server.py
```

既定はstdio。ローカルHTTPで接続する場合:

```bash
.venv/bin/python server.py --transport streamable-http
```

接続先は`http://127.0.0.1:8841/mcp`。HTTPサーバーはloopbackに限定し、DNS rebinding保護も有効。`YOUTUBE_DATA_DIR`または`--data-dir`でGit外の永続領域を指定できる。`YOUTUBE_SYSTEM_CA=1`を既定にしてシステムの信頼ストアを使う。certifiを使う環境では`YOUTUBE_SYSTEM_CA=0`。TLS検証は無効化しない。

YouTubeのログイン情報、購入制限回避、DRM回避、PO Token生成、proxy切替機能は持たない。指定したvideo ID以外の任意URLを取得するtoolにもしていない。YouTubeの公開player・配信サーバーへ通常接続できる環境で動かす。

## 検証

```bash
.venv/bin/python -m pip install pytest==8.4.2
.venv/bin/python -m pytest -q
.venv/bin/python smoke_mcp.py --spawn
.venv/bin/python smoke_mcp.py --spawn --live
```

`--spawn`はサーバーとMCP clientを同じ実行環境で起動し、終了時に停止する。`--live`は公式Topic「Flutter」の実取得ジョブまで呼ぶ。失敗も実結果として出力するので、コマンド終了0だけで音声取得成功と判断しない。`live_result.status=succeeded`と`stage=decoded`、実hash付きmanifestを確認する。

テストでは、偽の「decoded」応答、欠落音声、別入力のkey再使用、誤channel、再起動、中断、任意URL／path入力、破損音声・尺不一致を検査する。合成音を使う後段接続試験はYouTube取得の証拠には数えない。

## ChatGPTへの接続

このサーバーはstdioまたはStreamable HTTPで動作する。ChatGPT側には、private serverへ接続するSecure MCP Tunnel、または適切に認証されたHTTPS MCP endpointの登録が必要。現在の実装はprivate tunnel／local use向けで、無認証のままpublic internetへ公開しない。

接続・配備の実施先は、この会話にはまだ提供されていない。ChatGPTへの登録、別hostへの配備、Secure MCP Tunnelの発行は未実施。Gitにコードがあることをインストール済み・接続済みとは扱わない。

公式手順:

- https://developers.openai.com/plugins/build/mcp-server
- https://developers.openai.com/plugins/plan/tools
- https://developers.openai.com/plugins/deploy/connect-chatgpt
- https://github.com/yt-dlp/yt-dlp/wiki/EJS

## 今回の結果と未完了

[VALIDATION.md](VALIDATION.md)に実行結果を記録する。前回のCDN timeoutは、MCPという入口を作るだけで消えるとは判断しない。コネクタ実装、MCP通信、YouTube実bytes取得、ChatGPT接続を別々に検証する。
