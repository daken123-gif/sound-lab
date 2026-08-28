import test from "node:test";
import assert from "node:assert/strict";
import {
  ContactGestureError,
  ContactGestureGate,
  normalizeContactGestureFrame,
} from "./contact-gesture.mjs";

function frame(overrides = {}) {
  return {
    schemaVersion: "sound-lab.contact-gesture/v0.1",
    gestureId: "gesture-1",
    pointerId: 0,
    phase: "contact",
    trackIds: [0],
    x: 0.25,
    y: 0.75,
    contactArea: null,
    pressure: null,
    pressureSource: "unavailable",
    velocityX: 0,
    velocityY: 0,
    timestampMs: 100,
    ...overrides,
  };
}

function rejectsCode(callback, code) {
  assert.throws(callback, error => error instanceof ContactGestureError && error.code === code);
}

test("normalizes track ownership without mutating input", () => {
  const input = frame({ trackIds: [3, 1] });
  const result = normalizeContactGestureFrame(input);
  assert.deepEqual(result.trackIds, [1, 3]);
  assert.deepEqual(input.trackIds, [3, 1]);
  assert.ok(Object.isFrozen(result));
  assert.ok(Object.isFrozen(result.trackIds));
});

test("accepts hardware and explicitly estimated pressure", () => {
  assert.equal(normalizeContactGestureFrame(frame({ pressure: 0.4, pressureSource: "hardware" })).pressure, 0.4);
  assert.equal(normalizeContactGestureFrame(frame({ pressure: 0.6, pressureSource: "estimated" })).pressure, 0.6);
});

test("rejects fabricated or missing pressure provenance", () => {
  rejectsCode(() => normalizeContactGestureFrame(frame({ pressure: 0.5 })), "PRESSURE_PROVENANCE");
  rejectsCode(() => normalizeContactGestureFrame(frame({ pressure: null, pressureSource: "hardware" })), "PRESSURE_PROVENANCE");
});

test("rejects empty, duplicate, and out-of-range track ownership", () => {
  rejectsCode(() => normalizeContactGestureFrame(frame({ trackIds: [] })), "TRACK_COUNT");
  rejectsCode(() => normalizeContactGestureFrame(frame({ trackIds: [1, 1] })), "TRACK_DUPLICATE");
  rejectsCode(() => normalizeContactGestureFrame(frame({ trackIds: [4] })), "TRACK_ID");
});

test("rejects unit values instead of silently clamping them", () => {
  rejectsCode(() => normalizeContactGestureFrame(frame({ x: 1.01 })), "UNIT_RANGE");
  rejectsCode(() => normalizeContactGestureFrame(frame({ contactArea: -0.01 })), "UNIT_RANGE");
});

test("rejects unknown fields and non-finite numbers", () => {
  rejectsCode(() => normalizeContactGestureFrame({ ...frame(), dspCutoff: 0.8 }), "UNKNOWN_FIELD");
  rejectsCode(() => normalizeContactGestureFrame(frame({ velocityX: Number.NaN })), "NUMBER");
});

test("accepts a causal contact, slide, press, release sequence", () => {
  const gate = new ContactGestureGate();
  gate.accept(frame());
  gate.accept(frame({ phase: "slide", timestampMs: 110, x: 0.4 }));
  gate.accept(frame({ phase: "press", timestampMs: 110, pressure: 0.3, pressureSource: "estimated" }));
  gate.accept(frame({ phase: "release", timestampMs: 130 }));
  assert.deepEqual(gate.stateFor("gesture-1", 0), { phase: "release", timestampMs: 130, terminal: true });
});

test("requires contact as the first phase", () => {
  const gate = new ContactGestureGate();
  rejectsCode(() => gate.accept(frame({ phase: "slide" })), "PHASE_START");
});

test("rejects timestamp regression", () => {
  const gate = new ContactGestureGate();
  gate.accept(frame({ timestampMs: 200 }));
  rejectsCode(() => gate.accept(frame({ phase: "slide", timestampMs: 199 })), "TIMESTAMP_REGRESSION");
});

test("rejects events after release or cancel until explicitly cleared", () => {
  const gate = new ContactGestureGate();
  gate.accept(frame());
  gate.accept(frame({ phase: "cancel", timestampMs: 101 }));
  rejectsCode(() => gate.accept(frame({ phase: "contact", timestampMs: 102 })), "PHASE_TERMINAL");
  assert.equal(gate.clear("gesture-1", 0), true);
  assert.equal(gate.accept(frame({ timestampMs: 102 })).phase, "contact");
});

test("tracks concurrent pointers independently", () => {
  const gate = new ContactGestureGate();
  gate.accept(frame());
  gate.accept(frame({ gestureId: "gesture-2", pointerId: 1, trackIds: [2], timestampMs: 90 }));
  gate.accept(frame({ phase: "release", timestampMs: 120 }));
  assert.equal(gate.stateFor("gesture-1", 0).terminal, true);
  assert.equal(gate.stateFor("gesture-2", 1).terminal, false);
});
