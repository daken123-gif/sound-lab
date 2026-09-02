# Skulptur host integration

Skulpturは再生・録音・マイクを所有しません。4トラック本体が持つAudioContext、4本のループ出力、独立ドラム出力、トランスポートへ接続します。

## 固定配線

| Worklet入力 | 本体側の信号 | スペクトル処理 |
| --- | --- | --- |
| 0 | LOOP 1 | 通る |
| 1 | LOOP 2 | 通る |
| 2 | LOOP 3 | 通る |
| 3 | LOOP 4 | 通る |
| 4 | DRUM | 通らない |

## 最小接続

```js
import { SkulpturHostController } from "./src/skulptur-host-controller.js";

const skulptur = await SkulpturHostController.create(audioContext, {
  order: 4,
  loopDurationSeconds: 4
});

skulptur.attach({
  loops: [loop1Output, loop2Output, loop3Output, loop4Output],
  drum: drumOutput,
  output: masterInput
});

skulptur.setTransport({ running: true, phase: 0, loopDurationSeconds: 4 });
```

本体の再生開始と同時に`setTransport`を送り、ループ位置が飛んだ場合は`phase`も更新します。Skulptur側から再生や録音を勝手に始める処理はありません。

## 指操作

ブラウザUIでは、Pointer Eventを直接`beginTouch`へ渡さず、接触入力bridgeを通します。

```js
import { bindPointerContactSurface } from "./src/pointer-contact-adapter.js";
import { skulpturCommandFromContactFrame } from "./src/skulptur-contact-bridge.js";

bindPointerContactSurface({
  surface,
  scope: window,
  resolveTrackIds: () => [0, 1, 2, 3],
  onFrame(frame) {
    const command = skulpturCommandFromContactFrame(frame);
    // command.type: begin | move | end
  }
});
```

現DSPは4ループ合成後の共通スペクトル面なので、所有権は暗黙のmasterではなく`[0, 1, 2, 3]`と明示します。横位置は10帯域、縦位置はCut↔Feedbackへ変換します。pressure/contactAreaの音響割当は実機検証まで行いません。

低水準のホスト操作は次です。

```js
skulptur.beginTouch({ pointerId, band, position, timeSeconds: audioContext.currentTime });
skulptur.moveTouch({ pointerId, band, position, timeSeconds: audioContext.currentTime });
skulptur.endTouch(pointerId, { throwMotion: true });
```

`band`は0〜9です。`position`は0が最大Cut、0.5が無加工、1が最大Feedbackです。

## Contact Performance Take

接触軌跡を保存する場合は、描画用と音響用に別々の記録を作らず、bridgeが受理したframeをそのまま記録します。

```js
import {
  ContactPerformanceTakeRecorder,
  instantiateContactPerformanceTake
} from "./src/contact-performance-take.js";

const recorder = new ContactPerformanceTakeRecorder();
// onFrame内で
recorder.capture(frame);

const take = recorder.finish(); // 全gestureがrelease/cancel済みの場合だけ成功
project.skulpturContactTake = take;

const replayFrames = instantiateContactPerformanceTake(take, {
  startTimestampMs: performance.now(),
  instanceId: "take-2"
});
// timestampMsに従って、通常のonFrameと同じperformContactFrameへ渡す
```

再生列は座標、phase、trackIds、pressure由来を保持し、gesture ID、pointer ID、時刻を新しい再生instanceへ変換します。合成pointer IDにより、再生中の実指と衝突しません。

`ContactPerformanceTakePlayer`は単調時刻を`advance(timestampMs)`へ渡す表示playerです。開始時の`onSchedule(frames)`には、表示へ順次渡されるものと同じ再生frame object列が一度だけ渡ります。音響はその列から作ったcommandをAudioContext時計へ先行予約します。

```js
const commands = replayFrames.map(frame => {
  const mapped = skulpturCommandFromContactFrame(frame);
  const timeSeconds = audioStartTime + (frame.timestampMs - replayFrames[0].timestampMs) / 1000;
  if (mapped.type === "end") {
    return { type: "touch-end", pointerId: mapped.pointerId, throwMotion: mapped.throwMotion, timeSeconds };
  }
  return {
    type: mapped.type === "begin" ? "touch-begin" : "touch-move",
    pointerId: mapped.pointerId,
    band: mapped.band,
    position: mapped.position,
    timeSeconds
  };
});

skulptur.scheduleTouches("take-2", commands);
// 中断時
skulptur.cancelScheduledTouches("take-2");
```

予約batchは全pointerが`touch-begin`から`touch-end`まで完結し、時刻が後退しない場合だけ受理されます。AudioWorkletは`currentTime`が到来したcommandをrender quantumごとに適用します。表示は`requestAnimationFrame`で同じframe列を追跡しますが、音響時刻には使用しません。

## 演奏状態の保存

```js
skulptur.setRecording(true);
// 指で演奏
skulptur.setRecording(false);

const gestureState = await skulptur.dumpGestureState();
project.skulpturGesture = gestureState;

// プロジェクト再読込み時
skulptur.loadGestureState(project.skulpturGesture);
```

保存対象はジェスチャーだけです。音声ループ本体は従来どおり4トラック側が保存します。

## 終了

```js
skulptur.setTransport({ running: false });
skulptur.dispose();
```

`dispose()`は接続だけを外します。共有AudioContextは本体が管理します。
