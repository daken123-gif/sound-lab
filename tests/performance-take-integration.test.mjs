import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import test from 'node:test';

const html = await readFile(new URL('../field-processor/index.html', import.meta.url), 'utf8');

test('loads the recorder as a browser module', () => {
  assert.match(html, /<script type="module">/);
  assert.match(html, /import \{ PerformanceTakeRecorder \} from '\.\/performance-take\.mjs';/);
  assert.match(html, /new PerformanceTakeRecorder\(\)/);
});

test('keeps performance recording behind a separate explicit control', () => {
  assert.match(html, /id="takeRec"[^>]*>REC TAKE<\/button>/);
  assert.match(html, /performanceTake\.recording\?performanceTake\.stop\(\):performanceTake\.start\(\)/);
  assert.match(html, /先に4トラックへ録音/);
});

test('records composite seek and KAOSS only through the armed recorder', () => {
  assert.match(html, /recordTake\('loop-position'/);
  assert.match(html, /recordTake\('kaoss',[^\n]*active:true/);
  assert.match(html, /recordTake\('kaoss',[^\n]*active:false/);
});

test('renders event markers and exposes mute and hold-delete editing', () => {
  assert.match(html, /for\(const event of performanceTake\.snapshot\(\)\.events\)/);
  assert.match(html, /performanceTake\.setMuted/);
  assert.match(html, /performanceTake\.remove/);
  assert.match(html, /,650\)/);
});

test('stopping audio clears the take without touching recorded audio in the recorder', () => {
  assert.match(html, /performanceTake\.stop\(\);performanceTake\.clear\(\)/);
  assert.doesNotMatch(html, /performanceTake\.(?:buffer|source|audio)/);
});
