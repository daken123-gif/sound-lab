import assert from 'node:assert/strict';
import test from 'node:test';

import {
  PERFORMANCE_EVENT_TYPES,
  PerformanceTakeRecorder,
} from '../field-processor/performance-take.mjs';

function clockSequence(...values) {
  let index = 0;
  return () => values[Math.min(index++, values.length - 1)];
}

test('recording never begins implicitly', () => {
  const take = new PerformanceTakeRecorder({ clock: () => 0 });

  assert.equal(take.record('grab-start', { target: 'master' }, 1.25), null);
  assert.deepEqual(take.snapshot(), { recording: false, events: [] });
});

test('explicit start and stop gate every event', () => {
  const take = new PerformanceTakeRecorder({ clock: clockSequence(10, 20) });

  take.start();
  const start = take.record('grab-start', { target: 'master' }, 3.5);
  const direction = take.record('direction', { target: 'master', reverse: true }, 3.75);
  take.stop();

  assert.equal(start.id, 1);
  assert.equal(direction.id, 2);
  assert.equal(take.record('grab-end', { target: 'master' }, 4), null);
  assert.equal(take.snapshot().events.length, 2);
});

test('supports every event type defined by the research', () => {
  const take = new PerformanceTakeRecorder({ clock: () => 100, minimumContinuousIntervalMs: 0 });
  take.start();

  PERFORMANCE_EVENT_TYPES.forEach((type, index) => {
    assert.equal(take.record(type, { target: 'master', index }, index).type, type);
  });

  assert.deepEqual(take.snapshot().events.map(event => event.type), PERFORMANCE_EVENT_TYPES);
});

test('rejects unknown event types while armed', () => {
  const take = new PerformanceTakeRecorder({ clock: () => 0 });
  take.start();

  assert.throws(() => take.record('automatic-record', {}, 0), /unknown performance event/);
});

test('thins dense continuous gestures without losing their latest value', () => {
  const take = new PerformanceTakeRecorder({
    clock: clockSequence(0, 5, 20),
    minimumContinuousIntervalMs: 16,
  });
  take.start();

  const first = take.record('kaoss', { target: 'master', x: 0.1, y: 0.2 }, 1);
  const coalesced = take.record('kaoss', { target: 'master', x: 0.4, y: 0.5 }, 1.01);
  const next = take.record('kaoss', { target: 'master', x: 0.8, y: 0.9 }, 1.02);
  const events = take.snapshot().events;

  assert.equal(first.id, coalesced.id);
  assert.notEqual(coalesced.id, next.id);
  assert.equal(events.length, 2);
  assert.deepEqual(events[0].value, { target: 'master', x: 0.4, y: 0.5 });
});

test('mute and delete operate on events, not source audio', () => {
  const take = new PerformanceTakeRecorder({ clock: clockSequence(0, 20) });
  take.start();
  const grab = take.record('grab-start', { target: 'master' }, 2);
  const reverse = take.record('direction', { target: 'master', reverse: true }, 2.1);

  assert.equal(take.setMuted(grab.id), true);
  assert.deepEqual(take.snapshot({ includeMuted: false }).events.map(event => event.id), [reverse.id]);
  assert.equal(take.remove(reverse.id), true);
  assert.deepEqual(take.snapshot().events.map(event => event.id), [grab.id]);
});

test('replace is explicit and snapshots do not expose mutable payloads', () => {
  const take = new PerformanceTakeRecorder({ clock: clockSequence(0, 20) });
  take.start();
  const input = { target: 'master', preset: { name: 'tape-stop' } };
  take.record('fx-preset', input, 0);
  input.preset.name = 'changed-outside';

  assert.equal(take.snapshot().events[0].value.preset.name, 'tape-stop');
  take.start({ replace: true });
  assert.deepEqual(take.snapshot(), { recording: true, events: [] });
});
