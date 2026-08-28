import { FourTrackSpectralMixer } from "./four-track-spectral-mixer.js";
import { SpectralControlEngine } from "./spectral-control-engine.js";
import { SpectralGestureLoop } from "./spectral-gesture-loop.js";
import {
  composeFeedback,
  SpectralSurfaceControl
} from "./spectral-surface-control.js";

class SkulpturFilterBankProcessor extends AudioWorkletProcessor {
  constructor(options) {
    super();
    const processorOptions = options.processorOptions ?? {};
    this.mixer = new FourTrackSpectralMixer({
      sampleRate,
      channels: processorOptions.channels ?? 2,
      order: processorOptions.order ?? 4,
      loopBusTrim: processorOptions.loopBusTrim ?? 0.7,
      drumBusGain: processorOptions.drumBusGain ?? 0.9,
      outputCeiling: processorOptions.outputCeiling ?? 0.98,
      filterOptions: {
        edges: processorOptions.edges,
        feedbackLoopGain: processorOptions.feedbackLoopGain,
        feedbackDrive: processorOptions.feedbackDrive
      }
    });
    this.controls = new SpectralControlEngine();
    this.gestureLoop = new SpectralGestureLoop();
    this.feedbackGestureLoop = new SpectralGestureLoop();
    this.surface = new SpectralSurfaceControl();
    this.feedbackBase = new Array(10).fill(0);
    this.loopDurationSeconds = Math.max(0.05, processorOptions.loopDurationSeconds ?? 4);
    this.loopPhase = 0;
    this.transportRunning = false;
    this.telemetryElapsed = 0;
    this.telemetryIntervalSeconds = 1 / 30;

    this.port.onmessage = ({ data }) => {
      if (data?.type === "reset") this.mixer.reset();
      if (data?.type === "touch-begin") {
        const position = data.position ?? Number(data.value) / 2;
        const mapped = this.surface.beginTouch(data.pointerId, data.band, position);
        this.controls.beginTouch(data.pointerId, data.band, mapped.gain, data.timeSeconds);
      }
      if (data?.type === "touch-move") {
        const position = data.position ?? Number(data.value) / 2;
        const mapped = this.surface.moveTouch(data.pointerId, data.band, position);
        this.controls.moveTouch(data.pointerId, data.band, mapped.gain, data.timeSeconds);
      }
      if (data?.type === "touch-end") {
        this.surface.endTouch(data.pointerId);
        this.controls.endTouch(data.pointerId, { throwMotion: data.throwMotion !== false });
      }
      if (data?.type === "flow") this.controls.setFlow(data);
      if (data?.type === "clear-motion") this.controls.clearMotion();
      if (data?.type === "transport") {
        if (data.loopDurationSeconds !== undefined) {
          this.loopDurationSeconds = Math.max(0.05, data.loopDurationSeconds);
        }
        if (data.phase !== undefined) this.loopPhase = ((data.phase % 1) + 1) % 1;
        if (data.running !== undefined) this.transportRunning = Boolean(data.running);
      }
      if (data?.type === "gesture-record") {
        if (data.enabled) {
          this.gestureLoop.startRecording();
          this.feedbackGestureLoop.startRecording();
        } else {
          this.gestureLoop.stopRecording();
          this.feedbackGestureLoop.stopRecording();
        }
      }
      if (data?.type === "gesture-clear") {
        this.gestureLoop.clear(data.band);
        this.feedbackGestureLoop.clear(data.band);
      }
      if (data?.type === "gesture-load") {
        if (data.state?.version === 2) {
          this.gestureLoop.deserialize(data.state.gain);
          this.feedbackGestureLoop.deserialize(data.state.feedback);
        } else {
          this.gestureLoop.deserialize(data.state);
          this.feedbackGestureLoop.clear();
        }
      }
      if (data?.type === "gesture-dump") {
        this.port.postMessage({
          type: "gesture-state",
          requestId: data.requestId,
          state: {
            version: 2,
            gain: this.gestureLoop.serialize(),
            feedback: this.feedbackGestureLoop.serialize()
          }
        });
      }
      if (data?.type === "track-state") {
        this.mixer.setTrack(data.track, { gain: data.gain, muted: data.muted });
      }
      if (data?.type === "drum-gain") this.mixer.setDrumBusGain(data.gain);
      if (data?.type === "feedback") {
        if (data.values) this.feedbackBase = Array.from(data.values);
        else this.feedbackBase[data.band] = data.value;
      }
    };
  }

  process(inputs, outputs) {
    const output = outputs[0];
    if (!output?.length) return true;

    const frameCount = output[0].length;
    const toChannels = input => {
      if (!input?.length) return null;
      return Array.from({ length: this.mixer.channels }, (_, index) =>
        input[Math.min(index, input.length - 1)] ?? new Float32Array(frameCount)
      );
    };
    const loopTracks = Array.from({ length: 4 }, (_, track) => toChannels(inputs[track]));
    const drums = toChannels(inputs[4]);
    if (![...loopTracks, drums].some(Boolean)) return true;
    const blockSeconds = output[0].length / sampleRate;
    if (this.gestureLoop.recording && this.transportRunning) {
      const gains = this.controls.manualSnapshot();
      const feedback = this.surface.feedbackSnapshot();
      gains.forEach((value, band) => {
        if (value !== null) {
          this.gestureLoop.capture(band, value, this.loopPhase);
          this.feedbackGestureLoop.capture(band, feedback[band] ?? 0, this.loopPhase);
        }
      });
    }
    this.controls.setRecordedValues(this.gestureLoop.valuesAt(this.loopPhase));
    const manualFeedback = this.surface.feedbackSnapshot();
    const feedback = composeFeedback(
      this.feedbackBase,
      this.feedbackGestureLoop.valuesAt(this.loopPhase),
      manualFeedback
    );
    this.mixer.spectral.setFeedbackBands(feedback);
    const gains = this.controls.update(blockSeconds);
    this.mixer.spectral.setBands(gains);
    this.mixer.spectral.setActive(this.controls.isActive || this.mixer.spectral.hasFeedback);
    const rendered = this.mixer.process(loopTracks, drums);

    for (let channel = 0; channel < output.length; channel += 1) {
      output[channel].set(rendered[Math.min(channel, rendered.length - 1)]);
    }
    if (this.transportRunning) {
      this.loopPhase = (this.loopPhase + blockSeconds / this.loopDurationSeconds) % 1;
    }
    this.telemetryElapsed += blockSeconds;
    if (this.telemetryElapsed >= this.telemetryIntervalSeconds) {
      this.telemetryElapsed %= this.telemetryIntervalSeconds;
      this.port.postMessage({
        type: "control-frame",
        phase: this.loopPhase,
        gains: Array.from(gains),
        feedback,
        sources: Array.from({ length: 10 }, (_, band) => this.controls.sourceAt(band))
      });
    }
    return true;
  }
}

registerProcessor("skulptur-filter-bank", SkulpturFilterBankProcessor);
