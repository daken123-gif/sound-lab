import {
  Biquad,
  highpassCoefficients,
  lowpassCoefficients
} from "./biquad.js";

const DEFAULT_EDGES = [110, 190, 330, 570, 1000, 1750, 3000, 5200, 9000];
const BUTTERWORTH_Q = {
  2: [Math.SQRT1_2],
  4: [0.541196100146197, 1.306562964876377],
  8: [
    0.509795579104159,
    0.601344886935045,
    0.899976223136416,
    2.562915447741506
  ]
};

const clamp = (value, min, max) => Math.min(max, Math.max(min, value));

function smoothingCoefficient(timeSeconds, sampleRate) {
  if (timeSeconds <= 0) return 0;
  return Math.exp(-1 / (timeSeconds * sampleRate));
}

function buildCascade(sampleRate, bandIndex, order, edges) {
  const lastBand = edges.length;

  if (bandIndex === 0) {
    return BUTTERWORTH_Q[order].map(
      q => new Biquad(lowpassCoefficients(sampleRate, edges[0], q))
    );
  }

  if (bandIndex === lastBand) {
    return BUTTERWORTH_Q[order].map(
      q => new Biquad(highpassCoefficients(sampleRate, edges.at(-1), q))
    );
  }

  // Interior bands divide the requested total pole count between both edges.
  const edgeOrder = order / 2;
  const sections = BUTTERWORTH_Q[edgeOrder];
  const lower = edges[bandIndex - 1];
  const upper = edges[bandIndex];
  return [
    ...sections.map(q => new Biquad(highpassCoefficients(sampleRate, lower, q))),
    ...sections.map(q => new Biquad(lowpassCoefficients(sampleRate, upper, q)))
  ];
}

export class SkulpturFilterBank {
  constructor({
    sampleRate = 48000,
    channels = 2,
    order = 4,
    edges = DEFAULT_EDGES,
    gainSmoothingSeconds = 0.006,
    feedbackSmoothingSeconds = 0.02,
    feedbackLoopGain = 1.5,
    feedbackDrive = 2.4,
    wetAttackSeconds = 0.015,
    wetReleaseSeconds = 0.06,
    wetTrim = 0.72
  } = {}) {
    if (![4, 8].includes(order)) {
      throw new RangeError("order must be 4 or 8");
    }
    if (edges.length !== 9 || edges.some((value, i) => i && value <= edges[i - 1])) {
      throw new RangeError("edges must contain nine ascending frequencies");
    }

    this.sampleRate = sampleRate;
    this.channels = channels;
    this.order = order;
    this.edges = [...edges];
    this.bandCount = edges.length + 1;
    this.wetTrim = wetTrim;
    this.bandTarget = new Float64Array(this.bandCount).fill(1);
    this.bandCurrent = new Float64Array(this.bandCount).fill(1);
    this.feedbackTarget = new Float64Array(this.bandCount);
    this.feedbackCurrent = new Float64Array(this.bandCount);
    this.feedbackLoopGain = feedbackLoopGain;
    this.feedbackDrive = Math.max(0.1, feedbackDrive);
    this.feedbackState = Array.from({ length: channels }, () =>
      new Float64Array(this.bandCount)
    );
    this.wetTarget = 0;
    this.wetCurrent = 0;
    this.gainSmoothing = smoothingCoefficient(gainSmoothingSeconds, sampleRate);
    this.feedbackSmoothing = smoothingCoefficient(feedbackSmoothingSeconds, sampleRate);
    this.wetAttack = smoothingCoefficient(wetAttackSeconds, sampleRate);
    this.wetRelease = smoothingCoefficient(wetReleaseSeconds, sampleRate);

    this.filters = Array.from({ length: channels }, () =>
      Array.from({ length: this.bandCount }, (_, bandIndex) =>
        buildCascade(sampleRate, bandIndex, order, this.edges)
      )
    );
  }

  setBand(index, value) {
    if (!Number.isInteger(index) || index < 0 || index >= this.bandCount) {
      throw new RangeError(`band index must be 0..${this.bandCount - 1}`);
    }
    this.bandTarget[index] = clamp(Number(value), 0, 1);
  }

  setBands(values) {
    if (values.length !== this.bandCount) {
      throw new RangeError(`expected ${this.bandCount} band values`);
    }
    values.forEach((value, index) => this.setBand(index, value));
  }

  setFeedback(index, value) {
    if (!Number.isInteger(index) || index < 0 || index >= this.bandCount) {
      throw new RangeError(`band index must be 0..${this.bandCount - 1}`);
    }
    this.feedbackTarget[index] = clamp(Number(value), 0, 1);
  }

  setFeedbackBands(values) {
    if (values.length !== this.bandCount) {
      throw new RangeError(`expected ${this.bandCount} feedback values`);
    }
    values.forEach((value, index) => this.setFeedback(index, value));
  }

  get hasFeedback() {
    return this.feedbackTarget.some(value => value > 1e-5) ||
      this.feedbackCurrent.some(value => value > 1e-5);
  }

  setActive(active) {
    this.wetTarget = active ? 1 : 0;
  }

  reset() {
    for (const channel of this.filters) {
      for (const band of channel) {
        for (const filter of band) filter.reset();
      }
    }
    this.bandCurrent.fill(1);
    this.bandTarget.fill(1);
    this.feedbackTarget.fill(0);
    this.feedbackCurrent.fill(0);
    for (const channel of this.feedbackState) channel.fill(0);
    this.wetCurrent = 0;
    this.wetTarget = 0;
  }

  process(inputChannels) {
    if (inputChannels.length !== this.channels) {
      throw new RangeError(`expected ${this.channels} input channels`);
    }
    const frameCount = inputChannels[0].length;
    if (inputChannels.some(channel => channel.length !== frameCount)) {
      throw new RangeError("all channels must have equal length");
    }

    const output = inputChannels.map(() => new Float32Array(frameCount));

    for (let frame = 0; frame < frameCount; frame += 1) {
      for (let band = 0; band < this.bandCount; band += 1) {
        this.bandCurrent[band] =
          this.bandTarget[band] +
          this.gainSmoothing * (this.bandCurrent[band] - this.bandTarget[band]);
        this.feedbackCurrent[band] =
          this.feedbackTarget[band] +
          this.feedbackSmoothing * (this.feedbackCurrent[band] - this.feedbackTarget[band]);
      }

      const wetCoefficient = this.wetTarget > this.wetCurrent
        ? this.wetAttack
        : this.wetRelease;
      this.wetCurrent =
        this.wetTarget + wetCoefficient * (this.wetCurrent - this.wetTarget);

      for (let channelIndex = 0; channelIndex < this.channels; channelIndex += 1) {
        const dry = inputChannels[channelIndex][frame];
        let wet = 0;

        for (let bandIndex = 0; bandIndex < this.bandCount; bandIndex += 1) {
          const feedback = this.feedbackState[channelIndex][bandIndex] *
            this.feedbackCurrent[bandIndex] * this.feedbackLoopGain;
          let bandSample = dry + feedback;
          for (const filter of this.filters[channelIndex][bandIndex]) {
            bandSample = filter.process(bandSample);
          }
          const driven = bandSample * this.feedbackDrive;
          this.feedbackState[channelIndex][bandIndex] =
            Math.tanh(driven) / this.feedbackDrive;
          wet += bandSample * this.bandCurrent[bandIndex];
        }

        wet *= this.wetTrim;
        const mixed = dry + this.wetCurrent * (wet - dry);
        output[channelIndex][frame] = Number.isFinite(mixed) ? mixed : 0;
      }
    }

    return output;
  }
}

export { DEFAULT_EDGES };
