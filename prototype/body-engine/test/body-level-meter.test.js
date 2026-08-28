import test from "node:test";
import assert from "node:assert/strict";
import { BodyLevelMeter } from "../body-level-meter.js";

test("level meter reports input and BODY output independently", () => {
  const meter = new BodyLevelMeter(4);
  const report = meter.add(
    new Float32Array([0.5, -0.5, 0.5, -0.5]),
    new Float32Array([0.25, -0.25, 0.25, -0.25])
  );
  assert.equal(report.type, "levels");
  assert.equal(report.frames, 4);
  assert.equal(report.inputRms, 0.5);
  assert.equal(report.inputPeak, 0.5);
  assert.equal(report.outputRms, 0.25);
  assert.equal(report.outputPeak, 0.25);
});

test("level meter waits for its reporting interval and resets", () => {
  const meter = new BodyLevelMeter(4);
  assert.equal(meter.add(new Float32Array(2).fill(1), new Float32Array(2)), null);
  assert.ok(meter.add(new Float32Array(2).fill(1), new Float32Array(2)));
  assert.equal(meter.add(new Float32Array(2), new Float32Array(2)), null);
});

test("level meter rejects unequal buffers and invalid intervals", () => {
  assert.throws(() => new BodyLevelMeter(0), /positive integer/);
  const meter = new BodyLevelMeter(1);
  assert.throws(() => meter.add(new Float32Array(2), new Float32Array(1)), /equal length/);
});
