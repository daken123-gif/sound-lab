import assert from "node:assert/strict";
import test from "node:test";
import {
  ContactPerformanceTakeError,
  ContactPerformanceTakePlayer,
  ContactPerformanceTakeRecorder,
  instantiateContactPerformanceTake,
  normalizeContactPerformanceTake,
} from "../src/contact-performance-take.js";

const frame = overrides => ({ schemaVersion: "sound-lab.contact-gesture/v0.1", gestureId: "g-1", pointerId: 1,
  phase: "contact", trackIds: [0, 1, 2, 3], x: 0.2, y: 0.8, contactArea: null,
  pressure: null, pressureSource: "unavailable", velocityX: 0, velocityY: 0, timestampMs: 1000, ...overrides });
const rejects = (code, callback) => assert.throws(callback, error => error instanceof ContactPerformanceTakeError && error.code === code);

test("records one canonical relative event stream", () => {
  const recorder = new ContactPerformanceTakeRecorder();
  recorder.capture(frame());
  recorder.capture(frame({ phase: "slide", x: 0.5, timestampMs: 1025 }));
  recorder.capture(frame({ phase: "release", timestampMs: 1040 }));
  const take = recorder.finish();
  assert.equal(take.durationMs, 40);
  assert.deepEqual(take.frames.map(item => item.timestampMs), [0, 25, 40]);
  assert.deepEqual(take.frames.map(item => item.phase), ["contact", "slide", "release"]);
  assert.ok(Object.isFrozen(take)); assert.ok(Object.isFrozen(take.frames));
});

test("preserves concurrent pointer ordering and explicit ownership", () => {
  const recorder = new ContactPerformanceTakeRecorder();
  recorder.capture(frame());
  recorder.capture(frame({ gestureId: "g-2", pointerId: 2, phase: "contact", trackIds: [2], timestampMs: 1005 }));
  recorder.capture(frame({ gestureId: "g-2", pointerId: 2, phase: "cancel", trackIds: [2], timestampMs: 1010 }));
  recorder.capture(frame({ phase: "release", timestampMs: 1015 }));
  const take = recorder.finish();
  assert.deepEqual(take.frames[1].trackIds, [2]); assert.equal(take.frames[2].phase, "cancel");
});

test("refuses empty, unfinished, and globally regressing takes", () => {
  rejects("TAKE_EMPTY", () => new ContactPerformanceTakeRecorder().finish());
  const unfinished = new ContactPerformanceTakeRecorder(); unfinished.capture(frame());
  rejects("TAKE_INCOMPLETE", () => unfinished.finish());
  const regressing = new ContactPerformanceTakeRecorder(); regressing.capture(frame());
  rejects("TAKE_TIME_REGRESSION", () => regressing.capture(frame({ phase: "slide", timestampMs: 999 })));
});

test("validates serialized take duration and terminal phases", () => {
  const recorder = new ContactPerformanceTakeRecorder(); recorder.capture(frame());
  recorder.capture(frame({ phase: "release", timestampMs: 1010 }));
  const take = recorder.finish();
  assert.equal(normalizeContactPerformanceTake(JSON.parse(JSON.stringify(take))).durationMs, 10);
  rejects("TAKE_DURATION", () => normalizeContactPerformanceTake({ ...take, durationMs: 11 }));
});

test("instantiates a replay with new gesture identity and shifted monotonic time", () => {
  const recorder = new ContactPerformanceTakeRecorder(); recorder.capture(frame());
  recorder.capture(frame({ phase: "release", timestampMs: 1010 }));
  const replay = instantiateContactPerformanceTake(recorder.finish(), { startTimestampMs: 5000, instanceId: "a" });
  assert.deepEqual(replay.map(item => item.timestampMs), [5000, 5010]);
  assert.equal(replay[0].gestureId, replay[1].gestureId); assert.notEqual(replay[0].gestureId, "g-1");
  assert.equal(replay[0].pointerId, 1_000_000_000);
  assert.equal(replay[0].x, 0.2); assert.deepEqual(replay[0].trackIds, [0, 1, 2, 3]);
});

test("player emits due frames in time order and finishes once", () => {
  const recorder = new ContactPerformanceTakeRecorder(); recorder.capture(frame());
  recorder.capture(frame({ phase: "slide", x: 0.4, timestampMs: 1010 }));
  recorder.capture(frame({ phase: "release", timestampMs: 1020 }));
  const emitted = []; let finishes = 0;
  const player = new ContactPerformanceTakePlayer({ onFrame: item => emitted.push(item), onFinish: () => finishes++ });
  assert.equal(player.start(recorder.finish(), { startTimestampMs: 500, instanceId: "play" }), 3);
  assert.equal(player.advance(500), 1); assert.equal(player.activeGestureCount, 1);
  assert.equal(player.advance(509), 0); assert.equal(player.advance(510), 1);
  assert.equal(player.advance(520), 1); assert.equal(player.isPlaying, false); assert.equal(finishes, 1);
  assert.deepEqual(emitted.map(item => item.phase), ["contact", "slide", "release"]);
});

test("stopping playback emits cancel for every active synthetic pointer", () => {
  const recorder = new ContactPerformanceTakeRecorder(); recorder.capture(frame());
  recorder.capture(frame({ phase: "release", timestampMs: 1100 }));
  const emitted = [];
  const player = new ContactPerformanceTakePlayer({ onFrame: item => emitted.push(item) });
  player.start(recorder.finish(), { startTimestampMs: 2000, instanceId: "stop" });
  player.advance(2000);
  const cancelled = player.stop(2025);
  assert.equal(cancelled.length, 1); assert.equal(cancelled[0].phase, "cancel");
  assert.equal(cancelled[0].timestampMs, 2025); assert.equal(player.isPlaying, false);
  assert.deepEqual(emitted.map(item => item.phase), ["contact", "cancel"]);
});

test("player rejects overlapping playback and regressing clocks", () => {
  const recorder = new ContactPerformanceTakeRecorder(); recorder.capture(frame());
  recorder.capture(frame({ phase: "release", timestampMs: 1010 }));
  const take = recorder.finish(); const player = new ContactPerformanceTakePlayer({ onFrame: () => {} });
  player.start(take, { startTimestampMs: 100 });
  rejects("PLAYER_ACTIVE", () => player.start(take, { startTimestampMs: 100 }));
  player.advance(100);
  rejects("PLAYER_TIME", () => player.advance(99));
});
