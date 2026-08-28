import test from "node:test";
import assert from "node:assert/strict";
import {
  collectBrowserAssets,
  extractRelativeAssetReferences
} from "../browser-asset-graph.js";

test("browser diagnostic dependency graph has no missing files", () => {
  const assets = collectBrowserAssets(new URL("../mic-test.html", import.meta.url));
  assert.deepEqual(assets, [
    "body-browser-errors.js",
    "body-browser-session.js",
    "body-engine.js",
    "body-level-meter.js",
    "body-level-watchdog.js",
    "body-realtime-core.js",
    "body-worklet-processor.js",
    "mic-diagnostic.js",
    "mic-test.html"
  ]);
});

test("asset extraction includes modules and worklet URLs but excludes remote URLs", () => {
  const references = extractRelativeAssetReferences(`
    <script type="module" src="./page.js"></script>
    import { x } from "./module.js";
    new URL("./processor.js", import.meta.url);
    new URL("https://example.com/external.js", import.meta.url);
  `);
  assert.deepEqual(references.sort(), ["./module.js", "./page.js", "./processor.js"]);
});

test("asset graph rejects a missing entry instead of producing a manifest", () => {
  assert.throws(
    () => collectBrowserAssets(new URL("../missing-mic-test.html", import.meta.url)),
    /missing browser asset/
  );
});
