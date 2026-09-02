# 拡張関係証拠：S09〜S12検証結果

## 目的

合成反証ベンチマークの最終4ケースで、空間、反復変形、cycle伸縮、低域音源重畳を単一特徴へ還元しない。`extended_evidence_analyzer.py`は`ground-truth.json`を読まず、音声から観測できる関係と、観測だけでは確定できないidentityを分けて返す。

## 結果

| ケース | 音声から得た観測 | 退けた早期統合 | 結果 |
| --- | --- | --- | --- |
| S09 | mono onset周期0.5秒、左右balanceの反復周期1.0秒 | stereoを先にmono化 | 左右交替をlag 2の空間cycleとして保持 |
| S10 | 4 cycleすべてのonset offsetsが`[0, 0.5, 1.0, 1.5]`、strength範囲0.066980 | timing一致を完全audio反復と判定 | `rhythmic_repetition_with_dynamics_transformation`として保持 |
| S11 | cycle周期1.80、1.95、2.10、2.25、2.40秒 | 全cycleを中央値2.10秒へ固定 | cycleごとのperiodと1 cycleあたり+0.15秒のtrendを保持 |
| S12 | 66 Hzと62 Hzを主なresonance候補として観測。energy flux onsetは85個へ破砕 | resonanceへkick／bass identityを付与 | `source_assignment: null`、`unresolved_from_mixture`として保持 |

## 解釈

S09は、発音時刻だけなら0.5秒周期だが、空間関係まで含めると1.0秒で一巡する。同じイベント列でも、どの観測軸を捨てるかでcycleが変わる。

S10は、音高と発音位置が一致していても強度がcycleごとに変わるため、反復のidentityと差異を同時に記述する必要がある。`exact_audio_repeat`は`false`とした。

S11の2.10秒は中央値としては正しいが、各cycleを置換する値ではない。伸縮を演奏対象にするField Looperでは、global tempoよりcycle-local period列が主要データになる。

S12では全体スペクトルから近接resonanceを観測できるが、混合波形のenergy fluxは持続するsaw成分によって過検出する。62 Hzをkick、66 Hzをbassと命名するのは生成規則を知る評価者には可能でも、audio-only解析器の観測ではない。

## 残る限界

- S09の空間特徴は左右RMS balanceであり、実空間の音源定位ではない。
- S10のcycle分割はpiecewise-constantなonset strengthに依存する。
- S11のanchor検出はcycle先頭のaccent contrastに依存し、最終cycle周期は内部subdivisionから外挿している。
- S12のglobal spectrumにはsource周波数だけでなく、反復によるsidebandや倍音も現れる。
- S01〜S12の合格は合成音源上の第一輪であり、実録音や公開データ上の一般化を証明しない。

機械可読結果は`generated/extended-s09-s12.json`へ生成する。生成物はGit管理せず、解析器・生成器・テストを再現の正本とする。
