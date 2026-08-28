import { BodyEngine } from "./body-engine.js";

function parameterValue(parameter, index, fallback) {
  if (!parameter || parameter.length === 0) return fallback;
  return parameter.length === 1 ? parameter[0] : parameter[index];
}

/**
 * Allocation-free block adapter for AudioWorklet and native callback tests.
 * The gate controls excitation only: resonator tails are allowed to decay.
 */
export class BodyRealtimeCore {
  constructor(sampleRate = 48000) {
    this.sampleRate = sampleRate;
    this.engine = new BodyEngine({ sampleRate });
    this.gate = 0;
    this.attack = Math.exp(-1 / (0.003 * sampleRate));
    this.release = Math.exp(-1 / (0.012 * sampleRate));
  }

  processBlock(input, output, parameters = {}) {
    if (!(input instanceof Float32Array) || !(output instanceof Float32Array)) {
      throw new TypeError("input and output must be Float32Array");
    }
    if (input.length !== output.length) {
      throw new RangeError("input and output blocks must have equal length");
    }

    this.engine.setParameters({
      size: parameterValue(parameters.size, 0, 0.5),
      decay: parameterValue(parameters.decay, 0, 0.45),
      body: parameterValue(parameters.body, 0, 0.65),
      dry: parameterValue(parameters.dry, 0, 0.12),
      drive: parameterValue(parameters.drive, 0, 0.7)
    });

    for (let index = 0; index < input.length; index += 1) {
      const target = Math.min(1, Math.max(0,
        parameterValue(parameters.gate, index, 0)
      ));
      const coefficient = target > this.gate ? this.attack : this.release;
      this.gate = target + coefficient * (this.gate - target);
      output[index] = this.engine.processSample(input[index] * this.gate);
    }
    return output;
  }

  reset() {
    this.engine.reset();
    this.gate = 0;
  }
}
