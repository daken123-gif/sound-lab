export class BodyLevelWatchdog {
  constructor(staleAfterMs = 2000) {
    if (!Number.isFinite(staleAfterMs) || staleAfterMs <= 0) {
      throw new RangeError("staleAfterMs must be positive");
    }
    this.staleAfterMs = staleAfterMs;
    this.reset();
  }

  start(now) {
    this.#requireTime(now);
    this.startedAt = now;
    this.lastReportAt = null;
  }

  mark(now) {
    this.#requireTime(now);
    if (this.startedAt === null) this.startedAt = now;
    this.lastReportAt = now;
  }

  state(now) {
    this.#requireTime(now);
    if (this.startedAt === null) return "idle";
    const anchor = this.lastReportAt ?? this.startedAt;
    if (now - anchor >= this.staleAfterMs) return "stalled";
    return this.lastReportAt === null ? "waiting" : "active";
  }

  reset() {
    this.startedAt = null;
    this.lastReportAt = null;
  }

  #requireTime(now) {
    if (!Number.isFinite(now)) throw new TypeError("time must be finite");
  }
}
