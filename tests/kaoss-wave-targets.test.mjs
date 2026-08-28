import fs from 'node:fs';
import vm from 'node:vm';
import assert from 'node:assert/strict';

const html = fs.readFileSync(new URL('../field-processor/index.html', import.meta.url), 'utf8');
const script = html.match(/<script>([\s\S]*?)<\/script>/)?.[1];
assert.ok(script, 'inline script exists');
new vm.Script(script);

const targetValues = [...html.matchAll(/class="wave-target(?: active)?" data-target="([^"]+)"/g)].map(match => match[1]);
assert.deepEqual(targetValues, ['0', '1', '2', '3', 'mix']);
assert.match(html, /Array\.from\(\{length:4\}/);
assert.match(html, /expected=\(item\.position\+elapsed\*\(rates\[i\]\|\|1\)\/lane\.buffer\.duration\)%1/);
assert.equal((html.match(/beginRecord\(/g) || []).length, 2);
assert.match(html, /if\(lane\.state==='empty'\)beginRecord\(lane\)/);
assert.match(html, /loopBus\.connect\(masterDry\)\.connect\(master\);loopBus\.connect\(kaossFilter\)/);
for (const anchor of ['preampProfiles', "body:{label:'BODY'", "open:{label:'OPEN'", "focus:{label:'FOCUS'", 'presenceQMin:.55', 'presenceQMax:1.35', 'characterPresenceQ(d,p)', 'setPreampMode(preampStyle)']) {
  assert.ok(html.includes(anchor), `latest mic feature retained: ${anchor}`);
}
const targetHeight = Number(html.match(/\.wave-target\{height:(\d+)px/)?.[1]);
assert.ok(targetHeight >= 40, 'wave target touch height is at least 40px');
assert.match(html, /pointermove',e=>\{if\(waveGesture\)performWave\(e\)\}/);
assert.match(html, /function selectWaveTarget\(target\)\{if\(waveGesture\)releaseWave\(\)/);
assert.doesNotMatch(html, /function seekComposite/);

function functionSource(name) {
  const start = script.indexOf(`function ${name}`);
  assert.ok(start >= 0, `function exists: ${name}`);
  let cursor = script.indexOf('{', start);
  let depth = 0;
  for (; cursor < script.length; cursor += 1) {
    if (script[cursor] === '{') depth += 1;
    else if (script[cursor] === '}' && --depth === 0) break;
  }
  return script.slice(start, cursor + 1);
}

const events = [];
const gainParam = () => ({
  value: .25,
  setValueAtTime(value, at) { events.push(['set', value, at]); this.value = value; },
  linearRampToValueAtTime(value, at) { events.push(['ramp', value, at]); this.value = value; },
  cancelScheduledValues(at) { events.push(['cancel', at]); }
});
const context = {
  currentTime: 10,
  createBufferSource: () => ({
    playbackRate: { value: 0 },
    connect() { return this; },
    start(at, offset) { events.push(['start', at, offset]); },
    stop(at) { events.push(['stop', at]); }
  }),
  createGain: () => ({ gain: gainParam(), connect() { return this; } }),
  createBiquadFilter: () => ({ frequency: { value: 0 }, Q: { value: 0 }, connect() { return this; } })
};
const lane = {
  buffer: { duration: 4 },
  source: { stop(at) { events.push(['old-stop', at]); } },
  gain: { gain: gainParam() },
  state: 'playing',
  startedAt: 0
};
const audio = {
  ctx: context,
  loopBus: {},
  rates: [1, 1, 1, 1],
  trackLevels: [.27, .25, .23, .21],
  lanes: [lane, {}, {}, {}],
  setState(target, state) { target.state = state; }
};
vm.createContext(audio);
vm.runInContext(`${functionSource('playLane')}\n${functionSource('lanePosition')}`, audio);
audio.playLane(lane, .5, .1, .02);
assert.deepEqual(events.find(event => event[0] === 'start'), ['start', 10, 2]);
assert.equal(lane.source.loopStart, 2);
assert.equal(lane.source.loopEnd, 2.4);
assert.ok(events.some(event => event[0] === 'ramp' && event[1] === .27 && event[2] === 10.02));
assert.ok(events.some(event => event[0] === 'old-stop' && Math.abs(event[1] - 10.03) < 1e-9));
context.currentTime = 10.5;
assert.equal(audio.lanePosition(lane), .625);

const releaseCalls = [];
const releaseLane = { buffer: { duration: 4 }, state: 'playing' };
const release = {
  ctx: { currentTime: 11 },
  waveGesture: { startedAt: 10, targets: [{ lane: releaseLane, position: .25 }] },
  waveTouch: .5,
  waveWindow: .1,
  rates: [1],
  lanes: [releaseLane],
  drawWave() {},
  playLane(...args) { releaseCalls.push(args); }
};
vm.createContext(release);
vm.runInContext(functionSource('releaseWave'), release);
release.releaseWave();
assert.equal(releaseCalls.length, 1);
assert.equal(releaseCalls[0][1], .5);
assert.deepEqual(releaseCalls[0].slice(2), [0, .028]);
assert.equal(release.waveGesture, null);

const order = [];
const selection = {
  waveGesture: {},
  waveTarget: 'mix',
  waveTouch: .5,
  waveWindow: .1,
  releaseWave() { order.push('release'); selection.waveGesture = null; },
  updateWaveTargetUI() { order.push('ui'); },
  drawWave() { order.push('draw'); }
};
vm.createContext(selection);
vm.runInContext(functionSource('selectWaveTarget'), selection);
selection.selectWaveTarget('2');
assert.deepEqual(order, ['release', 'ui', 'draw']);
assert.equal(selection.waveTarget, '2');

console.log('PASS script syntax');
console.log('PASS targets 1/2/3/4/MIX');
console.log('PASS X position / Y repeat with release resync');
console.log('PASS manual recording only');
console.log('PASS KAOSS master routing retained');
console.log('PASS BODY / OPEN / FOCUS retained');
console.log('PASS latest FOCUS dynamic Q retained');
console.log('PASS target touch height >= 40px');
console.log('PASS target switch releases active gesture safely');
console.log('PASS fragment boundaries and crossfade schedule');
console.log('PASS moving sync phase restoration');
