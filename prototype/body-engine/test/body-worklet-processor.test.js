import test from "node:test";
import assert from "node:assert/strict";

let registeredName = null;
let RegisteredProcessor = null;

globalThis.sampleRate = 48000;
globalThis.AudioWorkletProcessor = class {
  constructor() {
    this.messages = [];
    this.port = { postMessage: message => this.messages.push(message) };
  }
};
globalThis.registerProcessor = (name, ProcessorClass) => {
  registeredName = name;
  RegisteredProcessor = ProcessorClass;
};

await import("../body-worklet-processor.js");

function parameters(gate) {
  return {
    size: new Float32Array([0.55]),
    decay: new Float32Array([0.42]),
    body: new Float32Array([0.55]),
    dry: new Float32Array([0.12]),
    drive: new Float32Array([0.7]),
    gate: new Float32Array([gate])
  };
}

function render(processor, inputChannels, gate = 1, frames = 128) {
  const output = new Float32Array(frames);
  const keepAlive = processor.process([[...inputChannels]], [[output]], parameters(gate));
  assert.equal(keepAlive, true);
  return output;
}

test("AudioWorklet adapter registers the soma-body processor", () => {
  assert.equal(registeredName, "soma-body");
  assert.equal(typeof RegisteredProcessor, "function");
});

test("closed gate reports microphone input while BODY remains silent", () => {
  const processor = new RegisteredProcessor();
  const input = new Float32Array(128).fill(0.25);
  for (let block = 0; block < 16; block += 1) {
    const output = render(processor, [input], 0);
    assert.ok(output.every(sample => sample === 0));
  }

  assert.equal(processor.messages.length, 1);
  const report = processor.messages[0];
  assert.equal(report.type, "levels");
  assert.equal(report.frames, 2048);
  assert.equal(report.inputRms, 0.25);
  assert.equal(report.outputRms, 0);
});

test("open gate produces bounded BODY audio and level reports", () => {
  const processor = new RegisteredProcessor();
  const left = new Float32Array(128);
  const right = new Float32Array(128);
  for (let index = 0; index < 128; index += 1) {
    left[index] = Math.sin(index * 0.19) * 0.4;
    right[index] = Math.sin(index * 0.19) * 0.2;
  }

  let nonZero = false;
  for (let block = 0; block < 16; block += 1) {
    const output = render(processor, [left, right], 1);
    for (const sample of output) {
      assert.ok(Number.isFinite(sample));
      assert.ok(sample >= -1 && sample <= 1);
      if (sample !== 0) nonZero = true;
    }
  }

  assert.equal(nonZero, true);
  assert.equal(processor.messages.length, 1);
  assert.ok(processor.messages[0].inputRms > 0);
  assert.ok(processor.messages[0].outputRms > 0);
});
