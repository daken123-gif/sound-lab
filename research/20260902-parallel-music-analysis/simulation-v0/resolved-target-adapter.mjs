const CONTACT_PHASES = new Set(["contact", "press", "slide", "release", "cancel"]);

const freezeEnvelope = (value) => {
  Object.freeze(value.source.trackIds);
  Object.freeze(value.source);
  Object.freeze(value.target);
  return Object.freeze(value);
};

const pointDistance = (a, b) => Math.hypot(a.x - b.x, a.y - b.y);

function segmentDistance(point, start, end) {
  const dx = end.x - start.x;
  const dy = end.y - start.y;
  const lengthSquared = dx * dx + dy * dy;
  if (lengthSquared === 0) return pointDistance(point, start);
  const projection = ((point.x - start.x) * dx + (point.y - start.y) * dy) / lengthSquared;
  const t = Math.max(0, Math.min(1, projection));
  return pointDistance(point, { x: start.x + t * dx, y: start.y + t * dy });
}

function assertRoutableFrame(frame) {
  if (!CONTACT_PHASES.has(frame.phase)) throw new Error("invalid phase");
  if (!Number.isInteger(frame.pointerId) || frame.pointerId < 0) throw new Error("invalid pointerId");
  if (![frame.x, frame.y].every((value) => Number.isFinite(value) && value >= 0 && value <= 1)) {
    throw new Error("x/y out of range");
  }
}

export class ResolvedTargetAdapter {
  constructor({ nodeRadius = 0.08, edgeRadius = 0.04 } = {}) {
    this.nodeRadius = nodeRadius;
    this.edgeRadius = edgeRadius;
    this.bindings = new Map();
    this.nextResolution = 1;
  }

  resolve(frame, surface) {
    assertRoutableFrame(frame);
    const source = structuredClone(frame);
    let binding;
    let method;

    if (frame.phase === "contact") {
      if (this.bindings.has(frame.pointerId)) throw new Error("pointer already bound");
      binding = {
        resolutionId: `target-${this.nextResolution++}`,
        target: this.#hitTest(frame, surface),
      };
      this.bindings.set(frame.pointerId, binding);
      method = "single-hit-test";
    } else {
      binding = this.bindings.get(frame.pointerId);
      if (!binding) throw new Error("pointer has no resolved target");
      method = "bound-claim";
    }

    const envelope = freezeEnvelope({
      schemaVersion: "sound-lab.resolved-contact/v0.1",
      resolutionId: binding.resolutionId,
      source,
      target: { ...binding.target },
      resolutionMethod: method,
    });

    if (frame.phase === "release" || frame.phase === "cancel") {
      this.bindings.delete(frame.pointerId);
    }
    return envelope;
  }

  #hitTest(point, surface) {
    const nodes = surface?.nodes ?? [];
    const edges = surface?.edges ?? [];
    let nodeHit = null;
    let nodeDistance = Infinity;

    for (const node of nodes) {
      if (node.visible === false) continue;
      const candidate = pointDistance(point, node);
      if (candidate <= this.nodeRadius && candidate < nodeDistance) {
        nodeHit = node;
        nodeDistance = candidate;
      }
    }
    if (nodeHit) return { kind: "node", id: nodeHit.id };

    const nodeById = new Map(nodes.map((node) => [node.id, node]));
    let edgeHit = null;
    let edgeDistance = Infinity;
    for (const edge of edges) {
      if (edge.visible === false) continue;
      const start = nodeById.get(edge.from);
      const end = nodeById.get(edge.to);
      if (!start || !end) continue;
      const candidate = segmentDistance(point, start, end);
      if (candidate <= this.edgeRadius && candidate < edgeDistance) {
        edgeHit = edge;
        edgeDistance = candidate;
      }
    }
    if (edgeHit) return { kind: "edge", id: edgeHit.id };
    return { kind: "empty", id: null };
  }
}

