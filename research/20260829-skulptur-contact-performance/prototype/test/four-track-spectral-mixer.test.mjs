import assert from "node:assert/strict";
import test from "node:test";
import { FourTrackSpectralMixer } from "../src/four-track-spectral-mixer.js";

const mono = values => [Float32Array.from(values)];
const emptyTrack = length => mono(new Array(length).fill(0));

test("the loop bus combines exactly four tracks", () => {
  const mixer = new FourTrackSpectralMixer({ channels: 1, loopBusTrim: 0.25, drumBusGain: 1 });
  const tracks = [mono([1, 0]), mono([1, 0]), mono([1, 0]), mono([1, 0])];
  const [output] = mixer.process(tracks, mono([0, 0]));
  assert.deepEqual([...output], [0.9800000190734863, 0]);
});

test("track gain and mute act before the shared spectral bus", () => {
  const mixer = new FourTrackSpectralMixer({ channels: 1, loopBusTrim: 1 });
  mixer.setTrack(0, { gain: 0.5 });
  mixer.setTrack(1, { muted: true });
  const [output] = mixer.process(
    [mono([1]), mono([1]), emptyTrack(1), emptyTrack(1)],
    mono([0])
  );
  assert.equal(output[0], 0.5);
});

test("the independent drum bus bypasses spectral processing", () => {
  const mixer = new FourTrackSpectralMixer({
    channels: 1,
    loopBusTrim: 1,
    drumBusGain: 0.8,
    filterOptions: { wetAttackSeconds: 0, gainSmoothingSeconds: 0 }
  });
  mixer.spectral.setBands(new Array(10).fill(0));
  mixer.spectral.setActive(true);
  const drums = Float32Array.from([0.5, -0.25, 0.1]);
  const [output] = mixer.process(
    [emptyTrack(3), emptyTrack(3), emptyTrack(3), emptyTrack(3)],
    [drums]
  );
  output.forEach((value, index) => assert.ok(Math.abs(value - drums[index] * 0.8) < 1e-7));
});

test("spectral movement changes loops without changing the added drum contribution", () => {
  const options = {
    channels: 1,
    loopBusTrim: 0.5,
    drumBusGain: 0.75,
    filterOptions: { wetAttackSeconds: 0, gainSmoothingSeconds: 0 }
  };
  const withDrums = new FourTrackSpectralMixer(options);
  const withoutDrums = new FourTrackSpectralMixer(options);
  for (const mixer of [withDrums, withoutDrums]) {
    mixer.spectral.setBands([1, 0, 0, 0, 0, 0, 0, 0, 0, 0]);
    mixer.spectral.setActive(true);
  }
  const length = 1024;
  const loop = Float32Array.from({ length }, (_, i) => Math.sin(2 * Math.PI * 2000 * i / 48000));
  const drum = Float32Array.from({ length }, (_, i) => i % 128 === 0 ? 0.6 : 0);
  const tracks = [[loop], emptyTrack(length), emptyTrack(length), emptyTrack(length)];
  const wet = withDrums.process(tracks, [drum])[0];
  const dryDrumless = withoutDrums.process(tracks, mono(new Array(length).fill(0)))[0];
  for (let i = 0; i < length; i += 1) {
    assert.ok(Math.abs((wet[i] - dryDrumless[i]) - drum[i] * 0.75) < 1e-6);
  }
});

test("the final safety ceiling catches only combined-bus overloads", () => {
  const mixer = new FourTrackSpectralMixer({ channels: 1, loopBusTrim: 1, drumBusGain: 1 });
  const [output] = mixer.process(
    [mono([0.8, -0.8]), emptyTrack(2), emptyTrack(2), emptyTrack(2)],
    mono([0.7, -0.7])
  );
  assert.deepEqual([...output], [0.9800000190734863, -0.9800000190734863]);
});
