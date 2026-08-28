import { resolve } from "node:path";
import { BodyEngine } from "./body-engine.js";
import { readPcmWav, writeMonoWav } from "./wav-io.js";

const PRESETS = Object.freeze({
  light: { size: 0.42, decay: 0.26, body: 0.38, dry: 0.14, drive: 0.7 },
  deep: { size: 0.78, decay: 0.7, body: 0.82, dry: 0.04, drive: 1.0 }
});

function measure(samples) {
  let sumSquares = 0;
  let peak = 0;
  for (const sample of samples) {
    sumSquares += sample * sample;
    peak = Math.max(peak, Math.abs(sample));
  }
  return { rms: Math.sqrt(sumSquares / Math.max(1, samples.length)), peak };
}

export function processWav(inputPath, outputPath, presetName = "light") {
  const preset = PRESETS[presetName];
  if (!preset) throw new Error(`unknown preset: ${presetName}; use light or deep`);

  const input = readPcmWav(inputPath);
  const engine = new BodyEngine({ sampleRate: input.sampleRate });
  engine.setParameters(preset);
  const output = engine.process(input.samples);
  writeMonoWav(outputPath, output, input.sampleRate);

  return {
    input: resolve(inputPath),
    output: resolve(outputPath),
    preset: presetName,
    sampleRate: input.sampleRate,
    sourceChannels: input.sourceChannels,
    seconds: input.samples.length / input.sampleRate,
    inputLevel: measure(input.samples),
    outputLevel: measure(output)
  };
}

const invokedPath = process.argv[1] ? resolve(process.argv[1]) : null;
if (invokedPath === resolve(new URL(import.meta.url).pathname)) {
  const [, , inputPath, outputPath, preset = "light"] = process.argv;
  if (!inputPath || !outputPath) {
    console.error("usage: node process-wav.js INPUT.wav OUTPUT.wav [light|deep]");
    process.exitCode = 2;
  } else {
    try {
      console.log(JSON.stringify(processWav(inputPath, outputPath, preset), null, 2));
    } catch (error) {
      console.error(error instanceof Error ? error.message : String(error));
      process.exitCode = 1;
    }
  }
}

export { PRESETS };
