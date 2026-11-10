# Skulptur-inspired DSP prototype

10帯域フィルターバンクの音響経路と、指で直接彫る試奏面を検証するための実験実装です。
Skulpturのソースコードを解析・複製したものではなく、公開マニュアルから確認できる構造を基にした独立実装です。

## 含まれるもの

- 10帯域：1 LP + 8 BP + 1 HP
- 4次／8次の切替
- 待機時の完全Dry経路
- 帯域音量とWet切替のサンプル単位平滑化
- AudioWorklet用ラッパー
- マルチタッチ制御
- Elastic復帰
- Throw慣性と端点反射
- Flowの帯域波
- 明示RECによる帯域別ジェスチャーループ（自動録音なし）
- 一周をまたぐ補間と、触れた帯域だけの差し替え録音
- 手動タッチ > 記録演奏 > Throw > Flow > 基準位置の優先制御
- 4ループ合成バスへのSkulptur適用
- スペクトル処理を通らない独立ドラムバス
- 帯域別Feedbackと非線形の発散防止
- 合流後0.98の最終安全天井
- 中央基準の単一ジェスチャー（下＝Cut、上＝Feedback）
- CutとFeedbackを同じRECへ記録
- iPhone縦横対応のマルチタッチ試奏面
- 画像島の接触研究から移植した`ContactGestureFrame v0.1`入力境界
- `contact / press / slide / release / cancel`の因果検証と中断時cancel
- 正規化座標、4トラック所有権、pressure由来を共有するPointer Event adapter
- 画面外release、capture喪失、画面回転でもpointer所有権を残さないcancel回復
- 同じ接触frame列を保存し、別時刻・別gesture IDの再生列へ展開するContact Performance Take
- 一つの`TAKE`ボタンによる接触演奏の録音・一回再生・安全停止
- 画面非表示時の接触cancelとTAKE再演停止、iOS復帰時の音響時計検査と同一STARTボタンからの再開
- 同じTAKE再生frame列をAudioContext時計へ40ms先行予約し、音をAudioWorkletのrender quantumで発行
- 再生中の実指と衝突しない合成pointer ID
- DSPが実際に再生しているREC・Flow・Throwの帯域位置を30fpsで表示
- 4トラック本体へ接続する`SkulpturHostController`
- 本体プロジェクトへ保存できるジェスチャー状態の取得・復元
- LOOP 1〜4を押して手元の音声ファイルへ明示的に差し替える試奏機能
- 読み込んだ音声の4秒整形、切断点フェード、再生位置同期クロスフェード
- 自動テスト
- 4次／8次の比較用WAV生成

## 実行

```bash
npm test
npm run render
npm run demo
```

生成音は `renders/` に出ます。最初の1秒はDry、その後に10帯域を波状に動かし、最後にDryへ復帰します。
試奏面はサーバー起動後に `http://localhost:8080/demo/` を開き、`DEMO START`を押すまで音を開始しません。
起動後、下端の`LOOP 1`〜`LOOP 4`を押すと、そのトラックだけ手元の音声ファイルへ差し替えられます。

## 操作

- 画面は左から低音、右へ行くほど高音になる10本の縦帯です。
- 縦の中央が無加工。中央から下へ動かすと、その帯域を削ります。
- 中央から上へ動かすと、その帯域のFeedbackが増え、上端付近で音が自己持続します。
- 横へなぞると、低音から高音へ連続して彫れます。複数の指で別帯域を同時に触れます。
- RECなしの操作は指を離せば戻ります。RECを明示した間だけ、触れた帯域のCutとFeedbackを一周へ記録します。
- 素早く下側を弾いて離すとThrowが残ります。Flowは触れていない帯域だけを自動で波打たせます。
- 指を離した後の細いマーカーは、DSP側で再生中のREC・Flow・Throwです。画面だけの疑似アニメーションではありません。
- `LOOP 1`〜`LOOP 4`を押して音声ファイルを選ぶと、選んだトラックだけが現在位置から差し替わります。読み込むのは先頭4秒です。
- `TAKE`を押して演奏し、指を離して`TAKE STOP`を押すと接触演奏を保持します。次の`TAKE PLAY`で音と表示を同じframe列から一回再生します。再生中の`TAKE STOP`はcancelを発行して止めます。
- 再演中にアプリを隠すとTAKEをその場でcancelします。復帰後は`AudioContext.state`だけでなく`currentTime`が実際に進むかを検査します。時計が止まっていれば既存のSTARTボタンが`RESUME`へ変わり、明示操作で`suspend → resume`して再検査します。
- TAKEの音響接触は再生開始時に40ms先行してAudioWorkletへ予約します。表示は同じframe列を画面更新に合わせて追い、描画落ちで音響eventまで16ms単位に遅れる経路を避けます。
- 接触面では、Pointer Eventをまず検証済み接触frameへ変換し、その同じframeから表示と音響操作を駆動します。

## 現段階の境界

- フィルター周波数は暫定値です。
- 4次／8次の優劣はiPhone実機で試聴・負荷検証するまで確定しません。
- 試奏面は実装しましたが、製品全体の画面へはまだ統合していません。
- 試奏面のファイル読込は音程を変えるタイムストレッチではありません。4秒より長い音は切り、短い音は無音で埋めます。
- 試奏面で選んだ音声ファイル自体は保存しません。製品本体では従来の4トラック保存を使います。
- FeedbackはローカルDSP検証済みですが、iPhone実機の音量安全性は未検証です。
- pressureとcontactAreaは入力契約へ保持しますが、iPhone実機で由来を検証するまで音響パラメータへ割り当てません。
- `REC`は一周ごとの帯域カーブ録音、`TAKE`は指の接触そのものを一回録音・再生する別機能です。複数Takeの一覧、名前、永続保存UIは未実装です。
- TAKEの予約精度はNode上のqueue因果とAudioContext時刻mappingを検証済みですが、Mobile Safariの実render quantumと聴覚上のずれは未検証です。
- 音響時計停止の判定と復旧手順は単体検証済みですが、WebKit不具合をiPhone実機で再現して復旧できることは未検証です。
- 内部オーバーサンプリングは未実装です。
- `wetTrim` は暫定値で、ラウドネス整合はまだ行っていません。

## AudioWorkletへの接続例

製品本体への接続は[`INTEGRATION.md`](./INTEGRATION.md)と`SkulpturHostController`を使います。下記はWorkletへ直接メッセージを送る低水準例です。

```js
await audioContext.audioWorklet.addModule(
  new URL("./src/skulptur-filter-bank.worklet.js", import.meta.url)
);

const node = new AudioWorkletNode(audioContext, "skulptur-filter-bank", {
  numberOfInputs: 5, // loop 1〜4 + 独立drum
  numberOfOutputs: 1,
  outputChannelCount: [2],
  processorOptions: { channels: 2, order: 8 }
});

node.port.postMessage({
  type: "touch-begin",
  pointerId: 1,
  band: 4,
  position: 0.15, // 0=最大Cut、0.5=無加工、1=最大Feedback
  timeSeconds: audioContext.currentTime
});
node.port.postMessage({ type: "touch-end", pointerId: 1 });
node.port.postMessage({ type: "transport", running: true, loopDurationSeconds: 4 });
node.port.postMessage({ type: "gesture-record", enabled: true });
// 指で演奏する。RECを止めても、触れた帯域だけが一周ごとに再生される。
node.port.postMessage({ type: "gesture-record", enabled: false });
node.port.postMessage({ type: "feedback", band: 5, value: 0.82 }); // 1.0付近で自己持続域
```

入力0〜3は4本のループ、入力4は独立ドラムです。Skulpturはループの合成音だけを処理し、ドラムは処理後に加算します。

接触研究の由来、採用範囲、保留事項は[`CONTACT-BRIDGE.md`](./CONTACT-BRIDGE.md)にあります。
