import assert from 'node:assert/strict';
import test from 'node:test';

import { LOOP_DIVISIONS, SharedTransport } from '../field-processor/shared-transport.mjs';

function manualClock(initial = 0) {
  let now = initial;
  return {
    clock: () => now,
    set(value) { now = value; },
  };
}

test('four tracks inherit one longest shared timeline', () => {
  const time = manualClock();
  const transport = new SharedTransport({ clock: time.clock });

  transport.setTrackDuration(0, 4);
  transport.setTrackDuration(1, 7.5);
  transport.setTrackDuration(2, 2);

  assert.equal(transport.snapshot().duration, 7.5);
  assert.deepEqual(transport.snapshot().trackDurations, [4, 7.5, 2, 0]);
  assert.deepEqual([transport.snapshot().loopStart, transport.snapshot().loopEnd], [0, 7.5]);
});

test('one clock drives play, stop and wrap for every track', () => {
  const time = manualClock(10);
  const transport = new SharedTransport({ clock: time.clock });
  transport.setTrackDuration(0, 4);
  transport.setTrackDuration(1, 4);
  transport.start({ position: 3.5 });

  time.set(11);
  assert.equal(transport.position(), 0.5);
  transport.stop();
  time.set(20);
  assert.equal(transport.position(), 0.5);
});

test('playback plan gives every non-empty source one exact start time', () => {
  const time = manualClock(2);
  const transport = new SharedTransport({ clock: time.clock });
  transport.setTrackDuration(0, 8);
  transport.setTrackDuration(1, 3);
  transport.seek(5.5);

  const plan = transport.playbackPlan({ leadTime: 0.05 });

  assert.equal(plan.when, 2.05);
  assert.equal(plan.tracks[0].when, plan.tracks[1].when);
  assert.equal(plan.tracks[0].offset, 5.5);
  assert.equal(plan.tracks[1].offset, 2.5);
  assert.equal(plan.tracks[2].empty, true);
});

test('loop range is shared and seeking cannot escape it', () => {
  const time = manualClock();
  const transport = new SharedTransport({ clock: time.clock });
  transport.setTrackDuration(0, 8);
  transport.setLoop(2, 4);
  transport.seek(7);

  assert.equal(transport.position(), 3);
  transport.start();
  time.set(1.5);
  assert.equal(transport.position(), 2.5);
});

test('reverse changes direction without jumping position', () => {
  const time = manualClock();
  const transport = new SharedTransport({ clock: time.clock });
  transport.setTrackDuration(0, 8);
  transport.start({ position: 3 });
  time.set(1);
  assert.equal(transport.position(), 4);

  transport.setDirection(-1);
  assert.equal(transport.position(), 4);
  time.set(2.5);
  assert.equal(transport.position(), 2.5);
});

test('research loop stages shorten one common range around the gesture', () => {
  const time = manualClock();
  const transport = new SharedTransport({ clock: time.clock });
  transport.setTrackDuration(0, 16);

  transport.setLoopDivision('1/4', { anchor: 6 });
  assert.deepEqual([transport.snapshot().loopStart, transport.snapshot().loopEnd], [6, 10]);
  assert.equal(transport.snapshot().loopDivision, '1/4');

  transport.setLoopDivision('GRAIN', { anchor: 6 });
  assert.equal(transport.snapshot().loopEnd - transport.snapshot().loopStart, 16 * LOOP_DIVISIONS.GRAIN);
});

test('removing every recording returns the transport to an inert state', () => {
  const time = manualClock();
  const transport = new SharedTransport({ clock: time.clock });
  transport.setTrackDuration(0, 4);
  transport.start();
  transport.setTrackDuration(0, 0);

  assert.deepEqual(transport.snapshot(), {
    playing: false,
    position: 0,
    duration: 0,
    direction: 1,
    loopStart: 0,
    loopEnd: 0,
    loopDivision: '1 BAR',
    trackDurations: [0, 0, 0, 0],
  });
});
