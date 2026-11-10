import assert from "node:assert/strict";
import test from "node:test";
import { fitAudioBufferToLoop } from "../src/audio-loop-fit.js";

function createBuffer(numberOfChannels, length, sampleRate, values = []) {
  const channels = Array.from({ length: numberOfChannels }, (_, channel) => {
    const data = new Float32Array(length);
    if (values[channel]) data.set(values[channel].slice(0, length));
    return data;
  });
  return {
    numberOfChannels,
    length,
    sampleRate,
    getChannelData(channel) { return channels[channel]; }
  };
}

function createContext(sampleRate) {
  return {
    sampleRate,
    createBuffer(numberOfChannels, length, rate) {
      return createBuffer(numberOfChannels, length, rate);
    }
  };
}

test("audio fitting creates an exact loop and pads short input with silence", () => {
  const context = createContext(4);
  const source = createBuffer(1, 2, 4, [[0.25, -0.5]]);
  const output = fitAudioBufferToLoop(context, source, {
    durationSeconds: 1,
    fadeInSeconds: 0,
    fadeOutSeconds: 0
  });
  assert.equal(output.length, 4);
  assert.deepEqual([...output.getChannelData(0)], [0.25, -0.5, 0, 0]);
});

test("audio fitting caps imported material at stereo and the requested duration", () => {
  const context = createContext(10);
  const source = createBuffer(3, 30, 10, [
    new Array(30).fill(1),
    new Array(30).fill(0.5),
    new Array(30).fill(-1)
  ]);
  const output = fitAudioBufferToLoop(context, source, {
    durationSeconds: 1,
    fadeInSeconds: 0,
    fadeOutSeconds: 0
  });
  assert.equal(output.numberOfChannels, 2);
  assert.equal(output.length, 10);
  assert.equal(output.getChannelData(0)[9], 1);
  assert.equal(output.getChannelData(1)[9], 0.5);
});

test("audio fitting fades both cut boundaries to suppress clicks", () => {
  const context = createContext(1000);
  const source = createBuffer(1, 1000, 1000, [new Array(1000).fill(1)]);
  const output = fitAudioBufferToLoop(context, source, { durationSeconds: 1 });
  const data = output.getChannelData(0);
  assert.equal(data[0], 0);
  assert.equal(data.at(-1), 0);
  assert.equal(data[100], 1);
});
