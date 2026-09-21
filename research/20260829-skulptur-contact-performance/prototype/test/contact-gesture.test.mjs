import assert from "node:assert/strict";
import test from "node:test";
import { ContactGestureError, ContactGestureGate, normalizeContactGestureFrame } from "../src/contact-gesture.js";

function frame(overrides = {}) {
  return {
    schemaVersion: "sound-lab.contact-gesture/v0.1", gestureId: "g-1", pointerId: 0,
    phase: "contact", trackIds: [0], x: 0.25, y: 0.75, contactArea: null,
    pressure: null, pressureSource: "unavailable", velocityX: 0, velocityY: 0,
    timestampMs: 100, ...overrides,
  };
}
function rejects(code, callback) {
  assert.throws(callback, error => error instanceof ContactGestureError && error.code === code);
}

test("normalizes and freezes explicit track ownership", () => {
  const result = normalizeContactGestureFrame(frame({ trackIds: [3, 1] }));
  assert.deepEqual(result.trackIds, [1, 3]);
  assert.ok(Object.isFrozen(result));
  assert.ok(Object.isFrozen(result.trackIds));
});
test("keeps pressure provenance honest", () => {
  assert.equal(normalizeContactGestureFrame(frame()).pressure, null);
  assert.equal(normalizeContactGestureFrame(frame({ pressure: 0.4, pressureSource: "hardware" })).pressure, 0.4);
  rejects("PRESSURE_PROVENANCE", () => normalizeContactGestureFrame(frame({ pressure: 0.5 })));
  rejects("PRESSURE_PROVENANCE", () => normalizeContactGestureFrame(frame({ pressure: null, pressureSource: "estimated" })));
});
test("rejects invalid ownership, ranges, and unknown fields", () => {
  rejects("TRACK_COUNT", () => normalizeContactGestureFrame(frame({ trackIds: [] })));
  rejects("TRACK_DUPLICATE", () => normalizeContactGestureFrame(frame({ trackIds: [1, 1] })));
  rejects("TRACK_ID", () => normalizeContactGestureFrame(frame({ trackIds: [4] })));
  rejects("UNIT_RANGE", () => normalizeContactGestureFrame(frame({ x: 1.01 })));
  rejects("UNKNOWN_FIELD", () => normalizeContactGestureFrame({ ...frame(), cutoff: 2 }));
});
test("accepts a causal contact sequence", () => {
  const gate = new ContactGestureGate();
  gate.accept(frame());
  gate.accept(frame({ phase: "slide", timestampMs: 110, x: 0.4 }));
  gate.accept(frame({ phase: "press", timestampMs: 115, pressure: 0.3, pressureSource: "estimated" }));
  gate.accept(frame({ phase: "release", timestampMs: 130 }));
  assert.deepEqual(gate.stateFor("g-1", 0), { phase: "release", timestampMs: 130, terminal: true });
});
test("rejects bad starts, time regression, and terminal resumption", () => {
  rejects("PHASE_START", () => new ContactGestureGate().accept(frame({ phase: "slide" })));
  const gate = new ContactGestureGate();
  gate.accept(frame({ timestampMs: 200 }));
  rejects("TIMESTAMP_REGRESSION", () => gate.accept(frame({ phase: "slide", timestampMs: 199 })));
  gate.accept(frame({ phase: "cancel", timestampMs: 201 }));
  rejects("PHASE_TERMINAL", () => gate.accept(frame({ timestampMs: 202 })));
});
