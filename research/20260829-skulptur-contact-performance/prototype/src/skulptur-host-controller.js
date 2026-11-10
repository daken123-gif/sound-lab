import { normalizeScheduledTouchBatch } from "./scheduled-touch-queue.js";

const clamp = (value, min, max) => Math.min(max, Math.max(min, value));

export class SkulpturHostController {
  static async create(audioContext, {
    workletUrl = new URL("./skulptur-filter-bank.worklet.js", import.meta.url),
    audioWorkletNodeClass = globalThis.AudioWorkletNode,
    channels = 2,
    order = 4,
    loopDurationSeconds = 4,
    processorOptions = {}
  } = {}) {
    if (!audioContext?.audioWorklet?.addModule) {
      throw new TypeError("an AudioContext with audioWorklet support is required");
    }
    if (!audioWorkletNodeClass) throw new TypeError("AudioWorkletNode is unavailable");
    await audioContext.audioWorklet.addModule(workletUrl);
    const node = new audioWorkletNodeClass(audioContext, "skulptur-filter-bank", {
      numberOfInputs: 5,
      numberOfOutputs: 1,
      outputChannelCount: [channels],
      processorOptions: {
        channels,
        order,
        loopDurationSeconds,
        ...processorOptions
      }
    });
    return new SkulpturHostController(audioContext, node);
  }

  constructor(audioContext, node) {
    this.audioContext = audioContext;
    this.node = node;
    this.inputNodes = [];
    this.outputNode = null;
    this.onControlFrame = null;
    this.pendingStateRequests = new Map();
    this.nextRequestId = 1;
    this.disposed = false;
    this.node.port.onmessage = ({ data }) => this.#receive(data);
  }

  attach({ loops, drum = null, output = null }) {
    if (!Array.isArray(loops) || loops.length !== 4) {
      throw new RangeError("Skulptur requires exactly four loop inputs");
    }
    this.detachInputs();
    loops.forEach((source, track) => this.#connectInput(source, track));
    this.#connectInput(drum, 4);
    if (output) this.connectOutput(output);
  }

  detachInputs() {
    for (const source of this.inputNodes) {
      try { source.disconnect(this.node); } catch { /* already disconnected */ }
    }
    this.inputNodes = [];
  }

  connectOutput(destination) {
    if (!destination?.connect && destination !== this.audioContext?.destination) {
      throw new TypeError("an AudioNode destination is required");
    }
    this.disconnectOutput();
    this.node.connect(destination);
    this.outputNode = destination;
  }

  disconnectOutput() {
    if (!this.outputNode) return;
    try { this.node.disconnect(this.outputNode); } catch { /* already disconnected */ }
    this.outputNode = null;
  }

  setTransport({ running, phase, loopDurationSeconds } = {}) {
    this.#post({ type: "transport", running, phase, loopDurationSeconds });
  }

  beginTouch({ pointerId, band, position, timeSeconds = this.audioContext.currentTime }) {
    this.#post({ type: "touch-begin", pointerId, band, position, timeSeconds });
  }

  moveTouch({ pointerId, band, position, timeSeconds = this.audioContext.currentTime }) {
    this.#post({ type: "touch-move", pointerId, band, position, timeSeconds });
  }

  endTouch(pointerId, { throwMotion = true } = {}) {
    this.#post({ type: "touch-end", pointerId, throwMotion });
  }

  scheduleTouches(scheduleId, commands) {
    const batch = normalizeScheduledTouchBatch(scheduleId, commands);
    this.#post({ type: "touch-schedule", ...batch });
    return batch.commands.length;
  }

  cancelScheduledTouches(scheduleId) {
    if (typeof scheduleId !== "string" || scheduleId.length < 1 || scheduleId.length > 80) {
      throw new TypeError("scheduleId must contain 1 to 80 characters");
    }
    this.#post({ type: "touch-schedule-cancel", scheduleId });
  }

  setRecording(enabled) {
    this.#post({ type: "gesture-record", enabled: Boolean(enabled) });
  }

  setFlow({ enabled, depth = 0.72, periodSeconds = 2, bandPhase = 0.08 } = {}) {
    this.#post({ type: "flow", enabled: Boolean(enabled), depth, periodSeconds, bandPhase });
  }

  clearPerformance() {
    this.#post({ type: "gesture-clear" });
    this.#post({ type: "clear-motion" });
  }

  setTrackState(track, { gain, muted } = {}) {
    if (!Number.isInteger(track) || track < 0 || track > 3) {
      throw new RangeError("track index must be 0..3");
    }
    this.#post({ type: "track-state", track, gain, muted });
  }

  setDrumGain(gain) {
    this.#post({ type: "drum-gain", gain: clamp(Number(gain), 0, 2) });
  }

  loadGestureState(state) {
    this.#post({ type: "gesture-load", state });
  }

  dumpGestureState({ timeoutMs = 1000 } = {}) {
    const requestId = this.nextRequestId++;
    return new Promise((resolve, reject) => {
      const timeout = setTimeout(() => {
        this.pendingStateRequests.delete(requestId);
        reject(new Error("gesture state request timed out"));
      }, timeoutMs);
      this.pendingStateRequests.set(requestId, { resolve, reject, timeout });
      this.#post({ type: "gesture-dump", requestId });
    });
  }

  dispose() {
    if (this.disposed) return;
    this.detachInputs();
    this.disconnectOutput();
    for (const { reject, timeout } of this.pendingStateRequests.values()) {
      clearTimeout(timeout);
      reject(new Error("SkulpturHostController was disposed"));
    }
    this.pendingStateRequests.clear();
    this.node.port.onmessage = null;
    this.disposed = true;
  }

  #connectInput(source, inputIndex) {
    if (!source) return;
    if (typeof source.connect !== "function") throw new TypeError("input must be an AudioNode");
    source.connect(this.node, 0, inputIndex);
    this.inputNodes.push(source);
  }

  #post(message) {
    if (this.disposed) throw new Error("SkulpturHostController is disposed");
    const compact = Object.fromEntries(Object.entries(message).filter(([, value]) => value !== undefined));
    this.node.port.postMessage(compact);
  }

  #receive(data) {
    if (data?.type === "control-frame") {
      this.onControlFrame?.(data);
      return;
    }
    if (data?.type !== "gesture-state") return;
    const pending = this.pendingStateRequests.get(data.requestId);
    if (!pending) return;
    clearTimeout(pending.timeout);
    this.pendingStateRequests.delete(data.requestId);
    pending.resolve(data.state);
  }
}
