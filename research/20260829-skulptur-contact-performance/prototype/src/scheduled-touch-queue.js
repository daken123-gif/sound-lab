const TYPES = new Set(["touch-begin", "touch-move", "touch-end"]);

function reject(message) { throw new TypeError(message); }

function normalizeCommand(input) {
  if (!input || typeof input !== "object" || Array.isArray(input)) reject("scheduled touch command must be an object");
  if (!TYPES.has(input.type)) reject("scheduled touch command type is invalid");
  if (!Number.isSafeInteger(input.pointerId) || input.pointerId < 0) reject("scheduled pointerId must be a non-negative safe integer");
  if (typeof input.timeSeconds !== "number" || !Number.isFinite(input.timeSeconds) || input.timeSeconds < 0) {
    reject("scheduled timeSeconds must be a non-negative finite number");
  }
  const command = { type: input.type, pointerId: input.pointerId, timeSeconds: input.timeSeconds };
  if (input.type !== "touch-end") {
    if (!Number.isInteger(input.band) || input.band < 0 || input.band > 9) reject("scheduled band must be 0..9");
    if (typeof input.position !== "number" || !Number.isFinite(input.position) || input.position < 0 || input.position > 1) {
      reject("scheduled position must be 0..1");
    }
    command.band = input.band;
    command.position = input.position;
  } else {
    command.throwMotion = input.throwMotion !== false;
  }
  return Object.freeze(command);
}

export function normalizeScheduledTouchBatch(scheduleId, commands) {
  if (typeof scheduleId !== "string" || scheduleId.length < 1 || scheduleId.length > 80) {
    reject("scheduleId must contain 1 to 80 characters");
  }
  if (!Array.isArray(commands) || commands.length === 0) reject("scheduled touch batch cannot be empty");
  const normalized = commands.map(normalizeCommand);
  const active = new Set();
  for (let index = 1; index < normalized.length; index += 1) {
    if (normalized[index].timeSeconds < normalized[index - 1].timeSeconds) {
      reject("scheduled touch commands must be in non-decreasing time order");
    }
  }
  for (const command of normalized) {
    if (command.type === "touch-begin") {
      if (active.has(command.pointerId)) reject("scheduled pointer cannot begin twice");
      active.add(command.pointerId);
    } else if (command.type === "touch-move") {
      if (!active.has(command.pointerId)) reject("scheduled move requires an active pointer");
    } else {
      if (!active.has(command.pointerId)) reject("scheduled end requires an active pointer");
      active.delete(command.pointerId);
    }
  }
  if (active.size > 0) reject("scheduled touch batch must end every pointer");
  return Object.freeze({ scheduleId, commands: Object.freeze(normalized) });
}

export class ScheduledTouchQueue {
  #items = [];
  #scheduleIds = new Set();
  #sequence = 0;

  enqueue(scheduleId, commands) {
    if (this.#scheduleIds.has(scheduleId)) reject("scheduleId is already active");
    const batch = normalizeScheduledTouchBatch(scheduleId, commands);
    this.#scheduleIds.add(scheduleId);
    this.#items.push(...batch.commands.map(command => ({ scheduleId, command, sequence: this.#sequence++ })));
    this.#items.sort((a, b) => a.command.timeSeconds - b.command.timeSeconds || a.sequence - b.sequence);
    return batch.commands.length;
  }

  drainDue(timeSeconds) {
    if (typeof timeSeconds !== "number" || !Number.isFinite(timeSeconds) || timeSeconds < 0) reject("drain time must be non-negative and finite");
    let count = 0;
    while (count < this.#items.length && this.#items[count].command.timeSeconds <= timeSeconds) count += 1;
    const due = this.#items.splice(0, count);
    const remainingScheduleIds = new Set(this.#items.map(item => item.scheduleId));
    for (const scheduleId of new Set(due.map(item => item.scheduleId))) {
      if (!remainingScheduleIds.has(scheduleId)) this.#scheduleIds.delete(scheduleId);
    }
    return Object.freeze(due.map(({ scheduleId, command }) => Object.freeze({ scheduleId, command })));
  }

  cancel(scheduleId) {
    const before = this.#items.length;
    this.#items = this.#items.filter(item => item.scheduleId !== scheduleId);
    this.#scheduleIds.delete(scheduleId);
    return before - this.#items.length;
  }

  get pendingCount() { return this.#items.length; }
}
