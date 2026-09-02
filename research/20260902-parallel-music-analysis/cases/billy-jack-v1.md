# ケース01 — Curtis Mayfield “Billy Jack”

- status: `active / partial`
- case-id: `parallel-music-analysis/billy-jack-v1`
- 更新日時: 2026-09-02 UTC
- 対象範囲: Apple Music由来30秒プレビューと保存済みMDX監査結果
- 実施内容: Git上の既存監査結果を共通SOURCE / EVENT / RELATION形式へ再記述
- 未実施: 新規音源取得、波形再解析、人手採譜、フル尺分析、聴取実験
- 採用状態: research-only

## 1. このケースで判定すること

抽象的に定義した共通分析インターフェースが、既存の実測結果とCurtis Mayfield研究の解釈を混ぜずに保持できるかを調べる。

このケースでは次を別状態に置く。

1. 保存済みJSONから直接読める観測
2. 既存Curtis研究が提示する関係仮説
3. 観測が支持できる範囲
4. 現在の資料では判定できない範囲
5. 他研究へ接続したときの誤一般化

## 2. 参照したGit実体

| 種別 | ref | path | blob SHA |
| --- | --- | --- | --- |
| ブラインド監査本文 | `main` | `research/music-analysis/blind20-audit-20260902.md` | `5f68b76ea105ada904bec58b3385575164045ced` |
| 復号済み結果 | `main` | `research/music-analysis/blind20-results-decoded.json` | `60d2f41aa4f2a350224b3b3734674182d33e3794` |
| 固定標本manifest | `main` | `research/music-analysis/blind20-manifest.json` | `6e0319efed84c8e98c0dffafb30f35b3405752d4` |
| 事後復号表 | `main` | `research/music-analysis/blind20-title-map.json` | `7fabcaa2e263fd0974bd40349cb1d9374d80ee2f` |
| Curtis Mayfield研究 | `research/20260831-curtis-mayfield` | `research/20260831-curtis-mayfield/README.md` | `7fe9816c4f0613d8c566cf140fe0d03fcc82e6ce` |

Curtis研究のblobは今回取得した時点のものを固定した。並行更新される研究なので、以前の取得SHAを現在本文の代用にしない。

## 3. SOURCE

```text
SOURCE {
  source_id: "curtis-blind20-v1/B09"
  recording_identity: "Curtis Mayfield — Billy Jack"
  album: "There's No Place Like America Today"
  track_id: 120146023
  acquisition_route: "Apple API preview -> locked local M4A"
  local_source: "quota-probe-5/01-billy-jack.m4a"
  time_scope: "approximately 30 seconds; exact position in full composition not established here"
  sha256: "e298d2a8ff43aa257c1a86a81d8fc71503b72e2e867353bc9c63b3df90057d3f"
  identity_check: "remote preview SHA-256 exactly matched locked local source"
}
```

これは録音全体の同一性ではなく、解析したプレビュー資産の同一性を固定する。

## 4. 直接観測

### 4.1 ブラインド監査の判定

100プレビューから決定論的に選んだ20資産をB01–B20として解析し、曲名を復号する前にカテゴリを決定した。B09だけが事前固定された `concentrated_non_triplet_reproduced` を通過し、復号後に“Billy Jack”と判明した。

- 20資産中15件: `stable_intermediate`
- 4件: `rejected`
- 1件: `concentrated_non_triplet_reproduced`
- `triplet_spacing_reproduced`: 0件

人間参加者を使った二重盲検ではなく、解析プログラムへ曲名を渡さない機械処理上の事後復号ブラインドである。

### 4.2 B09の保存値

| 指標 | MDX model A | MDX model B |
| --- | ---: | ---: |
| full BPM候補 | 141.14 | 141.78 |
| beat confidence | 3.638 | 3.589 |
| onset rate / s | 2.936 | 2.969 |
| phase entropy | 0.358 | 0.333 |
| binary spacing score | 0.269 | 0.143 |
| triplet spacing score | 0.005 | 0.016 |
| usable onsets | 86 | 87 |
| 最大phase bin中心 | 0.958 | 0.958 |

A/B推定ドラム波形のcosineは `0.9465`。scale-invariant similarityは `9.343 dB` と保存されているが、正解stemがないため分離品質のSDRとは扱わない。

### 4.3 三つの時間窓

| 窓 | A BPM / triplet / entropy | B BPM / triplet / entropy |
| --- | --- | --- |
| 0–10秒 | 142.40 / 0.045 / 0.237 | 142.40 / 0.044 / 0.264 |
| 10–20秒 | 140.24 / 0.047 / 0.403 | 140.22 / 0.044 / 0.346 |
| 20–29.976秒 | 141.35 / 0.007 / 0.324 | 141.05 / 0.000 / 0.264 |

full集約値だけでなく、A/B両モデルの三窓すべてでtriplet scoreが0.1以下だった。これは事前規則の「各モデルで三窓中二窓以上」を上回る。

## 5. EVENT形式へ入れられるもの

現在のJSONはonsetごとの時刻列を保存せず、区間集約と12-bin phase histogramを保存している。したがって完全なEVENT列は復元できない。

```text
EVENT_AGGREGATE {
  source_id: "curtis-blind20-v1/B09"
  window: full | 0-10 | 10-20 | 20-29.976
  clock_candidate: "beat tracker candidate"
  role: "MDX-estimated drum stem"
  bpm_candidate
  beat_confidence
  onset_rate_per_s
  phase_histogram_12
  phase_entropy
  binary_spacing_score
  triplet_spacing_score
  usable_onsets
  separation_provenance: "kuielab_a_drums | kuielab_b_drums"
  original_mix_recheck: "not represented per onset in decoded JSON"
}
```

欠けているもの:

- 各onsetのabsolute time
- bar / beat / subdivision
- kick、snare、hat等の役割
- onsetごとのconfidence
- attack rise time
- 音価と休符
- bass、voice、guitar、horizon層との関係
- 原mix上の各onset再確認結果

よって、B09は共通EVENT schemaの**集約値テストには通るが、イベント列テストには未到達**である。

## 6. RELATION仮説との照合

Curtis研究は“Billy Jack”をBODY / VOICE / HORIZONの異なる時間幅として読み、三層が同じフレーズや初期状態へ同時に戻らないという仮説を置く。

### R-BJ-01: BODYが安定した場を作る

- 関係仮説: ドラム、ベース、打楽器が重心を保ちながら内部のアタックと隙間を変える。
- 現在の支持: 推定ドラムstemのBPM候補、phase集中、三窓安定がA/Bで再現した。
- 支持しない部分: bassとのcoupling、音価、休符、重心、演奏者間関係。
- 判定: `partially_supported_by_drum_aggregate`

### R-BJ-02: VOICEはBODYと別の句読点を持つ

- 関係仮説: 歌詞と息の終端が伴奏周期と常に一致しない。
- 現在の支持: なし。監査JSONはvoice eventを持たない。
- 判定: `untested`

### R-BJ-03: HORIZONが物語圧力を長時間で変える

- 関係仮説: ギター、ホーン／木管、鍵盤等の短い介入や長時間変化が危険度を担う。
- 現在の支持: なし。監査JSONは推定ドラムstemだけを扱う。
- 判定: `untested`

### R-BJ-04: 三層が同時に初期状態へ戻らない

- 関係仮説: 部分反復はあるが、BODY / VOICE / HORIZONの総ループは成立しない。
- 現在の支持: なし。30秒・ドラム集約・位置不明では他層のreturn conditionを観測できない。
- 判定: `untested`

### R-BJ-05: 最小核は楽器数でなく機能関係である

Curtis研究が候補化する機能:

- `CORE.body`: 重心、attack、隙間
- `CORE.narrator`: 句読点を持つ前景主体
- `CORE.puncture`: 全面を埋めない短い切れ目
- `COLOR.horizon`: ゼロでもCOREが成立すべき任意層

これは音源分析結果ではなく、編成縮約から導いた設計仮説である。B09のドラム集約値は `CORE.body` の存在全体を証明しない。

## 7. 他の並行研究と接続した結果

### James Brown

B09のphase集中を、James Brown研究の「Oneへの収束」と同一視できない。James Brown側の主張は小節内部の散開、secondary One、次のOneへの偏差縮小を含む。B09にはbar-level onset列がなく、収束曲線を比較できない。

**必要な比較:** 各小節位置における偏差分布と、小節末から次のOneまでの縮小率。

### J Dilla

B09の「集中した非三連系」は、Dilla研究の複数clockや声部間摩擦の証拠ではない。むしろ、すべての魅力的なグルーヴをswing、triplet、複数clockで説明しないための対照になる。

**必要な比較:** 同じEVENT形式で、単一clock内集中、声部別timing shape、競合clock候補を判別する。

### Anderson .Paak

三窓の安定は「一定」に近い観測だが、「同一イベント列の再生ではない」ことをまだ証明しない。小節別イベント列がないため、反復ごとの不変項と変化量を分離できない。

**必要な比較:** bar-to-bar event identityと、pulse / 重心 / roleの保持率。

### Charlie Hunter

推定ドラム集約から、低音と上声の拘束された対位法は観測できない。Hunter研究との接続は、将来のbass–guitar–drum関係測定の分析形式に限る。

### Dub

完成録音の30秒プレビューから、CUT / THROW / REVEALやdry / tailの操作事件を復元しない。Dub研究との接続は、将来の変形実験をabsolute audio timeで記録する形式に限る。

## 8. 反例が示した境界

B02 “All Night Long”はfull triplet scoreがA/Bで0.808 / 0.845だったが、区間BPMが不安定なため棄却された。

この反例により、次を固定する。

- full集約値だけで作家性を語らない。
- 高いtriplet scoreだけで三連系グルーヴと断定しない。
- `rejected`を失敗として隠さない。
- 分離器二本の一致をground truthにしない。
- “Billy Jack”の受理をCurtis Mayfield全作品へ一般化しない。
- Sweet Exorcistはblind20標本外なので肯定も否定もしない。

## 9. 次の実証ファイル

次の更新では、同じSOURCEに対して次を作る必要がある。

1. 人手で確認したbar / beat map
2. 原mixと二つの分離stemを対応づけたonset event列
3. kick / snare / hat / percussion候補とconfidence
4. bass onsetとdrum onsetの差
5. voice句読点とBODY周期終端の差
6. puncture / horizon介入のabsolute time
7. 1、2、4、8小節でのreturn候補
8. 全層が同時に初期状態へ戻るという対立仮説の検査
9. 量子化、偏差交換、短周期化、foreground固定の変形版
10. 音楽家による拍・細分位置アノテーション

フル尺・同一マスターの音源、または現在プレビューのonset時刻列を取得・生成しない限り、この境界を越えた値は作らない。

## 10. 現在の結論

“Billy Jack”について、現在直接言えるのは次だけである。

> Curtis Mayfield 100プレビューから決定論的に抽出したblind20内で、同一30秒プレビューの推定ドラムonset-spacingは、二つのMDX weightと三つの時間窓を通して、集中した非三連系という事前規則を唯一通過した。

BODY / VOICE / HORIZON、総ループ非形成、物語圧力、低温のグルーヴは、これと接続可能な研究仮説だが、今回の監査値による確定結果ではない。
