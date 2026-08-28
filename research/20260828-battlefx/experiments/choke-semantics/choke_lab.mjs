import { createHash } from "node:crypto";
import { mkdirSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const sampleRate = 48_000;
const durationSeconds = 3.0;
const frames = Math.round(sampleRate * durationSeconds);
const delayFrames = Math.round(sampleRate * 0.1);
const feedback = 0.83;
const chokeStart = 0.957;
const chokeEnd = 1.557;
const probeTime = 1.17;
const rampFrames = Math.round(sampleRate * 0.005);
const modes = ["output-gate", "feedback-cut", "buffer-clear", "input-choke"];
const outputDir = join(dirname(fileURLToPath(import.meta.url)), "output");

function seededNoise(seed = 0x51f15e) {
  let state = seed >>> 0;
  return () => {
    state = (Math.imul(state, 1_664_525) + 1_013_904_223) >>> 0;
    return (state / 0xffff_ffff) * 2 - 1;
  };
}

function addBurst(signal, startSeconds, amplitude, seed) {
  const random = seededNoise(seed);
  const start = Math.round(startSeconds * sampleRate);
  const length = Math.round(0.018 * sampleRate);
  for (let n = 0; n < length; n += 1) {
    const phase = n / Math.max(1, length - 1);
    const envelope = Math.sin(Math.PI * phase) ** 2;
    const tone = Math.sin(2 * Math.PI * (440 + 2_100 * phase) * (n / sampleRate));
    signal[start + n] += amplitude * envelope * (0.7 * tone + 0.3 * random());
  }
}

function makeInput(includeProbe) {
  const input = new Float64Array(frames);
  addBurst(input, 0.05, 0.72, 0xabc123);
  if (includeProbe) addBurst(input, probeTime, 0.52, 0xdef456);
  return input;
}

function rampDown(index, boundary) {
  const distance = index - boundary;
  if (distance <= 0) return 1;
  if (distance >= rampFrames) return 0;
  return 1 - distance / rampFrames;
}

function rampUp(index, boundary) {
  const distance = index - boundary;
  if (distance <= 0) return 0;
  if (distance >= rampFrames) return 1;
  return distance / rampFrames;
}

function render(mode, includeProbe) {
  const input = makeInput(includeProbe);
  const output = new Float64Array(frames);
  const delay = new Float64Array(delayFrames);
  const startFrame = Math.round(chokeStart * sampleRate);
  const endFrame = Math.round(chokeEnd * sampleRate);
  let writeIndex = 0;

  for (let i = 0; i < frames; i += 1) {
    if (mode === "buffer-clear" && i === startFrame) delay.fill(0);

    const delayed = delay[writeIndex];
    const choking = i >= startFrame && i < endFrame;
    let outputGain = 1;
    let feedbackGain = feedback;
    let inputGain = 1;

    if (mode === "output-gate") {
      if (i >= startFrame && i < startFrame + rampFrames) outputGain = rampDown(i, startFrame);
      else if (choking) outputGain = 0;
      else if (i >= endFrame && i < endFrame + rampFrames) outputGain = rampUp(i, endFrame);
    }

    if (mode === "feedback-cut") {
      if (i >= startFrame && i < startFrame + rampFrames) feedbackGain *= rampDown(i, startFrame);
      else if (choking) feedbackGain = 0;
      else if (i >= endFrame && i < endFrame + rampFrames) feedbackGain *= rampUp(i, endFrame);
    }

    if (mode === "input-choke" && choking) inputGain = 0;

    output[i] = delayed * outputGain;
    delay[writeIndex] = input[i] * inputGain + delayed * feedbackGain;
    writeIndex = (writeIndex + 1) % delayFrames;
  }
  return output;
}

function rms(signal, startSeconds, endSeconds) {
  const start = Math.max(0, Math.round(startSeconds * sampleRate));
  const end = Math.min(signal.length, Math.round(endSeconds * sampleRate));
  let sum = 0;
  for (let i = start; i < end; i += 1) sum += signal[i] ** 2;
  return Math.sqrt(sum / Math.max(1, end - start));
}

function subtract(a, b) {
  const result = new Float64Array(a.length);
  for (let i = 0; i < a.length; i += 1) result[i] = a[i] - b[i];
  return result;
}

function maxStep(signal, centerSeconds, radiusSeconds = 0.012) {
  const start = Math.max(1, Math.round((centerSeconds - radiusSeconds) * sampleRate));
  const end = Math.min(signal.length, Math.round((centerSeconds + radiusSeconds) * sampleRate));
  let maximum = 0;
  for (let i = start; i < end; i += 1) maximum = Math.max(maximum, Math.abs(signal[i] - signal[i - 1]));
  return maximum;
}

function peak(signal) {
  let maximum = 0;
  for (const sample of signal) maximum = Math.max(maximum, Math.abs(sample));
  return maximum;
}

function pcm16Wav(signal) {
  const dataBytes = signal.length * 2;
  const buffer = Buffer.alloc(44 + dataBytes);
  buffer.write("RIFF", 0);
  buffer.writeUInt32LE(36 + dataBytes, 4);
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
  buffer.writeUInt32LE(dataBytes, 40);
  for (let i = 0; i < signal.length; i += 1) {
    const value = Math.max(-1, Math.min(1, signal[i]));
    buffer.writeInt16LE(Math.round(value * (value < 0 ? 32_768 : 32_767)), 44 + i * 2);
  }
  return buffer;
}

function fixed(value) {
  return Number(value.toFixed(8));
}

mkdirSync(outputDir, { recursive: true });
const unchokedReference = render("none", true);
const results = {
  schema: "battlefx-choke-semantics-offline/v1",
  boundary: "Independent delay-network models; not a BattleFX implementation or device observation.",
  config: { sampleRate, durationSeconds, delayFrames, feedback, chokeStart, chokeEnd, probeTime, rampMs: 5 },
  modes: {},
  assertions: []
};

for (const mode of modes) {
  const tailOnly = render(mode, false);
  const withProbe = render(mode, true);
  const probeDelta = subtract(withProbe, tailOnly);
  const eventDelta = subtract(withProbe, unchokedReference);
  const wav = pcm16Wav(withProbe);
  const filename = `${mode}.wav`;
  writeFileSync(join(outputDir, filename), wav);
  results.modes[mode] = {
    duringChokeRms: fixed(rms(tailOnly, chokeStart + 0.04, chokeEnd - 0.04)),
    oldTailAfterReleaseRms: fixed(rms(tailOnly, chokeEnd + 0.04, chokeEnd + 0.34)),
    probeAcceptanceRms: fixed(rms(probeDelta, probeTime + 0.1, chokeEnd + 0.38)),
    lateTailRms: fixed(rms(tailOnly, 2.2, 2.7)),
    onsetEventStepProxy: fixed(maxStep(eventDelta, chokeStart)),
    releaseEventStepProxy: fixed(maxStep(eventDelta, chokeEnd)),
    peak: fixed(peak(withProbe)),
    wav: filename,
    wavBytes: wav.length,
    wavSha256: createHash("sha256").update(wav).digest("hex")
  };
}

const m = results.modes;
results.assertions = [
  {
    id: "output-gate-resurrects-tail",
    pass: m["output-gate"].oldTailAfterReleaseRms > m["output-gate"].duringChokeRms * 10
  },
  {
    id: "input-choke-rejects-probe",
    pass: m["input-choke"].probeAcceptanceRms < 0.000001
  },
  {
    id: "input-choke-preserves-existing-tail",
    pass: m["input-choke"].duringChokeRms > m["feedback-cut"].duringChokeRms * 1.5
  },
  {
    id: "buffer-clear-removes-old-tail",
    pass: m["buffer-clear"].oldTailAfterReleaseRms < m["output-gate"].oldTailAfterReleaseRms * 0.05
  },
  {
    id: "feedback-cut-removes-recurrence",
    pass: m["feedback-cut"].lateTailRms < m["input-choke"].lateTailRms * 0.05
  }
];
results.allAssertionsPassed = results.assertions.every(({ pass }) => pass);
writeFileSync(join(outputDir, "results.json"), `${JSON.stringify(results, null, 2)}\n`);

if (!results.allAssertionsPassed) {
  console.error(JSON.stringify(results, null, 2));
  process.exitCode = 1;
} else {
  console.log(JSON.stringify(results, null, 2));
}
