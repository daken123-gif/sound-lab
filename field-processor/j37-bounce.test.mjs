import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { createRequire } from 'node:module';
import test from 'node:test';

const require = createRequire(import.meta.url);
const { defaults, processChannel, bounceChannels } = require('./j37-bounce.js');

const sampleRate = 48000;

function sine(frequency, seconds, level = 0.5) {
  const output = new Float32Array(sampleRate * seconds);
  for (let index = 0; index < output.length; index += 1) {
    output[index] = Math.sin(2 * Math.PI * frequency * index / sampleRate) * level;
  }
  return output;
}

function difference(a, b) {
  let total = 0;
  for (let index = 0; index < a.length; index += 1) total += Math.abs(a[index] - b[index]);
  return total / a.length;
}

test('bounce is non-mutating and creates a distinct generation', () => {
  const source = sine(440, 0.1);
  const snapshot = source.slice();
  const result = bounceChannels([source], sampleRate);
  assert.deepEqual(source, snapshot);
  assert.notStrictEqual(result.channels[0], source);
  assert.ok(difference(result.channels[0], source) > 0.001);
  assert.equal(result.model, 'J37 research-informed generation bounce');
});

test('noise, wow and flutter remain off by default', () => {
  const silence = new Float32Array(2048);
  const output = processChannel(silence, sampleRate, defaults);
  assert.ok(output.every(sample => sample === 0));
});

test('HIT and saturation are independent controls', () => {
  const source = sine(997, 0.1, 0.72);
  const lowHit = processChannel(source, sampleRate, { hit: 0, saturation: 0.6 });
  const highHit = processChannel(source, sampleRate, { hit: 1, saturation: 0.6 });
  const lowSat = processChannel(source, sampleRate, { hit: 0.5, saturation: 0 });
  const highSat = processChannel(source, sampleRate, { hit: 0.5, saturation: 1 });
  assert.ok(difference(lowHit, highHit) > 0.01);
  assert.ok(difference(lowSat, highSat) > 0.01);
});

test('successive bounces accumulate generation color while remaining bounded', () => {
  const source = sine(331, 0.12, 0.9);
  const first = processChannel(source, sampleRate);
  const second = processChannel(first, sampleRate);
  assert.ok(difference(second, first) > 0.0005);
  assert.ok(second.every(sample => Number.isFinite(sample) && sample >= -1 && sample <= 1));
});

test('7.5 ips and 15 ips render different bandwidth behavior', () => {
  const source = sine(12000, 0.1, 0.6);
  const slow = processChannel(source, sampleRate, { speed: 7.5 });
  const fast = processChannel(source, sampleRate, { speed: 15 });
  assert.ok(difference(slow, fast) > 0.005);
});

test('Field Looper loads the engine and keeps RAW separate from bounced generations', async () => {
  const html = await readFile(new URL('./index.html', import.meta.url), 'utf8');
  assert.match(html, /<script src="\.\/j37-bounce\.js"><\/script>/);
  assert.match(html, /lane\.rawBuffer=buf/);
  assert.match(html, /lane\.buffer=rendered;lane\.generation\+=1/);
  assert.match(html, /<button id="bounce" type="button">J37 バウンス<\/button>/);
  assert.match(html, /bounce\.addEventListener\('click',bounceAllJ37\)/);
});
