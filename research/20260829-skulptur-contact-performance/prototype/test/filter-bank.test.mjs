import assert from "node:assert/strict";
import test from "node:test";
import { SkulpturFilterBank } from "../src/filter-bank-core.js";

function signal(length, sampleRate = 48000) {
  const data = new Float32Array(length);
  for (let i = 0; i < length; i += 1) {
    const t = i / sampleRate;
    data[i] =
      0.4 * Math.sin(2 * Math.PI * 110 * t) +
      0.25 * Math.sin(2 * Math.PI * 1000 * t) +
      0.2 * Math.sin(2 * Math.PI * 7000 * t);
  }
  return data;
}

function rms(values) {
  return Math.sqrt(values.reduce((sum, value) => sum + value * value, 0) / values.length);
}

test("inactive engine is bit-transparent", () => {
  const engine = new SkulpturFilterBank({ channels: 1 });
  const input = signal(4096);
  const [output] = engine.process([input]);
  assert.deepEqual(output, input);
});

test("both supported orders remain finite under an impulse", () => {
  for (const order of [4, 8]) {
    const engine = new SkulpturFilterBank({ channels: 1, order });
    const impulse = new Float32Array(48000);
    impulse[0] = 1;
    engine.setActive(true);
    const [output] = engine.process([impulse]);
    assert.ok(output.every(Number.isFinite));
    assert.ok(Math.max(...output.map(Math.abs)) < 8);
  }
});

test("muting a matching band changes the rendered energy", () => {
  const warmup = signal(24000);
  const probe = signal(24000);
  const engine = new SkulpturFilterBank({ channels: 1, order: 4 });
  engine.setActive(true);
  engine.process([warmup]);
  const [full] = engine.process([probe]);

  engine.setBand(5, 0);
  engine.process([new Float32Array(12000)]);
  const [cut] = engine.process([probe]);
  assert.ok(Math.abs(rms(full) - rms(cut)) > 0.005);
});

test("fourth and eighth order banks are measurably different", () => {
  const input = signal(48000);
  const results = [];
  for (const order of [4, 8]) {
    const engine = new SkulpturFilterBank({ channels: 1, order });
    engine.setActive(true);
    engine.setBands([1, 0.1, 1, 0.2, 1, 0.3, 1, 0.4, 1, 0.5]);
    results.push(engine.process([input])[0]);
  }
  let difference = 0;
  for (let i = 0; i < input.length; i += 1) {
    difference += Math.abs(results[0][i] - results[1][i]);
  }
  assert.ok(difference / input.length > 0.001);
});

test("release returns close to dry without a discontinuity", () => {
  const engine = new SkulpturFilterBank({ channels: 1, order: 8 });
  engine.setActive(true);
  engine.setBand(4, 0);
  engine.process([signal(24000)]);
  engine.setActive(false);
  const input = signal(48000);
  const [output] = engine.process([input]);
  const tailStart = output.length - 1024;
  let tailError = 0;
  for (let i = tailStart; i < output.length; i += 1) {
    tailError = Math.max(tailError, Math.abs(output[i] - input[i]));
  }
  assert.ok(tailError < 1e-4);
});

test("band feedback extends a filtered tail", () => {
  const makeEngine = feedback => {
    const engine = new SkulpturFilterBank({
      channels: 1,
      order: 4,
      wetAttackSeconds: 0,
      gainSmoothingSeconds: 0,
      feedbackSmoothingSeconds: 0
    });
    engine.setActive(true);
    engine.setBands([0, 0, 0, 0, 0, 1, 0, 0, 0, 0]);
    engine.setFeedback(5, feedback);
    return engine;
  };
  const impulse = new Float32Array(48000);
  impulse[0] = 0.5;
  const plain = makeEngine(0).process([impulse])[0];
  const resonant = makeEngine(1).process([impulse])[0];
  const tail = values => rms(values.slice(-4096));
  assert.ok(tail(resonant) > tail(plain) * 10);
});

test("maximum feedback remains finite and bounded", () => {
  const engine = new SkulpturFilterBank({
    channels: 1,
    order: 8,
    wetAttackSeconds: 0,
    feedbackSmoothingSeconds: 0
  });
  engine.setActive(true);
  engine.setFeedbackBands(new Array(10).fill(1));
  const impulse = new Float32Array(96000);
  impulse[0] = 1;
  const [output] = engine.process([impulse]);
  assert.ok(output.every(Number.isFinite));
  assert.ok(Math.max(...output.map(Math.abs)) < 8);
});

test("clearing feedback returns the activity flag to idle after smoothing", () => {
  const engine = new SkulpturFilterBank({ channels: 1, feedbackSmoothingSeconds: 0 });
  engine.setFeedback(2, 0.8);
  assert.equal(engine.hasFeedback, true);
  engine.setFeedback(2, 0);
  engine.process([new Float32Array(1)]);
  assert.equal(engine.hasFeedback, false);
});
