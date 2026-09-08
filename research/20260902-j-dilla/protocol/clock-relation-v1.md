# J Dilla clock-relation experiment v1

## 目的

J Dillaの時間感覚を単一グリッドからの誤差や一括humanizeへ縮めず、安定層、voice間関係、競合する分割、attack、長周期として比較する。

このプロトコルは測定方法を固定する。音源取得済み、測定済み、仮説支持、製品採用を意味しない。

## 対象

最低コーパスは次の7版とする。

1. The Pharcyde「Runnin'」の分析対象版
2. Slum Village「Players」の分析対象版
3. Slum Village「Keep It On (This Beat)」の分析対象版
4. J Dilla「Come Get It」の通常版
5. 同 instrumental
6. 同 cassette demo
7. 同 alt beat

版を推測で同一視しない。各音源は取得経路、リリース表記、収録位置、尺、sample rate、channel数、file size、SHA-256を記録してから分析へ進む。

## 音源境界

- 正当に利用できるローカル音源またはユーザー提供音源だけを解析する。
- 音源ファイル、stem、変形音声はGitへcommitしない。
- Gitへ保存するのはhash、メタデータ、区間、onset表、派生統計、処理条件、試聴回答だけとする。
- previewとfull-lengthを同じ証拠水準にしない。
- lossy sourceはcodecを記録し、過渡形状の確定根拠には単独で使わない。

## 版固定ゲート

`analysis_status`を`ready`へ変更できるのは、次をすべて満たす場合だけである。

1. `sha256`が64桁の小文字hex
2. `duration_seconds`、`sample_rate_hz`、`channels`、`file_size_bytes`が取得済み
3. `source_kind`が`full_length`または`preview`
4. `rights_basis`と`local_filename`が記録済み
5. 分析区間が16小節以上。ただし版比較で16小節存在しない場合は理由を記録

## 分析区間

- 曲ごとに最低16小節を一つの連続区間として固定する。
- intro、verse、chorus等の名称は資料または構造確認なしに付けない。
- `start_seconds`、`end_seconds`、`start_bar`、`bar_count`を保存する。
- 同一曲の別版比較では、対応区間の根拠を`alignment_note`へ記録する。

## voice候補とonset確認

最低voice候補は`kick`、`snare`、`hat`、`bass`、`sample`、`other`とする。

1. 原mixでtransient候補を作る。
2. 分離結果は候補付けだけに使う。
3. 各onsetを原mixで再確認する。
4. 自信のないvoiceは無理に一つへ決めず、候補とconfidenceを残す。
5. 物理onsetと知覚onsetを混ぜないため、attack rise timeも保存する。

onset行の最低項目:

```text
recording_id, region_id, onset_seconds, bar, beat, subdivision,
voice, voice_confidence, clock_candidate, offset_from_clock_ms,
attack_rise_ms, peak_dbfs, separation_model, human_verified, note
```

## clock候補

単一BPMを正解として固定せず、少なくとも次を別候補として評価する。

- 全体pulse
- snare / hatが作る安定層
- kick / bassの局所pulse
- sample由来pulse
- binary subdivision
- triplet subdivision
- 2、4、8、16、20小節の長周期

各onsetは、どの`clock_candidate`に対する偏差かを失わない。

## voice間関係

最低限、同じ対応規則で次を求める。

```text
delta_kick_snare_ms = t_kick - t_snare
delta_bass_kick_ms = t_bass - t_kick
delta_hat_grid_ms = t_hat - t_clock
```

平均値だけでなく、小節内位置別分布、符号、分散、自己相関、周期間の変化を保存する。

## 変形条件

同一区間から次の10条件を生成する。ラウドネス、開始位置、終端長を揃え、条件名を試聴者へ見せない。

1. `original`
2. `quantize_all`
3. `quantize_kick`
4. `quantize_snare`
5. `unify_hat_swing`
6. `align_bass_to_grid`
7. `exchange_voice_offsets`
8. `invert_offset_signs`
9. `shuffle_positions_keep_magnitudes`
10. `random_humanize_same_distribution`

追加の横断条件として、`BODY_COUPLING`、`FLOOR_AND_BREAK`、`STATE_TRANSITION`を別実験で扱う。10条件へ混ぜず、まず`CLOCK_RELATION`の寄与を測る。

## ブラインド試聴

- ファイル名はランダムIDへ置換する。
- 処理条件の対応表は回答確定まで隠す。
- 最低質問は`groove continuity`、`forward motion`、`instability`、`human intention`、`preference`。
- 「Dillaらしさ」だけを唯一の評価にしない。
- 同一被験者内で提示順を変える。
- 未聴取を0点として扱わない。

## 停止条件

次の場合は数値を確定しない。

- 版またはhashが未固定
- 16小節区間を同定できない
- 分離出力だけでonsetを確定した
- clock候補間で対応規則が定まらない
- attack変化とonset移動を分離できない
- previewからフル尺構造を補った

## 成果物

- `data/clock-relation-manifest-v1.json`: 版取得と実験条件の台帳
- 将来の`data/onsets-<recording_id>-v1.csv`: 人手確認済みonset
- 将来の`data/relations-<recording_id>-v1.json`: clock候補とvoice間統計
- 将来の`data/listening-test-v1.json`: 匿名化した提示条件と回答

