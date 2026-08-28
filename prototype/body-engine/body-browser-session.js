import { BodyBrowserSessionError } from "./body-browser-errors.js";

export const BODY_MIC_CONSTRAINTS = Object.freeze({
  audio: Object.freeze({
    channelCount: Object.freeze({ ideal: 1 }),
    echoCancellation: Object.freeze({ ideal: false }),
    noiseSuppression: Object.freeze({ ideal: false }),
    autoGainControl: Object.freeze({ ideal: false })
  }),
  video: false
});

const MACROS = new Set(["size", "decay", "body", "dry", "drive"]);

/**
 * Browser microphone lifecycle without UI or automatic recording.
 * Call start() only from a user gesture handler.
 */
export class BodyBrowserSession {
  constructor({
    audioContext,
    mediaDevices,
    AudioWorkletNodeClass,
    workletUrl = "./body-worklet-processor.js",
    onLevels = null
  }) {
    if (!audioContext?.audioWorklet || typeof audioContext.resume !== "function") {
      throw new TypeError("audioContext with AudioWorklet is required");
    }
    if (typeof mediaDevices?.getUserMedia !== "function") {
      throw new TypeError("mediaDevices.getUserMedia is required");
    }
    if (typeof AudioWorkletNodeClass !== "function") {
      throw new TypeError("AudioWorkletNode constructor is required");
    }
    if (onLevels !== null && typeof onLevels !== "function") {
      throw new TypeError("onLevels must be a function or null");
    }

    this.audioContext = audioContext;
    this.mediaDevices = mediaDevices;
    this.AudioWorkletNodeClass = AudioWorkletNodeClass;
    this.workletUrl = workletUrl;
    this.onLevels = onLevels;
    this.state = "idle";
    this.monitoring = false;
  }

  async start() {
    if (this.state !== "idle" && this.state !== "stopped") {
      throw new Error(`cannot start session from state: ${this.state}`);
    }
    this.state = "starting";
    let stream = null;
    let phase = "resume";

    try {
      await this.audioContext.resume();
      phase = "worklet";
      await this.audioContext.audioWorklet.addModule(this.workletUrl);
      phase = "microphone";
      stream = await this.mediaDevices.getUserMedia(BODY_MIC_CONSTRAINTS);
      phase = "graph";
      const track = stream.getAudioTracks()[0];
      if (!track) throw new Error("microphone stream has no audio track");

      const source = this.audioContext.createMediaStreamSource(stream);
      const bodyNode = new this.AudioWorkletNodeClass(this.audioContext, "soma-body", {
        channelCount: 1,
        channelCountMode: "explicit",
        outputChannelCount: [1]
      });
      if (this.onLevels && bodyNode.port) {
        bodyNode.port.onmessage = (event) => {
          if (event.data?.type === "levels") this.onLevels(event.data);
        };
      }

      source.connect(bodyNode);
      const gate = bodyNode.parameters.get("gate");
      if (!gate) throw new Error("soma-body gate parameter is missing");
      gate.setValueAtTime(0, this.audioContext.currentTime);

      this.stream = stream;
      this.track = track;
      this.source = source;
      this.bodyNode = bodyNode;
      this.monitoring = false;
      this.state = "ready";

      return this.diagnostics();
    } catch (error) {
      if (stream) {
        for (const track of stream.getTracks()) track.stop();
      }
      this.state = "failed";
      throw new BodyBrowserSessionError(phase, error);
    }
  }

  diagnostics() {
    return {
      state: this.state,
      monitoring: this.monitoring,
      requested: BODY_MIC_CONSTRAINTS.audio,
      supported: typeof this.mediaDevices.getSupportedConstraints === "function"
        ? this.mediaDevices.getSupportedConstraints()
        : null,
      actual: this.track && typeof this.track.getSettings === "function"
        ? this.track.getSettings()
        : null,
      audioContext: {
        state: this.audioContext.state,
        sampleRate: this.audioContext.sampleRate,
        baseLatency: Number.isFinite(this.audioContext.baseLatency)
          ? this.audioContext.baseLatency
          : null,
        outputLatency: Number.isFinite(this.audioContext.outputLatency)
          ? this.audioContext.outputLatency
          : null
      }
    };
  }

  setMonitoring(enabled) {
    this.#requireReady();
    const next = Boolean(enabled);
    if (next === this.monitoring) return;
    if (next) this.bodyNode.connect(this.audioContext.destination);
    else this.bodyNode.disconnect(this.audioContext.destination);
    this.monitoring = next;
  }

  setGate(open, when = this.audioContext.currentTime) {
    this.#requireReady();
    const gate = this.bodyNode.parameters.get("gate");
    gate.cancelScheduledValues(when);
    gate.setValueAtTime(open ? 1 : 0, when);
  }

  setMacro(name, value, when = this.audioContext.currentTime) {
    this.#requireReady();
    if (!MACROS.has(name)) throw new Error(`unknown BODY macro: ${name}`);
    if (!Number.isFinite(value)) throw new TypeError("macro value must be finite");
    const parameter = this.bodyNode.parameters.get(name);
    if (!parameter) throw new Error(`soma-body parameter is missing: ${name}`);
    parameter.setValueAtTime(value, when);
  }

  stop() {
    if (this.state === "stopped" || this.state === "idle") return;
    if (this.bodyNode) {
      if (this.bodyNode.port) this.bodyNode.port.onmessage = null;
      try { this.bodyNode.disconnect(); } catch {}
    }
    if (this.source) {
      try { this.source.disconnect(); } catch {}
    }
    if (this.stream) {
      for (const track of this.stream.getTracks()) track.stop();
    }
    this.monitoring = false;
    this.state = "stopped";
  }

  #requireReady() {
    if (this.state !== "ready") throw new Error(`session is not ready: ${this.state}`);
  }
}

export function createBodyBrowserSession(options) {
  return new BodyBrowserSession(options);
}
