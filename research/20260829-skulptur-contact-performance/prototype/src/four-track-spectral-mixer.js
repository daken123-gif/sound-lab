import { SkulpturFilterBank } from "./filter-bank-core.js";

const clamp = (value, min, max) => Math.min(max, Math.max(min, value));

export class FourTrackSpectralMixer {
  constructor({
    sampleRate = 48000,
    channels = 2,
    trackCount = 4,
    order = 4,
    loopBusTrim = 0.7,
    drumBusGain = 0.9,
    outputCeiling = 0.98,
    filterOptions = {}
  } = {}) {
    if (trackCount !== 4) throw new RangeError("Skulptur loop bus requires exactly four tracks");
    this.channels = channels;
    this.trackCount = trackCount;
    this.loopBusTrim = Math.max(0, Number(loopBusTrim));
    this.drumBusGain = Math.max(0, Number(drumBusGain));
    this.outputCeiling = clamp(Number(outputCeiling), 0.1, 1);
    this.tracks = Array.from({ length: trackCount }, () => ({ gain: 1, muted: false }));
    this.spectral = new SkulpturFilterBank({
      sampleRate,
      channels,
      order,
      ...filterOptions
    });
  }

  setTrack(index, { gain, muted } = {}) {
    this.#validateTrack(index);
    if (gain !== undefined) this.tracks[index].gain = clamp(Number(gain), 0, 2);
    if (muted !== undefined) this.tracks[index].muted = Boolean(muted);
  }

  setDrumBusGain(gain) {
    this.drumBusGain = clamp(Number(gain), 0, 2);
  }

  reset() {
    this.spectral.reset();
  }

  process(loopTracks, drumChannels) {
    if (!Array.isArray(loopTracks) || loopTracks.length !== this.trackCount) {
      throw new RangeError(`expected ${this.trackCount} loop tracks`);
    }

    const inputs = [...loopTracks, drumChannels].filter(Boolean);
    const firstChannel = inputs.find(input => input?.[0])?.[0];
    if (!firstChannel) throw new RangeError("at least one input channel is required");
    const frameCount = firstChannel.length;

    for (const input of inputs) this.#validateChannels(input, frameCount);

    const loopBus = Array.from({ length: this.channels }, () => new Float32Array(frameCount));
    for (let track = 0; track < this.trackCount; track += 1) {
      const input = loopTracks[track];
      const state = this.tracks[track];
      if (!input || state.muted || state.gain === 0) continue;
      const gain = state.gain * this.loopBusTrim;
      for (let channel = 0; channel < this.channels; channel += 1) {
        for (let frame = 0; frame < frameCount; frame += 1) {
          loopBus[channel][frame] += input[channel][frame] * gain;
        }
      }
    }

    const sculptedLoops = this.spectral.process(loopBus);
    return sculptedLoops.map((loopChannel, channel) => {
      const output = new Float32Array(frameCount);
      for (let frame = 0; frame < frameCount; frame += 1) {
        const drum = drumChannels ? drumChannels[channel][frame] * this.drumBusGain : 0;
        output[frame] = clamp(loopChannel[frame] + drum, -this.outputCeiling, this.outputCeiling);
      }
      return output;
    });
  }

  #validateChannels(input, frameCount) {
    if (!Array.isArray(input) || input.length !== this.channels) {
      throw new RangeError(`expected ${this.channels} channels per input`);
    }
    if (input.some(channel => channel.length !== frameCount)) {
      throw new RangeError("all input channels must have equal length");
    }
  }

  #validateTrack(index) {
    if (!Number.isInteger(index) || index < 0 || index >= this.trackCount) {
      throw new RangeError(`track index must be 0..${this.trackCount - 1}`);
    }
  }
}
