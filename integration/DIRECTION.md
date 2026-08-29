# プロジェクト方向

更新日: 2026-08-29

## 中心

このプロジェクトは、iPhoneを素材採取、4トラック録音、録音素材への直接演奏、音響処理、演奏結果の保存まで一続きにする個人用楽器を作る。

既存DAWの縮小版、調べた機材の全部載せ、ユーザーの代わりに演奏を決める自動生成機にはしない。

## 現在固定する境界

1. **4トラックを録音の中心にする**
   - 4本の元音声を保ち、録音・再生・停止・消去の状態を明示する。
   - 波形は実サンプルから描き、無音を偽波形で埋めない。
2. **録音開始は人間が決める**
   - 入力検出、機器選択、プリセット選択で自動録音しない。
   - 入力元、接続状態、録音中かを常時判別できるようにする。
3. **RAWと音作りを分離する**
   - iPhoneマイクを専用入力として研究し、実際の入力経路を隠さない。
   - RAWを保持し、校正、COLOR、ダイナミクス、空間、バウンスを非破壊の後段として扱う。
4. **録音後の主演奏面はSkulptur型を中心にする**
   - 録音素材そのものへ触る音色運動を主演奏経路に置く。
   - `sympathia` のDraft契約はSculptorCoreをpost-loop / pre-mixへ置く。
   - `sound-lab` PR #44には、接触入力、10帯域スペクトル面、Contact Performance Take、4ループ＋独立DRUM接続の専用候補実装がある。ただし `x`→10帯域、`1-y`→Cut / Neutral / Feedback、4次／8次フィルター、画面構成は `candidate / implemented-unverified` であり、製品採用ではない。
   - `pressure` / `contactArea` は入力frameに保持するが、実機検証まで音響へ割り当てない。
5. **KAOSSをプロジェクト全体の主演奏モデルにしない**
   - KAOSS型Master採用は失効した。
   - KAOSS固有の研究は歴史資料または限定部品としてのみ参照し、中心階層を復活させない。
6. **ドラムは独立演奏系にする**
   - 4トラックへ常時飲み込ませず、同期または明示的音声接続を別判断にする。
7. **簡単さを演奏経路の短さで守る**
   - Koala Samplerより複雑にしない。
   - 深い階層、隠れたモード、同時押し、常設ノブの増殖を中心に置かない。
8. **旧Field Looper UIを設計資産として再利用しない**
   - 退役したKAOSS中心の視覚言語、円形ループ、微小ラベル、強制横画面は隔離を維持する。
   - `main` のLive Canvas置換はローカル実装候補であり、プロジェクト全体のテンプレートではない。ブラウザ描画とiPhone実機QAを通るまで設計採用を固定しない。
9. **Abbey Road研究を入力構造へ限定接続する**
   - 物理配置、RAW保持、入力経路ごとの校正、コンソール色の分離をiPhone入力段の採用原則とする。
   - REDD/TG入力DSP試作は`main`へ入ったがUI・実音経路へ未接続。RS124、SPACE、RS56、J37、ADTを含め、実測・実機検証なしで原機再現としない。
10. **入力・描画・音響・Takeの因果を一つにする**
   - `ContactGestureFrame`として受理した同じframe列から描画、音響操作、Contact Performance Takeを導出する。
   - Pointer演出だけを別系統で動かしたり、拒否された入力からreleaseを捏造したりしない。
   - この原則は`main`の画像接触bridgeで研究済みだが、PR #44の製品統合と実機runtimeは未検証である。

## 現在の構造

```text
物理配置／iPhone入力
  -> RAW保存
  -> 入力校正／非破壊COLOR
  -> 4トラック録音
  -> Skulptur型の主演奏面
  -> 必要な処理だけを明示接続
  -> 出力／Performance Take／非破壊バウンス
```

THE PIPE型音源は録音前の入力楽器候補。Chroma Console型の可変直列経路、Things Motor型4入力Rotor、Microcosm型時間変換、Strymon／OTO空間は、主演奏面を置き換えない候補部品として扱う。Dedalus型時間メモリとBattleFX型rhythmic-tailは、4トラックを増やさず明示sendで接続する後段候補であり、採用・信号順・UIはまだ固定しない。Abbey Road研究からは配置・RAW・校正・コンソール色分離だけを入力構造へ採用し、COLOR・SPACE・BOUNCE各DSPは個別候補として扱う。

## 統合していない候補

- Skulptur接触演奏: `sound-lab` Draft PR #44。10帯域、Cut / Neutral / Feedback、4次／8次、Elastic / Throw / Flow、明示REC、Contact Performance Take、4ループ＋独立DRUM接続の参照実装。Node 84/84と比較WAV生成の再検証はあるが、製品コード未統合、ブラウザ音響・Mobile Safari・iPhone・聴感・負荷・音量安全性は未検証。
- THE PIPE / BODY: 研究と独立DSP試作。人声、iPhone、Safariは未検証。
- Chroma Console: 可変直列経路、Gesture、固有Drift、単一Captureの研究候補。
- Things Motor: 4入力Rotorの係数・慣性モデル候補。
- Dedalus: 4トラックから明示sendする一基の共有時間メモリ候補。二読取ヘッドのクロスフェード、Scrub、Drift、feedback帯域制限等は研究段階で、第五トラック／第五ルーパーにはしない。
- BattleFX: 選択トラック用の一基のrhythmic-tail send候補。delay/reverb tailの独立choke、密度、nudgeを候補とし、master常設、4インスタンス、KAOSS型XY復活には使わない。
- Abbey Road: 配置、RAW、入力経路別校正、マイク特性とコンソール色の分離は入力構造へ採用。REDD/TG入力DSP試作は`main`統合済みだがUI・実音未接続。他のDSPも未検証候補。
- Max/MSP / RNBO: `sympathia` Draftの4-track LooperCoreとhost/control契約。構造テスト報告はあるが、RNBO runtime、Max compile、実音は未検証。
- AUM: `sympathia` DraftのAUv3 Host Input / Main / Aux契約候補。Swift・AUM・iPhone runtimeは未検証。
- Microcosm: `sympathia` Draftのsource-aware memory研究候補。実装・runtime検証は未着手。
- 1176LN Blackface: `sympathia` Draftの線形reference core候補。非線形、実機校正、resampling、iPhone検証は未完了。
- Transit 2: `sympathia` DraftのMotion Engine研究候補。実装・端末検証は未着手。
- Combustor: `sympathia` branchの独立resonator仮説。コード・テスト・比較WAVはあるが、製品再現や採用の証拠ではない。
- Performance Take: 明示開始の記録核は候補。PR #44のContact Takeは同一frame列の一回記録・再生とAudioContext時計へのscheduleまで実装したが、実ブラウザ時間精度、複数Take、永続保存、製品UI、端末runtimeは未固定。

これらの`Draft`、non-Canon branch、テスト成功は、`sound-lab/main`への採用、実機動作、聴感採用を意味しない。

## まだ固定しないもの

- Skulptur型主演奏面の最終DSP、フィルター次数、周波数、`x / y` mapping、`pressure / contactArea`割当、画面構成
- PR #44の製品統合方法と4トラック個別処理へ発展させる場合のtrack ownership
- Elektron／独立ドラム、OTO BIM / BAM / BOUM、Strymonの固有研究本文と接続仕様
- AUv3、Web、ネイティブiOSの最終分担
- 各候補部品の信号順、同時搭載数、CPU予算
- Performance Takeの複数Take、永続保存形式、最終UI
- 縦横画面の最終配置

研究本文がGitにない領域は名称から内容を補わない。別リポジトリのDraft研究は証拠として参照できるが、個別の統合判断なしにCanonまたは製品仕様へ昇格させない。
