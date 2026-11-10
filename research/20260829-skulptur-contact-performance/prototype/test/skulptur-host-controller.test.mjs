import assert from "node:assert/strict";
import test from "node:test";
import { SkulpturHostController } from "../src/skulptur-host-controller.js";

class FakePort {
  constructor() {
    this.messages = [];
    this.onmessage = null;
  }

  postMessage(message) {
    this.messages.push(message);
  }
}

class FakeWorkletNode {
  constructor(context, name, options) {
    this.context = context;
    this.name = name;
    this.options = options;
    this.port = new FakePort();
    this.connections = [];
    this.disconnections = [];
  }

  connect(destination) {
    this.connections.push(destination);
  }

  disconnect(destination) {
    this.disconnections.push(destination);
  }
}

class FakeSource {
  constructor() {
    this.connections = [];
    this.disconnections = [];
  }

  connect(...connection) {
    this.connections.push(connection);
  }

  disconnect(destination) {
    this.disconnections.push(destination);
  }
}

function createContext() {
  const loaded = [];
  return {
    currentTime: 1.25,
    destination: { name: "destination", connect() {} },
    loaded,
    audioWorklet: { async addModule(url) { loaded.push(String(url)); } }
  };
}

test("host creation fixes the graph at four loops plus one drum input", async () => {
  const context = createContext();
  const controller = await SkulpturHostController.create(context, {
    workletUrl: "worklet.js",
    audioWorkletNodeClass: FakeWorkletNode,
    order: 8,
    loopDurationSeconds: 6
  });
  assert.deepEqual(context.loaded, ["worklet.js"]);
  assert.equal(controller.node.options.numberOfInputs, 5);
  assert.equal(controller.node.options.numberOfOutputs, 1);
  assert.equal(controller.node.options.processorOptions.order, 8);
  assert.equal(controller.node.options.processorOptions.loopDurationSeconds, 6);
  assert.deepEqual(controller.node.port.messages, []);
});

test("host attachment routes four loops and bypass drums to fixed ports", async () => {
  const context = createContext();
  const controller = await SkulpturHostController.create(context, {
    workletUrl: "worklet.js",
    audioWorkletNodeClass: FakeWorkletNode
  });
  const loops = Array.from({ length: 4 }, () => new FakeSource());
  const drum = new FakeSource();
  controller.attach({ loops, drum, output: context.destination });
  loops.forEach((source, track) => assert.deepEqual(source.connections[0], [controller.node, 0, track]));
  assert.deepEqual(drum.connections[0], [controller.node, 0, 4]);
  assert.equal(controller.node.connections[0], context.destination);
  assert.throws(() => controller.attach({ loops: loops.slice(0, 3), drum }), /exactly four/);
});

test("host methods preserve explicit transport, record, and touch control", async () => {
  const context = createContext();
  const controller = await SkulpturHostController.create(context, {
    workletUrl: "worklet.js",
    audioWorkletNodeClass: FakeWorkletNode
  });
  controller.setTransport({ running: true, phase: 0.25, loopDurationSeconds: 4 });
  controller.setRecording(true);
  controller.beginTouch({ pointerId: 7, band: 3, position: 0.8 });
  controller.endTouch(7, { throwMotion: false });
  assert.deepEqual(controller.node.port.messages.map(message => message.type), [
    "transport", "gesture-record", "touch-begin", "touch-end"
  ]);
  assert.equal(controller.node.port.messages[2].timeSeconds, 1.25);
  assert.equal(controller.node.port.messages[3].throwMotion, false);
});

test("host posts one validated audio-clock touch schedule and explicit cancellation", async () => {
  const context = createContext();
  const controller = await SkulpturHostController.create(context, {
    workletUrl: "worklet.js", audioWorkletNodeClass: FakeWorkletNode
  });
  const commands = [
    { type: "touch-begin", pointerId: 100, band: 2, position: 0.8, timeSeconds: 2 },
    { type: "touch-end", pointerId: 100, throwMotion: false, timeSeconds: 2.1 }
  ];
  assert.equal(controller.scheduleTouches("take-1", commands), 2);
  controller.cancelScheduledTouches("take-1");
  assert.deepEqual(controller.node.port.messages.map(message => message.type), [
    "touch-schedule", "touch-schedule-cancel"
  ]);
  assert.equal(controller.node.port.messages[0].commands[0].timeSeconds, 2);
});

test("gesture state round-trips through a correlated request", async () => {
  const context = createContext();
  const controller = await SkulpturHostController.create(context, {
    workletUrl: "worklet.js",
    audioWorkletNodeClass: FakeWorkletNode
  });
  const statePromise = controller.dumpGestureState();
  const request = controller.node.port.messages.at(-1);
  const state = { version: 2, gain: { bands: [] }, feedback: { bands: [] } };
  controller.node.port.onmessage({ data: { type: "gesture-state", requestId: request.requestId, state } });
  assert.equal(await statePromise, state);
  controller.loadGestureState(state);
  assert.equal(controller.node.port.messages.at(-1).type, "gesture-load");
});

test("disposing detaches the host graph and blocks further commands", async () => {
  const context = createContext();
  const controller = await SkulpturHostController.create(context, {
    workletUrl: "worklet.js",
    audioWorkletNodeClass: FakeWorkletNode
  });
  const loops = Array.from({ length: 4 }, () => new FakeSource());
  controller.attach({ loops, output: context.destination });
  controller.dispose();
  loops.forEach(source => assert.deepEqual(source.disconnections, [controller.node]));
  assert.deepEqual(controller.node.disconnections, [context.destination]);
  assert.throws(() => controller.setRecording(true), /disposed/);
});
