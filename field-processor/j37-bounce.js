(function (root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  if (root) root.J37Bounce = api;
})(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';

  const defaults = Object.freeze({
    speed: 15,
    hit: 0.28,
    saturation: 0.34,
    headBump: 0.08,
    highLoss: 0.1,
    wow: 0,
    flutter: 0,
    noise: 0,
    seed: 1965
  });

  function clamp(value, min, max) {
    return Math.max(min, Math.min(max, value));
  }

  function onePoleCoefficient(frequency, sampleRate) {
    return Math.exp(-2 * Math.PI * frequency / sampleRate);
  }

  function seededNoise(seed) {
    let state = seed >>> 0 || 1;
    return function () {
      state ^= state << 13;
      state ^= state >>> 17;
      state ^= state << 5;
      return ((state >>> 0) / 4294967296) * 2 - 1;
    };
  }

  function readLinear(input, position) {
    const length = input.length;
    if (!length) return 0;
    const wrapped = ((position % length) + length) % length;
    const left = Math.floor(wrapped);
    const right = (left + 1) % length;
    const mix = wrapped - left;
    return input[left] + (input[right] - input[left]) * mix;
  }

  function processChannel(input, sampleRate, options) {
    if (!(input instanceof Float32Array)) throw new TypeError('input must be Float32Array');
    if (!Number.isFinite(sampleRate) || sampleRate < 8000) throw new RangeError('invalid sampleRate');
    const settings = Object.assign({}, defaults, options || {});
    const output = new Float32Array(input.length);
    const hitGain = Math.pow(10, clamp(settings.hit, 0, 1) * 8 / 20);
    const saturation = clamp(settings.saturation, 0, 1);
    const drive = 1 + saturation * 5.2;
    const normalizer = Math.tanh(drive) || 1;
    const bump = clamp(settings.headBump, 0, 1) * 0.28;
    const loss = clamp(settings.highLoss, 0, 1);
    const speed = settings.speed === 7.5 ? 7.5 : 15;
    const lowCoefficient = onePoleCoefficient(speed === 7.5 ? 72 : 88, sampleRate);
    const cutoff = (speed === 7.5 ? 11200 : 16800) * (1 - loss * 0.34);
    const highCoefficient = onePoleCoefficient(clamp(cutoff, 5000, sampleRate * 0.45), sampleRate);
    const wow = clamp(settings.wow, 0, 1);
    const flutter = clamp(settings.flutter, 0, 1);
    const modulated = wow > 0 || flutter > 0;
    const noiseAmount = clamp(settings.noise, 0, 1) * 0.0025;
    const random = seededNoise(settings.seed);
    let low = 0;
    let smooth = 0;

    for (let index = 0; index < input.length; index += 1) {
      const source = modulated
        ? readLinear(input, index
          + wow * sampleRate * 0.0009 * Math.sin(2 * Math.PI * 0.55 * index / sampleRate)
          + flutter * sampleRate * 0.00012 * Math.sin(2 * Math.PI * 6.1 * index / sampleRate))
        : input[index];
      low = lowCoefficient * low + (1 - lowCoefficient) * source;
      const preTape = (source + low * bump) * hitGain;
      const colored = Math.tanh(preTape * drive) / normalizer;
      smooth = highCoefficient * smooth + (1 - highCoefficient) * colored;
      const compensated = smooth / Math.max(1, hitGain * (0.9 + saturation * 0.1));
      output[index] = clamp(compensated + random() * noiseAmount, -1, 1);
    }
    return output;
  }

  function bounceChannels(channels, sampleRate, options) {
    if (!Array.isArray(channels) || !channels.length) throw new TypeError('channels are required');
    const rendered = channels.map((channel, index) => processChannel(
      channel,
      sampleRate,
      Object.assign({}, options || {}, { seed: ((options && options.seed) || defaults.seed) + index * 101 })
    ));
    return {
      channels: rendered,
      sampleRate,
      settings: Object.assign({}, defaults, options || {}),
      model: 'J37 research-informed generation bounce'
    };
  }

  return { defaults, processChannel, bounceChannels };
});
