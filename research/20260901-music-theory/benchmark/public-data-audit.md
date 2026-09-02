# 第二輪・公開実録音データ受入れ監査

調査日: 2026-09-02

## 結論

合成音源S01〜S12を実録音へ移す第二輪の候補として、E-GMD、MAESTRO v3.0.0、RWC v2、MUSDB18を採用する。ただし、**音源の取得、checksum照合、注釈schemaの読取りはまだ行っていない**。したがって、現時点で実録音に対する性能値や合否は一つも確定していない。

候補情報と取得状態の正本は`public-dataset-manifest.json`とする。`validate_public_dataset_manifest.py`は、未取得データを`evaluation_ready: true`へ昇格できないようにする。

## 候補と役割

| データセット | 第二輪で見る証拠 | 対応ケース | 現在状態 |
| --- | --- | --- | --- |
| E-GMD 1.0.0 | 人間が演奏したドラムの発音時刻、velocity、kit差 | S04–S07、S10–S11 | 未取得・評価不可 |
| MAESTRO 3.0.0 | 約3 ms整列の音声/MIDI、velocity、pedal、composition split | S04–S05、S08、S10–S11 | 未取得・評価不可 |
| RWC v2 | 複数ジャンルの実録音と拍・旋律・サビ等の別管理注釈 | S01–S03、S06–S12 | 未取得・評価不可 |
| MUSDB18 | stereo mixとdrums/bass/vocals/other stem | S07、S09、S12 | 承認・曲別license監査前、評価不可 |

対応ケースは「そのデータだけで正解が得られる」という意味ではない。何を観測でき、何が観測できないかを検査する入口である。

## 受入れゲート

| 段階 | 必須証拠 | 許可する主張 |
| --- | --- | --- |
| P0 候補 | 公式URL、version、利用条件、想定ケース、既知の限界 | 候補として監査済み |
| P1 取得 | artifact取得、宣言checksumとの一致、local root | データ取得・同一性確認済み |
| P2 schema | audio/annotation pairの実読取り、時間単位・channel・欠損値確認 | adapter実装可能 |
| P3 pilot | split unitを守った少数曲、入力と出力を保存、手動spot check | pilot結果 |
| P4 benchmark | 事前固定した対象、除外条件、指標、失敗例を全件保存 | 第二輪評価結果 |

P0からP4を一足飛びにしない。公式ページに書かれたデータ規模は、ローカル取得や解析成功の証拠ではない。

## 評価契約

1. **単一の総合accuracyを作らない。** S01〜S12それぞれに観測量と棄却条件を持たせる。
2. **注釈を万能なground truthと呼ばない。** MIDI alignmentは発音参照であり、聴取上の拍、直接音終了、残響終了、音源identityの完全な正解ではない。
3. **分割単位を守る。** E-GMDはunique sequence、MAESTROはcomposition、RWCはpiece、MUSDB18はtrackを最低単位とし、同一単位をtrain/testへ跨がせない。
4. **stereoを保持する。** S09の検査前にmono化しない。mono結果を併記する場合も別条件として保存する。
5. **混合とstemを別の証拠にする。** MUSDB18のstem名を解析器の観測結果へ注入せず、推定後の照合だけに使う。
6. **失敗資料を除外して終わらせない。** 公式errataや欠損を`known_issue`として保持し、除外前後の件数を出す。
7. **信頼度と代替候補を保存する。** 周期・境界・役割・音源を早期に一意化しない。

### ケース別の最低出力

| ケース | 最低出力 | 合格を主張しない条件 |
| --- | --- | --- |
| S01–S03 | 上位K周期、位相、layer/channel別証拠、整数比関係 | 一つのBPM/拍子だけを保存 |
| S04–S05 | local tempo curve、符号つき発音残差、楽器class別分布 | 偏差量だけからgroove品質を命名 |
| S06 | rhythm/pitch/timbre/amplitudeの境界stream | 一特徴の境界を全体境界へ無条件昇格 |
| S07 | 時間窓ごとのpulse-anchor候補と役割遷移 | 音域やstem名を固定役割として返す |
| S08 | onset、note-off/pedal、音響減衰の別時刻 | MIDI note-offを残響終了と同一視 |
| S09 | stereo/mono別の周期・空間特徴 | monoだけで空間周期不存在と判定 |
| S10 | onset topologyとvelocity/dynamics変換量 | 発音位置一致だけで完全反復と判定 |
| S11 | cycle-local period列と変化率 | 全区間を中央値BPMだけで保存 |
| S12 | mix観測、stem照合、identity不確実性 | 分離stemを無条件の音源正解として扱う |

## 公式資料の監査結果

### E-GMD

Google/Magentaの公式ページは、43 drum kitsで再録音した444.5時間の音声、44.1 kHz/24-bit、元MIDIとの2 ms以内の整列、velocity注釈、CC BY 4.0を明記する。90 GB archiveのSHA-256も公開されている。一方、semi-manual pipelineにより使用不能なtrackがあると公式に注意されている。

- [Expanded Groove MIDI Dataset](https://magenta.withgoogle.com/datasets/e-gmd)

### MAESTRO

公式ページは、v3.0.0が198.7時間、音声とMIDIが約3 msで整列し、velocityとpedal情報を持つこと、同一compositionが複数splitへ入らない提案splitを示す。v3 archiveは101 GB、SHA-256は公式ページに記載される。利用条件はCC BY-NC-SA 4.0である。

- [The MAESTRO Dataset](https://magenta.tensorflow.org/datasets/maestro)

### RWC v2

2026年のZenodo v2はCC BY-NC 4.0でオンライン公開され、Popular、Royalty-Free、Classical、Jazz、Genreの音声archiveを含む。音声は13.4 GBで、現行注釈は別の`rwc-music/rwc-annotations`で管理される。旧AIST注釈ページ自身が注釈に誤りが残ると明記するため、注釈を無謬の正解として扱わない。

- [RWC Music Database v2](https://zenodo.org/records/18656623)
- [AIST Annotation for the RWC Music Database](https://staff.aist.go.jp/m.goto/RWC-MDB/AIST-Annotation/)
- [rwc-music/rwc-annotations](https://github.com/rwc-music/rwc-annotations)

### MUSDB18

SigSep公式ページは、150曲・約10時間、44.1 kHz stereo、mix＋4 stem、100/50 splitを示す。アクセスは承認制でacademic useに限定され、収録元ごとにlicenseが異なる。また、stem bleedや左右channelのsum不一致などのerrataが公開されている。したがって、取得前に承認、取得後に曲別licenseとerrataを固定する必要がある。

- [MUSDB18](https://sigsep.github.io/datasets/musdb.html)

## claim-to-source ledger

| 主張群 | 資料 | 公開者・日付 | URL | 2026-09-02の確認範囲 |
| --- | --- | --- | --- | --- |
| E-GMDの規模、録音条件、整列、split、license、checksum、既知の欠陥 | *The Expanded Groove MIDI Dataset* | Google/Magenta、2020-03-31 | [公式ページ](https://magenta.withgoogle.com/datasets/e-gmd) | 本文とdownload/license欄を読取り |
| MAESTRO v3の規模、整列、MIDI内容、composition split、license、checksum | *The MAESTRO Dataset* | Google/Magenta、2018-10-29、v3情報を含む | [公式ページ](https://magenta.tensorflow.org/datasets/maestro) | dataset、v3 download、license欄を読取り |
| RWC v2の再公開日、license、audio内容、容量、注釈の別管理 | *RWC Music Database v2* | Goto・Balke・Mueller、Zenodo、2026-02-16 | [Zenodo record](https://zenodo.org/records/18656623) | record本文、files、versionを読取り |
| RWC注釈の種類と誤りに関する注意 | *AIST Annotation for the RWC Music Database* | AIST / Masataka Goto、archive page | [公式ページ](https://staff.aist.go.jp/m.goto/RWC-MDB/AIST-Annotation/) | overview、notes regarding useを読取り |
| MUSDB18の曲数、stem、stereo、split、access、混合license、errata | *MUSDB18* | SigSep、最終更新2022-09-29 | [公式ページ](https://sigsep.github.io/datasets/musdb.html) | corpus、access、format、errata欄を読取り |

この調査は第二輪の受入れ判断に必要な公式情報が揃った時点で止めた。MedleyDBはMUSDB18の構成元として確認したが、単独audioの現在の取得経路と曲別licenseをこの段階で十分に確定できなかったため、manifestへは加えていない。

## 次の実行単位

最初のpilotは、直接取得でき利用条件が明瞭なE-GMDから始める。ただし90 GB全体を先に取得せず、公式metadataと小さな許諾済みsubsetでadapter・split・出力schemaを検証する。RWC v2はRoyalty-Free subset（約320 MB）を次候補にする。MUSDB18は承認と曲別license監査が済むまで取得済みへ進めない。
