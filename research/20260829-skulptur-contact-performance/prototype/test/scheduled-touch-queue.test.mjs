import assert from "node:assert/strict";
import test from "node:test";
import { normalizeScheduledTouchBatch, ScheduledTouchQueue } from "../src/scheduled-touch-queue.js";

const begin = (timeSeconds = 1, pointerId = 7) => ({
  type: "touch-begin", pointerId, band: 3, position: 0.75, timeSeconds
});
const end = (timeSeconds = 1.1, pointerId = 7) => ({
  type: "touch-end", pointerId, throwMotion: false, timeSeconds
});

test("normalizes one immutable audio-clock touch batch", () => {
  const batch = normalizeScheduledTouchBatch("take-1", [begin(), end()]);
  assert.equal(batch.scheduleId, "take-1");
  assert.equal(batch.commands[1].throwMotion, false);
  assert.ok(Object.isFrozen(batch)); assert.ok(Object.isFrozen(batch.commands));
});

test("drains commands by audio time while preserving equal-time order", () => {
  const queue = new ScheduledTouchQueue();
  queue.enqueue("take-1", [begin(1, 7), begin(1, 8), end(1.1, 7), end(1.1, 8)]);
  assert.equal(queue.drainDue(0.99).length, 0);
  assert.deepEqual(queue.drainDue(1).map(item => item.command.pointerId), [7, 8]);
  assert.equal(queue.pendingCount, 2);
});

test("cancels only the named schedule before its commands are due", () => {
  const queue = new ScheduledTouchQueue();
  queue.enqueue("a", [begin(1, 1), end(2, 1)]);
  queue.enqueue("b", [begin(1, 2), end(2, 2)]);
  assert.equal(queue.cancel("a"), 2);
  assert.deepEqual(queue.drainDue(2).map(item => item.scheduleId), ["b", "b"]);
});

test("rejects malformed, regressing, and duplicate schedules", () => {
  const queue = new ScheduledTouchQueue();
  assert.throws(() => normalizeScheduledTouchBatch("x", [end(2), begin(1)]), /non-decreasing/);
  assert.throws(() => normalizeScheduledTouchBatch("x", [{ ...begin(), position: 2 }]), /position/);
  assert.throws(() => normalizeScheduledTouchBatch("x", [{ ...begin(), type: "touch-move" }, end()]), /active pointer/);
  assert.throws(() => normalizeScheduledTouchBatch("x", [begin()]), /end every pointer/);
  assert.throws(() => normalizeScheduledTouchBatch("x", [begin(), begin(1.05), end()]), /begin twice/);
  queue.enqueue("x", [begin(), end()]);
  assert.throws(() => queue.enqueue("x", [begin(2), end(3)]), /already active/);
});
