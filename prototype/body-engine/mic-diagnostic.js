import { createBodyBrowserSession } from "./body-browser-session.js";
import { classifyBodyBrowserFailure } from "./body-browser-errors.js";
import { BodyLevelWatchdog } from "./body-level-watchdog.js";

const startButton = document.querySelector("#start");
const stopButton = document.querySelector("#stop");
const monitor = document.querySelector("#monitor");
const gate = document.querySelector("#gate");
const status = document.querySelector("#status");
const levels = document.querySelector("#levels");
const macros = ["size", "decay", "body"].map((name) => ({
  name,
  input: document.querySelector(`#${name}`),
  output: document.querySelector(`#${name}-value`)
}));

let session = null;
let audioContext = null;
let starting = false;
let gateOpen = false;
let levelWatchTimer = null;
const levelWatchdog = new BodyLevelWatchdog(2000);

function toDbfs(value) {
  if (!Number.isFinite(value) || value <= 0) return "−∞";
  return Math.max(-96, 20 * Math.log10(value)).toFixed(1);
}

function showLevels(report) {
  levelWatchdog.mark(performance.now());
  levels.textContent = `INPUT ${toDbfs(report.inputRms)} dBFS / BODY ${toDbfs(report.outputRms)} dBFS`;
}

function startLevelWatch() {
  levelWatchdog.start(performance.now());
  clearInterval(levelWatchTimer);
  levelWatchTimer = setInterval(() => {
    const state = levelWatchdog.state(performance.now());
    if (state === "stalled") levels.textContent = "INPUT／BODY レベル報告なし";
  }, 500);
}

function stopLevelWatch() {
  clearInterval(levelWatchTimer);
  levelWatchTimer = null;
  levelWatchdog.reset();
}

function setControlsReady(ready) {
  stopButton.disabled = !ready;
  monitor.disabled = !ready;
  gate.disabled = !ready;
  for (const macro of macros) macro.input.disabled = !ready;
}

function sanitizedDiagnostics(diagnostics) {
  const actual = diagnostics.actual ? { ...diagnostics.actual } : null;
  if (actual) {
    delete actual.deviceId;
    delete actual.groupId;
  }
  return { ...diagnostics, actual };
}

function showDiagnostics(diagnostics) {
  status.textContent = JSON.stringify(sanitizedDiagnostics(diagnostics), null, 2);
}

function showError(error) {
  const report = classifyBodyBrowserFailure(error, { secureContext: window.isSecureContext });
  status.textContent = JSON.stringify(report, null, 2);
}

function unavailableError(name, message) {
  const error = new Error(message);
  error.name = name;
  return error;
}

function closeGate() {
  if (!gateOpen) return;
  gateOpen = false;
  gate.dataset.open = "false";
  if (session?.state === "ready") session.setGate(false);
}

function openGate(event) {
  if (session?.state !== "ready" || gateOpen) return;
  event.preventDefault();
  if (typeof gate.setPointerCapture === "function") gate.setPointerCapture(event.pointerId);
  gateOpen = true;
  gate.dataset.open = "true";
  session.setGate(true);
}

async function stopSession() {
  stopLevelWatch();
  closeGate();
  monitor.checked = false;
  session?.stop();
  session = null;
  setControlsReady(false);
  startButton.disabled = false;
  if (audioContext && audioContext.state !== "closed") await audioContext.close();
  audioContext = null;
  levels.textContent = "INPUT -- dBFS / BODY -- dBFS";
  status.textContent = "stopped — マイクトラックと音声出力を停止しました。";
}

startButton.addEventListener("click", async () => {
  if (starting || session?.state === "ready") return;
  starting = true;
  startButton.disabled = true;
  status.textContent = "starting — マイク許可とAudioWorkletを確認中…";

  try {
    const AudioContextClass = window.AudioContext || window.webkitAudioContext;
    if (!AudioContextClass) throw unavailableError("AudioContextUnavailableError", "Web Audio API is not available");
    if (!navigator.mediaDevices?.getUserMedia) throw unavailableError("MediaDevicesUnavailableError", "getUserMedia is not available; HTTPSで開いてください");
    if (!window.AudioWorkletNode) throw unavailableError("AudioWorkletUnavailableError", "AudioWorkletNode is not available");

    audioContext = new AudioContextClass({ latencyHint: "interactive" });
    session = createBodyBrowserSession({
      audioContext,
      mediaDevices: navigator.mediaDevices,
      AudioWorkletNodeClass: window.AudioWorkletNode,
      workletUrl: new URL("./body-worklet-processor.js", import.meta.url).href,
      onLevels: showLevels
    });

    const diagnostics = await session.start();
    for (const macro of macros) session.setMacro(macro.name, Number(macro.input.value));
    setControlsReady(true);
    startLevelWatch();
    showDiagnostics(diagnostics);
  } catch (error) {
    stopLevelWatch();
    session?.stop();
    session = null;
    if (audioContext && audioContext.state !== "closed") await audioContext.close();
    audioContext = null;
    startButton.disabled = false;
    showError(error);
  } finally {
    starting = false;
  }
});

stopButton.addEventListener("click", () => {
  stopSession().catch(showError);
});

monitor.addEventListener("change", () => {
  if (session?.state !== "ready") return;
  session.setMonitoring(monitor.checked);
  showDiagnostics(session.diagnostics());
});

gate.addEventListener("pointerdown", openGate);
gate.addEventListener("pointerup", closeGate);
gate.addEventListener("pointercancel", closeGate);
gate.addEventListener("lostpointercapture", closeGate);
window.addEventListener("blur", closeGate);
window.addEventListener("pagehide", closeGate);

for (const macro of macros) {
  macro.input.addEventListener("input", () => {
    macro.output.value = macro.input.value;
    if (session?.state === "ready") session.setMacro(macro.name, Number(macro.input.value));
  });
}
