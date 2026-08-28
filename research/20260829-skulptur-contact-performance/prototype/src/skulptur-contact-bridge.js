import { normalizeContactGestureFrame } from "./contact-gesture.js";

export function skulpturCommandFromContactFrame(input) {
  const frame = normalizeContactGestureFrame(input);
  const base = Object.freeze({
    gestureId: frame.gestureId,
    pointerId: frame.pointerId,
    trackIds: frame.trackIds,
    phase: frame.phase,
    timestampMs: frame.timestampMs,
  });
  if (frame.phase === "release" || frame.phase === "cancel") {
    return Object.freeze({ ...base, type: "end", throwMotion: frame.phase === "release" });
  }
  return Object.freeze({
    ...base,
    type: frame.phase === "contact" ? "begin" : "move",
    band: Math.min(9, Math.floor(frame.x * 10)),
    position: 1 - frame.y,
    pressure: frame.pressure,
    pressureSource: frame.pressureSource,
    contactArea: frame.contactArea,
  });
}
