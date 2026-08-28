import "../prototype/abbey-input-engine.js";

const { AbbeyInputEngine, MODES } = globalThis.AbbeyInputDSP;

class AbbeyInputProcessor extends AudioWorkletProcessor {
  constructor() {
    super();
    this.engine = new AbbeyInputEngine(sampleRate);
    this.engine.configure(MODES.BODY, 0.35);
    this.port.onmessage = ({ data }) => {
      if (data?.type !== "configure") return;
      const mode = data.mode === MODES.OPEN ? MODES.OPEN : MODES.BODY;
      this.engine.configure(mode, data.density);
    };
  }

  process(inputs, outputs) {
    const inputChannels = inputs[0];
    const outputChannels = outputs[0];
    for (let channel = 0; channel < outputChannels.length; channel += 1) {
      const input = inputChannels[Math.min(channel, inputChannels.length - 1)];
      const output = outputChannels[channel];
      if (!input) {
        output.fill(0);
        continue;
      }
      this.engine.processBlock(input, output);
    }
    return true;
  }
}

registerProcessor("abbey-input-processor", AbbeyInputProcessor);
