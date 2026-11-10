const clamp = (value, min, max) => Math.min(max, Math.max(min, value));

function approach(current, target, seconds, dt) {
  if (seconds <= 0) return target;
  const coefficient = Math.exp(-dt / seconds);
  return target + coefficient * (current - target);
}

export class SpectralControlEngine {
  constructor({
    bandCount = 10,
    baseline = 1,
    elasticSeconds = 0.075,
    throwFriction = 3.2,
    throwThreshold = 0.025
  } = {}) {
    this.bandCount = bandCount;
    this.baseline = clamp(baseline, 0, 1);
    this.elasticSeconds = elasticSeconds;
    this.throwFriction = throwFriction;
    this.throwThreshold = throwThreshold;
    this.values = new Float64Array(bandCount).fill(this.baseline);
    this.touches = new Map();
    this.touchSequence = 0;
    this.throws = Array.from({ length: bandCount }, () => null);
    this.recordedValues = Array.from({ length: bandCount }, () => null);
    this.flow = {
      enabled: false,
      depth: 0.55,
      periodSeconds: 2,
      bandPhase: 0.1,
      phase: 0
    };
  }

  beginTouch(pointerId, band, value, timeSeconds = 0) {
    this.#validateBand(band);
    this.throws[band] = null;
    this.touches.set(pointerId, {
      band,
      value: clamp(value, 0, 1),
      velocity: 0,
      timeSeconds,
      sequence: ++this.touchSequence
    });
  }

  moveTouch(pointerId, band, value, timeSeconds) {
    this.#validateBand(band);
    const touch = this.touches.get(pointerId);
    if (!touch) {
      this.beginTouch(pointerId, band, value, timeSeconds);
      return;
    }

    const nextValue = clamp(value, 0, 1);
    const dt = Math.max(1 / 240, timeSeconds - touch.timeSeconds);
    const velocity = (nextValue - touch.value) / dt;

    if (touch.band !== band) {
      this.throws[touch.band] = null;
      this.throws[band] = null;
    }

    Object.assign(touch, {
      band,
      value: nextValue,
      velocity,
      timeSeconds,
      sequence: ++this.touchSequence
    });
  }

  endTouch(pointerId, { throwMotion = true } = {}) {
    const touch = this.touches.get(pointerId);
    if (!touch) return;
    this.touches.delete(pointerId);

    if (throwMotion && Math.abs(touch.velocity) >= this.throwThreshold) {
      this.throws[touch.band] = {
        value: touch.value,
        velocity: touch.velocity
      };
    }
  }

  cancelTouches() {
    this.touches.clear();
  }

  clearMotion() {
    this.throws.fill(null);
    this.flow.enabled = false;
  }

  get isActive() {
    return this.touches.size > 0 || this.recordedValues.some(value => value !== null) ||
      this.flow.enabled || this.throws.some(Boolean);
  }

  setRecordedValues(values) {
    if (!values || values.length !== this.bandCount) {
      throw new RangeError(`expected ${this.bandCount} recorded values`);
    }
    this.recordedValues = Array.from(values, value =>
      value === null || value === undefined ? null : clamp(Number(value), 0, 1)
    );
  }

  manualSnapshot() {
    return Array.from({ length: this.bandCount }, (_, band) =>
      this.#winningTouch(band)?.value ?? null
    );
  }

  sourceAt(band) {
    this.#validateBand(band);
    if (this.#winningTouch(band)) return "touch";
    if (this.recordedValues[band] !== null) return "recorded";
    if (this.throws[band]) return "throw";
    if (this.flow.enabled) return "flow";
    return "idle";
  }

  setFlow({ enabled, depth, periodSeconds, bandPhase } = {}) {
    if (enabled !== undefined) this.flow.enabled = Boolean(enabled);
    if (depth !== undefined) this.flow.depth = clamp(depth, 0, 1);
    if (periodSeconds !== undefined) this.flow.periodSeconds = Math.max(0.05, periodSeconds);
    if (bandPhase !== undefined) this.flow.bandPhase = bandPhase;
  }

  update(dt) {
    const safeDt = clamp(dt, 1 / 1000, 0.1);
    this.flow.phase = (this.flow.phase + safeDt / this.flow.periodSeconds) % 1;

    for (let band = 0; band < this.bandCount; band += 1) {
      let target = this.#flowValue(band);
      const motion = this.throws[band];
      if (motion) {
        motion.value += motion.velocity * safeDt;
        while (motion.value < 0 || motion.value > 1) {
          if (motion.value < 0) {
            motion.value = -motion.value;
            motion.velocity = -motion.velocity;
          }
          if (motion.value > 1) {
            motion.value = 2 - motion.value;
            motion.velocity = -motion.velocity;
          }
        }
        motion.velocity *= Math.exp(-this.throwFriction * safeDt);
        target = motion.value;
        if (Math.abs(motion.velocity) < this.throwThreshold) {
          this.throws[band] = null;
        }
      }

      const recorded = this.recordedValues[band];
      if (recorded !== null) target = recorded;

      const touch = this.#winningTouch(band);
      if (touch) target = touch.value;

      this.values[band] = touch
        ? target
        : approach(this.values[band], target, this.elasticSeconds, safeDt);
    }

    return Float64Array.from(this.values);
  }

  #flowValue(band) {
    if (!this.flow.enabled) return this.baseline;
    const phase = this.flow.phase - band * this.flow.bandPhase;
    const wave = 0.5 + 0.5 * Math.sin(2 * Math.PI * phase);
    return this.baseline - this.flow.depth * wave;
  }

  #winningTouch(band) {
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
