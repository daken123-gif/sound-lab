import test from "node:test";
import assert from "node:assert/strict";
import { BodyEngine } from "../body-engine.js";

const sampleRate = 48000;

function rms(signal, start = 0) {
  let sum = 0;
  for (let index = start; index < signal.length; index += 1) {
    sum += signal[index] * signal[index];
  }
  return Math.sqrt(sum / Math.max(1, signal.length - start));
}

test("silence stays silent", () => {
  const engine = new BodyEngine({ sampleRate });
  const output = engine.process(new Float32Array(4096));
  assert.equal(rms(output), 0);
});

test("an impulse excites a finite, bounded, decaying body", () => {
  const engine = new BodyEngine({ sampleRate });
  engine.setParameters({ size: 0.55, decay: 0.3, body: 0.7, dry: 0 });
  const input = new Float32Array(sampleRate * 2);
  input[0] = 1;
  const output = engine.process(input);

  for (const sample of output) assert.ok(Number.isFinite(sample));
  assert.ok(Math.max(...output) <= 1);
  assert.ok(Math.min(...output) >= -1);
  assert.ok(rms(output, sampleRate) < rms(output, 0) * 0.5);
});

test("breath-like noise produces wet output without pitch detection", () => {
  const engine = new BodyEngine({ sampleRate });
  engine.setParameters({ dry: 0, drive: 2 });
  const input = new Float32Array(12000);
  let state = 0x12345678;
  for (let index = 0; index < input.length; index += 1) {
    state ^= state << 13;
    state ^= state >>> 17;
    state ^= state << 5;
    input[index] = ((state >>> 0) / 0xffffffff - 0.5) * 0.12;
  }

  assert.ok(rms(engine.process(input)) > 0.00001);
});

test("macros are clamped and invalid samples cannot poison the state", () => {
  const engine = new BodyEngine({ sampleRate });
  engine.setParameters({ size: -10, decay: 4, body: 7, dry: -1, drive: 99 });
  assert.equal(engine.size, 0);
  assert.equal(engine.decay, 1);
  assert.equal(engine.body, 1);
  assert.equal(engine.dry, 0);
  assert.equal(engine.drive, 6);

  const output = engine.process(new Float32Array([NaN, Infinity, -Infinity, 0.5]));
  for (const sample of output) assert.ok(Number.isFinite(sample));
});
