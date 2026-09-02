const DECAY_PER_MS = 0.0005;
const HOLD_SUPPLY_PER_MS = DECAY_PER_MS;
const INPUT_ENERGY = 0.35;
const MAX_ENERGY = 1;
const HIT_RADIUS = 0.08;
const CUT_SPEED = 1.2;
const CUT_BOUNDARY = 0.04;

const clamp = (value, minimum, maximum) =>
  Math.min(maximum, Math.max(minimum, value));

const distance = (a, b) => Math.hypot(a.x - b.x, a.y - b.y);

function validateFrame(frame) {
  const phases = new Set(["contact", "press", "slide", "release", "cancel"]);
  if (frame.schemaVersion !== "sound-lab.contact-gesture/v0.1") {
    throw new Error("unsupported schemaVersion");
  }
  if (!phases.has(frame.phase)) throw new Error("invalid phase");
  if (!Number.isInteger(frame.pointerId) || frame.pointerId < 0) {
    throw new Error("invalid pointerId");
  }
  if (!Number.isFinite(frame.timestampMs) || frame.timestampMs < 0) {
    throw new Error("invalid timestampMs");
  }
  if (![frame.x, frame.y].every((value) => Number.isFinite(value) && value >= 0 && value <= 1)) {
    throw new Error("x/y out of range");
  }
  if (!Array.isArray(frame.trackIds) || frame.trackIds.length < 1 || frame.trackIds.length > 4) {
    throw new Error("invalid trackIds");
  }
  if (new Set(frame.trackIds).size !== frame.trackIds.length) {
    throw new Error("duplicate trackIds");
  }
  if (!frame.trackIds.every((id) => Number.isInteger(id) && id >= 0 && id <= 3)) {
    throw new Error("trackId out of range");
  }
  if (frame.pressureSource === "unavailable" && frame.pressure !== null) {
    throw new Error("unavailable pressure must be null");
  }
}

export class ContactCausalField {
  constructor() {
    this.timeMs = 0;
    this.nextNodeId = 1;
    this.nodes = new Map();
    this.edges = new Map();
    this.claims = new Map();
    this.audioEvents = [];
    this.floor = "absent";
    this.hadStructure = false;
  }

  process(frame) {
    validateFrame(frame);
    this.advanceTo(frame.timestampMs);

    if (frame.phase === "contact") this.#contact(frame);
    if (frame.phase === "press") this.#press(frame);
    if (frame.phase === "slide") this.#slide(frame);
    if (frame.phase === "release" || frame.phase === "cancel") this.#release(frame);

    return this.snapshot();
  }

  processAll(frames) {
    return frames.map((frame) => this.process(frame));
  }

  advanceTo(timestampMs) {
    if (timestampMs < this.timeMs) throw new Error("timestamp moved backwards");
    const elapsed = timestampMs - this.timeMs;
    if (elapsed === 0) return this.snapshot();

    for (const node of this.nodes.values()) {
      const holding = [...this.claims.values()].some(
        (claim) => claim.active && claim.nodeId === node.id,
      );
      const supplied = holding ? elapsed * HOLD_SUPPLY_PER_MS : 0;
      const previous = node.energy;
      node.energy = clamp(node.energy + supplied - elapsed * DECAY_PER_MS, 0, MAX_ENERGY);
      if (!holding && previous > 0 && node.energy === 0 && node.audible) {
        node.audible = false;
        this.#emit("decay-stop", node, timestampMs, null);
      }
    }

    this.timeMs = timestampMs;
    this.#deriveFloor();
    return this.snapshot();
  }

  snapshot() {
    return {
      timestampMs: this.timeMs,
      floor: this.floor,
      claims: [...this.claims.values()].map((claim) => ({ ...claim })),
      nodes: [...this.nodes.values()].map((node) => ({ ...node, trackIds: [...node.trackIds] })),
      edges: [...this.edges.values()].map((edge) => ({ ...edge })),
      audioEvents: this.audioEvents.map((event) => ({ ...event, trackIds: [...event.trackIds] })),
    };
  }

  #contact(frame) {
    if (this.claims.get(frame.pointerId)?.active) throw new Error("pointer already active");
    const previousFloor = this.floor;
    const ghost = this.#nearestNode(frame, (node) => !node.audible);
    let node;
    let action;

    if (ghost && distance(frame, ghost) <= HIT_RADIUS) {
      node = ghost;
      node.audible = true;
      node.energy = clamp(node.energy + INPUT_ENERGY, 0, MAX_ENERGY);
      node.x = frame.x;
      node.y = frame.y;
      action = "reveal";
    } else {
      node = {
        id: `node-${this.nextNodeId++}`,
        x: frame.x,
        y: frame.y,
        energy: INPUT_ENERGY,
        audible: true,
        trackIds: [...frame.trackIds],
        clockOffset: 0,
        pitchRelation: 0,
      };
      const neighbour = this.#nearestNode(frame, (candidate) => candidate.audible);
      this.nodes.set(node.id, node);
      if (neighbour) this.#connect(neighbour, node, frame.timestampMs);
      action = "enter";
    }

    this.claims.set(frame.pointerId, {
      contactId: frame.pointerId,
      gestureId: frame.gestureId,
      nodeId: node.id,
      target: "node",
      phase: "enter",
      active: true,
      causalEnergy: node.energy,
      lastX: frame.x,
      lastY: frame.y,
    });
    this.hadStructure = true;
    this.#emit(action, node, frame.timestampMs, frame);
    this.#deriveFloor(previousFloor === "broken" ? "rebuilt" : null);
  }

  #press(frame) {
    const { claim, node } = this.#active(frame.pointerId);
    claim.phase = "hold";
    node.energy = clamp(node.energy + INPUT_ENERGY * 0.5, 0, MAX_ENERGY);
    claim.causalEnergy = node.energy;
    this.#emit("hold", node, frame.timestampMs, frame);
    this.#deriveFloor();
  }

  #slide(frame) {
    const { claim, node } = this.#active(frame.pointerId);
    const dx = frame.x - claim.lastX;
    const dy = frame.y - claim.lastY;
    const speed = Math.hypot(frame.velocityX, frame.velocityY);
    claim.lastX = frame.x;
    claim.lastY = frame.y;
    claim.phase = "deform";
    node.x = frame.x;
    node.y = frame.y;
    node.energy = clamp(node.energy + INPUT_ENERGY * Math.min(1, Math.hypot(dx, dy) * 5), 0, MAX_ENERGY);
    claim.causalEnergy = node.energy;

    const atBoundary =
      frame.x <= CUT_BOUNDARY || frame.x >= 1 - CUT_BOUNDARY ||
      frame.y <= CUT_BOUNDARY || frame.y >= 1 - CUT_BOUNDARY;
    if (atBoundary && speed >= CUT_SPEED) {
      node.audible = false;
      node.energy = Math.min(node.energy, 0.2);
      claim.phase = "cut";
      this.#emit("cut", node, frame.timestampMs, frame);
    } else {
      node.clockOffset = clamp(node.clockOffset + dx * 0.25, -0.25, 0.25);
      node.pitchRelation = clamp(node.pitchRelation - dy * 12, -24, 24);
      this.#emit("deform", node, frame.timestampMs, frame, { dx, dy });
    }
    this.#deriveFloor(atBoundary ? null : "tensioned");
  }

  #release(frame) {
    const { claim, node } = this.#active(frame.pointerId);
    claim.phase = "release";
    claim.active = false;
    claim.causalEnergy = node.energy;
    this.#emit(frame.phase === "cancel" ? "cancel" : "release-tail", node, frame.timestampMs, frame);
    this.#deriveFloor();
  }

  #active(pointerId) {
    const claim = this.claims.get(pointerId);
    if (!claim?.active) throw new Error("pointer is not active");
    const node = this.nodes.get(claim.nodeId);
    return { claim, node };
  }

  #nearestNode(point, predicate) {
    let nearest = null;
    let nearestDistance = Infinity;
    for (const node of this.nodes.values()) {
      if (!predicate(node)) continue;
      const candidateDistance = distance(point, node);
      if (candidateDistance < nearestDistance) {
        nearest = node;
        nearestDistance = candidateDistance;
      }
    }
    return nearest;
  }

  #connect(a, b, timestampMs) {
    const id = [a.id, b.id].sort().join("--");
    this.edges.set(id, {
      id,
      from: a.id,
      to: b.id,
      createdAtMs: timestampMs,
      memory: true,
      coupling: 1,
    });
  }

  #emit(type, node, timestampMs, frame, extra = {}) {
    this.audioEvents.push({
      type,
      timestampMs,
      nodeId: node.id,
      gestureId: frame?.gestureId ?? null,
      pointerId: frame?.pointerId ?? null,
      trackIds: [...node.trackIds],
      energy: node.energy,
      ...extra,
    });
  }

  #deriveFloor(override = null) {
    if (override) {
      this.floor = override;
      return;
    }
    const audible = [...this.nodes.values()].filter((node) => node.audible).length;
    if (audible === 0) this.floor = this.hadStructure ? "broken" : "absent";
    else if (audible === 1) this.floor = "forming";
    else this.floor = "held";
  }
}

