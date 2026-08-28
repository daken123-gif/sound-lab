import test from "node:test";
import assert from "node:assert/strict";
import { BodyLevelWatchdog } from "../body-level-watchdog.js";

test("level watchdog distinguishes idle, waiting, and stalled", () => {
  const watchdog = new BodyLevelWatchdog(2000);
  assert.equal(watchdog.state(0), "idle");
  watchdog.start(100);
  assert.equal(watchdog.state(2099), "waiting");
  assert.equal(watchdog.state(2100), "stalled");
});

test("a level report activates and refreshes the watchdog", () => {
  const watchdog = new BodyLevelWatchdog(2000);
  watchdog.start(0);
  watchdog.mark(1500);
  assert.equal(watchdog.state(3499), "active");
  assert.equal(watchdog.state(3500), "stalled");
  watchdog.mark(3600);
  assert.equal(watchdog.state(3600), "active");
});

test("level watchdog validates timing input and can reset", () => {
  assert.throws(() => new BodyLevelWatchdog(0), /positive/);
  const watchdog = new BodyLevelWatchdog();
  assert.throws(() => watchdog.start(Number.NaN), /finite/);
  watchdog.start(0);
  watchdog.reset();
  assert.equal(watchdog.state(1), "idle");
});
