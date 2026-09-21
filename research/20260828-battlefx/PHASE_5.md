# BattleFX研究 Phase 5 — Choke semantics独立音響実験

- research-id: `20260828-battlefx`
- status: `offline-experiment-passed`
- 更新日: 2026-08-28
- BattleFX実機観測: 未実施
- Field Looper統合: 未実施

## 1. 今回進めた問い

Phase 2で未解決だった「chokeがどこを殺すか」を、実機なしでも識別可能な波形signatureへ変えた。

比較対象は次の四つ。

1. output gate
2. feedback cut
3. buffer clear
4. input choke

これはBattleFXの複製ではない。同一の最小delay networkへchoke位置だけを変え、後の実機録音を分類するための対照群を作る実験である。

## 2. 固定条件

| condition | value |
| --- | ---: |
| sample rate | 48,000 Hz |
| duration | 3.0 s |
| delay | 4,800 samples / 100 ms |
| feedback | 0.83 |
| choke | 0.957–1.557 s |
| choke内probe | 1.170 s |
| smooth ramp | 5 ms |

同一のchoke前burstを全modelへ入れる。さらにchoke中probeの有無を二回renderし、差分から新規入力の受理を測る。

## 3. 実測結果

| mode | choke中tail RMS | 解除後の古いtail RMS | choke中probe受理 RMS | late tail RMS | onset event-step proxy |
| --- | ---: | ---: | ---: | ---: | ---: |
| output gate | 0.00000000 | 0.00519856 | 0.02506520 | 0.00147498 | 0.08097242 |
| feedback cut | 0.00543581 | 0.00000000 | 0.02777796 | 0.00000000 | 0.00000000 |
| buffer clear | 0.00000000 | 0.00000000 | 0.04793371 | 0.00000000 | 0.10929513 |
| input choke | 0.01353112 | 0.00519856 | 0.00000000 | 0.00147498 | 0.00000000 |

自動assertionは5/5 pass。

- output gateだけはchoke中に無音でも、解除後に古いtailが復帰する。
- input chokeだけは既存tailを鳴らし続けながら、choke中probeを拒否する。
- feedback cutはchoke直後の残存音を許すが、循環を失うため解除後の古いtailとlate tailが戻らない。
- buffer clearは古いtailを即座に失う。新規probeは受けるため、解除後に聞こえるものがあれば「復帰」ではなく「再励起」と判別する。
- この条件ではbuffer clearのonset event-step proxyが最大。hard clearへfadeを置かない場合の不連続riskを確認した。

`event-step proxy`は、同じ入力のunchoked referenceとの差分における隣接sample最大変化である。知覚上のclick量そのものではない。

## 4. 実機照合規則

BattleFX実機のT2録音では、単に「choke中に無音か」を見るだけでは足りない。次を同時に録る。

| 観測 | 強く示すsemantics |
| --- | --- |
| 無音期間の後に古いtailが戻る | output gate |
| 既存tailは残るがchoke中の新規probeが消える | input choke |
| 直後の残存音はあるが循環とlate tailが消える | feedback cut |
| 古いtailが即時消滅し、新規入力からのみ再開 | buffer clear |

実機側がcrossfade、複合経路、delay/reverb別方式を使う場合、単一modelへ無理に分類せず混合または未解決として残す。

## 5. 生成物

- `experiments/choke-semantics/choke_lab.mjs`: dependency-free rendererと測定
- `experiments/choke-semantics/output/results.json`: 全条件、metric、WAV SHA-256、自動assertion
- `experiments/choke-semantics/output/output-gate.wav`
- `experiments/choke-semantics/output/feedback-cut.wav`
- `experiments/choke-semantics/output/buffer-clear.wav`
- `experiments/choke-semantics/output/input-choke.wav`

各WAVは48 kHz / mono / PCM16 / 3.0 s / 288,044 bytes。

## 6. 現在判断

- offline実験コード: 実行済み
- 自動assertion: 5/5 pass
- 生成WAV: header、frame数、duration、非ゼロPCM、SHA-256を別検証する
- BattleFXのchoke方式: 未判定
- 実機T2への進行条件: 同じ二刺激（choke前tail、choke中probe）を録音できること
- Field Looper製品実装: まだ行わない

