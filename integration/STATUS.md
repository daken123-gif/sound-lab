# 統合状況

最終観測: 2026-08-28 / GitHub `daken123-gif/sound-lab`

この表は採否と実装状態を分ける。open PRがあることは、採用または実機検証の証拠ではない。

| 領域 | 現在位置 | プロジェクトでの扱い | 次の統合条件 |
|---|---|---|---|
| 4トラック・合成波形 | `adopted` | 製品中心 | iPhone実機で録音、再生、波形操作を確認 |
| iPhoneマイク／入力段 | `integrating` | 専用入力段を採用 | 本体マイクとヘッドホン経路を別々に実機確認 |
| KAOSSマスターFX | `candidate` | 配置は採用、アルゴリズム構成は未決定 | 4トラック出力への接続とマルチタッチ確認 |
| Performance Take | `implemented-unverified` | 元音声を変えない演奏記録層の候補 | Draft PR #15をiPhone実機で確認 |
| Koala Sampler研究 | `researching` | 複雑度の上限として利用 | PR #12の研究判断を統合島へ採否登録 |
| SOMA研究 | `researching` | 有機的な相互作用と記憶の候補 | PR #16のうちThe Pipeを含む音声入力系を再整理 |
| ドラム／Elektron | `researching` | ルーパー外の独立演奏系 | 専用research-idと接続境界をGitへ保存 |
| 空間系／Strymon | `researching` | マスターFX候補の基礎研究 | 製品別アルゴリズムと一般残響研究を分離 |
| Microcosm | `researching` | グラニュラー／反復変形候補 | KAOSS層との責務重複を判定 |
| Skulptur | `researching` | 音色生成・モーフ候補 | KAOSSと競合させず、発音源として位置づけを確定 |

## Gitで観測できた現在状態

- `main`: `4c29b503681881521ce98ef9cd89ace47d20567f`
- open PR #12: Koala Sampler研究
- Draft PR #15: Performance Take実装。ブラウザ／iPhone実機は未検証
- open PR #16: SOMA organismic instruments研究。実機検証とDSP実装は未実施
- `integration/` という全体方針の正本は、この変更以前の `main` には存在しなかった

## 次の優先順

1. iPhone実機で「入力される、録れる、4トラックで返る」を安定させる。
2. 合成波形を直接触る演奏経路を安定させる。
3. KAOSSマスター層を接続する。
4. Performance Takeを実機検証する。
5. 独立ドラム系を接続仕様から設計する。

新しい機材研究は続けてよいが、上の順番を崩して製品コードへ入れない。

