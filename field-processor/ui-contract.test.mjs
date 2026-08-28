import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';

const html = readFileSync(new URL('./index.html', import.meta.url), 'utf8');
const drumEngine = readFileSync(new URL('./drum-engine.js', import.meta.url), 'utf8');
const count = value => html.split(value).length - 1;

test('Live Canvas identity and primary surfaces remain present', () => {
  assert.match(html, /<title>Live Canvas<\/title>/);
  assert.match(html, /合成波形/);
  assert.match(html, /aria-label="4つの手動ループ"/);
  assert.match(html, /id="inFill"/);
  assert.match(html, /id="outFill"/);
  assert.match(html, /id="input"/);
  assert.match(html, /id="output"/);
  assert.match(html, /id="drumsOpen"/);
  assert.match(html, /id="drumsPanel"/);
});

test('runtime control ids stay unique', () => {
  const ids = [
    'route', 'status', 'inFill', 'outFill', 'inVal', 'outVal',
    'loops', 'waveform', 'xy', 'input', 'hpf', 'density', 'air',
    'output', 'preampMode', 'mode', 'start', 'drumsOpen', 'drumsPanel',
    'drumStart', 'drumRec', 'drumClear', 'drumStatus',
    'drumMap0', 'drumMap1', 'drumMap2', 'drumMap3',
    'drumChance', 'drumDrive'
  ];
  for (const id of ids) assert.equal(count(`id="${id}"`), 1, id);
});

test('retired provisional UI does not return', () => {
  assert.doesNotMatch(html, /KAOSS MASTER/i);
  assert.doesNotMatch(html, /横向きにしてください/);
  assert.doesNotMatch(html, /conic-gradient/i);
  assert.doesNotMatch(html, /border-radius\s*:\s*50%/i);
});

test('portrait and landscape layouts both remain defined', () => {
  assert.match(html, /grid-template-areas:"meters" "wave" "loops" "shape"/);
  assert.match(html, /@media\(orientation:landscape\)/);
  assert.match(html, /"meters wave shape" "loops wave shape"/);
});

test('recording remains a manual track action', () => {
  assert.match(html, /addEventListener\('click',\(\)=>trackTap\(l\)\)/);
  assert.match(html, /state:'empty'/);
  assert.doesNotMatch(html, /auto.?record/i);
  assert.doesNotMatch(html, /start\(\)[\s\S]{0,400}beginRecord\(/);
});

test('embedded JavaScript parses', () => {
  const scripts = [...html.matchAll(/<script(?:\s[^>]*)?>([\s\S]*?)<\/script>/gi)];
  assert.ok(scripts.length > 0);
  for (const [, source] of scripts) new Function(source);
});

test('DRUMS is one direct entry and remains separate from the four loop lanes', () => {
  assert.equal(count('id="drumsOpen"'), 1);
  assert.equal(count('data-drum-pad='), 4);
  assert.equal(count('data-drum-map='), 4);
  assert.match(html, /new MappingDrumEngine\(\$\('#drumsPanel'\)\)/);
  assert.doesNotMatch(html, /loopBus\.connect\([^\n]*drum/i);
  assert.match(drumEngine, /new \(window\.AudioContext \|\| window\.webkitAudioContext\)/);
  assert.match(drumEngine, /recordingLength = 256/);
  assert.match(drumEngine, /\[16, 13, 15\]/);
  assert.doesNotMatch(drumEngine, /loopBus|capture\(/);
  new Function(drumEngine);
});
