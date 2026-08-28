# 統合島

ここはミュージックプロジェクト全体の方向を管理する場所である。個別の機材研究を集めた要約ではない。

各研究島は観測、比較、仮説、試作を持つ。統合島は、それらを製品へ採るか、保留するか、採らないかを管理する。

## 正本

- [`DIRECTION.md`](DIRECTION.md): 現在の製品像と設計境界
- [`DECISIONS.md`](DECISIONS.md): 採用、保留、却下、失効の履歴
- [`STATUS.md`](STATUS.md): 研究、統合、実装、実機検証の現在位置

同じ内容が個別研究と統合島で食い違う場合、研究上の事実は研究README、プロジェクトとしての採否は統合島を正本とする。

## 各島の読み方

作業開始時に次の順で読む。

1. `integration/DIRECTION.md`
2. `integration/STATUS.md` の自分の領域
3. 対象研究のREADME
4. 触る実装パスと競合するopen PR

研究島は、統合島にない機能を製品の決定事項として扱わない。統合島は、研究READMEにない検証結果を作らない。

## 更新の単位

- 新しい方向や境界: `DIRECTION.md`
- 採否の変更: `DECISIONS.md` に追記してから `DIRECTION.md` を更新
- 現在位置の変更: `STATUS.md`
- 詳細な根拠や製品解析: 各 `research/<research-id>/README.md`
- 製品コード: 統合ブランチまたは実装ブランチ

過去の判断を黙って消さない。変更された判断には `superseded-by` を付ける。

## 状態語

- `researching`: 研究中
- `candidate`: 統合候補。まだ製品決定ではない
- `adopted`: プロジェクト方針として採用済み
- `integrating`: 実装へ接続中
- `implemented-unverified`: 実装済み、実機未検証
- `validated`: 必要な実機またはブラウザ検証済み
- `paused`: 保留
- `rejected`: 採らない
- `superseded`: 後の判断で失効

`candidate`、`implemented-unverified`、`validated`を混同しない。

