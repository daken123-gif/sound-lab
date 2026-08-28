import { collectBrowserAssets } from "./browser-asset-graph.js";

const assets = collectBrowserAssets(new URL("./mic-test.html", import.meta.url));
process.stdout.write(`${JSON.stringify({ entry: "mic-test.html", assets }, null, 2)}\n`);
