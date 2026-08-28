# 統合島

ここは Sound Lab 全体の方向、採否、失効、実装境界を管理する正本である。個別研究の要約置場ではない。

## 正本

- `DIRECTION.md`: 現在の製品像と固定境界
- `DECISIONS.md`: 採用、保留、却下、失効の履歴
- `STATUS.md`: Gitで観測できた研究、実装、検証、欠落

研究上の事実は各 `research/<research-id>/README.md`、プロジェクトとしての採否は統合島を正本とする。統合島は、研究本文にない検証結果を作らない。

## 読む順序

1. `integration/DIRECTION.md`
2. `integration/DECISIONS.md` の最新判断と `superseded-by`
3. `integration/STATUS.md` の対象領域
4. 対象研究のREADME、実験、テスト
5. 触るパスと競合するopen PR・修理ロック

## 証拠境界

- `main` にある: 現行製品または現行文書として観測できる。
- branch / PRだけにある: 保存済み研究または試作。統合・製品採用とは限らない。
- 名称だけ参照される: 研究本文はGit未確認。内容を推定して統合しない。
- テスト成功: そのテストが測った範囲だけを検証済みとする。実音、iPhone、UI、聴感へ拡張しない。

過去判断は黙って消さない。現在判断と矛盾するものは `superseded` とし、置換先を残す。

## 状態語

- `researching`: 研究中
- `candidate`: 統合候補
- `adopted`: プロジェクト方針として採用
- `integrating`: 実装へ接続中
- `implemented-unverified`: 実装済み、必要な実機検証前
- `validated`: 必要な実機またはブラウザ検証済み
- `paused`: 保留
- `rejected`: 採らない
- `superseded`: 後の判断で失効
- `coverage-gap`: 名称や判断はあるが、根拠研究本文をGitで取得できない

`candidate`、`adopted`、`implemented-unverified`、`validated`を混同しない。

## 候補bridge

- [画像接触研究 → Sound Lab 接触入力bridge](../research/20260828-image-contact-bridge/README.md) — `candidate / research-only`。画像研究から接触状態だけを受け取り、Skulpturの具体DSP・タッチ割当・UIは固定しない。画像研究側の安定したGit locatorは `coverage-gap`。
