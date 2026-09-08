import { ContactGestureGate } from "./contact-gesture.js";

const POINTER_TYPES = new Set(["pointerdown", "pointermove", "pointerup", "pointercancel"]);

export class PointerContactAdapterError extends TypeError {
  constructor(code, message) {
    super(message);
    this.name = "PointerContactAdapterError";
    this.code = code;
  }
}

function reject(code, message) { throw new PointerContactAdapterError(code, message); }
function finite(value, field) {
  if (typeof value !== "number" || !Number.isFinite(value)) reject("POINTER_NUMBER", `${field} must be finite`);
  return value;
}
function rectOf(surface) {
  if (!surface || typeof surface.getBoundingClientRect !== "function") reject("SURFACE", "surface must provide getBoundingClientRect()");
  const rect = surface.getBoundingClientRect();
  for (const field of ["left", "top", "width", "height"]) finite(rect[field], `rect.${field}`);
  if (rect.width <= 0 || rect.height <= 0) reject("SURFACE_RECT", "surface width and height must be positive");
  return rect;
}
function normalizedPoint(event, rect) {
  const x = (finite(event.clientX, "clientX") - rect.left) / rect.width;
  const y = (finite(event.clientY, "clientY") - rect.top) / rect.height;
  if (x < 0 || x > 1 || y < 0 || y > 1) reject("POINTER_OUTSIDE_SURFACE", "pointer coordinates are outside the performance surface");
  return { x, y };
}
const defaultPressure = () => ({ pressure: null, pressureSource: "unavailable" });
const defaultContactArea = () => null;
function validatePressureReading(reading) {
  if (!reading || typeof reading !== "object") reject("PRESSURE_READING", "pressureResolver must return an object");
  return { pressure: reading.pressure, pressureSource: reading.pressureSource };
}
function eventPointerId(event) {
  if (!Number.isInteger(event.pointerId) || event.pointerId < 0) reject("POINTER_ID", "PointerEvent.pointerId must be a non-negative integer");
  return event.pointerId;
}

export class PointerContactAdapter {
  #surface; #resolveTrackIds; #pressureResolver; #contactAreaResolver; #gestureIdFactory;
  #gate = new ContactGestureGate(); #active = new Map(); #originTimeStamp = null; #serial = 0;

  constructor({ surface, resolveTrackIds, pressureResolver = defaultPressure, contactAreaResolver = defaultContactArea,
    gestureIdFactory = ({ pointerId, serial }) => `pointer-${pointerId}-${serial}` }) {
    if (typeof resolveTrackIds !== "function") reject("TRACK_RESOLVER", "resolveTrackIds must be a function");
    if (typeof pressureResolver !== "function") reject("PRESSURE_RESOLVER", "pressureResolver must be a function");
    if (typeof contactAreaResolver !== "function") reject("AREA_RESOLVER", "contactAreaResolver must be a function");
    if (typeof gestureIdFactory !== "function") reject("GESTURE_FACTORY", "gestureIdFactory must be a function");
    rectOf(surface);
    this.#surface = surface; this.#resolveTrackIds = resolveTrackIds; this.#pressureResolver = pressureResolver;
    this.#contactAreaResolver = contactAreaResolver; this.#gestureIdFactory = gestureIdFactory;
  }

  handle(event) {
    if (!event || !POINTER_TYPES.has(event.type)) reject("POINTER_EVENT", "Unsupported pointer event type");
    const pointerId = eventPointerId(event);
    if (event.type === "pointerdown") return this.#start(event, pointerId);
    const state = this.#active.get(pointerId);
    if (!state) return null;
    if (event.type === "pointercancel") return this.#cancelState(state, this.#relativeTime(event.timeStamp));
    if (event.type === "pointerup") return this.#finishFromEvent(event, state, "release");
    return this.#move(event, state);
  }

  handleLostPointerCapture(event) {
    const pointerId = eventPointerId(event);
    const state = this.#active.get(pointerId);
    return state ? this.#cancelState(state, this.#relativeTime(event.timeStamp)) : null;
  }
  cancelAll(timeStamp) {
    if (this.#active.size === 0) return [];
    const relative = this.#relativeTime(timeStamp);
    return [...this.#active.values()].sort((a, b) => a.pointerId - b.pointerId).map(state => this.#cancelState(state, relative));
  }
  cancelPointer(pointerId, timeStamp) {
    if (!Number.isInteger(pointerId) || pointerId < 0) reject("POINTER_ID", "pointerId must be a non-negative integer");
    const state = this.#active.get(pointerId);
    if (!state) return null;
    const requested = timeStamp === undefined ? state.timestampMs : this.#relativeTime(timeStamp);
    return this.#cancelState(state, requested);
  }
  activeCount() { return this.#active.size; }

  #relativeTime(timeStamp) {
    const absolute = finite(timeStamp, "timeStamp");
    if (absolute < 0) reject("TIMESTAMP", "timeStamp must be non-negative");
    if (this.#originTimeStamp === null) this.#originTimeStamp = absolute;
    if (absolute < this.#originTimeStamp) reject("TIMESTAMP_REGRESSION", "timeStamp cannot precede the adapter origin");
    return absolute - this.#originTimeStamp;
  }
  #start(event, pointerId) {
    if (this.#active.has(pointerId)) reject("POINTER_ALREADY_ACTIVE", `pointer ${pointerId} is already active`);
    const rect = rectOf(this.#surface); const point = normalizedPoint(event, rect);
    const timestampMs = this.#relativeTime(event.timeStamp);
    const gestureId = this.#gestureIdFactory({ pointerId, serial: ++this.#serial, event });
    const accepted = this.#gate.accept(this.#buildFrame({ event, pointerId, gestureId, phase: "contact", point, timestampMs, previous: null, rect }));
    this.#active.set(pointerId, { ...accepted }); return accepted;
  }
  #move(event, state) {
    const rect = rectOf(this.#surface); const point = normalizedPoint(event, rect);
    const timestampMs = this.#relativeTime(event.timeStamp);
    const pressureReading = validatePressureReading(this.#pressureResolver(event));
    const contactArea = this.#contactAreaResolver(event, rect);
    const moved = point.x !== state.x || point.y !== state.y;
    const pressed = pressureReading.pressure !== state.pressure || contactArea !== state.contactArea;
    if (!moved && !pressed) return null;
    const phase = moved ? "slide" : "press";
    const accepted = this.#gate.accept(this.#buildFrame({ event, pointerId: state.pointerId, gestureId: state.gestureId,
      phase, point, timestampMs, previous: state, rect, pressureReading, contactArea }));
    this.#active.set(state.pointerId, { ...accepted }); return accepted;
  }
  #finishFromEvent(event, state, phase) {
    const rect = rectOf(this.#surface); const point = normalizedPoint(event, rect);
    const timestampMs = this.#relativeTime(event.timeStamp);
    const accepted = this.#gate.accept(this.#buildFrame({ event, pointerId: state.pointerId, gestureId: state.gestureId,
      phase, point, timestampMs, previous: state, rect }));
    this.#active.delete(state.pointerId); return accepted;
  }
  #cancelState(state, requestedTimestamp) {
    const accepted = this.#gate.accept({ ...state, phase: "cancel", velocityX: 0, velocityY: 0,
      timestampMs: Math.max(state.timestampMs, requestedTimestamp) });
    this.#active.delete(state.pointerId); return accepted;
  }
  #buildFrame({ event, pointerId, gestureId, phase, point, timestampMs, previous, rect, pressureReading, contactArea }) {
    const pressure = pressureReading ?? validatePressureReading(this.#pressureResolver(event));
    const area = contactArea === undefined ? this.#contactAreaResolver(event, rect) : contactArea;
    const elapsedSeconds = previous ? (timestampMs - previous.timestampMs) / 1000 : 0;
    return {
      schemaVersion: "sound-lab.contact-gesture/v0.1", gestureId, pointerId, phase,
      trackIds: this.#resolveTrackIds({ x: point.x, y: point.y, pointerId, pointerType: event.pointerType, phase, event }),
      x: point.x, y: point.y, contactArea: area, pressure: pressure.pressure, pressureSource: pressure.pressureSource,
      velocityX: previous && elapsedSeconds > 0 ? (point.x - previous.x) / elapsedSeconds : 0,
      velocityY: previous && elapsedSeconds > 0 ? (point.y - previous.y) / elapsedSeconds : 0, timestampMs,
    };
  }
}

export function bindPointerContactSurface({ surface, scope = globalThis, onFrame, onError = error => { throw error; }, ...adapterOptions }) {
  if (!surface || typeof surface.addEventListener !== "function" || typeof surface.removeEventListener !== "function") reject("SURFACE_EVENTS", "surface must support event listeners");
  if (!scope || typeof scope.addEventListener !== "function" || typeof scope.removeEventListener !== "function") reject("SCOPE_EVENTS", "scope must support event listeners");
  if (typeof onFrame !== "function") reject("FRAME_CALLBACK", "onFrame must be a function");
  if (typeof onError !== "function") reject("ERROR_CALLBACK", "onError must be a function");
  const adapter = new PointerContactAdapter({ surface, ...adapterOptions });
  const emit = frame => { if (frame) onFrame(frame); };
  const safely = operation => event => { try { operation(event); } catch (error) { onError(error); } };
  const pointer = event => {
    try {
      emit(adapter.handle(event));
      if (event.type === "pointerdown" && typeof surface.setPointerCapture === "function") {
        try { surface.setPointerCapture(event.pointerId); } catch { /* capture is best effort */ }
      }
    } catch (error) {
      if ((event.type === "pointerup" || event.type === "pointercancel") && Number.isInteger(event.pointerId)) {
        try { emit(adapter.cancelPointer(event.pointerId, event.timeStamp)); } catch { /* report the original boundary failure */ }
      }
      onError(error);
    }
  };
  const lostCapture = safely(event => emit(adapter.handleLostPointerCapture(event)));
  const interrupt = safely(event => { for (const frame of adapter.cancelAll(event.timeStamp)) emit(frame); });
  const pointerTypes = ["pointerdown", "pointermove", "pointerup", "pointercancel"];
  const interruptionTypes = ["blur", "pagehide", "orientationchange", "visibilitychange"];
  for (const type of pointerTypes) surface.addEventListener(type, pointer);
  surface.addEventListener("lostpointercapture", lostCapture);
  for (const type of interruptionTypes) scope.addEventListener(type, interrupt);
  return { adapter, dispose() {
    for (const type of pointerTypes) surface.removeEventListener(type, pointer);
    surface.removeEventListener("lostpointercapture", lostCapture);
    for (const type of interruptionTypes) scope.removeEventListener(type, interrupt);
  } };
}
