const PENTATONIC_RATIOS = Object.freeze([1, 9 / 8, 5 / 4, 3 / 2, 5 / 3, 2]);

function clamp(value, min, max) {
  return Math.min(max, Math.max(min, value));
}

function mapExponential(value, min, max) {
  return min * Math.pow(max / min, clamp(value, 0, 1));
}

class ModalResonator {
  constructor(sampleRate, frequency, decaySeconds, gain) {
    this.sampleRate = sampleRate;
    this.gain = gain;
    this.y1 = 0;
    this.y2 = 0;
    this.set(frequency, decaySeconds);
  }

  set(frequency, decaySeconds) {
    const nyquistSafe = this.sampleRate * 0.45;
    const f = clamp(frequency, 20, nyquistSafe);
    const decay = clamp(decaySeconds, 0.025, 8);

    // Reach -60 dB at decaySeconds. Keeping radius below one guarantees
    // that an undriven mode decays instead of self-oscillating.
    const radius = Math.exp(Math.log(0.001) / (decay * this.sampleRate));
    const omega = 2 * Math.PI * f / this.sampleRate;
    this.a1 = 2 * radius * Math.cos(omega);
    this.a2 = -(radius * radius);
    this.b0 = (1 - radius) * this.gain;
  }

  process(input) {
    const output = this.b0 * input + this.a1 * this.y1 + this.a2 * this.y2;
    this.y2 = this.y1;
    this.y1 = output;
    return output;
  }

  reset() {
    this.y1 = 0;
    this.y2 = 0;
  }
}

class ResonatorBank {
  constructor(sampleRate, modeRatios, detuneRatio) {
    this.sampleRate = sampleRate;
    this.modeRatios = modeRatios;
    this.detuneRatio = detuneRatio;
    this.modes = modeRatios.map((_, index) =>
      new ModalResonator(sampleRate, 110, 0.5, 1 / Math.sqrt(index + 1))
    );
  }

  update(baseFrequency, decaySeconds) {
    for (let index = 0; index < this.modes.length; index += 1) {
      const gain = 1 / Math.sqrt(index + 1);
      this.modes[index].gain = gain;
      this.modes[index].set(
        baseFrequency * this.modeRatios[index] * this.detuneRatio,
        decaySeconds / Math.sqrt(index + 1)
      );
    }
  }

  process(input) {
    let output = 0;
    for (const mode of this.modes) output += mode.process(input);
    return output / this.modes.length;
  }

  reset() {
    for (const mode of this.modes) mode.reset();
  }
}

/**
 * A minimal, original BODY engine inspired by the public description of
 * THE PIPE's ORPHEUS algorithm. It does not reproduce SOMA's internal DSP.
 *
 * The raw microphone signal remains the excitation. No pitch detector or
 * MIDI conversion is required, so breath and consonants can excite modes.
 */
export class BodyEngine {
  constructor({ sampleRate = 48000, modeRatios = PENTATONIC_RATIOS } = {}) {
    if (!Number.isFinite(sampleRate) || sampleRate < 8000) {
      throw new RangeError("sampleRate must be at least 8000 Hz");
    }

    this.sampleRate = sampleRate;
    this.bankA = new ResonatorBank(sampleRate, modeRatios, 1);
    this.bankB = new ResonatorBank(sampleRate, modeRatios, Math.pow(2, 7 / 1200));
    this.highpassX1 = 0;
    this.highpassY1 = 0;
    this.envelope = 0;
    this.setParameters({});
  }

  setParameters({ size = this.size ?? 0.5, decay = this.decay ?? 0.45,
    body = this.body ?? 0.65, dry = this.dry ?? 0.12,
    drive = this.drive ?? 1.4 } = {}) {
    this.size = clamp(size, 0, 1);
    this.decay = clamp(decay, 0, 1);
    this.body = clamp(body, 0, 1);
    this.dry = clamp(dry, 0, 1);
    this.drive = clamp(drive, 0.25, 6);

    const baseA = mapExponential(1 - this.size, 58, 210);
    const baseB = baseA * (1.48 + 0.12 * this.body);
    const decaySeconds = mapExponential(this.decay, 0.08, 3.5);
    this.bankA.update(baseA, decaySeconds);
    this.bankB.update(baseB, decaySeconds * (0.72 + 0.5 * this.body));
  }

  processSample(input) {
    const x = Number.isFinite(input) ? clamp(input, -4, 4) : 0;

    // One-pole DC/high-pass stage, useful for plosives and phone-mic handling.
    const hp = x - this.highpassX1 + 0.995 * this.highpassY1;
    this.highpassX1 = x;
    this.highpassY1 = hp;

    const absolute = Math.abs(hp);
    const coefficient = absolute > this.envelope ? 0.08 : 0.0015;
    this.envelope += coefficient * (absolute - this.envelope);

    // Preserve weak breath while allowing strong syllables to strike harder.
    const excitation = hp * (0.28 + 0.72 * Math.sqrt(this.envelope));
    const wetA = this.bankA.process(excitation);
    const wetB = this.bankB.process(excitation);
    const wet = wetA * (1 - this.body) + wetB * this.body;

    return Math.tanh(this.drive * (wet * 5.5 + x * this.dry));
  }

  process(input) {
    if (!(input instanceof Float32Array)) {
      throw new TypeError("input must be a Float32Array");
    }
    const output = new Float32Array(input.length);
    for (let index = 0; index < input.length; index += 1) {
      output[index] = this.processSample(input[index]);
    }
    return output;
  }

  reset() {
    this.bankA.reset();
    this.bankB.reset();
    this.highpassX1 = 0;
    this.highpassY1 = 0;
    this.envelope = 0;
  }
}

export { PENTATONIC_RATIOS };
