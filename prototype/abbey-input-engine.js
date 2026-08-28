/*
 * Abbey-input DSP prototype for the iPhone mic path.
 *
 * BODY = REDD-derived valve path.
 * OPEN = TG12345-derived solid-state path.
 * CLEAN and FOCUS are intentionally not Abbey Road emulations here.
 *
 * The frequencies and TG threshold follow the saved research. Transfer
 * curves, makeup values and smoothing are application design values, not
 * measurements of the original hardware.
 */
(function abbeyInputModule(root, factory) {
  const api = factory();
  if (typeof module === "object" && module.exports) module.exports = api;
  if (root) root.AbbeyInputDSP = api;
})(typeof globalThis !== "undefined" ? globalThis : this, function factory() {
  "use strict";

  const MODES = Object.freeze({ CLEAN: "CLEAN", BODY: "BODY", OPEN: "OPEN" });

  const clamp = (value, min, max) => Math.min(max, Math.max(min, value));
  const dbToGain = (db) => 10 ** (db / 20);
  const gainToDb = (gain) => 20 * Math.log10(Math.max(1e-12, gain));

  class Biquad {
    constructor(sampleRate) {
      this.sampleRate = sampleRate;
      this.b0 = 1;
      this.b1 = 0;
      this.b2 = 0;
      this.a1 = 0;
      this.a2 = 0;
      this.z1 = 0;
      this.z2 = 0;
    }

    set(type, frequency, q, gainDb) {
      const f = clamp(frequency, 10, this.sampleRate * 0.45);
      const w0 = (2 * Math.PI * f) / this.sampleRate;
      const cos = Math.cos(w0);
      const sin = Math.sin(w0);
      const A = 10 ** (gainDb / 40);
      let alpha;
      let b0;
      let b1;
      let b2;
      let a0;
      let a1;
      let a2;

      if (type === "peaking") {
        alpha = sin / (2 * Math.max(0.05, q));
        b0 = 1 + alpha * A;
        b1 = -2 * cos;
        b2 = 1 - alpha * A;
        a0 = 1 + alpha / A;
        a1 = -2 * cos;
        a2 = 1 - alpha / A;
      } else {
        const slope = Math.max(0.1, q);
        alpha = (sin / 2) * Math.sqrt((A + 1 / A) * (1 / slope - 1) + 2);
        const beta = 2 * Math.sqrt(A) * alpha;
        if (type === "lowshelf") {
          b0 = A * ((A + 1) - (A - 1) * cos + beta);
          b1 = 2 * A * ((A - 1) - (A + 1) * cos);
          b2 = A * ((A + 1) - (A - 1) * cos - beta);
          a0 = (A + 1) + (A - 1) * cos + beta;
          a1 = -2 * ((A - 1) + (A + 1) * cos);
          a2 = (A + 1) + (A - 1) * cos - beta;
        } else if (type === "highshelf") {
          b0 = A * ((A + 1) + (A - 1) * cos + beta);
          b1 = -2 * A * ((A - 1) + (A + 1) * cos);
          b2 = A * ((A + 1) + (A - 1) * cos - beta);
          a0 = (A + 1) - (A - 1) * cos + beta;
          a1 = 2 * ((A - 1) - (A + 1) * cos);
          a2 = (A + 1) - (A - 1) * cos - beta;
        } else {
          throw new Error(`Unsupported biquad type: ${type}`);
        }
      }

      this.b0 = b0 / a0;
      this.b1 = b1 / a0;
      this.b2 = b2 / a0;
      this.a1 = a1 / a0;
      this.a2 = a2 / a0;
    }

    process(input) {
      const output = input * this.b0 + this.z1;
      this.z1 = input * this.b1 - output * this.a1 + this.z2;
      this.z2 = input * this.b2 - output * this.a2;
      return output;
    }

    reset() {
      this.z1 = 0;
      this.z2 = 0;
    }
  }

  function modeParameters(mode, density = 0.35) {
    const amount = clamp(density, 0, 1);
    if (mode === MODES.BODY) {
      return Object.freeze({
        family: "REDD",
        inputDriveDb: 1 + 7 * amount,
        preLowGuardDb: -3 * amount,
        lowShelfHz: 100,
        lowShelfDb: 1.8 * amount,
        presenceHz: 5000,
        presenceDb: 1.0 * amount,
        highShelfHz: 10000,
        highShelfDb: -0.8 * amount,
        asymmetry: 0.18 * amount,
        outputDb: -0.7 - 2.2 * amount
      });
    }
    if (mode === MODES.OPEN) {
      return Object.freeze({
        family: "TG12345",
        lowShelfHz: 50,
        lowShelfDb: 0.5 * amount,
        presenceHz: 5000,
        presenceDb: 1.2 * amount,
        highShelfHz: 10000,
        highShelfDb: 0.8 * amount,
        thresholdDbfs: -19.3,
        ratio: 2,
        attackMs: 1,
        recoveryMs: 100 + 400 * amount,
        groupDriveDb: 0.5 + 2.5 * amount,
        outputDb: -0.4 - 1.2 * amount
      });
    }
    return Object.freeze({ family: "NONE" });
  }

  class AbbeyInputEngine {
    constructor(sampleRate = 48000) {
      this.sampleRate = sampleRate;
      this.mode = MODES.CLEAN;
      this.density = 0.35;
      this.feedbackEnvelope = 0;
      this.dcX = 0;
      this.dcY = 0;
      this.filters = Array.from({ length: 4 }, () => new Biquad(sampleRate));
      this.configure(this.mode, this.density);
    }

    configure(mode, density = this.density) {
      this.mode = Object.values(MODES).includes(mode) ? mode : MODES.CLEAN;
      this.density = clamp(density, 0, 1);
      this.parameters = modeParameters(this.mode, this.density);
      for (const filter of this.filters) filter.reset();

      if (this.mode === MODES.BODY) {
        this.filters[0].set("lowshelf", 120, 1, this.parameters.preLowGuardDb);
        this.filters[1].set("lowshelf", 100, 1, this.parameters.lowShelfDb);
        this.filters[2].set("peaking", 5000, 0.7, this.parameters.presenceDb);
        this.filters[3].set("highshelf", 10000, 1, this.parameters.highShelfDb);
      } else if (this.mode === MODES.OPEN) {
        this.filters[0].set("lowshelf", 50, 1, this.parameters.lowShelfDb);
        this.filters[1].set("peaking", 5000, 0.75, this.parameters.presenceDb);
        this.filters[2].set("highshelf", 10000, 1, this.parameters.highShelfDb);
      }
      this.reset();
      return this.parameters;
    }

    reset() {
      this.feedbackEnvelope = 0;
      this.lastTgOutput = 0;
      this.dcX = 0;
      this.dcY = 0;
      for (const filter of this.filters) filter.reset();
    }

    processSample(input) {
      const x = Number.isFinite(input) ? clamp(input, -4, 4) : 0;
      if (this.mode === MODES.BODY) return this.processRedd(x);
      if (this.mode === MODES.OPEN) return this.processTg(x);
      return x;
    }

    processRedd(input) {
      const p = this.parameters;
      let x = this.filters[0].process(input);
      const drive = dbToGain(p.inputDriveDb);
      const positive = 1 + p.asymmetry;
      const negative = 1 - p.asymmetry * 0.65;
      const shaped = x >= 0
        ? Math.tanh(x * drive * positive) / Math.tanh(drive * positive)
        : Math.tanh(x * drive * negative) / Math.tanh(drive * negative);
      x = this.filters[1].process(shaped);
      x = this.filters[2].process(x);
      x = this.filters[3].process(x) * dbToGain(p.outputDb);
      return this.dcBlock(x);
    }

    processTg(input) {
      const p = this.parameters;
      let x = this.filters[0].process(input);
      x = this.filters[1].process(x);
      x = this.filters[2].process(x);

      const detector = Math.abs(this.lastTgOutput || x);
      const attack = Math.exp(-1 / (this.sampleRate * p.attackMs * 0.001));
      const release = Math.exp(-1 / (this.sampleRate * p.recoveryMs * 0.001));
      const coeff = detector > this.feedbackEnvelope ? attack : release;
      this.feedbackEnvelope = coeff * this.feedbackEnvelope + (1 - coeff) * detector;

      const threshold = dbToGain(p.thresholdDbfs);
      let compressorGain = 1;
      if (this.feedbackEnvelope > threshold) {
        compressorGain = (threshold / this.feedbackEnvelope) ** (1 - 1 / p.ratio);
      }

      const envelopeDb = gainToDb(this.feedbackEnvelope);
      let lowLevelLiftDb = 0;
      if (envelopeDb > -60 && envelopeDb < p.thresholdDbfs) {
        lowLevelLiftDb = 3 * clamp((envelopeDb + 60) / 24, 0, 1);
      }

      const drive = dbToGain(p.groupDriveDb);
      x *= compressorGain * dbToGain(lowLevelLiftDb);
      x = Math.tanh(x * drive) / Math.tanh(drive);
      x *= dbToGain(p.outputDb);
      this.lastTgOutput = x;
      return this.dcBlock(x);
    }

    dcBlock(input) {
      const output = input - this.dcX + 0.99765 * this.dcY;
      this.dcX = input;
      this.dcY = output;
      return output;
    }

    processBlock(input, output = new Float32Array(input.length)) {
      for (let i = 0; i < input.length; i += 1) output[i] = this.processSample(input[i]);
      return output;
    }
  }

  return Object.freeze({ MODES, AbbeyInputEngine, modeParameters, dbToGain, gainToDb });
});
