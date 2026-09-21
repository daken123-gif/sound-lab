const clamp = (value, min, max) => Math.min(max, Math.max(min, value));

export function mapSurfacePosition(position) {
  const normalized = clamp(Number(position), 0, 1);
  if (normalized <= 0.5) {
    return { position: normalized, gain: normalized * 2, feedback: 0 };
  }
  return { position: normalized, gain: 1, feedback: (normalized - 0.5) * 2 };
}

export function surfacePositionFromValues(gain, feedback) {
  const safeFeedback = clamp(Number(feedback), 0, 1);
  if (safeFeedback > 0) return 0.5 + safeFeedback * 0.5;
  return clamp(Number(gain), 0, 1) * 0.5;
}

export function composeFeedback(base, recorded, manual) {
  if (!base || !recorded || !manual ||
      base.length !== recorded.length || base.length !== manual.length) {
    throw new RangeError("feedback layers must have equal lengths");
  }
  return Array.from(base, (value, band) => {
    let result = clamp(Number(value), 0, 1);
    if (recorded[band] !== null && recorded[band] !== undefined) {
      result = clamp(Number(recorded[band]), 0, 1);
    }
    if (manual[band] !== null && manual[band] !== undefined) {
      result = clamp(Number(manual[band]), 0, 1);
    }
    return result;
  });
}

export class SpectralSurfaceControl {
  constructor({ bandCount = 10 } = {}) {
    this.bandCount = bandCount;
    this.touches = new Map();
    this.sequence = 0;
  }

  beginTouch(pointerId, band, position) {
    this.#validateBand(band);
    const mapped = mapSurfacePosition(position);
    this.touches.set(pointerId, { band, ...mapped, sequence: ++this.sequence });
    return mapped;
  }

  moveTouch(pointerId, band, position) {
    if (!this.touches.has(pointerId)) return this.beginTouch(pointerId, band, position);
    this.#validateBand(band);
    const mapped = mapSurfacePosition(position);
    this.touches.set(pointerId, { band, ...mapped, sequence: ++this.sequence });
    return mapped;
  }

  endTouch(pointerId) {
    this.touches.delete(pointerId);
  }

  feedbackSnapshot() {
    return Array.from({ length: this.bandCount }, (_, band) =>
      this.#winner(band)?.feedback ?? null
    );
  }

  positionSnapshot() {
    return Array.from({ length: this.bandCount }, (_, band) =>
      this.#winner(band)?.position ?? null
    );
  }

  #winner(band) {
    let winner = null;
    for (const touch of this.touches.values()) {
      if (touch.band !== band) continue;
      if (!winner || touch.sequence > winner.sequence) winner = touch;
    }
    return winner;
  }

  #validateBand(band) {
    if (!Number.isInteger(band) || band < 0 || band >= this.bandCount) {
      throw new RangeError(`band index must be 0..${this.bandCount - 1}`);
    }
  }
}
