# 採譜用の打点検証

research-id: `20260908-onset-audit`

打点JSONを入力し、対応した打点・片側だけの打点・時刻ずれを出す、オフラインの検証コマンド。
音源の採譜器ではなく、採譜候補や検出器の結果を検証する道具。
Python 3.10以上。標準ライブラリだけで動き、pip install、ネット接続、Essentia、音声ファイルは不要。

## すぐ実行する

このフォルダを作業ディレクトリにする。

```bash
python -m unittest -v
python onset_audit.py compare examples/reference.json examples/estimate.json --output-dir output-demo
python onset_audit.py windows examples/jeff-mills-windows.json --output-dir output-jeff
```

出力は各ディレクトリの `report.html` と `report.json`。
HTMLは外部通信・外部スクリプトなし。食い違いの多い区間から、確認すべき絶対時刻へ進める。
JSONには一対一の対応打点、左右どちらかだけの打点、入力ファイルとツール自身のSHA-256を残す。
既存の出力ディレクトリは上書きしない。再実行は `--output-dir output-jeff-02` のように別名を使う。

`compare` のデモは既知4打に対して3打一致、1打見逃し、2打余分。
precision 0.6、recall 0.75、F1 約0.667が期待値。実録音ではなく架空の検証用データ。

## 自分の採譜データを使う

参照と候補をそれぞれ次のJSONにする。時刻は秒単位、音源先頭基準、昇順。

```json
{
  "schema_version": 1,
  "source_sha256": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
  "scope_seconds": [570, 580],
  "reference_kind": "candidate",
  "provenance": "抽出器名・版・設定・対象パート・作成方法を記載",
  "onsets_seconds": [570.5, 571.0, 571.125]
}
```

上のhashは説明用。実使用時は元音声のSHA-256に置き換える。
同じ音源hash・同じ区間でなければ比較を拒否する。異なるcodecの版や別録音は、先に対応関係を確認する。
時刻基準や対象パートの意味は利用側で合わせる必要があり、hash一致だけでは保証しない。
範囲は `[開始, 終了)`。重複打点は削除せず、一対一照合で余計な検出として残す。

```bash
python onset_audit.py compare reference.json detected.json --tolerance-ms 15 --output-dir output-take01
```

### 精度と一致度を分ける

| 参照JSONの reference_kind | 用途 | 出力 |
| --- | --- | --- |
| known_events | 生成時刻が既知の合成音など | precision / recall / F1 |
| human_annotations | 人が原音と照合した参照打点 | precision / recall / F1 |
| candidate | 別方式の候補・未確定の採譜 | 一致度のみ。正解率は出さない |

参照の権威は入力の申告であり、このプログラムが認定するものではない。
human_annotations なら provenance に照合者・対象・方法・改訂版などを記載する。
モデル間合意を known_events に変更して正解扱いしない。
参照が空の場合は `no_reference_events`。両側空を「100%成功」にしない。

### 時刻ずれ

最大数の一対一対応を選び、その中で絶対時刻誤差の総和を最小化する。
符号は `候補 - 参照`。正なら候補が遅い。
時刻合わせ、量子化、±18.3msなどの固定補正は一切行わない。
許容差の外側に落ちた打点は対応しないため、対応打点だけの誤差と、見逃し・余分を必ず一緒に読む。
既定±15msはJeff Mills研究の暫定作業条件であり、普遍的知覚閾値でも自動合格基準でもない。
密な連打では隣の打点との対応が生じ得る。対応表を残して確認できるようにしている。

## Jeff Mills既存形式をそのまま読む

`windows` は既存の `source_sha256 / scope_seconds / windows` 形式に対応。
各窓の `start_s / end_s / onset_candidates_absolute_s` を使用する。
同じ開始時刻の10秒窓と30秒窓から、共通区間の両端100msを除いて比較する。
窓設定は `--short-s / --long-s / --edge-s` で明示できる。
対応する長窓がない短窓は、無視せず `skipped_short_windows` に残す。
これは窓依存性の検査であって、どちらの打点が正しいかを決めるものではない。

同梱の45窓データでは13組を比較し、4短窓は同開始の長窓がない。
620.1–629.9秒では短窓93候補、長窓66候補、66対応、短窓だけ27候補を再現する。
重複区間があるため、各窓の食い違い数を合計して全曲の誤検出数にしない。

## 他の島から使う

コードの対象リポジトリは `daken123-gif/sound-lab`。
作業・配布ブランチは `research/20260908-onset-audit`。mainへの統合は別工程。
同ブランチからこのフォルダ一式を取得し、上のテストを実行してから利用する。
取得したcommit IDを記録する。ブランチへの保存を、全島への導入・main統合済みとは扱わない。
通常の評価に必要なのは `onset_audit.py` 1本と入力JSONだけ。親ディレクトリへのimportや特定の作業場所には依存しない。
入力・出力のhashを各研究の結果に残し、古い結果を新しい方式の測定値で上書きしない。
既存router、全島の設定、定期タスク、SOURCE_POLICY、抽出器は変更していない。

## 来歴と範囲

- 共通方針: main の `research/music-analysis/SOURCE_POLICY.md`。Bandcamp追加を保持。
- 既存コードの検証基準: `calibrate_analyzer.py` のSHA-256 `4c779281be198346acc64aea3f9b40a9468afce01b8621fd4913110839c8176f`。
- 同梱のJeff Millsデータは既存研究の取得済みJSONを内容を変えず複製した検証fixture。
- 原本: `research/20260902-jeff-mills` ブランチの `research/20260902-jeff-mills/reconstruction-precision-results-20260907.json`。
- 原本Git blob: `b5f278302e8ea69c9868bc3f78dd1ed60fabd1eb`。
- 音源本体、期限付きURL、認証情報、モデルは含まない。fixtureは新たな音声取得・再抽出の証拠ではない。

観測: 旧方式には合成音の連打検出不足と時刻ずれがあり、短窓候補には減衰音の過剰検出がある。
設計への採用: どちらも検出器として確定採用せず、対応打点と不一致箇所を比較できる評価器を独立実装した。
未達: 実録音の正解採譜、音高・音色・楽器帰属、MIDI、原音との再合成比較。
終了コード0は検査処理の完了、2は入力・資源・保存エラー。0を「採譜合格」にしない。
照合はO(n*m)。200万セルを超える要求は明示的に拒否し、共通区間の分割を求める。
変更範囲: この新規研究ディレクトリのみ。既存研究・製品コードは変更しない。
