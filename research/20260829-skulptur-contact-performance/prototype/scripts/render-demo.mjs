import { mkdir, writeFile } from "node:fs/promises";
import { FourTrackSpectralMixer } from "../src/four-track-spectral-mixer.js";
import { SpectralControlEngine } from "../src/spectral-control-engine.js";

const sampleRate = 48000;
const durationSeconds = 8;
const frameCount = sampleRate * durationSeconds;

function sourceSignals() {
  const loops = Array.from({ length: 4 }, () => new Float32Array(frameCount));
  const drums = new Float32Array(frameCount);
  let seed = 0x12345678;
  const random = () => {
    seed ^= seed << 13;
    seed ^= seed >>> 17;
    seed ^= seed << 5;
    return ((seed >>> 0) / 0xffffffff) * 2 - 1;
  };

  for (let i = 0; i < frameCount; i += 1) {
    const t = i / sampleRate;
    const beatPhase = (t * 2) % 1;
    const kickEnvelope = Math.exp(-beatPhase * 18);
    const kick = Math.sin(2 * Math.PI * (48 + 70 * kickEnvelope) * t) * kickEnvelope;
    const voiceEnvelope = 0.55 + 0.45 * Math.sin(2 * Math.PI * 0.35 * t) ** 2;
    loops[0][i] = voiceEnvelope * (
      0.38 * Math.sin(2 * Math.PI * 145 * t) +
      0.18 * Math.sin(2 * Math.PI * 580 * t) +
      0.14 * Math.sin(2 * Math.PI * 1160 * t) +
      0.08 * Math.sin(2 * Math.PI * 2600 * t)
    );
    loops[1][i] = 0.32 * Math.sin(2 * Math.PI * 72.5 * t) *
      (0.65 + 0.35 * Math.sin(2 * Math.PI * 0.125 * t));
    loops[2][i] = 0.13 * random() * (0.35 + 0.65 * Math.sin(2 * Math.PI * 0.2 * t) ** 2);
    const pluckEnvelope = Math.exp(-((t * 1.5) % 1) * 7);
    loops[3][i] = 0.24 * pluckEnvelope * (
      Math.sin(2 * Math.PI * 435 * t) + 0.45 * Math.sin(2 * Math.PI * 870 * t)
    );
    const hatEnvelope = Math.exp(-((t * 4) % 1) * 42);
    drums[i] = 0.38 * kick + 0.07 * random() * hatEnvelope;
  }
  return { loops, drums };
}

function encodeWave(channels) {
  const channelCount = channels.length;
  const frames = channels[0].length;
  const bytesPerSample = 2;
  const dataBytes = frames * channelCount * bytesPerSample;
  const buffer = Buffer.alloc(44 + dataBytes);
  buffer.write("RIFF", 0);
  buffer.writeUInt32LE(36 + dataBytes, 4);
  buffer.write("WAVE", 8);
  buffer.write("fmt ", 12);
  buffer.writeUInt32LE(16, 16);
  buffer.writeUInt16LE(1, 20);
  buffer.writeUInt16LE(channelCount, 22);
  buffer.writeUInt32LE(sampleRate, 24);
  buffer.writeUInt32LE(sampleRate * channelCount * bytesPerSample, 28);
  buffer.writeUInt16LE(channelCount * bytesPerSample, 32);
  buffer.writeUInt16LE(16, 34);
  buffer.write("data", 36);
  buffer.writeUInt32LE(dataBytes, 40);

  let offset = 44;
  for (let i = 0; i < frames; i += 1) {
    for (const channel of channels) {
      const value = Math.max(-1, Math.min(1, channel[i]));
      buffer.writeInt16LE(Math.round(value * (value < 0 ? 32768 : 32767)), offset);
      offset += 2;
    }
  }
  return buffer;
}

function render(order) {
  const source = sourceSignals();
  const mixer = new FourTrackSpectralMixer({
    channels: 2,
    order,
    loopBusTrim: 0.42,
    drumBusGain: 0.95,
    filterOptions: { wetTrim: 0.66 }
  });
  const controls = new SpectralControlEngine();
  const blockSize = 128;
  const left = new Float32Array(frameCount);
  const right = new Float32Array(frameCount);

  for (let offset = 0; offset < frameCount; offset += blockSize) {
    const end = Math.min(frameCount, offset + blockSize);
    const time = offset / sampleRate;
    const loopBlocks = source.loops.map(track => {
      const block = track.slice(offset, end);
      return [block, block];
    });
    const drumBlock = source.drums.slice(offset, end);

    controls.setFlow({
      enabled: time >= 1 && time < 7.4,
      depth: 0.92,
      periodSeconds: 2,
      bandPhase: 0.075
    });
    const feedback = time >= 3.2 && time < 6.7 ? 0.96 : 0;
    mixer.spectral.setFeedbackBands(
      Array.from({ length: 10 }, (_, band) => [3, 5, 7].includes(band) ? feedback : 0)
    );
    mixer.spectral.setBands(controls.update((end - offset) / sampleRate));
    mixer.spectral.setActive(controls.isActive || mixer.spectral.hasFeedback);

    const [renderedLeft, renderedRight] = mixer.process(loopBlocks, [drumBlock, drumBlock]);
    left.set(renderedLeft, offset);
    right.set(renderedRight, offset);
  }
  return [left, right];
}

await mkdir(new URL("../renders/", import.meta.url), { recursive: true });
for (const order of [4, 8]) {
  const channels = render(order);
  await writeFile(
    new URL(`../renders/skulptur-${order}th-demo.wav`, import.meta.url),
    encodeWave(channels)
  );
}
