const clamp = (value, min, max) => Math.min(max, Math.max(min, value));

function normalizePhase(phase) {
  const normalized = Number(phase) % 1;
  return normalized < 0 ? normalized + 1 : normalized;
}

export class SpectralGestureLoop {
  constructor({ bandCount = 10, minPhaseSpacing = 1 / 1024 } = {}) {
    this.bandCount = bandCount;
    this.minPhaseSpacing = Math.max(0, minPhaseSpacing);
    this.bands = Array.from({ length: bandCount }, () => []);
    this.recording = false;
    this.overwrittenBands = new Set();
  }

  startRecording() {
    this.recording = true;
    this.overwrittenBands.clear();
  }

  stopRecording() {
    this.recording = false;
    this.overwrittenBands.clear();
  }

  capture(band, value, phase) {
    this.#validateBand(band);
    if (!this.recording) return false;

    if (!this.overwrittenBands.has(band)) {
      this.bands[band] = [];
      this.overwrittenBands.add(band);
    }

    const point = {
      phase: normalizePhase(phase),
      value: clamp(Number(value), 0, 1)
    };
    const points = this.bands[band];
    const nearby = points.findIndex(existing => {
      const distance = Math.abs(existing.phase - point.phase);
      return Math.min(distance, 1 - distance) < this.minPhaseSpacing;
    });

    if (nearby >= 0) points[nearby] = point;
    else points.push(point);
    points.sort((a, b) => a.phase - b.phase);
    return true;
  }

  valuesAt(phase) {
    const normalized = normalizePhase(phase);
    return this.bands.map(points => this.#interpolate(points, normalized));
  }

  clear(band) {
    if (band === undefined) {
      this.bands = Array.from({ length: this.bandCount }, () => []);
      this.overwrittenBands.clear();
      return;
    }
    this.#validateBand(band);
    this.bands[band] = [];
    this.overwrittenBands.delete(band);
  }

  serialize() {
    return {
      version: 1,
      bandCount: this.bandCount,
      bands: this.bands.map(points => points.map(point => ({ ...point })))
    };
  }

  deserialize(state) {
    if (state?.bandCount !== this.bandCount || !Array.isArray(state.bands)) {
      throw new RangeError(`gesture loop must contain ${this.bandCount} bands`);
    }
    this.bands = Array.from({ length: this.bandCount }, (_, band) => {
      const points = state.bands[band];
      if (!Array.isArray(points)) throw new TypeError(`band ${band} must be an array`);
      return points
        .map(point => ({
          phase: normalizePhase(point.phase),
          value: clamp(Number(point.value), 0, 1)
        }))
        .sort((a, b) => a.phase - b.phase);
    });
    this.stopRecording();
  }

  #interpolate(points, phase) {
    if (points.length === 0) return null;
    if (points.length === 1) return points[0].value;

    const foundRight = points.findIndex(point => point.phase >= phase);
    const rightIndex = foundRight < 0 ? 0 : foundRight;
    const leftIndex = (rightIndex - 1 + points.length) % points.length;
    const left = points[leftIndex];
    const right = points[rightIndex];
    const wrapsAfterLast = foundRight < 0;
    const wrapsBeforeFirst = rightIndex === 0 && !wrapsAfterLast;
    const leftPhase = left.phase - (wrapsBeforeFirst ? 1 : 0);
    const rightPhase = right.phase + (wrapsAfterLast ? 1 : 0);
    const samplePhase = phase;
    const span = rightPhase - leftPhase;
    if (span <= 0) return right.value;
    const amount = clamp((samplePhase - leftPhase) / span, 0, 1);
    return left.value + (right.value - left.value) * amount;
  }

  #validateBand(band) {
    if (!Number.isInteger(band) || band < 0 || band >= this.bandCount) {
      throw new RangeError(`band index must be 0..${this.bandCount - 1}`);
    }
  }
}
