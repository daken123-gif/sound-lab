import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';

const html = readFileSync(new URL('./index.html', import.meta.url), 'utf8');
const count = value => html.split(value).length - 1;

test('Live Canvas identity and primary surfaces remain present', () => {
  assert.match(html, /<title>Live Canvas<\/title>/);
  assert.match(html, /合成波形/);
  assert.match(html, /aria-label="4つの手動ループ"/);
  assert.match(html, /id="inFill"/);
  assert.match(html, /id="outFill"/);
  assert.match(html, /id="input"/);
  assert.match(html, /id="output"/);
});

test('runtime control ids stay unique', () => {
  const ids = [
    'route', 'status', 'inFill', 'outFill', 'inVal', 'outVal',
    'loops', 'waveform', 'xy', 'input', 'hpf', 'density', 'air',
    'output', 'preampMode', 'mode', 'start'
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
