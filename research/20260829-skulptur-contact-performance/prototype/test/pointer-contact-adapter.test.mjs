import assert from "node:assert/strict";
import test from "node:test";
import { PointerContactAdapter, PointerContactAdapterError, bindPointerContactSurface } from "../src/pointer-contact-adapter.js";

class Target {
  #listeners = new Map();
  captures = [];
  getBoundingClientRect() { return { left: 10, top: 20, width: 200, height: 100 }; }
  setPointerCapture(id) { this.captures.push(id); }
  addEventListener(type, fn) { this.#listeners.set(type, [...(this.#listeners.get(type) ?? []), fn]); }
  removeEventListener(type, fn) { this.#listeners.set(type, (this.#listeners.get(type) ?? []).filter(item => item !== fn)); }
  dispatch(event) { for (const fn of this.#listeners.get(event.type) ?? []) fn(event); }
  count(type) { return (this.#listeners.get(type) ?? []).length; }
}
const event = (type, overrides = {}) => ({ type, pointerId: 7, pointerType: "touch", clientX: 110,
  clientY: 70, pressure: 0.5, width: 20, height: 10, timeStamp: 1000, ...overrides });
const make = (overrides = {}) => new PointerContactAdapter({ surface: new Target(), resolveTrackIds: () => [0, 1, 2, 3], ...overrides });

test("normalizes surface coordinates and names all owned tracks", () => {
  const frame = make().handle(event("pointerdown", { clientX: 60, clientY: 45 }));
  assert.equal(frame.x, 0.25); assert.equal(frame.y, 0.25);
  assert.deepEqual(frame.trackIds, [0, 1, 2, 3]); assert.equal(frame.timestampMs, 0);
});
test("does not present fallback pressure 0.5 as hardware evidence", () => {
  const frame = make().handle(event("pointerdown"));
  assert.equal(frame.pressure, null); assert.equal(frame.pressureSource, "unavailable");
});
test("emits slide velocity and press only on contact-state changes", () => {
  const moving = make(); moving.handle(event("pointerdown"));
  const slide = moving.handle(event("pointermove", { clientX: 130, timeStamp: 1100 }));
  assert.equal(slide.phase, "slide"); assert.ok(Math.abs(slide.velocityX - 1) < 1e-12);
  const pressing = make({ pressureResolver: e => ({ pressure: e.pressure, pressureSource: "estimated" }) });
  pressing.handle(event("pointerdown", { pressure: 0.2 }));
  assert.equal(pressing.handle(event("pointermove", { pressure: 0.4, timeStamp: 1010 })).phase, "press");
  assert.equal(pressing.handle(event("pointermove", { pressure: 0.4, timeStamp: 1020 })), null);
});
test("distinguishes release, cancel, and recycled pointer gestures", () => {
  const input = make(); const first = input.handle(event("pointerdown"));
  assert.equal(input.handle(event("pointerup", { timeStamp: 1010 })).phase, "release");
  const second = input.handle(event("pointerdown", { timeStamp: 1020 }));
  assert.notEqual(first.gestureId, second.gestureId);
  assert.equal(input.handle(event("pointercancel", { timeStamp: 1030 })).phase, "cancel");
});
test("pointercancel uses the last valid contact point even outside the surface", () => {
  const input = make(); input.handle(event("pointerdown"));
  const cancelled = input.handle(event("pointercancel", { clientX: 400, clientY: 400, timeStamp: 1010 }));
  assert.equal(cancelled.phase, "cancel"); assert.equal(cancelled.x, 0.5); assert.equal(cancelled.y, 0.5);
  assert.equal(input.activeCount(), 0);
});
test("capture loss and global interruption cancel active ownership", () => {
  const input = make(); input.handle(event("pointerdown"));
  assert.equal(input.handleLostPointerCapture(event("lostpointercapture", { timeStamp: 1010 })).phase, "cancel");
  input.handle(event("pointerdown", { pointerId: 9, timeStamp: 1020 }));
  input.handle(event("pointerdown", { pointerId: 3, timeStamp: 1021 }));
  assert.deepEqual(input.cancelAll(1030).map(frame => frame.pointerId), [3, 9]);
});
test("rejects outside coordinates and timestamp regression", () => {
  const input = make();
  assert.throws(() => input.handle(event("pointerdown", { clientX: 211 })), e => e instanceof PointerContactAdapterError && e.code === "POINTER_OUTSIDE_SURFACE");
  input.handle(event("pointerdown", { timeStamp: 1000 }));
  assert.throws(() => input.handle(event("pointermove", { clientX: 120, timeStamp: 999 })), e => e.code === "TIMESTAMP_REGRESSION");
});
test("binding requests capture, emits interruption cancel, and disposes", () => {
  const surface = new Target(); const scope = new Target(); const frames = [];
  const binding = bindPointerContactSurface({ surface, scope, resolveTrackIds: () => [0], onFrame: frame => frames.push(frame) });
  surface.dispatch(event("pointerdown")); scope.dispatch({ type: "orientationchange", timeStamp: 1020 });
  assert.deepEqual(frames.map(frame => frame.phase), ["contact", "cancel"]); assert.deepEqual(surface.captures, [7]);
  binding.dispose(); assert.equal(surface.count("pointerdown"), 0); assert.equal(scope.count("orientationchange"), 0);
});
test("visibility loss cancels active contact ownership", () => {
  const surface = new Target(); const scope = new Target(); const frames = [];
  const binding = bindPointerContactSurface({ surface, scope, resolveTrackIds: () => [0], onFrame: frame => frames.push(frame) });
  surface.dispatch(event("pointerdown")); scope.dispatch({ type: "visibilitychange", timeStamp: 1010 });
  assert.deepEqual(frames.map(frame => frame.phase), ["contact", "cancel"]);
  assert.equal(binding.adapter.activeCount(), 0);
  binding.dispose(); assert.equal(scope.count("visibilitychange"), 0);
});
test("binding converts an outside pointerup failure to cancel without leaking ownership", () => {
  const surface = new Target(); const scope = new Target(); const frames = []; const errors = [];
  const binding = bindPointerContactSurface({ surface, scope, resolveTrackIds: () => [0],
    onFrame: frame => frames.push(frame), onError: error => errors.push(error) });
  surface.dispatch(event("pointerdown"));
  surface.dispatch(event("pointerup", { clientX: 400, timeStamp: 1010 }));
  assert.deepEqual(frames.map(frame => frame.phase), ["contact", "cancel"]);
  assert.equal(errors[0].code, "POINTER_OUTSIDE_SURFACE"); assert.equal(binding.adapter.activeCount(), 0);
  binding.dispose();
});
