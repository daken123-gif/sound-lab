import test from "node:test";
import assert from "node:assert/strict";
import { BodyBrowserSession, BODY_MIC_CONSTRAINTS } from "../body-browser-session.js";

class FakeParameter {
  constructor() { this.events = []; }
  setValueAtTime(value, when) { this.events.push(["set", value, when]); }
  cancelScheduledValues(when) { this.events.push(["cancel", when]); }
}

class FakeNode {
  constructor() { this.connections = []; this.disconnections = []; }
  connect(target) { this.connections.push(target); return target; }
  disconnect(target) { this.disconnections.push(target ?? "all"); }
}

class FakeWorkletNode extends FakeNode {
  constructor(context, name, options) {
    super();
    this.context = context;
    this.name = name;
    this.options = options;
    this.parameters = new Map([
      "gate", "size", "decay", "body", "dry", "drive"
    ].map(name => [name, new FakeParameter()]));
  }
}

function fixture() {
  const track = {
    stopped: false,
    stop() { this.stopped = true; },
    getSettings() {
      return { sampleRate: 48000, channelCount: 1, echoCancellation: true };
    }
  };
  const stream = {
    getAudioTracks: () => [track],
    getTracks: () => [track]
  };
  const source = new FakeNode();
  const destination = { name: "speaker" };
  const loaded = [];
  const audioContext = {
    state: "suspended",
    sampleRate: 48000,
    baseLatency: 0.01,
    outputLatency: 0.02,
    currentTime: 4,
    destination,
    audioWorklet: { async addModule(url) { loaded.push(url); } },
    async resume() { this.state = "running"; },
    createMediaStreamSource(received) {
      assert.equal(received, stream);
      return source;
    }
  };
  const requested = [];
  const mediaDevices = {
    async getUserMedia(constraints) { requested.push(constraints); return stream; },
    getSupportedConstraints() {
      return { echoCancellation: true, noiseSuppression: true, autoGainControl: true };
    }
  };
  const session = new BodyBrowserSession({
    audioContext, mediaDevices, AudioWorkletNodeClass: FakeWorkletNode
  });
  return { session, audioContext, destination, track, source, loaded, requested };
}

test("start is explicit, requests raw-oriented ideals, and does not monitor", async () => {
  const f = fixture();
  assert.equal(f.requested.length, 0);
  const diagnostics = await f.session.start();
  assert.equal(f.requested[0], BODY_MIC_CONSTRAINTS);
  assert.equal(f.loaded[0], "./body-worklet-processor.js");
  assert.equal(f.session.bodyNode.name, "soma-body");
  assert.equal(f.session.monitoring, false);
  assert.equal(f.session.bodyNode.connections.length, 0);
  assert.equal(diagnostics.actual.echoCancellation, true);
  assert.equal(diagnostics.requested.echoCancellation.ideal, false);
  assert.deepEqual(
    f.session.bodyNode.parameters.get("gate").events[0], ["set", 0, 4]
  );
});

test("monitoring requires a separate explicit call", async () => {
  const f = fixture();
  await f.session.start();
  f.session.setMonitoring(true);
  assert.equal(f.session.bodyNode.connections[0], f.destination);
  f.session.setMonitoring(false);
  assert.equal(f.session.bodyNode.disconnections[0], f.destination);
});

test("gate and macros schedule only after the session is ready", async () => {
  const f = fixture();
  assert.throws(() => f.session.setGate(true), /not ready/);
  await f.session.start();
  f.session.setGate(true, 5);
  f.session.setMacro("size", 0.8, 5.25);
  assert.deepEqual(f.session.bodyNode.parameters.get("gate").events.slice(-2), [
    ["cancel", 5], ["set", 1, 5]
  ]);
  assert.deepEqual(f.session.bodyNode.parameters.get("size").events.at(-1), [
    "set", 0.8, 5.25
  ]);
  assert.throws(() => f.session.setMacro("unknown", 0.5), /unknown BODY macro/);
});

test("stop disconnects audio and releases every media track", async () => {
  const f = fixture();
  await f.session.start();
  f.session.setMonitoring(true);
  f.session.stop();
  assert.equal(f.track.stopped, true);
  assert.equal(f.session.state, "stopped");
  assert.equal(f.session.monitoring, false);
  assert.ok(f.source.disconnections.length > 0);
});

test("a second start while ready is rejected", async () => {
  const f = fixture();
  await f.session.start();
  await assert.rejects(() => f.session.start(), /cannot start session/);
});
