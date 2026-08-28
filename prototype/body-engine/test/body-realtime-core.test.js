import test from "node:test";
import assert from "node:assert/strict";
import { BodyRealtimeCore } from "../body-realtime-core.js";

function rms(samples) {
  let sum = 0;
  for (const sample of samples) sum += sample * sample;
  return Math.sqrt(sum / Math.max(1, samples.length));
}

test("a closed gate keeps a reset engine silent", () => {
  const core = new BodyRealtimeCore(48000);
  const input = new Float32Array(257).fill(1);
  const output = new Float32Array(257);
  core.processBlock(input, output, { gate: new Float32Array([0]) });
  assert.equal(rms(output), 0);
});

test("arbitrary render block lengths remain finite and bounded", () => {
  const core = new BodyRealtimeCore(48000);
  for (const length of [1, 64, 128, 257, 1024]) {
    const input = new Float32Array(length);
    for (let index = 0; index < length; index += 1) {
      input[index] = Math.sin(index * 0.17) * 0.4;
    }
    const output = new Float32Array(length);
    core.processBlock(input, output, { gate: new Float32Array([1]) });
    for (const sample of output) {
      assert.ok(Number.isFinite(sample));
      assert.ok(sample >= -1 && sample <= 1);
    }
  }
});

test("closing the gate stops excitation but preserves the resonator tail", () => {
  const core = new BodyRealtimeCore(48000);
  const strike = new Float32Array(512);
  strike.fill(0.7, 0, 64);
  const first = new Float32Array(512);
  core.processBlock(strike, first, { gate: new Float32Array([1]), dry: new Float32Array([0]) });

  const tail = new Float32Array(512);
  core.processBlock(new Float32Array(512), tail, {
    gate: new Float32Array([0]), dry: new Float32Array([0])
  });
  assert.ok(rms(first) > 0);
  assert.ok(rms(tail) > 0);
  assert.ok(rms(tail) < rms(first));
});

test("a-rate gate arrays are accepted without assuming 128 frames", () => {
  const core = new BodyRealtimeCore(44100);
  const input = new Float32Array(193).fill(0.25);
  const gate = new Float32Array(193);
  gate.fill(1, 71);
  const output = new Float32Array(193);
  core.processBlock(input, output, { gate });
  assert.equal(rms(output.subarray(0, 71)), 0);
  assert.ok(rms(output.subarray(71)) > 0);
});

test("mismatched block lengths are rejected", () => {
  const core = new BodyRealtimeCore(48000);
  assert.throws(() => core.processBlock(
    new Float32Array(64), new Float32Array(63)
  ), /equal length/);
});
