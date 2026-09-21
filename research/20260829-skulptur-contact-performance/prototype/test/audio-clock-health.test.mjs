import assert from "node:assert/strict";
import test from "node:test";
import { audioClockAdvanced } from "../src/audio-clock-health.js";

test("accepts a running AudioContext clock that actually advances", async () => {
  const context = { state: "running", currentTime: 4 };
  const result = await audioClockAdvanced(context, { wait: async () => { context.currentTime = 4.12; } });
  assert.equal(result, true);
});

test("detects WebKit-style running state with a stalled currentTime", async () => {
  const context = { state: "running", currentTime: 4 };
  assert.equal(await audioClockAdvanced(context, { wait: async () => {} }), false);
});

test("treats a state interruption during the probe as unhealthy", async () => {
  const context = { state: "running", currentTime: 4 };
  const result = await audioClockAdvanced(context, { wait: async () => {
    context.currentTime = 4.12;
    context.state = "interrupted";
  } });
  assert.equal(result, false);
});
