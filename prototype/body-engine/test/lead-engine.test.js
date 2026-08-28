import test from "node:test";
import assert from "node:assert/strict";
import { LeadEngine } from "../lead-engine.js";

const sampleRate = 48000;

function rms(signal) {
  let sum = 0;
  for (const sample of signal) sum += sample * sample;
  return Math.sqrt(sum / Math.max(1, signal.length));
}

function sine(frequency, amplitude, length = sampleRate / 2) {
  const signal = new Float32Array(length);
  for (let index = 0; index < length; index += 1) {
    signal[index] = amplitude * Math.sin(2 * Math.PI * frequency * index / sampleRate);
  }
  return signal;
}

test("LEAD silence stays silent", () => {
  const engine = new LeadEngine({ sampleRate });
  assert.equal(rms(engine.process(new Float32Array(4096))), 0);
});

test("LEAD keeps voiced input finite and audibly changes the waveform", () => {
  const engine = new LeadEngine({ sampleRate });
  const input = sine(180, 0.32);
  const output = engine.process(input);
  let difference = 0;

  for (let index = 0; index < output.length; index += 1) {
    assert.ok(Number.isFinite(output[index]));
    assert.ok(output[index] >= -1 && output[index] <= 1);
    difference += Math.abs(output[index] - input[index]);
  }
  assert.ok(difference / output.length > 0.02);
  assert.ok(rms(output) > 0.005);
});

test("LEAD responds to breath-like noise without pitch detection", () => {
  const engine = new LeadEngine({ sampleRate });
  const input = new Float32Array(16000);
  let state = 0x31415926;
  for (let index = 0; index < input.length; index += 1) {
    state ^= state << 13;
    state ^= state >>> 17;
    state ^= state << 5;
    input[index] = ((state >>> 0) / 0xffffffff - 0.5) * 0.16;
  }

  const output = engine.process(input);
  const observed = engine.diagnostics();
  assert.ok(rms(output) > 0.0001);
  assert.ok(observed.brightness > 0.05);
  assert.ok(observed.cutoffHz > 55);
});

test("brighter input raises the dynamic cutoff", () => {
  const lowEngine = new LeadEngine({ sampleRate });
  const highEngine = new LeadEngine({ sampleRate });
  lowEngine.process(sine(120, 0.18));
  highEngine.process(sine(4200, 0.18));

  const low = lowEngine.diagnostics();
  const high = highEngine.diagnostics();
  assert.ok(high.brightness > low.brightness);
  assert.ok(high.cutoffHz > low.cutoffHz);
});

test("the inverse safety region lowers resonance at high input level", () => {
  const mediumEngine = new LeadEngine({ sampleRate });
  const loudEngine = new LeadEngine({ sampleRate });
  mediumEngine.process(sine(220, 0.11, sampleRate));
  loudEngine.process(sine(220, 1.2, sampleRate));

  const medium = mediumEngine.diagnostics();
  const loud = loudEngine.diagnostics();
  assert.ok(loud.fastEnvelope > medium.fastEnvelope);
  assert.ok(loud.resonanceQ < medium.resonanceQ);
});

test("LEAD clamps macros and rejects state-poisoning samples", () => {
  const engine = new LeadEngine({ sampleRate });
  engine.setParameters({ tone: -8, motion: 4, space: 9, dry: -2, drive: 20 });
  assert.equal(engine.tone, 0);
  assert.equal(engine.motion, 1);
  assert.equal(engine.space, 1);
  assert.equal(engine.dry, 0);
  assert.equal(engine.drive, 4);

  const output = engine.process(new Float32Array([NaN, Infinity, -Infinity, 0.5]));
  for (const sample of output) assert.ok(Number.isFinite(sample));
  for (const value of Object.values(engine.diagnostics())) {
    assert.ok(Number.isFinite(value));
  }
});

test("LEAD requires explicit Float32Array input", () => {
  const engine = new LeadEngine({ sampleRate });
  assert.throws(() => engine.process([0, 1]), /Float32Array/);
});
