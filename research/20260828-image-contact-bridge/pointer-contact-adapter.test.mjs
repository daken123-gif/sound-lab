import test from "node:test";
import assert from "node:assert/strict";
import {
  PointerContactAdapter,
  PointerContactAdapterError,
  bindPointerContactSurface,
} from "./pointer-contact-adapter.mjs";

class EventTargetStub {
  #listeners = new Map();
  captures = [];
  rect = { left: 10, top: 20, width: 200, height: 100 };
  getBoundingClientRect() { return this.rect; }
  setPointerCapture(pointerId) { this.captures.push(pointerId); }
  addEventListener(type, listener) {
    const list = this.#listeners.get(type) ?? [];
    list.push(listener);
    this.#listeners.set(type, list);
  }
  removeEventListener(type, listener) {
    this.#listeners.set(type, (this.#listeners.get(type) ?? []).filter(item => item !== listener));
  }
  dispatch(event) { for (const listener of this.#listeners.get(event.type) ?? []) listener(event); }
  count(type) { return (this.#listeners.get(type) ?? []).length; }
}

function event(type, overrides = {}) {
  return {
    type,
    pointerId: 7,
    pointerType: "touch",
    clientX: 110,
    clientY: 70,
    pressure: 0.5,
    width: 20,
    height: 10,
    timeStamp: 1000,
    ...overrides,
  };
}

function adapter(overrides = {}) {
  const surface = overrides.surface ?? new EventTargetStub();
  return new PointerContactAdapter({
    surface,
    resolveTrackIds: ({ x }) => x < 0.5 ? [0] : [1],
    ...overrides,
  });
}

function rejectsCode(callback, code) {
  assert.throws(callback, error => error instanceof PointerContactAdapterError && error.code === code);
}

test("normalizes coordinates and assigns explicit track ownership", () => {
  const input = adapter();
  const frame = input.handle(event("pointerdown", { clientX: 60, clientY: 45 }));
  assert.equal(frame.x, 0.25);
  assert.equal(frame.y, 0.25);
  assert.deepEqual(frame.trackIds, [0]);
  assert.equal(frame.timestampMs, 0);
});

test("does not mistake the specification fallback pressure 0.5 for hardware", () => {
  const frame = adapter().handle(event("pointerdown", { pressure: 0.5 }));
  assert.equal(frame.pressure, null);
  assert.equal(frame.pressureSource, "unavailable");
});

test("accepts hardware pressure only through an explicit resolver", () => {
  const input = adapter({ pressureResolver: pointer => ({ pressure: pointer.pressure, pressureSource: "hardware" }) });
  const frame = input.handle(event("pointerdown", { pressure: 0.37 }));
  assert.equal(frame.pressure, 0.37);
  assert.equal(frame.pressureSource, "hardware");
});

test("emits slide with normalized velocity", () => {
  const input = adapter();
  input.handle(event("pointerdown"));
  const frame = input.handle(event("pointermove", { clientX: 130, timeStamp: 1100 }));
  assert.equal(frame.phase, "slide");
  assert.equal(frame.x, 0.6);
  assert.ok(Math.abs(frame.velocityX - 1) < 1e-12);
});

test("emits press when pressure changes without movement", () => {
  const input = adapter({ pressureResolver: pointer => ({ pressure: pointer.pressure, pressureSource: "estimated" }) });
  input.handle(event("pointerdown", { pressure: 0.2 }));
  const frame = input.handle(event("pointermove", { pressure: 0.4, timeStamp: 1010 }));
  assert.equal(frame.phase, "press");
  assert.equal(frame.pressure, 0.4);
});

test("suppresses pointermove when contact state did not change", () => {
  const input = adapter();
  input.handle(event("pointerdown"));
  assert.equal(input.handle(event("pointermove", { timeStamp: 1010 })), null);
});

test("maps pointerup to release and removes active ownership", () => {
  const input = adapter();
  input.handle(event("pointerdown"));
  assert.equal(input.handle(event("pointerup", { timeStamp: 1020 })).phase, "release");
  assert.equal(input.activeCount(), 0);
});

test("maps pointercancel to cancel", () => {
  const input = adapter();
  input.handle(event("pointerdown"));
  assert.equal(input.handle(event("pointercancel", { timeStamp: 1020 })).phase, "cancel");
  assert.equal(input.activeCount(), 0);
});

test("lostpointercapture cancels only an active pointer", () => {
  const input = adapter();
  input.handle(event("pointerdown"));
  assert.equal(input.handleLostPointerCapture(event("lostpointercapture", { timeStamp: 1020 })).phase, "cancel");
  assert.equal(input.handleLostPointerCapture(event("lostpointercapture", { timeStamp: 1030 })), null);
});

test("global interruption cancels all pointers deterministically", () => {
  const input = adapter();
  input.handle(event("pointerdown", { pointerId: 9 }));
  input.handle(event("pointerdown", { pointerId: 3, timeStamp: 1001 }));
  const frames = input.cancelAll(1010);
  assert.deepEqual(frames.map(frame => frame.pointerId), [3, 9]);
  assert.ok(frames.every(frame => frame.phase === "cancel"));
  assert.equal(input.activeCount(), 0);
});

test("recycled pointer IDs receive new gesture IDs", () => {
  const input = adapter();
  const first = input.handle(event("pointerdown"));
  input.handle(event("pointerup", { timeStamp: 1010 }));
  const second = input.handle(event("pointerdown", { timeStamp: 1020 }));
  assert.notEqual(first.gestureId, second.gestureId);
});

test("rejects out-of-surface coordinates instead of clamping", () => {
  const input = adapter();
  rejectsCode(() => input.handle(event("pointerdown", { clientX: 211 })), "POINTER_OUTSIDE_SURFACE");
});

test("preserves timestamp regression as an error", () => {
  const input = adapter();
  input.handle(event("pointerdown", { timeStamp: 1000 }));
  rejectsCode(() => input.handle(event("pointermove", { clientX: 120, timeStamp: 999 })), "TIMESTAMP_REGRESSION");
});

test("binding wires pointer capture, interruption cancel, and disposal", () => {
  const surface = new EventTargetStub();
  const scope = new EventTargetStub();
  const frames = [];
  const binding = bindPointerContactSurface({
    surface,
    scope,
    resolveTrackIds: () => [0],
    onFrame: frame => frames.push(frame),
  });
  surface.dispatch(event("pointerdown"));
  scope.dispatch({ type: "orientationchange", timeStamp: 1020 });
  assert.deepEqual(frames.map(frame => frame.phase), ["contact", "cancel"]);
  assert.deepEqual(surface.captures, [7]);
  binding.dispose();
  assert.equal(surface.count("pointerdown"), 0);
  assert.equal(scope.count("orientationchange"), 0);
});
