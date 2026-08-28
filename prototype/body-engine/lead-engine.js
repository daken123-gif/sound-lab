function clamp(value, min, max) {
  return Math.min(max, Math.max(min, value));
}

function finiteOr(value, fallback) {
  return Number.isFinite(value) ? value : fallback;
}

function followerCoefficient(seconds, sampleRate) {
  return 1 - Math.exp(-1 / (Math.max(seconds, 1 / sampleRate) * sampleRate));
}

/**
 * Original LEAD hypothesis informed by THE PIPE's public FILTERRA description.
 * This is not a reconstruction of SOMA's unpublished DSP.
 *
 * The voice waveform remains the source: amplitude and a pitch-independent
 * brightness proxy animate a stable resonant low-pass filter and short space.
 */
export class LeadEngine {
  constructor({ sampleRate = 48000 } = {}) {
    if (!Number.isFinite(sampleRate) || sampleRate < 8000) {
      throw new RangeError("sampleRate must be at least 8000 Hz");
    }

    this.sampleRate = sampleRate;
    this.fastAttack = followerCoefficient(0.0025, sampleRate);
    this.fastRelease = followerCoefficient(0.045, sampleRate);
    this.slowAttack = followerCoefficient(0.035, sampleRate);
    this.slowRelease = followerCoefficient(0.24, sampleRate);
    this.brightnessAttack = followerCoefficient(0.008, sampleRate);
    this.brightnessRelease = followerCoefficient(0.09, sampleRate);
    this.delayBuffer = new Float32Array(Math.max(1, Math.ceil(sampleRate * 0.045)));
    this.reset();
    this.setParameters({});
  }

  setParameters({
    tone = this.tone ?? 0.46,
    motion = this.motion ?? 0.62,
    space = this.space ?? 0.24,
    dry = this.dry ?? 0.16,
    drive = this.drive ?? 1.25
  } = {}) {
    this.tone = clamp(finiteOr(tone, this.tone ?? 0.46), 0, 1);
    this.motion = clamp(finiteOr(motion, this.motion ?? 0.62), 0, 1);
    this.space = clamp(finiteOr(space, this.space ?? 0.24), 0, 1);
    this.dry = clamp(finiteOr(dry, this.dry ?? 0.16), 0, 1);
    this.drive = clamp(finiteOr(drive, this.drive ?? 1.25), 0.25, 4);
    this.delaySamples = Math.round(
      this.sampleRate * (0.008 + 0.029 * this.space)
    );
  }

  processSample(input) {
    const x = clamp(finiteOr(input, 0), -4, 4);

    const hp = x - this.highpassX1 + 0.995 * this.highpassY1;
    this.highpassX1 = x;
    this.highpassY1 = hp;

    const magnitude = Math.abs(hp);
    const fastCoefficient = magnitude > this.fastEnvelope
      ? this.fastAttack : this.fastRelease;
    const slowCoefficient = magnitude > this.slowEnvelope
      ? this.slowAttack : this.slowRelease;
    this.fastEnvelope += fastCoefficient * (magnitude - this.fastEnvelope);
    this.slowEnvelope += slowCoefficient * (magnitude - this.slowEnvelope);

    // A first-difference energy ratio: deliberately not called a spectral
    // centroid, and usable for breath/noise without pitch detection.
    const difference = Math.abs(hp - this.previousHighpass);
    this.previousHighpass = hp;
    const brightnessTarget = difference / (difference + magnitude + 1e-6);
    const brightnessCoefficient = brightnessTarget > this.brightness
      ? this.brightnessAttack : this.brightnessRelease;
    this.brightness += brightnessCoefficient * (brightnessTarget - this.brightness);

    const slowDrive = this.slowEnvelope / (this.slowEnvelope + 0.075);
    const fastDrive = this.fastEnvelope / (this.fastEnvelope + 0.11);
    const baseCutoff = 105 * Math.pow(2, this.tone * 4.75);
    const octaveMotion = this.motion * (2.15 * slowDrive + 1.15 * this.brightness);
    this.lastCutoff = clamp(
      baseCutoff * Math.pow(2, octaveMotion),
      55,
      this.sampleRate * 0.42
    );

    // Resonance grows with articulation, then retreats at high level. This
    // inverse safety region avoids moving cutoff and Q upward without bound.
    const articulation = 4 * fastDrive * (1 - fastDrive);
    const highLevelSafety = 1 - 0.72 * clamp((fastDrive - 0.68) / 0.32, 0, 1);
    this.lastResonance = clamp(
      0.68 + 5.1 * this.motion * articulation * highLevelSafety,
      0.68,
      5.5
    );

    const low = this.processLowpass(hp, this.lastCutoff, this.lastResonance);
    const delayedIndex = (
      this.delayIndex - this.delaySamples + this.delayBuffer.length
    ) % this.delayBuffer.length;
    const delayed = this.delayBuffer[delayedIndex];
    const spaceMix = 0.34 * this.space;
    const feedback = 0.08 + 0.34 * this.space;
    this.delayBuffer[this.delayIndex] = clamp(low + delayed * feedback, -2, 2);
    this.delayIndex = (this.delayIndex + 1) % this.delayBuffer.length;

    const wet = low * (1 - spaceMix) + delayed * spaceMix;
    return Math.tanh(this.drive * (this.dry * x + wet * 1.65));
  }

  processLowpass(input, cutoff, resonance) {
    // Topology-preserving state-variable filter. Coefficients may move at
    // audio rate while the two integrator states remain continuous.
    const g = Math.tan(Math.PI * cutoff / this.sampleRate);
    const k = 1 / resonance;
    const a1 = 1 / (1 + g * (g + k));
    const a2 = g * a1;
    const a3 = g * a2;
    const v3 = input - this.ic2eq;
    const v1 = a1 * this.ic1eq + a2 * v3;
    const v2 = this.ic2eq + a2 * this.ic1eq + a3 * v3;
    this.ic1eq = 2 * v1 - this.ic1eq;
    this.ic2eq = 2 * v2 - this.ic2eq;
    return v2;
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

  diagnostics() {
    return Object.freeze({
      fastEnvelope: this.fastEnvelope,
      slowEnvelope: this.slowEnvelope,
      brightness: this.brightness,
      cutoffHz: this.lastCutoff,
      resonanceQ: this.lastResonance
    });
  }

  reset() {
    this.highpassX1 = 0;
    this.highpassY1 = 0;
    this.previousHighpass = 0;
    this.fastEnvelope = 0;
    this.slowEnvelope = 0;
    this.brightness = 0;
    this.lastCutoff = 0;
    this.lastResonance = 0.68;
    this.ic1eq = 0;
    this.ic2eq = 0;
    this.delayBuffer.fill(0);
    this.delayIndex = 0;
  }
}
