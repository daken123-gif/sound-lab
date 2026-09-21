const clamp = (value, min, max) => Math.min(max, Math.max(min, value));

export function fitAudioBufferToLoop(context, source, {
  durationSeconds = 4,
  maxChannels = 2,
  fadeInSeconds = 0.005,
  fadeOutSeconds = 0.01
} = {}) {
  if (!context?.createBuffer || !source?.getChannelData) {
    throw new TypeError("an AudioContext and decoded AudioBuffer are required");
  }
  const duration = Math.max(0.05, Number(durationSeconds));
  const outputRate = context.sampleRate;
  const frameCount = Math.round(duration * outputRate);
  const channelCount = clamp(source.numberOfChannels, 1, maxChannels);
  const output = context.createBuffer(channelCount, frameCount, outputRate);
  const sourceStep = source.sampleRate / outputRate;
  const copiedFrames = Math.min(frameCount, Math.ceil(source.length / sourceStep));
  const fadeInFrames = Math.min(copiedFrames, Math.round(fadeInSeconds * outputRate));
  const fadeOutFrames = Math.min(copiedFrames, Math.round(fadeOutSeconds * outputRate));

  for (let channel = 0; channel < channelCount; channel += 1) {
    const input = source.getChannelData(Math.min(channel, source.numberOfChannels - 1));
    const destination = output.getChannelData(channel);
    for (let frame = 0; frame < copiedFrames; frame += 1) {
      const sourceFrame = frame * sourceStep;
      const left = Math.floor(sourceFrame);
      if (left >= input.length) break;
      const right = Math.min(input.length - 1, left + 1);
      const fraction = sourceFrame - left;
      let value = input[left] + (input[right] - input[left]) * fraction;
      if (fadeInFrames > 0 && frame < fadeInFrames) value *= frame / fadeInFrames;
      if (fadeOutFrames > 0 && frame >= copiedFrames - fadeOutFrames) {
        value *= Math.max(0, (copiedFrames - 1 - frame) / fadeOutFrames);
      }
      destination[frame] = value;
    }
  }
  return output;
}
