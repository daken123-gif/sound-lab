# E-GMD MIDI・発音時刻／velocity pilot

実行日: 2026-09-04

## 範囲

- E-GMD v1.0.0のmetadata 45,537行とMIDI-only archive
- 43 kitの再録音行を独立演奏として重複計上せず、各unique sequence IDの`Acoustic Kit`行を一つだけ選択
- 対象は1,059演奏（train 819、validation 117、test 123）
- MIDI note-on時刻、note番号、velocity、tempo、time signatureだけを解析
- 音声は未取得・未解析

E-GMDの同一演奏には複数kitによる再録音行がある。45,537行をそのまま標本数にすると、記号上は同じ演奏を最大43回近く数えるため、symbolic pilotでは44,478行を除外してunique sequenceを単位とした。

## S04：tempoとmicrotiming

全1,059演奏のMIDI tempo mapは一つのtempo値だけを持ち、CSV記載BPMとの差は最大0.000773335 BPMだった。同時に、全1,059演奏でnote-onの16分音符格子からの平均絶対残差が2 tick以上あった。

| 指標 | tick |
| --- | ---: |
| 最小 | 2.666667 |
| 第1四分位 | 16.055707 |
| 中央値 | 21.705882 |
| 第3四分位 | 27.890889 |
| 最大 | 50.750000 |

これは「局所的な発音変位があるならtempo curveも変動している」という扱いを退ける。E-GMD MIDIでは、固定されたtempo metadataと局所的なgrid残差が同時に存在する。ただし、最寄り16分音符は今回の操作的基準であり、三連系の意図や知覚上の基準拍を確定しない。

## S05：偏差量と符号つき形状

`drummer1/session1/135`と`drummer7/session3/147`は、16分格子からの平均絶対残差がどちらも11.166667 tickだった。一方、両演奏で共通して観測された13 grid slotの符号つき残差profile相関は-0.085863だった。

したがって、同じ「偏差量」でも前後方向を含むtiming形状は同一ではない。平均絶対残差をgrooveのidentityや質へ変換できない。E-GMDにはgroove品質の主観評価ground truthがないため、本pilotは「どちらが良いgrooveか」を評価していない。

## S10：反復topologyとvelocity変形

隣接小節について、16分格子へ量子化した`(slot, note)`列が一致する場合だけtopology反復候補とした。そのうえで、対応note-on間の平均絶対velocity差が1以上ならvelocity変形として分離した。

| 指標 | 結果 |
| --- | ---: |
| 隣接topology反復を持つ演奏 | 47 / 1,059 |
| velocity変形を持つ演奏 | 46 / 1,059 |
| velocity変形した隣接小節pair | 103 |
| pair内の平均絶対velocity差・中央値 | 7.0 |
| pair内の平均絶対velocity差・最大 | 43.416667 |

47演奏はすべて`beat`群にあり、`fill`群ではこの厳しい隣接反復条件に該当しなかった。最大例は`drummer1/session3/2`（jazz/swing）の0始まり170–171小節で、12イベントの量子化topologyが一致しながら平均絶対velocity差43.416667、最大差83だった。

これは発音位置とnote構成が一致しても、反復全体を「同じイベント列」として潰せない実例である。ただしMIDI velocityは録音音圧ではなく、量子化topology一致はraw timingや音響の一致も意味しない。

## parser検証

内蔵した標準MIDI parserは単体fixture 6件で検査した。さらにcanonical sequence IDを辞書順に並べ、全域から等間隔に選んだ10演奏について、独立実装`mido 1.3.3`と次を照合した。

- ticks per beat
- 全note-onのtick、note、velocity、channel
- tempo event
- time-signature event

10演奏すべてでevent streamが一致した。対象IDとnote-on件数は`egmd-symbolic-pilot-results.json`に保存した。

## 判断

- S04：固定tempoとlocal microtimingを別の証拠として保持する必要が、実演奏MIDIでも確認できた。
- S05：偏差の絶対量は符号つきshapeを保持せず、groove品質を導かない。
- S10：量子化した反復identityとvelocityによる差異を同時に保持できる。

これはMIDI上のsymbolic pilotであり、E-GMD音声との整列、kitごとの音響差、知覚上のgroove評価は未検証である。再実行コードは`egmd_symbolic_pilot.py`、機械可読結果は`egmd-symbolic-pilot-results.json`に保存する。外部dataset自体はGitへ転載しない。
