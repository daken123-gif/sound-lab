const clamp = (value, min, max) => Math.min(max, Math.max(min, value));

export class Biquad {
  constructor(coefficients) {
    this.z1 = 0;
    this.z2 = 0;
    this.setCoefficients(coefficients);
  }

  setCoefficients({ b0, b1, b2, a1, a2 }) {
    this.b0 = b0;
    this.b1 = b1;
    this.b2 = b2;
    this.a1 = a1;
    this.a2 = a2;
  }

  reset() {
    this.z1 = 0;
    this.z2 = 0;
  }

  process(input) {
    const output = this.b0 * input + this.z1;
    this.z1 = this.b1 * input - this.a1 * output + this.z2;
    this.z2 = this.b2 * input - this.a2 * output;
    return output;
  }
}

export function lowpassCoefficients(sampleRate, frequency, q = Math.SQRT1_2) {
  return coefficients("lowpass", sampleRate, frequency, q);
}

export function highpassCoefficients(sampleRate, frequency, q = Math.SQRT1_2) {
  return coefficients("highpass", sampleRate, frequency, q);
}

function coefficients(type, sampleRate, frequency, q) {
  const safeFrequency = clamp(frequency, 10, sampleRate * 0.475);
  const safeQ = clamp(q, 0.1, 30);
  const omega = (2 * Math.PI * safeFrequency) / sampleRate;
  const cosine = Math.cos(omega);
  const sine = Math.sin(omega);
  const alpha = sine / (2 * safeQ);

  let b0;
  let b1;
  let b2;
  if (type === "lowpass") {
    b0 = (1 - cosine) / 2;
    b1 = 1 - cosine;
    b2 = (1 - cosine) / 2;
  } else {
    b0 = (1 + cosine) / 2;
    b1 = -(1 + cosine);
    b2 = (1 + cosine) / 2;
  }

  const a0 = 1 + alpha;
  return {
    b0: b0 / a0,
    b1: b1 / a0,
    b2: b2 / a0,
    a1: (-2 * cosine) / a0,
    a2: (1 - alpha) / a0
  };
}
