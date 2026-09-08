import assert from "node:assert/strict";
import test from "node:test";
import { skulpturCommandFromContactFrame } from "../src/skulptur-contact-bridge.js";

const frame = overrides => ({ schemaVersion: "sound-lab.contact-gesture/v0.1", gestureId: "g", pointerId: 2,
  phase: "contact", trackIds: [0, 1, 2, 3], x: 0.35, y: 0.2, contactArea: null,
  pressure: null, pressureSource: "unavailable", velocityX: 0, velocityY: 0, timestampMs: 0, ...overrides });

test("maps normalized contact to Skulptur band and vertical position", () => {
  const command = skulpturCommandFromContactFrame(frame());
  assert.equal(command.type, "begin"); assert.equal(command.band, 3); assert.equal(command.position, 0.8);
  assert.deepEqual(command.trackIds, [0, 1, 2, 3]);
});
test("maps the right edge to band 9 without clamping invalid input", () => {
  assert.equal(skulpturCommandFromContactFrame(frame({ phase: "slide", x: 1 })).band, 9);
  assert.throws(() => skulpturCommandFromContactFrame(frame({ x: 1.01 })));
});
test("release throws and cancel stops without throw", () => {
  assert.deepEqual(skulpturCommandFromContactFrame(frame({ phase: "release" })).throwMotion, true);
  assert.deepEqual(skulpturCommandFromContactFrame(frame({ phase: "cancel" })).throwMotion, false);
});
