import assert from "node:assert/strict";
import test from "node:test";
import {
  composeFeedback,
  mapSurfacePosition,
  SpectralSurfaceControl,
  surfacePositionFromValues
} from "../src/spectral-surface-control.js";
import { SpectralGestureLoop } from "../src/spectral-gesture-loop.js";

test("the surface center is neutral", () => {
  assert.deepEqual(mapSurfacePosition(0.5), { position: 0.5, gain: 1, feedback: 0 });
});

test("moving down carves while moving up excites feedback", () => {
  assert.deepEqual(mapSurfacePosition(0), { position: 0, gain: 0, feedback: 0 });
  assert.deepEqual(mapSurfacePosition(1), { position: 1, gain: 1, feedback: 1 });
  assert.deepEqual(mapSurfacePosition(0.25), { position: 0.25, gain: 0.5, feedback: 0 });
  assert.deepEqual(mapSurfacePosition(0.75), { position: 0.75, gain: 1, feedback: 0.5 });
});

test("surface positions clamp to the playable range", () => {
  assert.equal(mapSurfacePosition(-4).gain, 0);
  assert.equal(mapSurfacePosition(7).feedback, 1);
});

test("render values map back to the same cut and feedback surface", () => {
  assert.equal(surfacePositionFromValues(0, 0), 0);
  assert.equal(surfacePositionFromValues(0.5, 0), 0.25);
  assert.equal(surfacePositionFromValues(1, 0), 0.5);
  assert.equal(surfacePositionFromValues(1, 0.5), 0.75);
  assert.equal(surfacePositionFromValues(1, 1), 1);
});

test("multiple fingers control independent bands and newest wins collisions", () => {
  const surface = new SpectralSurfaceControl();
  surface.beginTouch(1, 2, 0.75);
  surface.beginTouch(2, 7, 1);
  surface.beginTouch(3, 2, 0.9);
  const values = surface.feedbackSnapshot();
  assert.ok(Math.abs(values[2] - 0.8) < 1e-12);
  assert.equal(values[7], 1);
  surface.endTouch(3);
  assert.equal(surface.feedbackSnapshot()[2], 0.5);
});

test("feedback priority is finger, recorded gesture, then fixed base", () => {
  const base = [0.1, 0.2, 0.3];
  const recorded = [null, 0.5, 0.6];
  const manual = [null, null, 0.9];
  assert.deepEqual(composeFeedback(base, recorded, manual), [0.1, 0.5, 0.9]);
});

test("one recording pass stores both carve and feedback from the same gesture", () => {
  const gainLoop = new SpectralGestureLoop();
  const feedbackLoop = new SpectralGestureLoop();
  gainLoop.startRecording();
  feedbackLoop.startRecording();
  const mapped = mapSurfacePosition(0.8);
  gainLoop.capture(5, mapped.gain, 0.25);
  feedbackLoop.capture(5, mapped.feedback, 0.25);
  gainLoop.stopRecording();
  feedbackLoop.stopRecording();
  assert.equal(gainLoop.valuesAt(0.25)[5], 1);
  assert.ok(Math.abs(feedbackLoop.valuesAt(0.25)[5] - 0.6) < 1e-12);
});
