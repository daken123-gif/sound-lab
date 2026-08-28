import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";

const html = readFileSync(new URL("./index.html", import.meta.url), "utf8");
const worklet = readFileSync(new URL("./abbey-input-worklet.js", import.meta.url), "utf8");

test("inline application script parses", () => {
  const script = html.slice(html.indexOf("<script>") + 8, html.lastIndexOf("</script>"));
  assert.doesNotThrow(() => new Function(script));
});

test("BODY and OPEN expose their actual Abbey-derived families", () => {
  assert.match(html, /BODY · REDD/);
  assert.match(html, /OPEN · TG/);
  assert.match(html, /bodyFreq:100/);
  assert.match(html, /presenceFreq:5000/);
  assert.match(html, /threshold:-19\.3/);
  assert.match(html, /ratioBase:2/);
  assert.match(html, /attack:\.001/);
});

test("the mic graph loads and connects the Abbey AudioWorklet", () => {
  assert.match(html, /audioWorklet\.addModule\('\.\/abbey-input-worklet\.js'\)/);
  assert.match(html, /new AudioWorkletNode\(ctx,'abbey-input-processor'/);
  assert.match(html, /inputLP\.connect\(abbeyNode\)\.connect\(abbeyGain\)\.connect\(preampBus\)/);
  assert.match(html, /abbeyNode\.port\.postMessage\(\{type:'configure'/);
});

test("CLEAN remains the explicit fallback when Worklet loading fails", () => {
  assert.match(html, /abbeyWorkletReady=false;try\{/);
  assert.match(html, /CLEAN · FALLBACK/);
  assert.match(html, /cleanGain\.gain\.setTargetAtTime\(!abbey&&!focus\?1:0/);
});

test("FOCUS stays outside the Abbey processor", () => {
  assert.match(html, /focus=preampStyle==='focus'/);
  assert.match(html, /analogGain\.gain\.setTargetAtTime\(focus\?1:0/);
  assert.match(html, /if\(preampStyle==='focus'&&analogAir\)/);
});

test("the Worklet imports the tested core and registers one processor", () => {
  assert.match(worklet, /import "\.\.\/prototype\/abbey-input-engine\.js"/);
  assert.match(worklet, /new AbbeyInputEngine\(sampleRate\)/);
  assert.match(worklet, /registerProcessor\("abbey-input-processor", AbbeyInputProcessor\)/);
});
