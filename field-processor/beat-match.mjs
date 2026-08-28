export const TIME_GESTURE_MODES = Object.freeze({
  AUTO: 'AUTO',
  RAW: 'RAW',
});

function finite(value, label) {
  if (!Number.isFinite(value)) throw new TypeError(`${label} must be finite`);
  return value;
}

function positive(value, label) {
  value = finite(value, label);
  if (value <= 0) throw new RangeError(`${label} must be greater than zero`);
  return value;
}

function clamp(value, minimum, maximum) {
  return Math.min(maximum, Math.max(minimum, value));
}

function validateMode(mode) {
  if (mode !== TIME_GESTURE_MODES.AUTO && mode !== TIME_GESTURE_MODES.RAW) {
    throw new RangeError(`unknown time gesture mode: ${mode}`);
  }
  return mode;
}

/**
 * Estimate a transparent beat grid from an already computed peak/onset envelope.
 *
 * It never edits, slices, stretches, or resamples source audio. Failure is
 * represented by null so the caller can continue in RAW time.
 */
export function estimateBeatGrid(
  envelope,
  {
    hopSeconds,
    minimumBpm = 60,
    maximumBpm = 180,
    minimumOnsets = 4,
  } = {},
) {
  if (!envelope || typeof envelope.length !== 'number') {
    throw new TypeError('envelope must be array-like');
  }
  hopSeconds = positive(hopSeconds, 'hopSeconds');
  minimumBpm = positive(minimumBpm, 'minimumBpm');
  maximumBpm = positive(maximumBpm, 'maximumBpm');
  if (maximumBpm <= minimumBpm) {
    throw new RangeError('maximumBpm must be greater than minimumBpm');
  }
  if (!Number.isInteger(minimumOnsets) || minimumOnsets < 2) {
    throw new RangeError('minimumOnsets must be an integer of at least two');
  }
  if (envelope.length < minimumOnsets * 2) return null;

  const novelty = new Float64Array(envelope.length);
  let previous = 0;
  for (let index = 0; index < envelope.length; index += 1) {
    const current = Math.max(0, finite(Number(envelope[index]), `envelope[${index}]`));
    novelty[index] = Math.max(0, current - previous);
    previous = current;
  }

  const mean = novelty.reduce((sum, value) => sum + value, 0) / novelty.length;
  const variance = novelty.reduce((sum, value) => sum + (value - mean) ** 2, 0) / novelty.length;
  const deviation = Math.sqrt(variance);
  if (deviation <= 1e-8) return null;
  const threshold = mean + deviation * 0.5;
  const onsetIndices = [];
  for (let index = 0; index < novelty.length; index += 1) {
    if (novelty[index] >= threshold) onsetIndices.push(index);
  }
  if (onsetIndices.length < minimumOnsets) return null;

  const minimumLag = Math.max(1, Math.round(60 / maximumBpm / hopSeconds));
  const maximumLag = Math.min(
    novelty.length - 1,
    Math.round(60 / minimumBpm / hopSeconds),
  );
  if (maximumLag < minimumLag) return null;

  let bestLag = 0;
  let bestScore = 0;
  for (let lag = minimumLag; lag <= maximumLag; lag += 1) {
    let correlation = 0;
    let leftEnergy = 0;
    let rightEnergy = 0;
    for (let index = lag; index < novelty.length; index += 1) {
      const left = novelty[index];
      const right = novelty[index - lag];
      correlation += left * right;
      leftEnergy += left * left;
      rightEnergy += right * right;
    }
    const score = leftEnergy > 0 && rightEnergy > 0
      ? correlation / Math.sqrt(leftEnergy * rightEnergy)
      : 0;
    if (score > bestScore + 1e-9) {
      bestScore = score;
      bestLag = lag;
    }
  }
  if (bestLag === 0 || bestScore <= 0) return null;

  let originIndex = onsetIndices[0];
  for (const index of onsetIndices) {
    if (index >= bestLag) break;
    if (novelty[index] > novelty[originIndex]) originIndex = index;
  }

  return Object.freeze({
    bpm: 60 / (bestLag * hopSeconds),
    origin: originIndex * hopSeconds,
    confidence: clamp(bestScore, 0, 1),
    beatSeconds: bestLag * hopSeconds,
    onsetCount: onsetIndices.length,
  });
}

/**
 * Resolve one waveform gesture without mutating the recorded material.
 *
 * AUTO only changes gesture coordinates. If its grid is absent or uncertain,
 * the exact RAW coordinates pass through and playback remains available.
 */
export class TimeGestureResolver {
  constructor({
    duration = 0,
    mode = TIME_GESTURE_MODES.RAW,
    subdivision = 4,
    minimumConfidence = 0.45,
  } = {}) {
    this.duration = 0;
    this.mode = validateMode(mode);
    this.grid = null;
    this.setDuration(duration);
    this.setSubdivision(subdivision);
    this.minimumConfidence = clamp(finite(minimumConfidence, 'minimumConfidence'), 0, 1);
  }

  setDuration(duration) {
    duration = finite(duration, 'duration');
    if (duration < 0) throw new RangeError('duration cannot be negative');
    this.duration = duration;
    return this;
  }

  setMode(mode) {
    this.mode = validateMode(mode);
    return this;
  }

  setSubdivision(subdivision) {
    if (!Number.isInteger(subdivision) || subdivision < 1 || subdivision > 64) {
      throw new RangeError('subdivision must be an integer from 1 to 64');
    }
    this.subdivision = subdivision;
    return this;
  }

  setGrid({ bpm, origin = 0, confidence = 1 } = {}) {
    bpm = positive(bpm, 'bpm');
    origin = finite(origin, 'origin');
    confidence = clamp(finite(confidence, 'confidence'), 0, 1);
    this.grid = Object.freeze({
      bpm,
      origin,
      confidence,
      beatSeconds: 60 / bpm,
    });
    return this.grid;
  }

  clearGrid() {
    this.grid = null;
    return this;
  }

  estimate(envelope, options) {
    const grid = estimateBeatGrid(envelope, options);
    if (grid) this.setGrid(grid);
    else this.clearGrid();
    return grid;
  }

  resolve({ position, length = null } = {}) {
    position = clamp(finite(position, 'position'), 0, this.duration);
    if (length !== null) {
      length = clamp(positive(length, 'length'), 0, this.duration);
    }

    const raw = (reason = null) => Object.freeze({
      requestedMode: this.mode,
      effectiveMode: TIME_GESTURE_MODES.RAW,
      position,
      length,
      end: length === null ? null : Math.min(this.duration, position + length),
      snapped: false,
      reason,
      grid: this.grid,
    });

    if (this.mode === TIME_GESTURE_MODES.RAW) return raw();
    if (!this.grid) return raw('NO_BEAT_GRID');
    if (this.grid.confidence < this.minimumConfidence) return raw('LOW_CONFIDENCE');
    if (this.duration === 0) return raw('EMPTY_TIMELINE');

    const step = this.grid.beatSeconds / this.subdivision;
    const quantize = value => this.grid.origin
      + Math.round((value - this.grid.origin) / step) * step;
    let snappedLength = length;
    if (length !== null) {
      snappedLength = clamp(
        Math.max(step, Math.round(length / step) * step),
        Math.min(step, this.duration),
        this.duration,
      );
    }
    const maximumPosition = length === null ? this.duration : this.duration - snappedLength;
    const snappedPosition = clamp(quantize(position), 0, Math.max(0, maximumPosition));

    return Object.freeze({
      requestedMode: this.mode,
      effectiveMode: TIME_GESTURE_MODES.AUTO,
      position: snappedPosition,
      length: snappedLength,
      end: snappedLength === null ? null : snappedPosition + snappedLength,
      snapped: Math.abs(snappedPosition - position) > 1e-9
        || (length !== null && Math.abs(snappedLength - length) > 1e-9),
      reason: null,
      grid: this.grid,
      step,
    });
  }
}
