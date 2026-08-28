import test from "node:test";
import assert from "node:assert/strict";
import { decodePcmWav, encodeMonoPcm16 } from "../wav-io.js";

test("16-bit mono WAV round-trips within quantization error", () => {
  const source = new Float32Array([-1, -0.5, 0, 0.25, 0.999]);
  const decoded = decodePcmWav(encodeMonoPcm16(source, 48000));
  assert.equal(decoded.sampleRate, 48000);
  assert.equal(decoded.sourceChannels, 1);
  assert.equal(decoded.samples.length, source.length);
  // Encoding uses the asymmetric signed PCM endpoints (-32768..32767),
  // while decoding divides by 32768. Allow two least-significant steps.
  for (let index = 0; index < source.length; index += 1) {
    assert.ok(Math.abs(decoded.samples[index] - source[index]) <= 2 / 32768);
  }
});

test("non-finite samples become silence during encoding", () => {
  const decoded = decodePcmWav(encodeMonoPcm16(
    new Float32Array([NaN, Infinity, -Infinity]), 44100
  ));
  assert.deepEqual([...decoded.samples], [0, 0, 0]);
});

test("malformed and unsupported WAV input is rejected", () => {
  assert.throws(() => decodePcmWav(Buffer.from("not wav")), /RIFF\/WAVE/);
  const wav = encodeMonoPcm16(new Float32Array([0]), 48000);
  wav.writeUInt16LE(3, 20);
  assert.throws(() => decodePcmWav(wav), /16-bit integer PCM/);
});
