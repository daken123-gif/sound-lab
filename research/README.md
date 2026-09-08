# Research

ここには機材、音響処理、演奏UIごとの研究を分離して保存する。

音楽そのものの取得・解析は、全アーティスト共通で [音源取得・解析方針](music-analysis/SOURCE_POLICY.md) を参照する。2026-09-07、Shazam／Apple Music previewを保持したまま、公式Bandcampを正式な全曲検証経路へ追加した。研究ブランチが古い場合も、この方針は `main` の最新版を読む。

新しい研究は `research/YYYYMMDD-slug/README.md` を起点にする。同名テーマでも問いが異なる場合は別の `research-id` を使う。研究の開始・更新・統合規則は [RESEARCH_WORKFLOW.md](../RESEARCH_WORKFLOW.md) を参照する。

進行中研究を別の会話・端末から再開する場合は、最初に [CURRENT.json](CURRENT.json) を読み、そこから同じGit commit上の研究本文へ進む。会話内の古い要約はGitの新しい版を上書きしない。

## 状態

各READMEの冒頭に次のいずれかを置く。

- `active`: 研究中
- `integrating`: 製品実装へ統合中
- `validated`: 実機または必要な検査で確認済み
- `superseded`: 後の研究または訂正により失効
- `paused`: 未解決のまま停止

`active` を `validated` として扱わない。
