import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";

const html = readFileSync(new URL("../mic-test.html", import.meta.url), "utf8");
const script = readFileSync(new URL("../mic-diagnostic.js", import.meta.url), "utf8");

test("mic diagnostic exposes only the intended controls", () => {
  for (const id of ["start", "stop", "monitor", "gate", "size", "decay", "body", "levels", "status"]) {
    assert.match(html, new RegExp(`id=["']${id}["']`));
  }
  assert.match(html, /MIC START/);
  assert.match(html, /HOLD VOICE GATE/);
  assert.doesNotMatch(html + script, /MediaRecorder/);
  assert.doesNotMatch(html, /autoplay/i);
});

test("voice gate closes on every pointer or page interruption", () => {
  for (const eventName of ["pointerdown", "pointerup", "pointercancel", "lostpointercapture", "blur", "pagehide"]) {
    assert.match(script, new RegExp(`["']${eventName}["']`));
  }
  assert.match(script, /setGate\(true\)/);
  assert.match(script, /setGate\(false\)/);
});

test("microphone and output require separate explicit actions", () => {
  assert.match(script, /startButton\.addEventListener\(["']click["']/);
  assert.match(script, /monitor\.addEventListener\(["']change["']/);
  assert.match(script, /setMonitoring\(monitor\.checked\)/);
  assert.match(script, /new AudioContextClass\(\{ latencyHint: ["']interactive["'] \}\)/);
});

test("diagnostics omit persistent device identifiers", () => {
  assert.match(script, /delete actual\.deviceId/);
  assert.match(script, /delete actual\.groupId/);
});

test("diagnostic shows numeric input and BODY levels without a waveform", () => {
  assert.match(html, /INPUT -- dBFS \/ BODY -- dBFS/);
  assert.match(script, /onLevels: showLevels/);
  assert.doesNotMatch(html, /canvas/i);
});

test("diagnostic reports a stalled AudioWorklet without enabling monitoring", () => {
  assert.match(script, /BodyLevelWatchdog\(2000\)/);
  assert.match(script, /INPUT／BODY レベル報告なし/);
  assert.doesNotMatch(script, /setMonitoring\(true\)/);
});

test("diagnostic renders structured browser failure codes", () => {
  assert.match(script, /classifyBodyBrowserFailure/);
  assert.match(script, /secureContext: window\.isSecureContext/);
  assert.match(script, /MediaDevicesUnavailableError/);
  assert.match(script, /AudioWorkletUnavailableError/);
});
