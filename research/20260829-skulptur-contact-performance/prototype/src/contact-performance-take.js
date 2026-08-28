import { ContactGestureGate, normalizeContactGestureFrame } from "./contact-gesture.js";

const TAKE_SCHEMA_VERSION = "skulptur.contact-performance-take/v0.1";
const TAKE_KEYS = new Set(["schemaVersion", "durationMs", "frames"]);

export class ContactPerformanceTakeError extends TypeError {
  constructor(code, message) {
    super(message);
    this.name = "ContactPerformanceTakeError";
    this.code = code;
  }
}

function reject(code, message) { throw new ContactPerformanceTakeError(code, message); }
function keyOf(frame) { return `${frame.gestureId}\u0000${frame.pointerId}`; }

function freezeTake(frames, durationMs) {
  return Object.freeze({
    schemaVersion: TAKE_SCHEMA_VERSION,
    durationMs,
    frames: Object.freeze([...frames]),
  });
}

export class ContactPerformanceTakeRecorder {
  #gate = new ContactGestureGate();
  #frames = [];
  #open = new Set();
  #originTimestampMs = null;
  #lastTimestampMs = null;

  capture(input) {
    const source = normalizeContactGestureFrame(input);
    if (this.#lastTimestampMs !== null && source.timestampMs < this.#lastTimestampMs) {
      reject("TAKE_TIME_REGRESSION", "frames must be captured in non-decreasing timestamp order");
    }
    if (this.#originTimestampMs === null) this.#originTimestampMs = source.timestampMs;
    const frame = this.#gate.accept({ ...source, timestampMs: source.timestampMs - this.#originTimestampMs });
    const key = keyOf(frame);
    if (frame.phase === "contact") this.#open.add(key);
    if (frame.phase === "release" || frame.phase === "cancel") this.#open.delete(key);
    this.#frames.push(frame);
    this.#lastTimestampMs = source.timestampMs;
    return frame;
  }

  finish() {
    if (this.#frames.length === 0) reject("TAKE_EMPTY", "a contact performance take cannot be empty");
    if (this.#open.size > 0) reject("TAKE_INCOMPLETE", "every contact must end with release or cancel");
    return freezeTake(this.#frames, this.#frames.at(-1).timestampMs);
  }

  get frameCount() { return this.#frames.length; }
  get activeGestureCount() { return this.#open.size; }
}

export function normalizeContactPerformanceTake(input) {
  if (!input || typeof input !== "object" || Array.isArray(input)) reject("TAKE_TYPE", "take must be a plain object");
  for (const key of ["schemaVersion", "durationMs", "frames"]) {
    if (!Object.hasOwn(input, key)) reject("TAKE_FIELD", `missing take field: ${key}`);
  }
  for (const key of Object.keys(input)) {
    if (!TAKE_KEYS.has(key)) reject("TAKE_FIELD", `unknown take field: ${key}`);
  }
  if (input.schemaVersion !== TAKE_SCHEMA_VERSION) reject("TAKE_VERSION", `schemaVersion must be ${TAKE_SCHEMA_VERSION}`);
  if (!Array.isArray(input.frames) || input.frames.length === 0) reject("TAKE_EMPTY", "frames must be a non-empty array");
  if (typeof input.durationMs !== "number" || !Number.isFinite(input.durationMs) || input.durationMs < 0) {
    reject("TAKE_DURATION", "durationMs must be a non-negative finite number");
  }

  const gate = new ContactGestureGate();
  const open = new Set();
  const frames = [];
  let lastTimestampMs = -Infinity;
  for (const candidate of input.frames) {
    const frame = gate.accept(candidate);
    if (frame.timestampMs < lastTimestampMs) reject("TAKE_TIME_REGRESSION", "take frames must be globally ordered");
    if (frame.phase === "contact") open.add(keyOf(frame));
    if (frame.phase === "release" || frame.phase === "cancel") open.delete(keyOf(frame));
    frames.push(frame);
    lastTimestampMs = frame.timestampMs;
  }
  if (frames[0].timestampMs !== 0) reject("TAKE_ORIGIN", "the first take frame must start at timestampMs 0");
  if (open.size > 0) reject("TAKE_INCOMPLETE", "every contact must end with release or cancel");
  if (input.durationMs !== frames.at(-1).timestampMs) reject("TAKE_DURATION", "durationMs must equal the final frame timestamp");
  return freezeTake(frames, input.durationMs);
}

export function instantiateContactPerformanceTake(input, {
  startTimestampMs = 0,
  instanceId = "replay",
  pointerIdBase = 1_000_000_000,
} = {}) {
  const take = normalizeContactPerformanceTake(input);
  if (typeof startTimestampMs !== "number" || !Number.isFinite(startTimestampMs) || startTimestampMs < 0) {
    reject("REPLAY_START", "startTimestampMs must be a non-negative finite number");
  }
  if (typeof instanceId !== "string" || instanceId.length < 1 || instanceId.length > 80) {
    reject("REPLAY_ID", "instanceId must contain 1 to 80 characters");
  }
  if (!Number.isSafeInteger(pointerIdBase) || pointerIdBase < 0) {
    reject("REPLAY_POINTER", "pointerIdBase must be a non-negative safe integer");
  }
  const gestureIds = new Map();
  const pointerIds = new Map();
  let serial = 0;
  return Object.freeze(take.frames.map(frame => {
    const sourceKey = keyOf(frame);
    if (!gestureIds.has(sourceKey)) {
      gestureIds.set(sourceKey, `take-${instanceId}-${++serial}`);
      pointerIds.set(sourceKey, pointerIdBase + serial - 1);
    }
    return normalizeContactGestureFrame({
      ...frame,
      gestureId: gestureIds.get(sourceKey),
      pointerId: pointerIds.get(sourceKey),
      timestampMs: startTimestampMs + frame.timestampMs,
    });
  }));
}

export class ContactPerformanceTakePlayer {
  #onFrame;
  #onFinish;
  #frames = [];
  #cursor = 0;
  #active = new Map();
  #lastAdvanceTimestampMs = null;
  #playing = false;

  constructor({ onFrame, onFinish = () => {} }) {
    if (typeof onFrame !== "function") reject("PLAYER_CALLBACK", "onFrame must be a function");
    if (typeof onFinish !== "function") reject("PLAYER_CALLBACK", "onFinish must be a function");
    this.#onFrame = onFrame;
    this.#onFinish = onFinish;
  }

  start(input, options = {}) {
    if (this.#playing) reject("PLAYER_ACTIVE", "stop the current take before starting another");
    this.#frames = instantiateContactPerformanceTake(input, options);
    this.#cursor = 0;
    this.#active.clear();
    this.#lastAdvanceTimestampMs = options.startTimestampMs ?? 0;
    this.#playing = true;
    return this.#frames.length;
  }

  advance(timestampMs) {
    if (!this.#playing) return 0;
    if (typeof timestampMs !== "number" || !Number.isFinite(timestampMs) || timestampMs < this.#lastAdvanceTimestampMs) {
      reject("PLAYER_TIME", "player time must be finite and monotonic");
    }
    this.#lastAdvanceTimestampMs = timestampMs;
    let emitted = 0;
    while (this.#cursor < this.#frames.length && this.#frames[this.#cursor].timestampMs <= timestampMs) {
      const frame = this.#frames[this.#cursor++];
      this.#onFrame(frame);
      const key = keyOf(frame);
      if (frame.phase === "release" || frame.phase === "cancel") this.#active.delete(key);
      else this.#active.set(key, frame);
      emitted += 1;
    }
    if (this.#cursor === this.#frames.length) {
      this.#playing = false;
      this.#onFinish();
    }
    return emitted;
  }

  stop(timestampMs = this.#lastAdvanceTimestampMs ?? 0) {
    if (!this.#playing) return Object.freeze([]);
    if (typeof timestampMs !== "number" || !Number.isFinite(timestampMs) || timestampMs < 0) {
      reject("PLAYER_TIME", "stop time must be a non-negative finite number");
    }
    const cancelled = [...this.#active.values()]
      .sort((a, b) => a.pointerId - b.pointerId)
      .map(frame => normalizeContactGestureFrame({
        ...frame,
        phase: "cancel",
        velocityX: 0,
        velocityY: 0,
        timestampMs: Math.max(frame.timestampMs, timestampMs),
      }));
    this.#playing = false;
    this.#frames = [];
    this.#cursor = 0;
    this.#active.clear();
    this.#lastAdvanceTimestampMs = timestampMs;
    for (const frame of cancelled) this.#onFrame(frame);
    return Object.freeze(cancelled);
  }

  get isPlaying() { return this.#playing; }
  get pendingFrameCount() { return this.#frames.length - this.#cursor; }
  get activeGestureCount() { return this.#active.size; }
}

export const CONTACT_PERFORMANCE_TAKE_SCHEMA_VERSION = TAKE_SCHEMA_VERSION;
