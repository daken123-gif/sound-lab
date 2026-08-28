import assert from 'node:assert/strict';
import test from 'node:test';

import {
  estimateBeatGrid,
  TIME_GESTURE_MODES,
  TimeGestureResolver,
} from '../field-processor/beat-match.mjs';

function pulseEnvelope({ seconds = 8, hopSeconds = 0.05, beatSeconds = 0.5 } = {}) {
  const values = Array(Math.round(seconds / hopSeconds)).fill(0);
  for (let time = 0; time < seconds; time += beatSeconds) {
    values[Math.round(time / hopSeconds)] = 1;
  }
  return values;
}

test('RAW preserves real waveform time without beat correction', () => {
  const resolver = new TimeGestureResolver({ duration: 8, mode: 'RAW' });
  resolver.setGrid({ bpm: 120, origin: 0, confidence: 1 });

  assert.deepEqual(resolver.resolve({ position: 1.137, length: 0.317 }), {
    requestedMode: 'RAW',
    effectiveMode: 'RAW',
    position: 1.137,
    length: 0.317,
    end: 1.454,
    snapped: false,
    reason: null,
    grid: {
      bpm: 120,
      origin: 0,
      confidence: 1,
      beatSeconds: 0.5,
    },
  });
});

test('periodic onsets produce a usable beat grid without editing the envelope', () => {
  const envelope = pulseEnvelope();
  const before = [...envelope];
  const grid = estimateBeatGrid(envelope, { hopSeconds: 0.05 });

  assert.ok(grid);
  assert.ok(Math.abs(grid.bpm - 120) < 0.001);
  assert.ok(grid.confidence > 0.9);
  assert.deepEqual(envelope, before);
});

test('AUTO snaps landing and loop length to the detected subdivision grid', () => {
  const resolver = new TimeGestureResolver({
    duration: 8,
    mode: TIME_GESTURE_MODES.AUTO,
    subdivision: 4,
  });
  resolver.estimate(pulseEnvelope(), { hopSeconds: 0.05 });

  const result = resolver.resolve({ position: 1.13, length: 0.31 });

  assert.equal(result.effectiveMode, 'AUTO');
  assert.equal(result.position, 1.125);
  assert.equal(result.length, 0.25);
  assert.equal(result.end, 1.375);
  assert.equal(result.step, 0.125);
  assert.equal(result.snapped, true);
});

test('beat detection failure falls back to RAW and never blocks playback', () => {
  const resolver = new TimeGestureResolver({ duration: 6, mode: 'AUTO' });
  const grid = resolver.estimate(Array(128).fill(0), { hopSeconds: 0.02 });
  const result = resolver.resolve({ position: 2.237, length: 0.19 });

  assert.equal(grid, null);
  assert.equal(result.effectiveMode, 'RAW');
  assert.equal(result.position, 2.237);
  assert.equal(result.length, 0.19);
  assert.equal(result.reason, 'NO_BEAT_GRID');
});

test('an uncertain grid also degrades to exact RAW coordinates', () => {
  const resolver = new TimeGestureResolver({
    duration: 5,
    mode: 'AUTO',
    minimumConfidence: 0.6,
  });
  resolver.setGrid({ bpm: 98, origin: 0.1, confidence: 0.4 });

  const result = resolver.resolve({ position: 1.234 });

  assert.equal(result.effectiveMode, 'RAW');
  assert.equal(result.position, 1.234);
  assert.equal(result.reason, 'LOW_CONFIDENCE');
});

test('AUTO keeps a snapped loop inside the shared tape boundary', () => {
  const resolver = new TimeGestureResolver({ duration: 2, mode: 'AUTO' });
  resolver.setGrid({ bpm: 120, confidence: 1 });

  const result = resolver.resolve({ position: 1.98, length: 0.31 });

  assert.equal(result.position, 1.75);
  assert.equal(result.length, 0.25);
  assert.equal(result.end, 2);
});

test('invalid modes and beat ranges are rejected explicitly', () => {
  assert.throws(() => new TimeGestureResolver({ mode: 'MAGIC' }), /unknown time gesture mode/);
  assert.throws(
    () => estimateBeatGrid([0, 1, 0, 1], {
      hopSeconds: 0.1,
      minimumBpm: 180,
      maximumBpm: 60,
    }),
    /maximumBpm must be greater/,
  );
});
