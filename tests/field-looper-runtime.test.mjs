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
  assert.match(html, /const copy=channel\.slice\(0,count\);track\.chunks\.push\(copy\)/);
  assert.match(html, /track\.frames\+=count/);
});

test('finalizes real captured samples into a playable loop', () => {
  assert.match(html, /new Float32Array\(track\.frames\)/);
  assert.match(html, /context\.createBuffer\(1,data\.length,context\.sampleRate\)/);
  assert.match(html, /const peakData=buildPeaks\(data\)/);
  assert.match(html, /source\.buffer=reverse\?track\.reverseBuffer:track\.buffer/);
  assert.match(html, /source\.loop=true/);
});

test('draws a growing real waveform while recording', () => {
  assert.match(html, /track\.livePeaks\.push\(peak\)/);
  assert.match(html, /track\.frames\/\(context\.sampleRate\*MAX_SECONDS\)/);
  assert.match(html, /recording\?track\.livePeaks:track\.peaks/);
});

test('renders an animated playhead with current and total time', () => {
  assert.match(html, /drawTrack\(track,local\/track\.buffer\.duration\)/);
  assert.match(html, /const position=transportPosition\(\)/);
  assert.match(html, /formatTime\(seconds\).*formatTime\(total\)/);
  assert.match(html, /draw\.lineTo\(x,height\)/);
});

test('labels silence instead of inventing a waveform', () => {
  assert.match(html, /track\.silent=peakData\.maximum<\.0005/);
  assert.match(html, /draw\.fillText\('SILENCE'/);
});

test('removes the rejected generic dark KAOSS interface', () => {
  assert.doesNotMatch(html, /KAOSS/i);
  assert.doesNotMatch(html, /radial-gradient/);
  assert.doesNotMatch(html, /backdrop-filter/);
  assert.match(html, /--paper:#e7e3d7/);
});

test('has separate portrait and compact landscape layouts', () => {
  assert.match(html, /@media\(orientation:portrait\)/);
  assert.match(html, /@media\(max-height:430px\) and \(orientation:landscape\)/);
});

test('schedules all recorded tracks from one shared tape clock', () => {
  assert.match(html, /const transport=\{playing:false,duration:0,basePosition:0,anchorAt:0/);
  assert.match(html, /function restartSources\(position,when=/);
  assert.match(html, /startTrackSource\(track,when,position\)/);
  assert.match(html, /source\.start\(when,/);
  assert.match(html, /transportPosition\(at=context\?\.currentTime\|\|0\)/);
});

test('shows four real waveforms on one playable composite surface', () => {
  assert.match(html, /id="compositeWave"[^>]*aria-label="4トラック合成波形"/);
  assert.match(html, /function drawComposite\(\)/);
  assert.match(html, /tracks\.forEach\(\(track,trackIndex\)=>/);
  assert.match(html, /transport\.loopStart\/transport\.duration\*width/);
  assert.match(html, /transportPosition\(\)\/transport\.duration\*width/);
});

test('implements the researched time gestures instead of a generic XY pad', () => {
  for (const label of ['1 BAR', '1/2', '1/4', '1/8', '1/16', 'GRAIN']) {
    assert.match(html, new RegExp(`name:'${label.replace('/', '\\/')}'`));
  }
  assert.match(html, /gesture\.holdTimer=setTimeout/);
  assert.match(html, /recordTake\('grab-start'/);
  assert.match(html, /setTransportLoop\(Math\.min\(gesture\.startPosition,position\)/);
  assert.match(html, /dx<-52&&transport\.direction!==-1/);
  assert.match(html, /recordTake\('direction'/);
});

test('performance take remains explicitly armed and records gesture events only', () => {
  assert.match(html, /take=\{recording:false,nextId:1,events:\[\]\}/);
  assert.match(html, /if\(!take\.recording\)return/);
  assert.match(html, /take\.recording=!take\.recording/);
  assert.match(html, /take\.events\.push\(/);
});
