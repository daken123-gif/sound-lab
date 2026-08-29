import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";

const html = readFileSync(new URL("./index.html", import.meta.url), "utf8");

test("inline application script parses", () => {
  const script = html.slice(html.indexOf("<script>") + 8, html.lastIndexOf("</script>"));
  assert.doesNotThrow(() => new Function(script));
});

test("raw mic and monitored preamp enter one aligned recorder callback", () => {
  assert.match(html, /recorderInput=ctx\.createChannelMerger\(2\)/);
  assert.match(html, /recorder=ctx\.createScriptProcessor\(1024,2,1\)/);
  assert.match(html, /mic\.connect\(recorderInput,0,0\)/);
  assert.match(html, /preampBus\.connect\(recorderInput,0,1\)/);
  assert.match(html, /capture\(e\.inputBuffer\.getChannelData\(0\),e\.inputBuffer\.getChannelData\(1\)\)/);
});

test("every base recording and overdub retains untouched raw samples", () => {
  assert.match(html, /rawData:\[\],rawTakes:\[\],takeSettings:null/);
  assert.match(html, /lane\.rawData\.push\(rawChunk\.slice\(0,take\)\)/);
  assert.match(html, /lane\.rawTakes=\[makeRawTake\(raw,'base',lane\.takeSettings\)\]/);
  assert.match(html, /lane\.rawTakes\.push\(makeRawTake\(raw,'overdub',lane\.takeSettings\)\)/);
  assert.doesNotMatch(html, /softenEdges\(raw\)/);
});

test("monitor settings are snapshotted without being applied to raw", () => {
  assert.match(html, /monitorStyle:preampStyle/);
  assert.match(html, /monitorDensity:\+density\.value\/100/);
  assert.match(html, /inputTrimDb:\+input\.value/);
  assert.match(html, /hpfHz:\+hpf\.value/);
});

test("cancel, clear, and engine stop release raw take state", () => {
  assert.match(html, /lane\.rawData=\[\];lane\.rawTakes=\[\];lane\.takeSettings=null/);
  assert.match(html, /l\.rawData=\[\];l\.rawTakes=\[\];l\.takeSettings=null/);
});
