import { performance } from "node:perf_hooks";
import { BodyRealtimeCore } from "./body-realtime-core.js";

const sampleRate = 48000;
const seconds = 30;
const blockSize = 128;
const blocks = Math.ceil(sampleRate * seconds / blockSize);
const core = new BodyRealtimeCore(sampleRate);
const input = new Float32Array(blockSize);
const output = new Float32Array(blockSize);
for (let index = 0; index < input.length; index += 1) {
  input[index] = Math.sin(2 * Math.PI * 173 * index / sampleRate) * 0.2;
}

const parameters = {
  gate: new Float32Array([1]),
  size: new Float32Array([0.5]),
  decay: new Float32Array([0.45]),
  body: new Float32Array([0.65]),
  dry: new Float32Array([0.12]),
  drive: new Float32Array([0.7])
};

const start = performance.now();
for (let block = 0; block < blocks; block += 1) {
  core.processBlock(input, output, parameters);
}
const elapsedMilliseconds = performance.now() - start;
const realtimeMilliseconds = seconds * 1000;

console.log(JSON.stringify({
  environment: `Node ${process.version}`,
  sampleRate,
  blockSize,
  renderedSeconds: seconds,
  elapsedMilliseconds,
  realtimeLoadRatio: elapsedMilliseconds / realtimeMilliseconds
}, null, 2));
