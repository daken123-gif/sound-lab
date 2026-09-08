import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";

const read = path => readFile(new URL(path, import.meta.url), "utf8");

test("the demo exposes explicit start, record, take, flow, and clear controls", async () => {
  const html = await read("../demo/index.html");
  for (const id of ["start", "record", "take", "flow", "clear", "surface"]) {
    assert.match(html, new RegExp(`id="${id}"`));
  }
  assert.match(html, /<script type="module"/);
});

test("one TAKE control records, replays, and safely stops contact frames", async () => {
  const source = await read("../demo/app.js");
  assert.match(source, /new ContactPerformanceTakeRecorder\(\)/);
  assert.match(source, /new ContactPerformanceTakePlayer/);
  assert.match(source, /takePlayer\.start\(lastContactTake/);
  assert.match(source, /takePlayer\.stop\(performance\.now\(\)\)/);
  assert.match(source, /if \(takeRecorder\) takeRecorder\.capture\(frame\)/);
  assert.match(source, /document\.addEventListener\("visibilitychange"/);
  assert.match(source, /画面が隠れたためTAKE再生を停止/);
});

test("TAKE audio uses the same replay frames on the AudioContext clock", async () => {
  const source = await read("../demo/app.js");
  assert.match(source, /onFrame: renderReplayedContactFrame/);
  assert.match(source, /onSchedule: scheduleReplayedContactFrames/);
  assert.match(source, /controller\.scheduleTouches\(takeAudioScheduleId, commands\)/);
  assert.match(source, /controller\.cancelScheduledTouches\(takeAudioScheduleId\)/);
  assert.match(source, /TAKE_AUDIO_LOOKAHEAD_SECONDS/);
  assert.match(source, /TAKE再生失敗/);
});

test("the existing start control resumes an iOS-suspended audio context", async () => {
  const source = await read("../demo/app.js");
  assert.match(source, /audioContext\.addEventListener\("statechange"/);
  assert.match(source, /startButton\.textContent = running \? "STOP" : "RESUME"/);
  assert.match(source, /if \(audioContext\?\.state !== "running" \|\| audioRecoveryRequired\) return resumeAudio\(\)/);
  assert.match(source, /audioContext\.removeEventListener\("statechange"/);
  assert.match(source, /verifyAudioClockAfterVisibility/);
  assert.match(source, /if \(context\.state === "running"\) await context\.suspend\(\)/);
  assert.match(source, /音響時計が停止中/);
});

test("the demo connects four loops and one independent drum input", async () => {
  const source = await read("../demo/app.js");
  assert.match(source, /controller\.attach\(\{ loops: inputBuses\.slice\(0, 4\), drum: inputBuses\[4\]/);
  assert.match(source, /SkulpturHostController\.create/);
});

test("audio starts only from the explicit start control", async () => {
  const source = await read("../demo/app.js");
  assert.match(source, /startButton\.addEventListener\("click"/);
  assert.doesNotMatch(source, /getUserMedia/);
  assert.doesNotMatch(source, /^startAudio\(\);/m);
});

test("the surface renders control frames returned by the audio worklet", async () => {
  const source = await read("../demo/app.js");
  assert.match(source, /controller\.onControlFrame = renderControlFrame/);
  assert.match(source, /surfacePositionFromValues/);
});

test("four explicit loop slots load files without opening the microphone", async () => {
  const html = await read("../demo/index.html");
  const source = await read("../demo/app.js");
  assert.equal((html.match(/class="bus loop-slot"/g) ?? []).length, 4);
  assert.match(html, /id="audio-file"[^>]+accept="audio\/\*"/);
  assert.match(source, /decodeAudioData/);
  assert.match(source, /fitAudioBufferToLoop/);
  assert.doesNotMatch(source, /getUserMedia/);
});

test("loaded loops replace one track on the current transport phase with a crossfade", async () => {
  const source = await read("../demo/app.js");
  assert.match(source, /lastPhase \* LOOP_SECONDS/);
  assert.match(source, /linearRampToValueAtTime\(1, fadeEnd\)/);
  assert.match(source, /linearRampToValueAtTime\(0, fadeEnd\)/);
});

test("the performance surface drives drawing and audio from one contact frame", async () => {
  const source = await read("../demo/app.js");
  assert.match(source, /bindPointerContactSurface/);
  assert.match(source, /skulpturCommandFromContactFrame\(frame\)/);
  assert.match(source, /resolveTrackIds: \(\) => \[0, 1, 2, 3\]/);
  assert.doesNotMatch(source, /function pointFromEvent/);
});
