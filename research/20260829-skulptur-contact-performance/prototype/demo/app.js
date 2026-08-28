import { surfacePositionFromValues } from "../src/spectral-surface-control.js";
import { SkulpturHostController } from "../src/skulptur-host-controller.js";
import { fitAudioBufferToLoop } from "../src/audio-loop-fit.js";
import { bindPointerContactSurface } from "../src/pointer-contact-adapter.js";
import { skulpturCommandFromContactFrame } from "../src/skulptur-contact-bridge.js";
import {
  ContactPerformanceTakePlayer,
  ContactPerformanceTakeRecorder
} from "../src/contact-performance-take.js";

const LOOP_SECONDS = 4;
const SAMPLE_RATE = 48000;

const startButton = document.querySelector("#start");
const recordButton = document.querySelector("#record");
const takeButton = document.querySelector("#take");
const flowButton = document.querySelector("#flow");
const clearButton = document.querySelector("#clear");
const status = document.querySelector("#status");
const progress = document.querySelector("#progress");
const surface = document.querySelector("#surface");
const bandsElement = document.querySelector("#bands");
const audioFileInput = document.querySelector("#audio-file");
const loopSlotButtons = [...document.querySelectorAll(".loop-slot")];

const bandElements = Array.from({ length: 10 }, (_, band) => {
  const element = document.createElement("div");
  element.className = "band";
  element.dataset.band = band;
  bandsElement.append(element);
  return element;
});

let audioContext = null;
let controller = null;
let inputBuses = [];
let sourceVoices = Array(5).fill(null);
let activeLoopBuffers = [];
let activeDrumBuffer = null;
let lastPhase = 0;
let pendingFileTrack = null;
let recording = false;
let flowing = false;
let takeRecorder = null;
let lastContactTake = null;
let takePlaySerial = 0;
let takeAnimationFrame = null;
const pointers = new Map();

const takePlayer = new ContactPerformanceTakePlayer({
  onFrame: performContactFrame,
  onFinish: () => {
    takeAnimationFrame = null;
    updateTakeButton();
    updateModeStatus();
  }
});

function setStatus(message) {
  status.textContent = message;
}

function setControlsEnabled(enabled) {
  recordButton.disabled = !enabled;
  takeButton.disabled = !enabled;
  flowButton.disabled = !enabled;
  clearButton.disabled = !enabled;
  surface.classList.toggle("disabled", !enabled);
  loopSlotButtons.forEach(button => button.disabled = !enabled);
}

function toggleButton(button, enabled) {
  button.setAttribute("aria-pressed", String(enabled));
}

function updateTakeButton() {
  if (takeRecorder) {
    takeButton.textContent = "TAKE STOP";
    toggleButton(takeButton, true);
    return;
  }
  if (takePlayer.isPlaying) {
    takeButton.textContent = "TAKE STOP";
    toggleButton(takeButton, true);
    return;
  }
  takeButton.textContent = lastContactTake ? "TAKE PLAY" : "TAKE";
  toggleButton(takeButton, false);
}

function runTakePlayback(timestampMs) {
  takeAnimationFrame = null;
  takePlayer.advance(timestampMs);
  if (takePlayer.isPlaying) takeAnimationFrame = requestAnimationFrame(runTakePlayback);
}

function stopTakePlayback() {
  if (!takePlayer.isPlaying) return;
  takePlayer.stop(performance.now());
  if (takeAnimationFrame !== null) cancelAnimationFrame(takeAnimationFrame);
  takeAnimationFrame = null;
  updateTakeButton();
}

function createDemoBuffers(context) {
  const frames = Math.round(LOOP_SECONDS * context.sampleRate);
  const loopBuffers = Array.from({ length: 4 }, () => context.createBuffer(1, frames, context.sampleRate));
  const drumBuffer = context.createBuffer(1, frames, context.sampleRate);
  const loops = loopBuffers.map(buffer => buffer.getChannelData(0));
  const drums = drumBuffer.getChannelData(0);
  let seed = 0x51f15e;
  const random = () => {
    seed ^= seed << 13;
    seed ^= seed >>> 17;
    seed ^= seed << 5;
    return ((seed >>> 0) / 0xffffffff) * 2 - 1;
  };

  for (let frame = 0; frame < frames; frame += 1) {
    const time = frame / context.sampleRate;
    loops[0][frame] = 0.26 * Math.sin(2 * Math.PI * 145 * time) +
      0.11 * Math.sin(2 * Math.PI * 580 * time) +
      0.07 * Math.sin(2 * Math.PI * 1160 * time);
    loops[1][frame] = 0.25 * Math.sin(2 * Math.PI * 72.5 * time) *
      (0.7 + 0.3 * Math.sin(2 * Math.PI * 0.25 * time));
    loops[2][frame] = 0.075 * random() * (0.3 + 0.7 * Math.sin(2 * Math.PI * 0.2 * time) ** 2);
    const pluckEnvelope = Math.exp(-((time * 1.5) % 1) * 7);
    loops[3][frame] = 0.14 * pluckEnvelope * (
      Math.sin(2 * Math.PI * 435 * time) + 0.4 * Math.sin(2 * Math.PI * 870 * time)
    );

    const beatPhase = (time * 2) % 1;
    const kickEnvelope = Math.exp(-beatPhase * 18);
    const kick = Math.sin(2 * Math.PI * (48 + 70 * kickEnvelope) * time) * kickEnvelope;
    const hatEnvelope = Math.exp(-((time * 4) % 1) * 42);
    drums[frame] = 0.3 * kick + 0.045 * random() * hatEnvelope;
  }
  return { loopBuffers, drumBuffer };
}

function createLoopingSource(context, buffer) {
  const source = context.createBufferSource();
  source.buffer = buffer;
  source.loop = true;
  return source;
}

function startVoice(buffer, inputIndex, startTime, offset = 0, crossfade = false) {
  const oldVoice = sourceVoices[inputIndex];
  const source = createLoopingSource(audioContext, buffer);
  const gain = audioContext.createGain();
  source.connect(gain);
  gain.connect(inputBuses[inputIndex]);
  if (crossfade) {
    const fadeEnd = startTime + 0.035;
    gain.gain.setValueAtTime(0, startTime);
    gain.gain.linearRampToValueAtTime(1, fadeEnd);
    if (oldVoice) {
      oldVoice.gain.gain.cancelScheduledValues(startTime);
      oldVoice.gain.gain.setValueAtTime(oldVoice.gain.gain.value, startTime);
      oldVoice.gain.gain.linearRampToValueAtTime(0, fadeEnd);
      try { oldVoice.source.stop(fadeEnd + 0.01); } catch { /* already stopped */ }
    }
  } else {
    gain.gain.setValueAtTime(1, startTime);
  }
  source.start(startTime, offset);
  sourceVoices[inputIndex] = { source, gain };
}

function stopVoices() {
  sourceVoices.forEach(voice => {
    if (!voice) return;
    try { voice.source.stop(); } catch { /* already stopped */ }
    try { voice.source.disconnect(); } catch { /* already disconnected */ }
    try { voice.gain.disconnect(); } catch { /* already disconnected */ }
  });
  sourceVoices = Array(5).fill(null);
}

async function loadTrackFile(track, file) {
  if (!controller || !audioContext) return;
  setStatus(`LOOP ${track + 1} 読み込み中`);
  try {
    const decoded = await audioContext.decodeAudioData(await file.arrayBuffer());
    if (!controller || audioContext.state === "closed") return;
    const buffer = fitAudioBufferToLoop(audioContext, decoded, { durationSeconds: LOOP_SECONDS });
    activeLoopBuffers[track] = buffer;
    const startTime = audioContext.currentTime + 0.02;
    startVoice(buffer, track, startTime, lastPhase * LOOP_SECONDS, true);
    loopSlotButtons[track].classList.add("loaded");
    loopSlotButtons[track].title = file.name;
    setStatus(`LOOP ${track + 1}: ${file.name} — 先頭4秒`);
  } catch (error) {
    setStatus(`読込失敗: ${error.message}`);
  }
}

function updateModeStatus() {
  if (takeRecorder) setStatus("TAKE録音中 — 演奏後、指を離してSTOP");
  else if (takePlayer.isPlaying) setStatus("TAKE再生中 — 同じ接触frameで音と表示を再生");
  else if (recording && flowing) setStatus("REC + FLOW — 触れた帯域を上書き");
  else if (recording) setStatus("REC中 — 触れた帯域だけ記録");
  else if (flowing) setStatus("FLOW中 — 指が最優先");
  else setStatus("演奏可能");
}

function renderControlFrame(frame) {
  lastPhase = Math.max(0, Math.min(1, frame.phase));
  progress.style.width = `${lastPhase * 100}%`;
  const touchedBands = new Set([...pointers.values()].map(point => point.band));
  bandElements.forEach((element, band) => {
    if (touchedBands.has(band)) return;
    const source = frame.sources[band];
    if (source === "idle") {
      element.className = "band";
      delete element.dataset.source;
      return;
    }
    const position = surfacePositionFromValues(frame.gains[band], frame.feedback[band]);
    drawBand(band, position, source);
  });
}

async function startAudio() {
  startButton.disabled = true;
  setStatus("音響エンジン起動中");
  try {
    audioContext = new AudioContext({ latencyHint: "interactive", sampleRate: SAMPLE_RATE });
    controller = await SkulpturHostController.create(audioContext, {
      workletUrl: "../src/skulptur-filter-bank.worklet.js",
      channels: 2,
      order: 4,
      loopDurationSeconds: LOOP_SECONDS
    });
    controller.onControlFrame = renderControlFrame;
    const { loopBuffers, drumBuffer } = createDemoBuffers(audioContext);
    activeLoopBuffers = loopBuffers;
    activeDrumBuffer = drumBuffer;
    const transportStart = audioContext.currentTime + 0.06;
    inputBuses = Array.from({ length: 5 }, () => audioContext.createGain());
    controller.attach({ loops: inputBuses.slice(0, 4), drum: inputBuses[4], output: audioContext.destination });
    activeLoopBuffers.forEach((buffer, track) => startVoice(buffer, track, transportStart));
    startVoice(activeDrumBuffer, 4, transportStart);
    controller.setTransport({
      running: true,
      phase: 0,
      loopDurationSeconds: LOOP_SECONDS
    });
    await audioContext.resume();
    startButton.textContent = "STOP";
    startButton.classList.add("running");
    setControlsEnabled(true);
    setStatus("演奏可能");
  } catch (error) {
    setStatus(`起動失敗: ${error.message}`);
    await stopAudio();
  } finally {
    startButton.disabled = false;
  }
}

async function stopAudio() {
  stopTakePlayback();
  takeRecorder = null;
  pointers.clear();
  stopVoices();
  controller?.dispose();
  controller = null;
  inputBuses = [];
  activeLoopBuffers = [];
  activeDrumBuffer = null;
  lastPhase = 0;
  pendingFileTrack = null;
  if (audioContext && audioContext.state !== "closed") await audioContext.close();
  audioContext = null;
  recording = false;
  flowing = false;
  toggleButton(recordButton, false);
  toggleButton(flowButton, false);
  updateTakeButton();
  loopSlotButtons.forEach(button => {
    button.classList.remove("loaded");
    button.removeAttribute("title");
  });
  bandElements.forEach(element => element.className = "band");
  progress.style.width = "0";
  startButton.textContent = "DEMO START";
  startButton.classList.remove("running");
  setControlsEnabled(false);
  setStatus("停止中");
}

startButton.addEventListener("click", () => controller ? stopAudio() : startAudio());

recordButton.addEventListener("click", () => {
  recording = !recording;
  toggleButton(recordButton, recording);
  controller.setRecording(recording);
  updateModeStatus();
});

takeButton.addEventListener("click", () => {
  if (!controller) return;
  if (takeRecorder) {
    if (takeRecorder.activeGestureCount > 0) {
      setStatus("指を離してからTAKEを止めてください");
      return;
    }
    try {
      lastContactTake = takeRecorder.finish();
      takeRecorder = null;
      updateTakeButton();
      setStatus(`TAKE記録完了 — ${lastContactTake.frames.length} events`);
    } catch (error) {
      setStatus(`TAKE記録失敗: ${error.message}`);
    }
    return;
  }
  if (takePlayer.isPlaying) {
    stopTakePlayback();
    setStatus("TAKE再生を停止");
    return;
  }
  if (lastContactTake) {
    const startTimestampMs = performance.now();
    takePlayer.start(lastContactTake, {
      startTimestampMs,
      instanceId: `demo-${++takePlaySerial}`
    });
    updateTakeButton();
    updateModeStatus();
    runTakePlayback(startTimestampMs);
    return;
  }
  takeRecorder = new ContactPerformanceTakeRecorder();
  updateTakeButton();
  updateModeStatus();
});

flowButton.addEventListener("click", () => {
  flowing = !flowing;
  toggleButton(flowButton, flowing);
  controller.setFlow({
    enabled: flowing,
    depth: 0.72,
    periodSeconds: 2,
    bandPhase: 0.08
  });
  updateModeStatus();
});

clearButton.addEventListener("click", () => {
  stopTakePlayback();
  takeRecorder = null;
  lastContactTake = null;
  updateTakeButton();
  controller.clearPerformance();
  flowing = false;
  toggleButton(flowButton, false);
  setStatus("記録演奏を消去");
});

loopSlotButtons.forEach(button => button.addEventListener("click", () => {
  if (!controller) return;
  pendingFileTrack = Number(button.dataset.track);
  audioFileInput.value = "";
  audioFileInput.click();
}));

audioFileInput.addEventListener("change", () => {
  const file = audioFileInput.files?.[0];
  const track = pendingFileTrack;
  pendingFileTrack = null;
  if (file && Number.isInteger(track)) loadTrackFile(track, file);
});

function drawPointer(pointerId, band, position) {
  const previous = pointers.get(pointerId);
  pointers.set(pointerId, { band, position });
  if (previous && previous.band !== band && ![...pointers.values()].some(point => point.band === previous.band)) {
    bandElements[previous.band].className = "band";
  }
  drawBand(band, position, "touch");
}

function drawBand(band, position, source) {
  const element = bandElements[band];
  element.style.setProperty("--y", `${(1 - position) * 100}%`);
  const zone = position > 0.5 ? "feedback" : position < 0.5 ? "cut" : "neutral";
  element.className = `band active ${zone} source-${source}`;
  element.dataset.source = source;
}

function releasePointer(pointerId) {
  const previous = pointers.get(pointerId);
  pointers.delete(pointerId);
  if (previous && ![...pointers.values()].some(point => point.band === previous.band)) {
    bandElements[previous.band].className = "band";
  }
}

function performContactFrame(frame) {
  if (!controller || !audioContext) return;
  if (takeRecorder) takeRecorder.capture(frame);
  const command = skulpturCommandFromContactFrame(frame);
  if (command.type === "end") {
    releasePointer(command.pointerId);
    controller.endTouch(command.pointerId, { throwMotion: command.throwMotion });
    return;
  }
  drawPointer(command.pointerId, command.band, command.position);
  const payload = {
    pointerId: command.pointerId,
    band: command.band,
    position: command.position,
    timeSeconds: audioContext.currentTime
  };
  if (command.type === "begin") controller.beginTouch(payload);
  else controller.moveTouch(payload);
}

bindPointerContactSurface({
  surface,
  scope: window,
  resolveTrackIds: () => [0, 1, 2, 3],
  onFrame: performContactFrame,
  onError: error => setStatus(`接触入力エラー: ${error.message}`)
});

window.addEventListener("pagehide", () => stopAudio());

setControlsEnabled(false);
