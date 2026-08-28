import test from "node:test";
import assert from "node:assert/strict";
import {
  BodyBrowserSessionError,
  classifyBodyBrowserFailure
} from "../body-browser-errors.js";

function namedError(name, message = "failure") {
  const error = new Error(message);
  error.name = name;
  return error;
}

test("insecure context is reported before lower-level browser errors", () => {
  const report = classifyBodyBrowserFailure(namedError("NotAllowedError"), {
    secureContext: false
  });
  assert.equal(report.code, "INSECURE_CONTEXT");
  assert.equal(report.phase, "preflight");
});

test("worklet loading failure preserves its execution phase", () => {
  const error = new BodyBrowserSessionError("worklet", namedError("NetworkError", "module missing"));
  const report = classifyBodyBrowserFailure(error);
  assert.equal(report.code, "WORKLET_LOAD_FAILED");
  assert.equal(report.phase, "worklet");
  assert.equal(report.name, "NetworkError");
});

test("microphone DOMException names map to distinct diagnostic codes", () => {
  const cases = [
    ["NotAllowedError", "MIC_PERMISSION_DENIED"],
    ["NotFoundError", "MIC_NOT_FOUND"],
    ["NotReadableError", "MIC_UNAVAILABLE"],
    ["AbortError", "MIC_UNAVAILABLE"],
    ["OverconstrainedError", "MIC_CONSTRAINT_FAILED"],
    ["SecurityError", "MIC_SECURITY_BLOCKED"]
  ];
  for (const [name, code] of cases) {
    const error = new BodyBrowserSessionError("microphone", namedError(name));
    assert.equal(classifyBodyBrowserFailure(error).code, code);
  }
});

test("missing browser capabilities have explicit preflight codes", () => {
  const cases = [
    ["AudioContextUnavailableError", "AUDIO_CONTEXT_UNAVAILABLE"],
    ["MediaDevicesUnavailableError", "MEDIA_DEVICES_UNAVAILABLE"],
    ["AudioWorkletUnavailableError", "AUDIO_WORKLET_UNAVAILABLE"]
  ];
  for (const [name, code] of cases) {
    assert.equal(classifyBodyBrowserFailure(namedError(name)).code, code);
  }
});
