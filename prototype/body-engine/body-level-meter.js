export class BodyLevelMeter {
  constructor(reportEveryFrames = 2048) {
    if (!Number.isInteger(reportEveryFrames) || reportEveryFrames < 1) {
      throw new RangeError("reportEveryFrames must be a positive integer");
    }
    this.reportEveryFrames = reportEveryFrames;
    this.reset();
  }

  add(input, output) {
    if (input.length !== output.length) throw new RangeError("input and output must have equal length");

    for (let index = 0; index < input.length; index += 1) {
      const inputSample = Number.isFinite(input[index]) ? input[index] : 0;
      const outputSample = Number.isFinite(output[index]) ? output[index] : 0;
      this.inputSquares += inputSample * inputSample;
      this.outputSquares += outputSample * outputSample;
      this.inputPeak = Math.max(this.inputPeak, Math.abs(inputSample));
      this.outputPeak = Math.max(this.outputPeak, Math.abs(outputSample));
    }
    this.frames += input.length;

    if (this.frames < this.reportEveryFrames) return null;
    const result = {
      type: "levels",
      frames: this.frames,
      inputRms: Math.sqrt(this.inputSquares / this.frames),
      inputPeak: this.inputPeak,
      outputRms: Math.sqrt(this.outputSquares / this.frames),
      outputPeak: this.outputPeak
    };
    this.reset();
    return result;
  }

  reset() {
    this.frames = 0;
    this.inputSquares = 0;
    this.outputSquares = 0;
    this.inputPeak = 0;
    this.outputPeak = 0;
  }
}
