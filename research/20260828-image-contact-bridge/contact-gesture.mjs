const SCHEMA_VERSION = "sound-lab.contact-gesture/v0.1";
const PHASES = new Set(["contact", "press", "slide", "release", "cancel"]);
const PRESSURE_SOURCES = new Set(["hardware", "estimated", "unavailable"]);
const REQUIRED_KEYS = Object.freeze([
  "schemaVersion", "gestureId", "pointerId", "phase", "trackIds", "x", "y",
  "contactArea", "pressure", "pressureSource", "velocityX", "velocityY", "timestampMs",
]);
const ALLOWED_KEYS = new Set(REQUIRED_KEYS);

const NEXT_PHASES = Object.freeze({
  contact: new Set(["press", "slide", "release", "cancel"]),
  press: new Set(["press", "slide", "release", "cancel"]),
  slide: new Set(["press", "slide", "release", "cancel"]),
});

export class ContactGestureError extends TypeError {
  constructor(code, message) {
    super(message);
    this.name = "ContactGestureError";
    this.code = code;
  }
}

function reject(code, message) {
  throw new ContactGestureError(code, message);
}

function requirePlainObject(value) {
  if (value === null || typeof value !== "object" || Array.isArray(value)) {
    reject("FRAME_TYPE", "ContactGestureFrame must be a plain object");
  }
  const prototype = Object.getPrototypeOf(value);
  if (prototype !== Object.prototype && prototype !== null) {
    reject("FRAME_TYPE", "ContactGestureFrame must be a plain object");
  }
}

function validateKeys(frame) {
  for (const key of REQUIRED_KEYS) {
    if (!Object.hasOwn(frame, key)) reject("MISSING_FIELD", `Missing required field: ${key}`);
  }
  for (const key of Object.keys(frame)) {
    if (!ALLOWED_KEYS.has(key)) reject("UNKNOWN_FIELD", `Unknown field: ${key}`);
  }
}

function finiteNumber(value, field) {
  if (typeof value !== "number" || !Number.isFinite(value)) {
    reject("NUMBER", `${field} must be a finite number`);
  }
  return value;
}

function unitNumber(value, field) {
  finiteNumber(value, field);
  if (value < 0 || value > 1) reject("UNIT_RANGE", `${field} must be between 0 and 1`);
  return value;
}

function optionalUnitNumber(value, field) {
  return value === null ? null : unitNumber(value, field);
}

function normalizeTrackIds(trackIds) {
  if (!Array.isArray(trackIds) || trackIds.length < 1 || trackIds.length > 4) {
    reject("TRACK_COUNT", "trackIds must contain one to four tracks");
  }
  const seen = new Set();
  for (const trackId of trackIds) {
    if (!Number.isInteger(trackId) || trackId < 0 || trackId > 3) {
      reject("TRACK_ID", "trackIds must contain only integers from 0 through 3");
    }
    if (seen.has(trackId)) reject("TRACK_DUPLICATE", `Duplicate trackId: ${trackId}`);
    seen.add(trackId);
  }
  return Object.freeze([...seen].sort((a, b) => a - b));
}

export function normalizeContactGestureFrame(input) {
  requirePlainObject(input);
  validateKeys(input);

  if (input.schemaVersion !== SCHEMA_VERSION) {
    reject("SCHEMA_VERSION", `schemaVersion must be ${SCHEMA_VERSION}`);
  }
  if (typeof input.gestureId !== "string" || input.gestureId.length < 1 || input.gestureId.length > 128) {
    reject("GESTURE_ID", "gestureId must contain 1 to 128 characters");
  }
  if (!Number.isInteger(input.pointerId) || input.pointerId < 0) {
    reject("POINTER_ID", "pointerId must be a non-negative integer");
  }
  if (!PHASES.has(input.phase)) reject("PHASE", `Unknown phase: ${input.phase}`);
  if (!PRESSURE_SOURCES.has(input.pressureSource)) {
    reject("PRESSURE_SOURCE", `Unknown pressureSource: ${input.pressureSource}`);
  }

  const pressure = optionalUnitNumber(input.pressure, "pressure");
  if (input.pressureSource === "unavailable" && pressure !== null) {
    reject("PRESSURE_PROVENANCE", "pressure must be null when pressureSource is unavailable");
  }
  if (input.pressureSource !== "unavailable" && pressure === null) {
    reject("PRESSURE_PROVENANCE", "pressure must be numeric for hardware or estimated sources");
  }

  const timestampMs = finiteNumber(input.timestampMs, "timestampMs");
  if (timestampMs < 0) reject("TIMESTAMP", "timestampMs must be non-negative");

  return Object.freeze({
    schemaVersion: SCHEMA_VERSION,
    gestureId: input.gestureId,
    pointerId: input.pointerId,
    phase: input.phase,
    trackIds: normalizeTrackIds(input.trackIds),
    x: unitNumber(input.x, "x"),
    y: unitNumber(input.y, "y"),
    contactArea: optionalUnitNumber(input.contactArea, "contactArea"),
    pressure,
    pressureSource: input.pressureSource,
    velocityX: finiteNumber(input.velocityX, "velocityX"),
    velocityY: finiteNumber(input.velocityY, "velocityY"),
    timestampMs,
  });
}

function sequenceKey(frame) {
  return `${frame.gestureId}\u0000${frame.pointerId}`;
}

export class ContactGestureGate {
  #states = new Map();

  accept(input) {
    const frame = normalizeContactGestureFrame(input);
    const key = sequenceKey(frame);
    const state = this.#states.get(key);

    if (!state) {
      if (frame.phase !== "contact") {
        reject("PHASE_START", "A gesture sequence must start with contact");
      }
      this.#states.set(key, { phase: frame.phase, timestampMs: frame.timestampMs, terminal: false });
      return frame;
    }

    if (state.terminal) reject("PHASE_TERMINAL", "A released or cancelled gesture cannot resume");
    if (frame.timestampMs < state.timestampMs) {
      reject("TIMESTAMP_REGRESSION", "timestampMs cannot move backwards within a gesture");
    }
    if (!NEXT_PHASES[state.phase]?.has(frame.phase)) {
      reject("PHASE_TRANSITION", `Invalid phase transition: ${state.phase} -> ${frame.phase}`);
    }

    this.#states.set(key, {
      phase: frame.phase,
      timestampMs: frame.timestampMs,
      terminal: frame.phase === "release" || frame.phase === "cancel",
    });
    return frame;
  }

  stateFor(gestureId, pointerId) {
    const state = this.#states.get(`${gestureId}\u0000${pointerId}`);
    return state ? Object.freeze({ ...state }) : null;
  }

  clear(gestureId, pointerId) {
    return this.#states.delete(`${gestureId}\u0000${pointerId}`);
  }

  clearAll() {
    this.#states.clear();
  }
}

export const CONTACT_GESTURE_SCHEMA_VERSION = SCHEMA_VERSION;
