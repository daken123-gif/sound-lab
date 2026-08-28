import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import test from 'node:test';

const html = await readFile(new URL('../field-processor/index.html', import.meta.url), 'utf8');

test('ships as one executable HTML file', () => {
  assert.match(html, /<script>/);
  assert.doesNotMatch(html, /<script type="module">/);
  assert.doesNotMatch(html, /src="[^\"]+\.js/);
});

test('starts microphone access from the explicit INPUT button', () => {
  assert.match(html, /id="inputButton"[^>]*>INPUT ON<\/button>/);
  assert.match(html, /inputButton'\)\.addEventListener\('click',async/);
  assert.match(html, /navigator\.mediaDevices\.getUserMedia\(\{audio:audioConstraints\(\)\}\)/);
});

test('exposes unambiguous controls on every one of four tracks', () => {
  assert.match(html, /Array\.from\(\{length:4\}/);
  assert.match(html, /class="rec"[^>]*>REC<\/button>/);
  assert.match(html, /class="play"[^>]*>PLAY<\/button>/);
  assert.match(html, /class="stop"[^>]*>STOP<\/button>/);
  assert.match(html, /class="erase"/);
});

test('captures with AudioWorklet and retains a Safari fallback', () => {
  assert.match(html, /context\.audioWorklet\.addModule\(url\)/);
  assert.match(html, /new AudioWorkletNode\(context,'field-capture'/);
  assert.match(html, /context\.createScriptProcessor\(1024,1,1\)/);
  assert.match(html, /catch\{setNotice\('互換録音モード'\)\}/);
});

test('writes microphone samples only into an explicitly recording track', () => {
  assert.match(html, /if\(track\.state!=='recording'\)continue/);
  assert.match(html, /track\.chunks\.push\(channel\.slice\(0,count\)\)/);
  assert.match(html, /track\.frames\+=count/);
});

test('finalizes real captured samples into a playable loop', () => {
  assert.match(html, /new Float32Array\(track\.frames\)/);
  assert.match(html, /context\.createBuffer\(1,data\.length,context\.sampleRate\)/);
  assert.match(html, /source\.buffer=track\.buffer/);
  assert.match(html, /source\.loop=true/);
});

test('removes the rejected generic dark KAOSS interface', () => {
  assert.doesNotMatch(html, /KAOSS/i);
  assert.doesNotMatch(html, /radial-gradient/);
  assert.doesNotMatch(html, /backdrop-filter/);
  assert.match(html, /--paper:#e7e3d7/);
});

test('has separate portrait and compact landscape layouts', () => {
  assert.match(html, /@media\(orientation:portrait\)/);
  assert.match(html, /@media\(max-height:420px\) and \(orientation:landscape\)/);
});
