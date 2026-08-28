import { createBodyBrowserSession } from "./body-browser-session.js";

const startButton = document.querySelector("#start");
const stopButton = document.querySelector("#stop");
const monitor = document.querySelector("#monitor");
const gate = document.querySelector("#gate");
const status = document.querySelector("#status");
const macros = ["size", "decay", "body"].map((name) => ({
  name,
  input: document.querySelector(`#${name}`),
  output: document.querySelector(`#${name}-value`)
}));

let session = null;
let audioContext = null;
let starting = false;
let gateOpen = false;

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
  const name = error instanceof Error ? error.name : "Error";
  const message = error instanceof Error ? error.message : String(error);
  status.textContent = `${name}: ${message}`;
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
  closeGate();
  monitor.checked = false;
  session?.stop();
  session = null;
  setControlsReady(false);
  startButton.disabled = false;
  if (audioContext && audioContext.state !== "closed") await audioContext.close();
  audioContext = null;
  status.textContent = "stopped — マイクトラックと音声出力を停止しました。";
}

startButton.addEventListener("click", async () => {
  if (starting || session?.state === "ready") return;
  starting = true;
  startButton.disabled = true;
  status.textContent = "starting — マイク許可とAudioWorkletを確認中…";

  try {
    const AudioContextClass = window.AudioContext || window.webkitAudioContext;
    if (!AudioContextClass) throw new Error("Web Audio API is not available");
    if (!navigator.mediaDevices?.getUserMedia) throw new Error("getUserMedia is not available; HTTPSで開いてください");
    if (!window.AudioWorkletNode) throw new Error("AudioWorkletNode is not available");

    audioContext = new AudioContextClass({ latencyHint: "interactive" });
    session = createBodyBrowserSession({
      audioContext,
      mediaDevices: navigator.mediaDevices,
      AudioWorkletNodeClass: window.AudioWorkletNode,
      workletUrl: new URL("./body-worklet-processor.js", import.meta.url).href
    });

    const diagnostics = await session.start();
    for (const macro of macros) session.setMacro(macro.name, Number(macro.input.value));
    setControlsReady(true);
    showDiagnostics(diagnostics);
  } catch (error) {
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
