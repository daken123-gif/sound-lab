import assert from "node:assert/strict";
import test from "node:test";
import { SpectralControlEngine } from "../src/spectral-control-engine.js";

function advance(engine, seconds, step = 1 / 120) {
  let values;
  for (let elapsed = 0; elapsed < seconds; elapsed += step) {
    values = engine.update(step);
  }
  return values;
}

test("control engine rests at an open baseline", () => {
  const engine = new SpectralControlEngine();
  assert.deepEqual([...engine.update(1 / 120)], new Array(10).fill(1));
});

test("two pointers independently control two bands", () => {
  const engine = new SpectralControlEngine();
  engine.beginTouch(11, 2, 0.15, 0);
  engine.beginTouch(12, 7, 0.72, 0);
  const values = engine.update(1 / 120);
  assert.equal(values[2], 0.15);
  assert.equal(values[7], 0.72);
  assert.equal(values[4], 1);
});

test("the newest pointer wins only on the shared band", () => {
  const engine = new SpectralControlEngine();
  engine.beginTouch(1, 4, 0.2, 0);
  engine.beginTouch(2, 4, 0.8, 0.01);
  assert.equal(engine.update(1 / 120)[4], 0.8);
  engine.endTouch(2, { throwMotion: false });
  assert.equal(engine.update(1 / 120)[4], 0.2);
});

test("elastic release returns to the baseline", () => {
  const engine = new SpectralControlEngine({ elasticSeconds: 0.04 });
  engine.beginTouch(1, 3, 0, 0);
  engine.update(1 / 120);
  engine.endTouch(1, { throwMotion: false });
  const values = advance(engine, 0.5);
  assert.ok(values[3] > 0.999);
});

test("throw motion survives release, reflects, then decays", () => {
  const engine = new SpectralControlEngine({ throwFriction: 4 });
  engine.beginTouch(1, 5, 0.2, 0);
  engine.moveTouch(1, 5, 0.8, 0.1);
  engine.endTouch(1, { throwMotion: true });
  const early = engine.update(1 / 120)[5];
  const later = advance(engine, 2)[5];
  assert.notEqual(early, 0.8);
  assert.ok(later >= 0 && later <= 1);
  assert.equal(engine.throws[5], null);
});

test("flow moves untouched bands while touch has priority", () => {
  const engine = new SpectralControlEngine({ elasticSeconds: 0.01 });
  engine.setFlow({ enabled: true, depth: 0.8, periodSeconds: 1, bandPhase: 0.1 });
  const before = advance(engine, 0.2);
  assert.ok(new Set([...before].map(value => value.toFixed(4))).size > 2);

  engine.beginTouch(9, 6, 0.33, 0.2);
  const during = engine.update(1 / 120);
  assert.equal(during[6], 0.33);
  assert.notEqual(during[5], 0.33);
});

test("recorded performance overrides throw and flow, while a finger overrides recording", () => {
  const engine = new SpectralControlEngine({ elasticSeconds: 0 });
  engine.setFlow({ enabled: true, depth: 0.8 });
  engine.beginTouch(1, 4, 0.2, 0);
  engine.moveTouch(1, 4, 0.8, 0.1);
  engine.endTouch(1, { throwMotion: true });
  engine.setRecordedValues(Array.from({ length: 10 }, (_, band) => band === 4 ? 0.55 : null));
  assert.equal(engine.update(1 / 120)[4], 0.55);

  engine.beginTouch(2, 4, 0.15, 0.2);
  assert.equal(engine.update(1 / 120)[4], 0.15);
  engine.endTouch(2, { throwMotion: false });
  assert.equal(engine.update(1 / 120)[4], 0.55);
});

test("recorded performance keeps the spectral path active", () => {
  const engine = new SpectralControlEngine();
  assert.equal(engine.isActive, false);
  engine.setRecordedValues([0.5, null, null, null, null, null, null, null, null, null]);
  assert.equal(engine.isActive, true);
});

test("control source reports the same finger-recording-throw-flow priority as rendering", () => {
  const engine = new SpectralControlEngine();
  assert.equal(engine.sourceAt(2), "idle");
  engine.setFlow({ enabled: true });
  assert.equal(engine.sourceAt(2), "flow");
  engine.throws[2] = { value: 0.4, velocity: 1 };
  assert.equal(engine.sourceAt(2), "throw");
  engine.setRecordedValues(Array.from({ length: 10 }, (_, band) => band === 2 ? 0.3 : null));
  assert.equal(engine.sourceAt(2), "recorded");
  engine.beginTouch(9, 2, 0.2, 0);
  assert.equal(engine.sourceAt(2), "touch");
});
