import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { writeFileSync } from "node:fs";
import { classifyChoke, readWav } from "./choke_classifier.mjs";

const root = dirname(fileURLToPath(import.meta.url));
const output = join(root, "output");
const config = { chokeStart: 0.957, chokeEnd: 1.557, probeTime: 1.17, delayMs: 100 };
const expected = {
  "output-gate": "OUTPUT_GATE",
  "feedback-cut": "FEEDBACK_CUT",
  "buffer-clear": "BUFFER_CLEAR",
  "input-choke": "INPUT_CHOKE"
};

const cases = [];
for (const [mode, classification] of Object.entries(expected)) {
  const result = classifyChoke(
    readWav(join(output, `${mode}-tail-only.wav`)),
    readWav(join(output, `${mode}.wav`)),
    config
  );
  const pass = result.classification === classification;
  cases.push({ mode, expected: classification, actual: result.classification, pass, metrics: result.metrics, signature: result.signature });
}

const controlTail = readWav(join(output, "output-gate-tail-only.wav"));
const controlProbe = readWav(join(output, "output-gate.wav"));
const unknown = classifyChoke(controlTail, controlTail, config);
cases.push({ mode: "missing-probe-control", expected: "UNKNOWN", actual: unknown.classification, pass: unknown.classification === "UNKNOWN", metrics: unknown.metrics, signature: unknown.signature });

function expectError(mode, action) {
  try {
    action();
    cases.push({ mode, expected: "ERROR", actual: "NO_ERROR", pass: false });
  } catch (error) {
    cases.push({ mode, expected: "ERROR", actual: "ERROR", pass: true, message: error instanceof Error ? error.message : String(error) });
  }
}

expectError("sample-rate-mismatch", () => classifyChoke(controlTail, { ...controlProbe, sampleRate: 44_100 }, config));
expectError("recording-too-short", () => classifyChoke({ ...controlTail, samples: controlTail.samples.slice(0, 48_000), durationSeconds: 1 }, controlProbe, config));

const report = { schema: "battlefx-choke-classifier-self-test/v1", cases, passed: cases.filter(({ pass }) => pass).length, total: cases.length };
writeFileSync(join(output, "classifier-self-test.json"), `${JSON.stringify(report, null, 2)}\n`);
console.log(JSON.stringify(report, null, 2));
if (report.passed !== report.total) process.exitCode = 1;
