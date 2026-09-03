import test from "node:test";
import assert from "node:assert/strict";

import { ResolvedTargetAdapter } from "./resolved-target-adapter.mjs";

const surface = {
  nodes: [
    { id: "node-a", x: 0.2, y: 0.5, visible: true },
    { id: "node-b", x: 0.8, y: 0.5, visible: true },
  ],
  edges: [{ id: "edge-a-b", from: "node-a", to: "node-b", visible: true }],
};

const frame = (pointerId, phase, x, y, timestampMs = 0) => ({
  schemaVersion: "sound-lab.contact-gesture/v0.1",
  gestureId: `gesture-${pointerId}`,
  pointerId,
  phase,
  trackIds: [0],
  x,
  y,
  contactArea: null,
  pressure: null,
  pressureSource: "unavailable",
  velocityX: 0,
  velocityY: 0,
  timestampMs,
});

test("元のContactGestureFrameを変更せずenvelopeへ包む", () => {
  const adapter = new ResolvedTargetAdapter();
  const input = frame(1, "contact", 0.5, 0.5);
  const before = structuredClone(input);
  const resolved = adapter.resolve(input, surface);
  assert.deepEqual(input, before);
  assert.deepEqual(resolved.source, before);
  assert.equal("targetKind" in input, false);
  assert.equal(resolved.schemaVersion, "sound-lab.resolved-contact/v0.1");
});

test("nodeから離れたedge中央をedgeとして一度だけ解決する", () => {
  const adapter = new ResolvedTargetAdapter();
  const resolved = adapter.resolve(frame(1, "contact", 0.5, 0.5), surface);
  assert.deepEqual(resolved.target, { kind: "edge", id: "edge-a-b" });
  assert.equal(resolved.resolutionMethod, "single-hit-test");
});

test("接触後に指がnode上へ移動してもedge claimを再判定しない", () => {
  const adapter = new ResolvedTargetAdapter();
  const contact = adapter.resolve(frame(1, "contact", 0.5, 0.5), surface);
  const slide = adapter.resolve(frame(1, "slide", 0.2, 0.5, 100), surface);
  assert.equal(slide.resolutionId, contact.resolutionId);
  assert.deepEqual(slide.target, contact.target);
  assert.equal(slide.resolutionMethod, "bound-claim");
});

test("nodeとedgeのhit領域が重なる場合は可視nodeを優先する", () => {
  const adapter = new ResolvedTargetAdapter();
  const resolved = adapter.resolve(frame(1, "contact", 0.2, 0.5), surface);
  assert.deepEqual(resolved.target, { kind: "node", id: "node-a" });
});

test("音響と描画へ同じimmutable envelopeをfan-outできる", () => {
  const adapter = new ResolvedTargetAdapter();
  const resolved = adapter.resolve(frame(1, "contact", 0.5, 0.5), surface);
  const audioInput = resolved;
  const visualInput = resolved;
  assert.strictEqual(audioInput, visualInput);
  assert.equal(Object.isFrozen(resolved), true);
  assert.equal(Object.isFrozen(resolved.target), true);
  assert.throws(() => { resolved.target.id = "node-a"; }, TypeError);
});

test("release後はbindingを破棄し、pointerId再利用時に新規解決する", () => {
  const adapter = new ResolvedTargetAdapter();
  const first = adapter.resolve(frame(1, "contact", 0.5, 0.5), surface);
  adapter.resolve(frame(1, "release", 0.5, 0.5, 100), surface);
  const second = adapter.resolve(frame(1, "contact", 0.95, 0.9, 200), surface);
  assert.notEqual(second.resolutionId, first.resolutionId);
  assert.deepEqual(second.target, { kind: "empty", id: null });
});

test("5接触を互いに独立したclaimとして保持する", () => {
  const adapter = new ResolvedTargetAdapter();
  const outputs = Array.from({ length: 5 }, (_, pointerId) =>
    adapter.resolve(frame(pointerId, "contact", 0.05 + pointerId * 0.22, 0.9), surface),
  );
  assert.equal(new Set(outputs.map((output) => output.resolutionId)).size, 5);
  assert.equal(adapter.bindings.size, 5);
});

