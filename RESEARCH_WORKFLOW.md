# 複数同時研究のGit運用

このリポジトリでは、製品実装と機材・UI・音響の研究を同時に進める。研究同士を一つの作業ブランチや一つの共有メモへ混ぜない。

## 研究単位

研究ごとに一意の `research-id` を付ける。

```text
YYYYMMDD-短い英数字名
```

各研究は次の組で分離する。

- ブランチ: `research/<research-id>`
- 記録: `research/<research-id>/README.md`
- 必要なら同じディレクトリ配下に比較表、画像、試作を置く
- PR: 一研究につき一件。別研究の変更を混ぜない

## 開始

1. `main` の最新コミットから `research/<research-id>` を作る。
2. READMEに目的、観測、推論、設計への採否を分けて書く。
3. 実装を触る場合は対象パスを列挙する。
4. 同じ対象パスを触る既存PRまたは現役修理ロックがあれば、そのパスの変更は止める。

## 研究記録の最低項目

- `research-id`
- 研究対象と現在の問い
- 一次資料または実機観測
- 観測できた事実
- 推論・仮説
- Field Looperへ採用する点／採用しない点
- 触る実装パス
- 依存する研究
- 失効した判断
- 未検証事項
- 更新日時

事実、ユーザーの実機評価、推論を混ぜない。訂正は古い記述を黙って消さず、何が失効したかを残す。

## 統合前の全体監査

統合島を更新する前に、同じ時点で次を取得する。

1. default branchと現在head
2. 全ブランチ
3. open・merged・closedを含むPR履歴
4. 対象研究README、実験結果、テスト
5. 競合する製品コードと現役修理ロック

状態を次のように分ける。

- `main`: 現行Git状態
- branch / PR only: 保存済み研究または試作
- referenced only: 名称だけで本文未取得
- implemented-unverified: コードはあるが必要な実機検証前
- validated: 対象実機・ブラウザ・音響条件で検証済み

他研究の要約や名称だけから、未取得研究の内容、research-id、採用状態を作らない。監査時刻、`main` SHA、取得できた範囲、被覆欠落を `integration/STATUS.md` に残す。

## 統合

- 全体の方向、採否、現在位置は `integration/` を正本とする。
- 各研究は統合島に記録されるまで製品採用済みと扱わない。
- 統合判断では `.github/pull_request_template/integration.md` を使う。
- 研究PRは `main` の最新状態へ追従してから統合する。
- 研究記録だけのPRは対象ディレクトリが固有なら並行統合できる。
- 製品コードを含むPRは変更パスが重ならない場合だけ並行統合できる。
- 同じ製品コードを触る後発研究は、先行変更後に再取得・再検証する。
- 複数研究から一つの機能を作る場合、各研究を先に保存し、その後 `integration/<機能名>` で統合する。
- `main` へ未検証の試作を直接入れない。

## 研究候補

Loopy Pro、RC-505mkII、KAOSS、Strymon、Dedalus、Teenage Engineering、Elektron、SOMA、Skulptur、Microcosm、Chroma Console、Things Motor、Abbey Road等は別研究として扱う。製品へ採る内容だけを統合島で判断する。
