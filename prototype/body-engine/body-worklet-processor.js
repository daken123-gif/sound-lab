import { BodyRealtimeCore } from "./body-realtime-core.js";
import { BodyLevelMeter } from "./body-level-meter.js";

class SomaBodyProcessor extends AudioWorkletProcessor {
  static get parameterDescriptors() {
    return [
      { name: "size", defaultValue: 0.5, minValue: 0, maxValue: 1, automationRate: "k-rate" },
      { name: "decay", defaultValue: 0.45, minValue: 0, maxValue: 1, automationRate: "k-rate" },
      { name: "body", defaultValue: 0.65, minValue: 0, maxValue: 1, automationRate: "k-rate" },
      { name: "dry", defaultValue: 0.12, minValue: 0, maxValue: 1, automationRate: "k-rate" },
      { name: "drive", defaultValue: 0.7, minValue: 0.25, maxValue: 6, automationRate: "k-rate" },
      { name: "gate", defaultValue: 0, minValue: 0, maxValue: 1, automationRate: "a-rate" }
    ];
  }

  constructor() {
    super();
    this.core = new BodyRealtimeCore(sampleRate);
    this.levelMeter = new BodyLevelMeter(2048);
    this.monoInput = new Float32Array(0);
  }

  process(inputs, outputs, parameters) {
    const outputChannels = outputs[0];
    if (!outputChannels || outputChannels.length === 0) return true;

    const frames = outputChannels[0].length;
    if (this.monoInput.length !== frames) this.monoInput = new Float32Array(frames);
    this.monoInput.fill(0);

    const inputChannels = inputs[0] ?? [];
    for (const channel of inputChannels) {
      const limit = Math.min(frames, channel.length);
      for (let index = 0; index < limit; index += 1) {
        this.monoInput[index] += channel[index];
      }
    }
    if (inputChannels.length > 1) {
      const scale = 1 / inputChannels.length;
      for (let index = 0; index < frames; index += 1) this.monoInput[index] *= scale;
    }

    this.core.processBlock(this.monoInput, outputChannels[0], parameters);
    const levels = this.levelMeter.add(this.monoInput, outputChannels[0]);
    if (levels) this.port.postMessage(levels);
    for (let channel = 1; channel < outputChannels.length; channel += 1) {
      outputChannels[channel].set(outputChannels[0]);
    }
    return true;
  }
}

registerProcessor("soma-body", SomaBodyProcessor);
