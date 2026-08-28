const EVENT_TYPES = new Set([
  'grab-start',
  'grab-end',
  'loop-position',
  'loop-length',
  'direction',
  'kaoss',
  'fx-preset',
]);

const CONTINUOUS_TYPES = new Set(['loop-position', 'loop-length', 'kaoss']);

function assertFinite(value, label) {
  if (!Number.isFinite(value)) throw new TypeError(`${label} must be finite`);
  return value;
}

function copyValue(value) {
  if (value === undefined) return null;
  if (value === null || typeof value !== 'object') return value;
  return structuredClone(value);
}

function sameTarget(a, b) {
  return (a?.target ?? null) === (b?.target ?? null);
}

export const PERFORMANCE_EVENT_TYPES = Object.freeze([...EVENT_TYPES]);

/**
 * Records non-destructive performance gestures against the shared transport.
 * Calling record() never arms recording; start() must be called explicitly.
 */
export class PerformanceTakeRecorder {
  constructor({ clock = () => performance.now(), minimumContinuousIntervalMs = 16 } = {}) {
    if (typeof clock !== 'function') throw new TypeError('clock must be a function');
    this.clock = clock;
    this.minimumContinuousIntervalMs = Math.max(
      0,
      assertFinite(minimumContinuousIntervalMs, 'minimumContinuousIntervalMs'),
    );
    this.recording = false;
    this.nextId = 1;
    this.events = [];
  }

  start({ replace = false } = {}) {
    if (replace) this.clear();
    this.recording = true;
    return this.snapshot();
  }

  stop() {
    this.recording = false;
    return this.snapshot();
  }

  record(type, value, transportTime) {
    if (!this.recording) return null;
    if (!EVENT_TYPES.has(type)) throw new RangeError(`unknown performance event: ${type}`);

    const time = Math.max(0, assertFinite(transportTime, 'transportTime'));
    const capturedAt = assertFinite(this.clock(), 'clock result');
    const copiedValue = copyValue(value);
    const previous = this.events.at(-1);

    if (
      previous &&
      CONTINUOUS_TYPES.has(type) &&
      previous.type === type &&
      sameTarget(previous.value, copiedValue) &&
      capturedAt - previous.capturedAt < this.minimumContinuousIntervalMs
    ) {
      previous.time = time;
      previous.value = copiedValue;
      return this.copyEvent(previous);
    }

    const event = {
      id: this.nextId++,
      type,
      time,
      value: copiedValue,
      capturedAt,
      muted: false,
    };
    this.events.push(event);
    return this.copyEvent(event);
  }

  setMuted(id, muted = true) {
    const event = this.events.find(item => item.id === id);
    if (!event) return false;
    event.muted = Boolean(muted);
    return true;
  }

  remove(id) {
    const index = this.events.findIndex(item => item.id === id);
    if (index < 0) return false;
    this.events.splice(index, 1);
    return true;
  }

  clear() {
    this.events.length = 0;
    this.nextId = 1;
  }

  snapshot({ includeMuted = true } = {}) {
    const events = includeMuted ? this.events : this.events.filter(event => !event.muted);
    return Object.freeze({
      recording: this.recording,
      events: Object.freeze(events.map(event => Object.freeze(this.copyEvent(event)))),
    });
  }

  copyEvent(event) {
    return { ...event, value: copyValue(event.value) };
  }
}
