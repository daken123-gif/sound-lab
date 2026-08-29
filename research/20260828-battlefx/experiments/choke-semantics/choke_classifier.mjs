import { readFileSync } from "node:fs";
import { pathToFileURL } from "node:url";

function findChunk(buffer, target) {
  let offset = 12;
  while (offset + 8 <= buffer.length) {
    const id = buffer.toString("ascii", offset, offset + 4);
    const size = buffer.readUInt32LE(offset + 4);
    const dataOffset = offset + 8;
    if (id === target) return { offset: dataOffset, size };
    offset = dataOffset + size + (size % 2);
  }
  return null;
}

export function readWav(path) {
  const buffer = readFileSync(path);
  if (buffer.toString("ascii", 0, 4) !== "RIFF" || buffer.toString("ascii", 8, 12) !== "WAVE") {
    throw new Error(`${path}: RIFF/WAVEではありません`);
  }
  const fmt = findChunk(buffer, "fmt ");
  const data = findChunk(buffer, "data");
  if (!fmt || !data || fmt.size < 16) throw new Error(`${path}: fmt/data chunkがありません`);

  const format = buffer.readUInt16LE(fmt.offset);
  const channels = buffer.readUInt16LE(fmt.offset + 2);
  const sampleRate = buffer.readUInt32LE(fmt.offset + 4);
  const blockAlign = buffer.readUInt16LE(fmt.offset + 12);
  const bits = buffer.readUInt16LE(fmt.offset + 14);
  if (channels < 1 || blockAlign < 1 || sampleRate < 1) throw new Error(`${path}: WAV formatが不正です`);
  if (!((format === 1 && [16, 24, 32].includes(bits)) || (format === 3 && bits === 32))) {
    throw new Error(`${path}: PCM16/24/32またはFloat32だけに対応しています`);
  }

  const frameCount = Math.floor(data.size / blockAlign);
  const samples = new Float64Array(frameCount);
  const bytesPerSample = bits / 8;
  for (let frame = 0; frame < frameCount; frame += 1) {
    let sum = 0;
    for (let channel = 0; channel < channels; channel += 1) {
      const offset = data.offset + frame * blockAlign + channel * bytesPerSample;
      let value;
      if (format === 3) value = buffer.readFloatLE(offset);
      else if (bits === 16) value = buffer.readInt16LE(offset) / 32_768;
      else if (bits === 24) {
        const raw = buffer.readUIntLE(offset, 3);
        value = (raw & 0x800000 ? raw - 0x1000000 : raw) / 8_388_608;
      } else value = buffer.readInt32LE(offset) / 2_147_483_648;
      sum += Number.isFinite(value) ? value : 0;
    }
    samples[frame] = sum / channels;
  }
  return { path, samples, sampleRate, channels, bits, format, durationSeconds: frameCount / sampleRate };
}

function rms(samples, sampleRate, startSeconds, endSeconds) {
  const start = Math.max(0, Math.round(startSeconds * sampleRate));
  const end = Math.min(samples.length, Math.round(endSeconds * sampleRate));
  if (end <= start) throw new Error(`測定windowが空です: ${startSeconds}–${endSeconds}s`);
  let sum = 0;
  for (let i = start; i < end; i += 1) sum += samples[i] ** 2;
  return Math.sqrt(sum / (end - start));
}

function difference(a, b) {
  const length = Math.min(a.length, b.length);
  const result = new Float64Array(length);
  for (let i = 0; i < length; i += 1) result[i] = a[i] - b[i];
  return result;
}

function fixed(value) {
  return Number(value.toFixed(8));
}

export function classifyChoke(tailOnly, withProbe, config) {
  if (tailOnly.sampleRate !== withProbe.sampleRate) throw new Error("二つのWAVのsample rateが一致しません");
  const { chokeStart, chokeEnd, probeTime, delayMs } = config;
  if (![chokeStart, chokeEnd, probeTime, delayMs].every(Number.isFinite) || chokeStart <= 0 || chokeEnd <= chokeStart) {
    throw new Error("chokeStart/chokeEnd/probeTime/delayMsが不正です");
  }
  const sampleRate = tailOnly.sampleRate;
  const minimumDuration = chokeEnd + 1.15;
  if (Math.min(tailOnly.durationSeconds, withProbe.durationSeconds) < minimumDuration) {
    throw new Error(`録音が短すぎます。最低${minimumDuration.toFixed(3)}秒必要です`);
  }

  const probeDelta = difference(withProbe.samples, tailOnly.samples);
  const noiseRms = rms(tailOnly.samples, sampleRate, 0, Math.min(0.04, chokeStart * 0.25));
  const preTailRms = rms(tailOnly.samples, sampleRate, Math.max(0.05, chokeStart - 0.31), chokeStart - 0.04);
  const threshold = Math.max(1e-7, noiseRms * 4, preTailRms * 0.03);
  const duringTailRms = rms(tailOnly.samples, sampleRate, chokeStart + 0.04, chokeEnd - 0.04);
  const oldTailAfterReleaseRms = rms(tailOnly.samples, sampleRate, chokeEnd + 0.04, chokeEnd + 0.34);
  const probeAcceptanceRms = rms(probeDelta, sampleRate, probeTime + delayMs / 1000, chokeEnd + 0.38);
  const lateTailRms = rms(tailOnly.samples, sampleRate, chokeEnd + 0.65, chokeEnd + 1.15);

  const signature = {
    tailAudibleDuringChoke: duringTailRms > threshold,
    oldTailReturnsAfterRelease: oldTailAfterReleaseRms > threshold,
    probeAcceptedDuringChoke: probeAcceptanceRms > threshold,
    recurrenceSurvivesLate: lateTailRms > threshold
  };

  let classification = "UNKNOWN";
  if (!signature.tailAudibleDuringChoke && signature.oldTailReturnsAfterRelease && signature.probeAcceptedDuringChoke) classification = "OUTPUT_GATE";
  else if (signature.tailAudibleDuringChoke && signature.oldTailReturnsAfterRelease && !signature.probeAcceptedDuringChoke) classification = "INPUT_CHOKE";
  else if (signature.tailAudibleDuringChoke && !signature.oldTailReturnsAfterRelease && signature.probeAcceptedDuringChoke) classification = "FEEDBACK_CUT";
  else if (!signature.tailAudibleDuringChoke && !signature.oldTailReturnsAfterRelease && signature.probeAcceptedDuringChoke) classification = "BUFFER_CLEAR";

  return {
    schema: "battlefx-choke-classifier/v1",
    classification,
    authority: "measurement-assist-only",
    boundary: "UNKNOWNまたは単一model不一致をBattleFX仕様へ自動昇格しない。",
    config: { chokeStart, chokeEnd, probeTime, delayMs, sampleRate },
    metrics: {
      noiseRms: fixed(noiseRms),
      preTailRms: fixed(preTailRms),
      threshold: fixed(threshold),
      duringTailRms: fixed(duringTailRms),
      oldTailAfterReleaseRms: fixed(oldTailAfterReleaseRms),
      probeAcceptanceRms: fixed(probeAcceptanceRms),
      lateTailRms: fixed(lateTailRms)
    },
    signature,
    inputs: {
      tailOnly: { path: tailOnly.path, channels: tailOnly.channels, bits: tailOnly.bits, durationSeconds: fixed(tailOnly.durationSeconds) },
      withProbe: { path: withProbe.path, channels: withProbe.channels, bits: withProbe.bits, durationSeconds: fixed(withProbe.durationSeconds) }
    }
  };
}

function parseArgs(args) {
  const values = {};
  for (let i = 0; i < args.length; i += 2) {
    const key = args[i];
    if (!key?.startsWith("--") || args[i + 1] === undefined) throw new Error(`引数が不正です: ${key ?? ""}`);
    values[key.slice(2)] = args[i + 1];
  }
  for (const required of ["tail-only", "with-probe", "choke-start", "choke-end", "probe-time", "delay-ms"]) {
    if (values[required] === undefined) throw new Error(`--${required}が必要です`);
  }
  return values;
}

if (process.argv[1] && pathToFileURL(process.argv[1]).href === import.meta.url) {
  try {
    const args = parseArgs(process.argv.slice(2));
    const result = classifyChoke(readWav(args["tail-only"]), readWav(args["with-probe"]), {
      chokeStart: Number(args["choke-start"]),
      chokeEnd: Number(args["choke-end"]),
      probeTime: Number(args["probe-time"]),
      delayMs: Number(args["delay-ms"])
    });
    console.log(JSON.stringify(result, null, 2));
  } catch (error) {
    console.error(error instanceof Error ? error.message : String(error));
    process.exitCode = 1;
  }
}
