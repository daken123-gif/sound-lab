const DIVISIONS = Object.freeze({
  '1 BAR': 1,
  '1/2': 1 / 2,
  '1/4': 1 / 4,
  '1/8': 1 / 8,
  '1/16': 1 / 16,
  GRAIN: 1 / 64,
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

function modulo(value, span) {
  return ((value % span) + span) % span;
}

function clamp(value, minimum, maximum) {
  return Math.min(maximum, Math.max(minimum, value));
}

export const LOOP_DIVISIONS = DIVISIONS;

/**
 * A non-destructive time authority shared by four audio tracks.
 *
 * This class does not own AudioBufferSourceNodes. A Web Audio adapter asks for
 * one playbackPlan() and schedules every source at the returned `when`, which
 * prevents four independent button presses from becoming four drifting clocks.
 */
export class SharedTransport {
  constructor({ clock = () => performance.now() / 1000, trackCount = 4 } = {}) {
    if (typeof clock !== 'function') throw new TypeError('clock must be a function');
    if (!Number.isInteger(trackCount) || trackCount < 1) {
      throw new RangeError('trackCount must be a positive integer');
    }

    this.clock = clock;
    this.trackDurations = Array(trackCount).fill(0);
    this.duration = 0;
    this.loopStart = 0;
    this.loopEnd = 0;
    this.basePosition = 0;
    this.anchoredAt = finite(clock(), 'clock result');
    this.direction = 1;
    this.playing = false;
    this.loopDivision = '1 BAR';
  }

  setTrackDuration(index, duration) {
    if (!Number.isInteger(index) || index < 0 || index >= this.trackDurations.length) {
      throw new RangeError('track index is outside the transport');
    }
    duration = finite(duration, 'track duration');
    if (duration < 0) throw new RangeError('track duration cannot be negative');

    const now = finite(this.clock(), 'clock result');
    const position = this.position(now);
    const followedFullRange = this.loopStart === 0 && this.loopEnd === this.duration;
    this.trackDurations[index] = duration;
    this.duration = Math.max(0, ...this.trackDurations);

    if (this.duration === 0) {
      this.playing = false;
      this.loopStart = 0;
      this.loopEnd = 0;
      this.basePosition = 0;
    } else {
      if (followedFullRange || this.loopEnd === 0) {
        this.loopStart = 0;
        this.loopEnd = this.duration;
      } else {
        this.loopStart = clamp(this.loopStart, 0, this.duration);
        this.loopEnd = clamp(this.loopEnd, this.loopStart, this.duration);
        if (this.loopEnd === this.loopStart) this.loopEnd = this.duration;
      }
      this.basePosition = this.wrap(position);
    }
    this.anchoredAt = now;
    return this.snapshot(now);
  }

  position(at = this.clock()) {
    at = finite(at, 'position time');
    if (!this.playing || this.duration === 0) return this.basePosition;
    const span = this.loopEnd - this.loopStart;
    if (span <= 0) return 0;
    const elapsed = Math.max(0, at - this.anchoredAt) * this.direction;
    return this.loopStart + modulo(this.basePosition - this.loopStart + elapsed, span);
  }

  start({ position = null, at = this.clock() } = {}) {
    at = finite(at, 'start time');
    if (this.duration === 0) return this.snapshot(at);
    this.basePosition = position === null ? this.position(at) : this.wrap(position);
    this.anchoredAt = at;
    this.playing = true;
    return this.snapshot(at);
  }

  stop(at = this.clock()) {
    at = finite(at, 'stop time');
    this.basePosition = this.position(at);
    this.anchoredAt = at;
    this.playing = false;
    return this.snapshot(at);
  }

  seek(position, at = this.clock()) {
    at = finite(at, 'seek time');
    this.basePosition = this.wrap(finite(position, 'position'));
    this.anchoredAt = at;
    return this.snapshot(at);
  }

  setDirection(direction, at = this.clock()) {
    if (direction !== 1 && direction !== -1) {
      throw new RangeError('direction must be 1 or -1');
    }
    at = finite(at, 'direction time');
    this.basePosition = this.position(at);
    this.anchoredAt = at;
    this.direction = direction;
    return this.snapshot(at);
  }

  setLoop(start, end, at = this.clock()) {
    if (this.duration === 0) return this.snapshot(at);
    at = finite(at, 'loop time');
    start = clamp(finite(start, 'loop start'), 0, this.duration);
    end = clamp(finite(end, 'loop end'), 0, this.duration);
    if (end <= start) throw new RangeError('loop end must be after loop start');

    const position = this.position(at);
    this.loopStart = start;
    this.loopEnd = end;
    this.basePosition = position >= start && position < end ? position : start;
    this.anchoredAt = at;
    return this.snapshot(at);
  }

  setLoopDivision(name, { anchor = this.position(), at = this.clock() } = {}) {
    if (!(name in DIVISIONS)) throw new RangeError(`unknown loop division: ${name}`);
    if (this.duration === 0) return this.snapshot(at);
    at = finite(at, 'division time');
    anchor = clamp(finite(anchor, 'division anchor'), 0, this.duration);
    const length = Math.max(0.01, this.duration * DIVISIONS[name]);
    let start;
    let end;

    if (this.direction === 1) {
      start = Math.min(anchor, Math.max(0, this.duration - length));
      end = Math.min(this.duration, start + length);
    } else {
      end = Math.max(anchor, Math.min(this.duration, length));
      start = Math.max(0, end - length);
    }

    this.loopDivision = name;
    return this.setLoop(start, end, at);
  }

  clearLoop(at = this.clock()) {
    if (this.duration === 0) return this.snapshot(at);
    this.loopDivision = '1 BAR';
    return this.setLoop(0, this.duration, at);
  }

  playbackPlan({ at = this.clock(), leadTime = 0.02 } = {}) {
    at = finite(at, 'plan time');
    leadTime = Math.max(0, finite(leadTime, 'lead time'));
    const position = this.position(at);
    const when = at + leadTime;
    const tracks = this.trackDurations.map((duration, index) => {
      if (duration === 0) return Object.freeze({ index, empty: true });
      return Object.freeze({
        index,
        empty: false,
        when,
        offset: modulo(position, duration),
        direction: this.direction,
        transportLoopStart: this.loopStart,
        transportLoopEnd: this.loopEnd,
      });
    });
    return Object.freeze({
      when,
      position,
      direction: this.direction,
      loopStart: this.loopStart,
      loopEnd: this.loopEnd,
      tracks: Object.freeze(tracks),
    });
  }

  snapshot(at = this.clock()) {
    return Object.freeze({
      playing: this.playing,
      position: this.position(at),
      duration: this.duration,
      direction: this.direction,
      loopStart: this.loopStart,
      loopEnd: this.loopEnd,
      loopDivision: this.loopDivision,
      trackDurations: Object.freeze([...this.trackDurations]),
    });
  }

  wrap(position) {
    if (this.duration === 0) return 0;
    const start = this.loopStart;
    const span = this.loopEnd - start;
    return span > 0 ? start + modulo(position - start, span) : 0;
  }
}
