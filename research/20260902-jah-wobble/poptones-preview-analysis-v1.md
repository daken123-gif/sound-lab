# `Poptones` Shazam preview analysis v1

- 測定日: 2026-09-04 UTC
- 状態: `preview-only / mixed-audio / research-only`
- 対象研究: `20260902-jah-wobble`
- 製品採用: なし

## 1. SOURCE

```text
SOURCE = (
  source_id = "shazam-apple-catalog-gb-song-724146777",
  recording_identity = "Public Image Ltd. — Poptones",
  edition_or_master = "Metal Box / catalog releaseDate 1979-01-01",
  acquisition_route = "Shazam plugin -> Apple Music catalog search -> preview URL",
  time_scope = "29.976961-second preview; full-track offset is not supplied",
  sha256 = "54c6441a3b93861f479943e5481398f65889954834aa03d8c143ff5f94c368bb",
  legal_or_access_boundary = "catalog preview only; audio is not committed to Git"
)
```

Catalog metadata:

| field | value |
| --- | --- |
| Apple Music song ID | `724146777` |
| ISRC | `GBAAA7900231` |
| catalog duration | `466333 ms` |
| preview duration | `29.976961 s` |
| album | `Metal Box` |
| track number | `4` |
| storefront | `gb` |
| catalog page | https://music.apple.com/gb/album/poptones/724146715?i=724146777 |

別ID `1443064713` の `Poptones (Remastered 2009)` は、同一演奏である可能性が高くても別masterとして分離した。こちらのpreview SHA-256は `f1779f5255c35dee1d08b1882f2c6740d1f5f60fce54f15bf1c6cc863bc16d33`。v1の周期・音高測定には混ぜていない。

## 2. 方法

1. AAC previewを22.05 kHz mono PCMへdecodeした。
2. STFTはHann窓4096 sample、hop 256 sampleを使用した。
3. 35–300 Hzへ時間方向／周波数方向のmedian filterによる簡易harmonic maskを適用した。
4. harmonic low-band featureの自己相似を5.5–8.5秒のlagで探索した。
5. 40–5000 Hzの正方向spectral flux自己相関から0.40–0.55秒のpulse候補を探索した。
6. pitch候補はharmonic成分を35–180 Hzへband-passし、pYINを38–130 Hzで実行した。

この処理はbass stem分離ではない。kick、tom、guitar、声、残響の混入を除去できたとは扱わない。

## 3. 観測値

### 3.1 周期候補

| 測定 | 値 | 境界 |
| --- | ---: | --- |
| 最強の低域回帰lag | `7.3607 s` | 解析feature上の候補 |
| 次候補 | `7.5581 s` / `7.1517 s` | 主候補より弱い |
| pulse候補 | `0.4528 s` | 混合音源のspectral flux |
| pulse候補からのtempo | `132.5 BPM` | 拍位置の人手確認前 |
| 7.3607秒を16拍と仮定したtempo | `130.42 BPM` | 16拍という仮定を含む |

したがって現段階では、約`130–133 BPM`、約16拍で戻る構造を候補とする。BPMと小節線は確定値ではない。

低域featureのlag scoreは主候補`0.1976`、隣接候補`0.0666`だった。この値は使用した標準化とmaskに依存し、音楽的な「類似率」ではない。主候補が周辺lagから分離していることだけを使う。

### 3.2 pitch候補

pYINがconfidence 0.5以上としたframeは`528 / 1289`だった。そのframe内の上位clusterは次の通り。

| tracker label | confidence通過frame内の比率 |
| --- | ---: |
| `E2` | `43.4%` |
| `A2` | `24.6%` |
| `B2` | `11.7%` |
| `A#1` | `8.5%` |
| `C2` | `5.1%` |

これは採譜結果ではない。低いfundamentalを失って倍音をoctave上のpitchとして選ぶ誤り、別楽器をbassとして選ぶ誤りが残る。frame比率を音価比率、発音回数、調性中心へ読み替えない。

## 4. 現在言えること

1. 29.98秒previewの低域には、約7.36秒で回帰する構造がある。
2. その回帰は約16拍の候補と整合する。
3. 自動pitch追跡ではAだけでなくE、B、B♭/A♯、Cの候補が現れた。
4. したがって、本人発言にある「Aを中心に留まる」を、単一pitchの持続やAだけの反復として解釈できない。
5. 一方、混合previewだけでは、各周のbass発音時刻・音価・mute・微小timing差を他声部から分離できない。

## 5. まだ言えないこと

- previewがフル尺のどの絶対時刻を切り出したか。
- 7.3607秒が正確に4小節なのか、別の長周期なのか。
- bass lineの確定音名とoctave。
- 各bass onsetとdrum onsetの前後関係。
- 周期ごとの差がWobbleの再発音によるものか、guitar、drum、voice、mix変化によるものか。
- 1979 catalog版と2009 remasterの音響差。
- 原版、現行live、`Rebuilt In Dub`の構造差。

## 6. 仮説の更新

### 維持する仮説

`Poptones`は、短い一小節loopではなく、複数拍にわたるpitch/register運動を約16拍で重力中心へ戻す可能性が高い。

### 弱めた仮説

「A中心」を、常時最強のfundamentalまたは最多pitch classと同一視する仮説は弱める。中心は、開始点、終止点、低域register、octave関係、周囲の和声との関係から人手で検証する必要がある。

### 未検証のまま残す仮説

固定録音loopと異なり、Wobbleが毎周を再発音して更新しているという中心仮説は維持するが、今回のpreview測定はまだその直接証拠ではない。

## 7. 次の検証

1. previewの約7.36秒区間を4つの拍候補へ分け、人手でbass onsetと音価を注釈する。
2. original mix上の注釈と、分離stem候補上の注釈を突き合わせる。
3. 1979 catalog ID、2009 remaster、Version 3、Peel Sessionを別SOURCEとして同じEVENT schemaで比較する。
4. 自動pitch候補をbass指板上の実行可能な運指と照合し、octave誤りを訂正する。
5. 各周期の差を、pitch、onset、duration、mute、周囲編成の五列へ分ける。

## 8. 保存境界

- preview audio、decode WAV、spectrogram画像はGitへ保存しない。
- 保存するのはsource identity、hash、方法、測定値、証拠境界だけである。
- 本報告は製品仕様、実装、main統合を変更しない。
