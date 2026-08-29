# Skulptur接触演奏とPerformance Take

- research-id: `20260829-skulptur-contact-performance`
- 状態: `candidate / implemented-unverified`
- 更新日: 2026-08-29
- 対象: 4トラック録音後のSkulptur型主演奏面
- 製品採用: 未判断
- iPhone実機: 未検証

## 現在の問い

画像接触研究の`ContactGestureFrame`を、見た目だけのPointer演出ではなく、Skulpturの音響操作、描画、明示録音、一回再生が同じevent列を共有する演奏経路へ発展させられるか。

## 権威と境界

### Gitで確認した前提

- `integration/DIRECTION.md`: 4トラック録音後の主演奏面はSkulptur型を中心とし、KAOSS中心階層は復活させない。
- `research/20260828-image-contact-bridge/`: 接触frame、実行時gate、Pointer Event adapter。Skulptur mapping、製品UI、DSP、Performance Takeは固定していない。
- `RESEARCH_WORKFLOW.md`: 未検証試作は固有research branchへ分離し、mainへ直接入れない。

### この研究が固定しないもの

- プロジェクト全体の最終Skulptur DSP
- pressure/contactAreaの音響割当
- 複数Takeの製品UI、永続保存形式
- iPhone実機での操作性、遅延、発熱、音量安全性
- 実製品への採用状態

## 実装した候補

### 接触から音響へのmapping

- 正規化`x`を10帯域へ割り当てる。
- `1-y`を既存のCut / Neutral / Feedback位置へ割り当てる。
- 現試作は4ループ合成後の共通スペクトル処理なので、`trackIds`を暗黙のmasterへ変換せず`[0,1,2,3]`と明示する。
- pressure/contactAreaはframeに保持するが音へ割り当てない。

### 中断回復

- `pointercancel`は画面外座標を再計算せず、最後に成立した接触点からcancelする。
- capture中の`pointerup`がsurface外で拒否された場合、releaseを捏造せずcancelを発行する。
- capture喪失、blur、pagehide、orientationchange、visibilitychangeでもactive pointerを残さない。

### Contact Performance Take

- 受理済みframeを相対時刻の一列として記録する。
- 空Take、時刻後退、未終了gesture、duration不一致を拒否する。
- 再生時はgesture IDとpointer IDを新しいinstanceへ分離し、実指との衝突を避ける。
- 実時間playerは期限到来frameだけを発行し、中断時は全active接触へcancelを発行する。
- デモは一つの`TAKE`ボタンで録音、停止、一回再生、再生中断を循環する。`REC`の帯域ループ録音とは別機能である。
- 画面非表示ではTAKE再演をcancelし、復帰時の残りframe一括発行を防ぐ。
- iOSがAudioContextを休止した場合は、既存STARTボタンを`RESUME`へ切り替え、追加モードなしで明示再開する。
- TAKE開始時に同じ再生frame object列を表示playerと音響schedulerへ渡し、音響は40ms先行してAudioContext時計へ予約する。
- AudioWorkletは予約commandをrender quantumごとに適用し、schedule IDの中断で未発行commandとactive接触を破棄する。
- 予約batchは時刻順、begin/move/end因果、全pointer終端を検査する。

## 触る実装パス

- `research/20260829-skulptur-contact-performance/README.md`
- `research/20260829-skulptur-contact-performance/prototype/`

既存の製品コード、統合正本、画像接触bridgeは変更しない。

## 検証

ローカルNode環境で次を実行した。

```sh
node --check demo/app.js
node --check src/contact-performance-take.js
node --test
node scripts/render-demo.mjs
```

- 自動テスト: 84 pass / 0 fail
- 4次／8次の比較WAV生成: 成功
- HTTP配信資産: 検証記録は`prototype/VALIDATION.md`
- ZIP展開後の同一テスト: 配布物作成時に実施

この結果はNode上の構造・数値・event検査であり、実ブラウザ音響、Mobile Safari、iPhone実機、聴感採用の証拠ではない。

## Field Looperへの扱い

- [x] 研究記録
- [x] 実装候補
- [x] ContactGestureFrameからSkulpturへのcandidate mapping
- [x] Contact Performance Take参照実装
- [x] 一ボタンTAKE試奏UI
- [ ] 製品コード統合
- [ ] 実ブラウザ音響検証
- [ ] iPhone実機検証
- [ ] プロジェクト採用判断

## 依存する研究

- `research/20260828-image-contact-bridge/`
- `integration/DIRECTION.md`
- `integration/DECISIONS.md`
- `integration/STATUS.md`

## 失効した判断

- KAOSSを主演奏面とする判断は復活させない。
- Pointerの見た目だけを動かし、音響eventと別系統にする実装は採らない。

## 未検証事項

- Mobile SafariのPointer Event順序、capture、pressure、contactArea
- iPhone 13 mini縦横での一画面収まりとマルチタッチ
- AudioWorklet実時間負荷、Feedback音量安全性
- 同じframe列を追う表示と音響の実機上の同期精度
- AudioContext時計への40ms先行予約がMobile Safariで十分か
- Mobile SafariがAudioContextを休止・再開する実際のタイミング
- 複数Takeの選択、命名、保存、再読込み
- 4トラック個別処理へ発展させる場合のtrack ownership
