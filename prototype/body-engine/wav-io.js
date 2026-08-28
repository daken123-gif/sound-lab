import { readFileSync, writeFileSync } from "node:fs";

function assertBuffer(buffer) {
  if (!Buffer.isBuffer(buffer)) throw new TypeError("WAV input must be a Buffer");
  if (buffer.length < 44 || buffer.toString("ascii", 0, 4) !== "RIFF"
    || buffer.toString("ascii", 8, 12) !== "WAVE") {
    throw new Error("not a RIFF/WAVE file");
  }
}

export function decodePcmWav(buffer) {
  assertBuffer(buffer);
  let offset = 12;
  let format = null;
  let data = null;

  while (offset + 8 <= buffer.length) {
    const id = buffer.toString("ascii", offset, offset + 4);
    const size = buffer.readUInt32LE(offset + 4);
    const start = offset + 8;
    const end = start + size;
    if (end > buffer.length) throw new Error(`truncated WAV chunk: ${id}`);

    if (id === "fmt ") {
      if (size < 16) throw new Error("invalid fmt chunk");
      format = {
        audioFormat: buffer.readUInt16LE(start),
        channels: buffer.readUInt16LE(start + 2),
        sampleRate: buffer.readUInt32LE(start + 4),
        blockAlign: buffer.readUInt16LE(start + 12),
        bitsPerSample: buffer.readUInt16LE(start + 14)
      };
    } else if (id === "data" && data === null) {
      data = buffer.subarray(start, end);
    }
    offset = end + (size & 1);
  }

  if (!format || !data) throw new Error("WAV requires fmt and data chunks");
  if (format.audioFormat !== 1 || format.bitsPerSample !== 16) {
    throw new Error("only 16-bit integer PCM WAV is supported");
  }
  if (format.channels < 1 || format.channels > 2) {
    throw new Error("only mono or stereo WAV is supported");
  }
  if (format.sampleRate < 8000) throw new Error("sample rate must be at least 8000 Hz");
  const expectedBlockAlign = format.channels * 2;
  if (format.blockAlign !== expectedBlockAlign || data.length % expectedBlockAlign !== 0) {
    throw new Error("invalid PCM block alignment");
  }

  const frames = data.length / expectedBlockAlign;
  const samples = new Float32Array(frames);
  for (let frame = 0; frame < frames; frame += 1) {
    let mixed = 0;
    for (let channel = 0; channel < format.channels; channel += 1) {
      mixed += data.readInt16LE((frame * format.channels + channel) * 2) / 32768;
    }
    samples[frame] = mixed / format.channels;
  }

  return { samples, sampleRate: format.sampleRate, sourceChannels: format.channels };
}

export function encodeMonoPcm16(samples, sampleRate) {
  if (!(samples instanceof Float32Array)) throw new TypeError("samples must be Float32Array");
  if (!Number.isInteger(sampleRate) || sampleRate < 8000) {
    throw new RangeError("sampleRate must be an integer of at least 8000 Hz");
  }

  const dataLength = samples.length * 2;
  const buffer = Buffer.alloc(44 + dataLength);
  buffer.write("RIFF", 0);
  buffer.writeUInt32LE(36 + dataLength, 4);
  buffer.write("WAVE", 8);
  buffer.write("fmt ", 12);
  buffer.writeUInt32LE(16, 16);
  buffer.writeUInt16LE(1, 20);
  buffer.writeUInt16LE(1, 22);
  buffer.writeUInt32LE(sampleRate, 24);
  buffer.writeUInt32LE(sampleRate * 2, 28);
  buffer.writeUInt16LE(2, 32);
  buffer.writeUInt16LE(16, 34);
  buffer.write("data", 36);
  buffer.writeUInt32LE(dataLength, 40);
  for (let index = 0; index < samples.length; index += 1) {
    const finite = Number.isFinite(samples[index]) ? samples[index] : 0;
    const sample = Math.min(1, Math.max(-1, finite));
    buffer.writeInt16LE(Math.round(sample * (sample < 0 ? 32768 : 32767)), 44 + index * 2);
  }
  return buffer;
}

export function readPcmWav(path) {
  return decodePcmWav(readFileSync(path));
}

export function writeMonoWav(path, samples, sampleRate) {
  writeFileSync(path, encodeMonoPcm16(samples, sampleRate));
}
