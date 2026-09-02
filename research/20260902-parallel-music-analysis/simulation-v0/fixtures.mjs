export function frame(pointerId, phase, timestampMs, overrides = {}) {
  return {
    schemaVersion: "sound-lab.contact-gesture/v0.1",
    gestureId: `gesture-${pointerId}`,
    pointerId,
    phase,
    trackIds: [pointerId % 4],
    x: 0.15 + pointerId * 0.13,
    y: 0.3 + (pointerId % 2) * 0.25,
    contactArea: null,
    pressure: null,
    pressureSource: "unavailable",
    velocityX: 0,
    velocityY: 0,
    timestampMs,
    ...overrides,
  };
}

export function simultaneousContacts(count) {
  return Array.from({ length: count }, (_, index) =>
    frame(index, "contact", index * 10),
  );
}

export const releaseAndDecay = [
  frame(0, "contact", 0, { x: 0.4, y: 0.4 }),
  frame(0, "slide", 100, { x: 0.46, y: 0.36, velocityX: 0.6, velocityY: -0.4 }),
  frame(0, "release", 200, { x: 0.46, y: 0.36 }),
];

export const breakAndRebuild = [
  frame(0, "contact", 0, { x: 0.5, y: 0.5 }),
  frame(0, "slide", 100, { x: 0.99, y: 0.5, velocityX: 2, velocityY: 0 }),
  frame(0, "release", 110, { x: 0.99, y: 0.5 }),
  frame(1, "contact", 180, { x: 0.99, y: 0.5 }),
];

