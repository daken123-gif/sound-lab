import test from "node:test";
import assert from "node:assert/strict";

import { ContactCausalField } from "./contact-causal-field.mjs";
import { breakAndRebuild, frame, releaseAndDecay, simultaneousContacts } from "./fixtures.mjs";

test("1、3、5接触を固定上限なしで受理する", () => {
  for (const count of [1, 3, 5]) {
    const field = new ContactCausalField();
    field.processAll(simultaneousContacts(count));
    const state = field.snapshot();
    assert.equal(state.claims.filter((claim) => claim.active).length, count);
    assert.equal(state.nodes.filter((node) => node.audible).length, count);
    assert.equal(state.edges.length, Math.max(0, count - 1));
    assert.equal(state.floor, count === 1 ? "forming" : "held");
  }
});

test("同じ入力列は同じ状態と可聴event列を返す", () => {
  const input = simultaneousContacts(5);
  const first = new ContactCausalField();
  const second = new ContactCausalField();
  first.processAll(input);
  second.processAll(input);
  assert.deepEqual(first.snapshot(), second.snapshot());
});

test("release後は新しい演奏eventを自走生成せず有限時間で停止する", () => {
  const field = new ContactCausalField();
  field.processAll(releaseAndDecay);
  const eventCountAtRelease = field.snapshot().audioEvents.length;
  field.advanceTo(4000);
  const state = field.snapshot();
  const laterEvents = state.audioEvents.slice(eventCountAtRelease);
  assert.deepEqual(laterEvents.map((event) => event.type), ["decay-stop"]);
  assert.equal(state.nodes[0].energy, 0);
  assert.equal(state.nodes[0].audible, false);
  assert.equal(state.floor, "broken");
});

test("CUT後の再接触はloop頭でなく同じnodeをREVEALしてrebuiltへ移す", () => {
  const field = new ContactCausalField();
  const states = field.processAll(breakAndRebuild);
  assert.equal(states[1].floor, "broken");
  assert.equal(states[3].floor, "rebuilt");
  assert.equal(states[3].nodes.length, 1);
  assert.equal(states[3].audioEvents.at(-1).type, "reveal");
});

test("pressure取得不能を架空値で補わない", () => {
  const field = new ContactCausalField();
  assert.throws(
    () => field.process(frame(0, "contact", 0, { pressure: 0.5 })),
    /unavailable pressure must be null/,
  );
});

test("timestampの逆行を拒否する", () => {
  const field = new ContactCausalField();
  field.process(frame(0, "contact", 100));
  assert.throws(() => field.process(frame(0, "slide", 90)), /timestamp moved backwards/);
});

