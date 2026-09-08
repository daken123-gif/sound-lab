# 検証結果

日付: 2026-09-07 UTC

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
