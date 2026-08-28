import assert from "node:assert/strict";
import { createRequire } from "node:module";
import test from "node:test";

const require = createRequire(import.meta.url);
const { AbbeyInputEngine, MODES, modeParameters } = require("../prototype/abbey-input-engine.js");

const sampleRate = 48000;

function sine(frequency, amplitude, seconds = 1) {
  const result = new Float32Array(Math.round(sampleRate * seconds));
  for (let i = 0; i < result.length; i += 1) {
    result[i] = amplitude * Math.sin((2 * Math.PI * frequency * i) / sampleRate);
  }
  return result;
}

function rms(values, skip = 4096) {
  let sum = 0;
  for (let i = skip; i < values.length; i += 1) sum += values[i] ** 2;
  return Math.sqrt(sum / Math.max(1, values.length - skip));
}

function peak(values) {
  let result = 0;
  for (const value of values) result = Math.max(result, Math.abs(value));
  return result;
}

test("CLEAN is sample-identical", () => {
  const engine = new AbbeyInputEngine(sampleRate);
  engine.configure(MODES.CLEAN, 0.7);
  const input = sine(997, 0.73, 0.2);
  const output = engine.processBlock(input);
  assert.deepEqual(output, input);
});

test("BODY exposes the REDD structure without claiming measured hardware values", () => {
  const p = modeParameters(MODES.BODY, 1);
  assert.equal(p.family, "REDD");
  assert.equal(p.lowShelfHz, 100);
  assert.equal(p.presenceHz, 5000);
  assert.equal(p.highShelfHz, 10000);
  assert.equal(p.preLowGuardDb, -3);
});

test("OPEN exposes TG fixed EQ and feedback-compression boundary", () => {
  const p = modeParameters(MODES.OPEN, 1);
  assert.equal(p.family, "TG12345");
  assert.equal(p.lowShelfHz, 50);
  assert.equal(p.presenceHz, 5000);
  assert.equal(p.highShelfHz, 10000);
  assert.equal(p.thresholdDbfs, -19.3);
  assert.equal(p.ratio, 2);
  assert.equal(p.attackMs, 1);
});

test("BODY is level-dependent: strong input receives less proportional output", () => {
  const quietEngine = new AbbeyInputEngine(sampleRate);
  quietEngine.configure(MODES.BODY, 0.8);
  const loudEngine = new AbbeyInputEngine(sampleRate);
  loudEngine.configure(MODES.BODY, 0.8);
  const quietRatio = rms(quietEngine.processBlock(sine(1000, 0.05))) / rms(sine(1000, 0.05));
  const loudRatio = rms(loudEngine.processBlock(sine(1000, 0.8))) / rms(sine(1000, 0.8));
  assert.ok(loudRatio < quietRatio * 0.85, `${loudRatio} should be below ${quietRatio}`);
});

test("OPEN feedback stage compresses above the -19.3 dBFS region", () => {
  const quietEngine = new AbbeyInputEngine(sampleRate);
  quietEngine.configure(MODES.OPEN, 0.5);
  const loudEngine = new AbbeyInputEngine(sampleRate);
  loudEngine.configure(MODES.OPEN, 0.5);
  const quietInput = sine(1000, 0.05, 2);
  const loudInput = sine(1000, 0.8, 2);
  const quietRatio = rms(quietEngine.processBlock(quietInput)) / rms(quietInput);
  const loudRatio = rms(loudEngine.processBlock(loudInput)) / rms(loudInput);
  assert.ok(loudRatio < quietRatio * 0.8, `${loudRatio} should be below ${quietRatio}`);
});

test("both color paths stay finite and bounded under accidental over-range input", () => {
  for (const mode of [MODES.BODY, MODES.OPEN]) {
    const engine = new AbbeyInputEngine(sampleRate);
    engine.configure(mode, 1);
    const input = Float32Array.from({ length: sampleRate }, (_, i) => (i % 2 ? 4 : -4));
    const output = engine.processBlock(input);
    assert.ok(output.every(Number.isFinite));
    assert.ok(peak(output) < 1.5, `${mode} peak was ${peak(output)}`);
  }
});

test("mode changes reset filter memory and preserve explicit family separation", () => {
  const engine = new AbbeyInputEngine(sampleRate);
  engine.configure(MODES.BODY, 0.5);
  engine.processBlock(sine(100, 0.8, 0.1));
  engine.configure(MODES.OPEN, 0.5);
  const output = engine.processBlock(new Float32Array(2048));
  assert.equal(peak(output), 0);
  assert.equal(engine.parameters.family, "TG12345");
});
