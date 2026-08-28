import assert from "node:assert/strict";
import test from "node:test";
import { SpectralGestureLoop } from "../src/spectral-gesture-loop.js";

test("capture is ignored until recording is explicitly enabled", () => {
  const loop = new SpectralGestureLoop();
  assert.equal(loop.capture(2, 0.4, 0.25), false);
  assert.equal(loop.valuesAt(0.25)[2], null);
});

test("an explicit recording pass creates a band curve", () => {
  const loop = new SpectralGestureLoop();
  loop.startRecording();
  loop.capture(3, 0.2, 0.25);
  loop.capture(3, 0.8, 0.75);
  loop.stopRecording();
  assert.equal(loop.valuesAt(0.5)[3], 0.5);
});

test("playback interpolates continuously across the loop boundary", () => {
  const loop = new SpectralGestureLoop();
  loop.startRecording();
  loop.capture(1, 0.2, 0.9);
  loop.capture(1, 0.8, 0.1);
  loop.stopRecording();
  assert.ok(Math.abs(loop.valuesAt(0)[1] - 0.5) < 1e-12);
});

test("a pass replaces only bands that are actually touched", () => {
  const loop = new SpectralGestureLoop();
  loop.startRecording();
  loop.capture(1, 0.1, 0.2);
  loop.capture(7, 0.7, 0.2);
  loop.stopRecording();

  loop.startRecording();
  loop.capture(1, 0.9, 0.4);
  loop.stopRecording();
  assert.equal(loop.valuesAt(0.2)[1], 0.9);
  assert.equal(loop.valuesAt(0.2)[7], 0.7);
});

test("serialized gesture data round-trips", () => {
  const source = new SpectralGestureLoop();
  source.startRecording();
  source.capture(4, 0.25, 0.1);
  source.capture(4, 0.75, 0.6);
  source.stopRecording();

  const restored = new SpectralGestureLoop();
  restored.deserialize(source.serialize());
  assert.deepEqual(restored.serialize(), source.serialize());
});
