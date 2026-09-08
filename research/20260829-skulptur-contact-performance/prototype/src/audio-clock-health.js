const defaultWait = delayMs => new Promise(resolve => setTimeout(resolve, delayMs));

export async function audioClockAdvanced(context, {
  delayMs = 120,
  minimumAdvanceSeconds = 0.01,
  wait = defaultWait
} = {}) {
  if (!context || typeof context.currentTime !== "number" || typeof context.state !== "string") {
    throw new TypeError("an AudioContext-like clock is required");
  }
  if (!Number.isFinite(delayMs) || delayMs < 0) throw new RangeError("delayMs must be non-negative and finite");
  if (!Number.isFinite(minimumAdvanceSeconds) || minimumAdvanceSeconds < 0) {
    throw new RangeError("minimumAdvanceSeconds must be non-negative and finite");
  }
  if (typeof wait !== "function") throw new TypeError("wait must be a function");
  if (context.state !== "running") return false;
  const before = context.currentTime;
  await wait(delayMs);
  if (context.state !== "running") return false;
  const after = context.currentTime;
  return Number.isFinite(after) && after - before >= minimumAdvanceSeconds;
}
