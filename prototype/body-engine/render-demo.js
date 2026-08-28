import { mkdirSync, writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";
import { BodyEngine } from "./body-engine.js";

const sampleRate = 48000;
const here = dirname(fileURLToPath(import.meta.url));
const outputDirectory = join(here, "demo-output");

function clamp(value, min, max) {
  return Math.min(max, Math.max(min, value));
}

class Formant {
  constructor(frequency, q = 10) {
    const omega = 2 * Math.PI * frequency / sampleRate;
    const alpha = Math.sin(omega) / (2 * q);
    const a0 = 1 + alpha;
    this.b0 = alpha / a0;
    this.b2 = -alpha / a0;
    this.a1 = -2 * Math.cos(omega) / a0;
    this.a2 = (1 - alpha) / a0;
    this.x1 = 0;
    this.x2 = 0;
    this.y1 = 0;
    this.y2 = 0;
  }

  process(input) {
    const output = this.b0 * input + this.b2 * this.x2
      - this.a1 * this.y1 - this.a2 * this.y2;
    this.x2 = this.x1;
    this.x1 = input;
    this.y2 = this.y1;
    this.y1 = output;
    return output;
  }
}

function seededNoise(seed = 0x5eed1234) {
  let state = seed >>> 0;
  return () => {
    state ^= state << 13;
    state ^= state >>> 17;
    state ^= state << 5;
    return (state >>> 0) / 0xffffffff * 2 - 1;
  };
}

function envelope(time, duration) {
  const attack = clamp(time / 0.045, 0, 1);
  const release = clamp((duration - time) / 0.11, 0, 1);
  return Math.sin(Math.PI * 0.5 * attack) * Math.sin(Math.PI * 0.5 * release);
}

function synthesizeVowel(formantFrequencies, duration, fundamental, noise) {
  const length = Math.round(duration * sampleRate);
  const output = new Float32Array(length);
  const formants = formantFrequencies.map((frequency, index) =>
    new Formant(frequency, 8 + index * 3)
  );

  for (let index = 0; index < length; index += 1) {
    const time = index / sampleRate;
    const phase = (time * fundamental) % 1;
    const glottal = 2 * phase - 1;
    const breath = noise() * 0.12;
    const onset = index < sampleRate * 0.018
      ? noise() * (1 - index / (sampleRate * 0.018)) * 0.9
      : 0;
    const excitation = (glottal * 0.72 + breath + onset) * envelope(time, duration);

    let shaped = 0;
    for (let formantIndex = 0; formantIndex < formants.length; formantIndex += 1) {
      shaped += formants[formantIndex].process(excitation) / (1 + formantIndex * 0.35);
    }
    output[index] = shaped;
  }
  return output;
}

function silence(seconds) {
  return new Float32Array(Math.round(seconds * sampleRate));
}

function concatenate(parts) {
  const total = parts.reduce((sum, part) => sum + part.length, 0);
  const output = new Float32Array(total);
  let offset = 0;
  for (const part of parts) {
    output.set(part, offset);
    offset += part.length;
  }
  return output;
}

function normalize(input, peak = 0.86) {
  let maximum = 0;
  for (const sample of input) maximum = Math.max(maximum, Math.abs(sample));
  const gain = maximum > 0 ? peak / maximum : 1;
  return Float32Array.from(input, sample => sample * gain);
}

function writeMonoWav(path, samples) {
  const dataLength = samples.length * 2;
  const buffer = Buffer.alloc(44 + dataLength);
  buffer.write("RIFF", 0);
  buffer.writeUInt32LE(36 + dataLength, 4);
  buffer.write("WAVE", 8);
  buffer.write("fmt ", 12);
  buffer.writeUInt32LE(16, 16);
  buffer.writeUInt16LE(1, 20);
  buffer.writeUInt16LE(1, 22);
  buffer.writeUInt32LE(sampleRate, 24);
  buffer.writeUInt32LE(sampleRate * 2, 28);
  buffer.writeUInt16LE(2, 32);
  buffer.writeUInt16LE(16, 34);
  buffer.write("data", 36);
  buffer.writeUInt32LE(dataLength, 40);
  for (let index = 0; index < samples.length; index += 1) {
    const sample = clamp(samples[index], -1, 1);
    buffer.writeInt16LE(Math.round(sample * (sample < 0 ? 32768 : 32767)), 44 + index * 2);
  }
  writeFileSync(path, buffer);
}

function measure(samples) {
  let sumSquares = 0;
  let peak = 0;
  for (const sample of samples) {
    sumSquares += sample * sample;
    peak = Math.max(peak, Math.abs(sample));
  }
  return {
    seconds: samples.length / sampleRate,
    rms: Math.sqrt(sumSquares / samples.length),
    peak
  };
}

const noise = seededNoise();
const vowelFormants = [
  [800, 1150, 2900],
  [500, 1700, 2500],
  [300, 2200, 3000],
  [500, 900, 2600],
  [350, 700, 2400]
];

const phrase = normalize(concatenate(vowelFormants.flatMap((formants, index) => [
  synthesizeVowel(formants, 0.68, 112 + index * 3, noise),
  silence(0.09)
])), 0.72);

const lightEngine = new BodyEngine({ sampleRate });
lightEngine.setParameters({ size: 0.42, decay: 0.26, body: 0.38, dry: 0.14, drive: 1.7 });
const light = normalize(lightEngine.process(phrase), 0.82);

const deepEngine = new BodyEngine({ sampleRate });
deepEngine.setParameters({ size: 0.78, decay: 0.7, body: 0.82, dry: 0.04, drive: 2.3 });
const deep = normalize(deepEngine.process(phrase), 0.82);

const gap = silence(0.55);
const comparison = concatenate([phrase, gap, light, gap, deep]);

mkdirSync(outputDirectory, { recursive: true });
writeMonoWav(join(outputDirectory, "body-input-synthetic.wav"), phrase);
writeMonoWav(join(outputDirectory, "body-light.wav"), light);
writeMonoWav(join(outputDirectory, "body-deep.wav"), deep);
writeMonoWav(join(outputDirectory, "body-comparison.wav"), comparison);

const report = {
  source: "synthetic vowel, consonant-like onset, and breath test signal",
  order: ["input", "light", "deep"],
  sampleRate,
  input: measure(phrase),
  light: measure(light),
  deep: measure(deep),
  comparison: measure(comparison)
};
writeFileSync(join(outputDirectory, "metrics.json"), `${JSON.stringify(report, null, 2)}\n`);
console.log(JSON.stringify(report, null, 2));
