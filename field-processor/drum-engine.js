(() => {
  "use strict";

  class MappingDrumEngine {
    constructor(root) {
      this.root = root;
      this.bpm = 132;
      this.recordingLength = 256;
      this.mapValues = [34, 28, 51, 22];
      this.manual = Array.from({ length: 4 }, () => Array(this.recordingLength).fill(0));
      this.padPointers = new Map();
      this.running = false;
      this.recording = false;
      this.globalTick = 0;
      this.nextTickTime = 0;
      this.timer = 0;
      this.hitSerial = 0;
      this.ctx = null;
      this.output = null;
      this.driveNode = null;
      this.noiseBuffer = null;

      this.startButton = root.querySelector("#drumStart");
      this.recButton = root.querySelector("#drumRec");
      this.clearButton = root.querySelector("#drumClear");
      this.status = root.querySelector("#drumStatus");
      this.chanceInput = root.querySelector("#drumChance");
      this.driveInput = root.querySelector("#drumDrive");

      root.querySelectorAll("[data-drum-map]").forEach(input => {
        const voice = Number(input.dataset.drumMap);
        input.addEventListener("input", () => {
          this.mapValues[voice] = Number(input.value);
          root.querySelector("#drumMapValue" + voice).textContent = input.value;
        });
      });
      this.chanceInput.addEventListener("input", () => {
        root.querySelector("#drumChanceValue").textContent = this.chanceInput.value;
      });
      this.driveInput.addEventListener("input", () => {
        root.querySelector("#drumDriveValue").textContent = this.driveInput.value;
        if (this.driveNode) this.driveNode.curve = this.makeCurve(Number(this.driveInput.value));
      });
      root.querySelectorAll("[data-drum-pad]").forEach(button => {
        button.addEventListener("pointerdown", event => this.padDown(event));
        button.addEventListener("pointermove", event => this.padMove(event));
        button.addEventListener("pointerup", event => this.padUp(event));
        button.addEventListener("pointercancel", event => this.padUp(event));
      });
      this.startButton.addEventListener("click", () => {
        if (this.running) this.stopTransport();
        else this.startTransport();
      });
      this.recButton.addEventListener("click", () => this.toggleRecord());
      this.clearButton.addEventListener("click", () => this.clearRecording());
    }

    ensureAudio() {
      if (!this.ctx || this.ctx.state === "closed") {
        this.ctx = new (window.AudioContext || window.webkitAudioContext)({ latencyHint: "interactive" });
        this.output = this.ctx.createGain();
        this.driveNode = this.ctx.createWaveShaper();
        const compressor = this.ctx.createDynamicsCompressor();
        this.output.gain.value = .68;
        this.driveNode.curve = this.makeCurve(Number(this.driveInput.value));
        this.driveNode.oversample = "2x";
        compressor.threshold.value = -16;
        compressor.knee.value = 7;
        compressor.ratio.value = 4.2;
        compressor.attack.value = .003;
        compressor.release.value = .12;
        this.output.connect(this.driveNode).connect(compressor).connect(this.ctx.destination);
        this.noiseBuffer = this.makeNoiseBuffer(2);
      }
      if (this.ctx.state === "suspended") this.ctx.resume();
    }

    resume() {
      if (this.ctx?.state === "suspended") this.ctx.resume();
    }

    makeCurve(value) {
      const amount = 1.1 + value / 100 * 5.4;
      const curve = new Float32Array(2048);
      for (let index = 0; index < curve.length; index++) {
        const x = index * 2 / (curve.length - 1) - 1;
        curve[index] = Math.tanh(x * amount);
      }
      return curve;
    }

    makeNoiseBuffer(seconds) {
      const buffer = this.ctx.createBuffer(2, Math.ceil(this.ctx.sampleRate * seconds), this.ctx.sampleRate);
      let seed = 0x5f3759df;
      for (let channel = 0; channel < 2; channel++) {
        const data = buffer.getChannelData(channel);
        for (let index = 0; index < data.length; index++) {
          seed = (seed * 1664525 + 1013904223) >>> 0;
          data[index] = seed / 2147483648 - 1;
        }
      }
      return buffer;
    }

    envelope(value, time, decay, destination = this.output) {
      const gain = this.ctx.createGain();
      gain.gain.setValueAtTime(Math.max(.0001, value), time);
      gain.gain.exponentialRampToValueAtTime(.0001, time + decay);
      gain.connect(destination);
      return gain;
    }

    oscillator(type, frequency, time, duration, destination) {
      const source = this.ctx.createOscillator();
      source.type = type;
      source.frequency.setValueAtTime(frequency, time);
      source.connect(destination);
      source.start(time);
      source.stop(time + duration);
      return source;
    }

    noise(time, duration, destination, rate = 1) {
      const source = this.ctx.createBufferSource();
      source.buffer = this.noiseBuffer;
      source.playbackRate.value = rate;
      source.connect(destination);
      const available = Math.max(0, this.noiseBuffer.duration - duration * rate - .01);
      source.start(time, ((this.hitSerial * .181) % 1) * available, duration);
    }

    playVoice(voice, velocity, time, variation = 0) {
      this.ensureAudio();
      const when = Number.isFinite(time) ? time : this.ctx.currentTime;
      this.hitSerial++;
      if (voice === 0) this.playKick(velocity, when, variation);
      else if (voice === 1) this.playSnare(velocity, when, variation);
      else if (voice === 2) this.playHat(velocity, when, variation);
      else this.playRim(velocity, when, variation);
    }

    playKick(velocity, time, variation) {
      const amp = this.envelope(velocity * .92, time, .4);
      const body = this.oscillator("sine", 166 + variation * 2, time, .44, amp);
      body.frequency.exponentialRampToValueAtTime(43 + variation % 3, time + .079);
      const filter = this.ctx.createBiquadFilter();
      filter.type = "highpass";
      filter.frequency.value = 2600 + variation * 130;
      const click = this.envelope(velocity * .13, time, .018);
      filter.connect(click);
      this.noise(time, .023, filter, 1.8);
    }

    playSnare(velocity, time, variation) {
      const filter = this.ctx.createBiquadFilter();
      filter.type = "bandpass";
      filter.frequency.value = 1420 + variation * 79;
      filter.Q.value = 1.05;
      const dust = this.envelope(velocity * .54, time, .18);
      filter.connect(dust);
      this.noise(time, .22, filter, .78 + variation * .035);
      [176, 289].forEach((frequency, index) => {
        const body = this.envelope(velocity * (.23 - index * .06), time, .11 + index * .04);
        this.oscillator(index ? "triangle" : "sine", frequency, time, .18, body);
      });
    }

    playHat(velocity, time, variation) {
      const filter = this.ctx.createBiquadFilter();
      filter.type = "highpass";
      filter.frequency.value = 5200 + variation * 170;
      const amp = this.envelope(velocity * .25, time, .075 + variation % 3 * .015);
      filter.connect(amp);
      [1, 1.342, 1.731, 2.117, 2.693, 3.417].forEach((ratio, index) => {
        const source = this.oscillator(index % 2 ? "square" : "triangle", 710 * ratio, time, .13, filter);
        source.detune.value = ((variation + index * 7) % 9 - 4) * 4;
      });
    }

    playRim(velocity, time, variation) {
      [510, 920, 1470].forEach((frequency, index) => {
        const filter = this.ctx.createBiquadFilter();
        filter.type = "bandpass";
        filter.frequency.value = frequency * (1 + variation * .009);
        filter.Q.value = 13 - index * 2;
        const amp = this.envelope(velocity * (.23 - index * .045), time, .065 + index * .025);
        filter.connect(amp);
        this.noise(time, .11, filter, 1.25);
      });
    }

    padDown(event) {
      this.ensureAudio();
      const button = event.currentTarget;
      const voice = Number(button.dataset.drumPad);
      button.setPointerCapture(event.pointerId);
      const rect = button.getBoundingClientRect();
      const x = Math.max(0, Math.min(1, (event.clientX - rect.left) / rect.width));
      const pressure = event.pressure > 0 ? event.pressure : .72;
      this.playVoice(voice, .62 + pressure * .34, this.ctx.currentTime, this.hitSerial % 9);
      if (this.recording) this.recordManual(voice, 1);
      const state = { voice, button, x, delay: 0, interval: 0 };
      state.delay = setTimeout(() => this.startRoll(event.pointerId), 260);
      this.padPointers.set(event.pointerId, state);
    }

    padMove(event) {
      const state = this.padPointers.get(event.pointerId);
      if (!state) return;
      const rect = state.button.getBoundingClientRect();
      state.x = Math.max(0, Math.min(1, (event.clientX - rect.left) / rect.width));
      if (state.interval) this.restartRoll(event.pointerId);
    }

    padUp(event) {
      const state = this.padPointers.get(event.pointerId);
      if (!state) return;
      clearTimeout(state.delay);
      clearInterval(state.interval);
      this.padPointers.delete(event.pointerId);
    }

    rollMs(x) {
      return 205 - x * 166;
    }

    startRoll(pointerId) {
      const state = this.padPointers.get(pointerId);
      if (!state) return;
      state.interval = setInterval(() => {
        this.playVoice(state.voice, .67, this.ctx.currentTime, this.hitSerial % 11);
        if (this.recording) this.recordManual(state.voice, state.x > .62 ? 4 : 2);
      }, this.rollMs(state.x));
    }

    restartRoll(pointerId) {
      const state = this.padPointers.get(pointerId);
      if (!state) return;
      clearInterval(state.interval);
      this.startRoll(pointerId);
    }

    recordManual(voice, repeats) {
      const index = this.globalTick % this.recordingLength;
      this.manual[voice][index] = Math.max(this.manual[voice][index], repeats);
    }

    trackLength(voice, value) {
      if (value < 58) return 16;
      const options = voice === 0 ? [16, 15] : voice === 1 ? [16, 15, 17] : voice === 2 ? [16, 13, 15] : [16, 11, 15];
      return options[Math.floor(value / 11) % options.length];
    }

    shouldMapHit(voice, tick, value) {
      if (value <= 1) return false;
      const length = this.trackLength(voice, value);
      const local = tick % length;
      const bank = Math.floor(value / 9);
      const maxima = [7, 6, 13, 8];
      const pulses = Math.max(1, Math.min(maxima[voice], Math.round(value / 100 * maxima[voice])));
      const rotation = (bank * [3, 5, 7, 4][voice] + voice * 2) % length;
      const position = (local + rotation) % length;
      let hit = (position * pulses) % length < pulses;
      if (voice === 0 && value < 45) hit = local === 0 || (value > 24 && local === 10);
      if (voice === 1 && value < 48) hit = local === 4 || local === 12;
      if (voice === 2 && value < 30) hit = local === 2 || local === 10;
      if (voice === 3 && value < 32) hit = value > 12 && local === 6;
      return hit;
    }

    hash01(a, b, c) {
      let value = (a * 374761393 + b * 668265263 + c * 2147483647) >>> 0;
      value = Math.imul(value ^ value >>> 13, 1274126177) >>> 0;
      return ((value ^ value >>> 16) >>> 0) / 4294967296;
    }

    startTransport() {
      if (this.running) return;
      this.ensureAudio();
      this.running = true;
      this.nextTickTime = this.ctx.currentTime + .06;
      this.startButton.textContent = "停止";
      this.startButton.setAttribute("aria-pressed", "true");
      this.timer = setInterval(() => this.schedule(), 25);
      this.schedule();
    }

    stopTransport() {
      this.running = false;
      clearInterval(this.timer);
      this.timer = 0;
      this.startButton.textContent = "開始";
      this.startButton.setAttribute("aria-pressed", "false");
      this.status.textContent = this.bpm + " BPM";
    }

    schedule() {
      const horizon = this.ctx.currentTime + .12;
      while (this.nextTickTime < horizon) {
        this.scheduleTick(this.globalTick, this.nextTickTime);
        this.globalTick++;
        this.nextTickTime += 60 / this.bpm / 4;
      }
    }

    scheduleTick(tick, time) {
      const chance = Number(this.chanceInput.value) / 100;
      for (let voice = 0; voice < 4; voice++) {
        const mapped = this.shouldMapHit(voice, tick, this.mapValues[voice]);
        const recorded = this.manual[voice][tick % this.recordingLength];
        const conditional = chance > 0 && this.mapValues[voice] > 4 && this.hash01(tick, voice, Math.floor(tick / this.recordingLength)) < chance * [.08, .1, .18, .13][voice];
        if (!mapped && !recorded && !conditional) continue;
        let repeats = recorded || 1;
        if (conditional && voice >= 2 && this.hash01(voice, tick, 91) < chance * .55) repeats = chance > .72 ? 4 : 2;
        const step = 60 / this.bpm / 4;
        for (let repeat = 0; repeat < repeats; repeat++) {
          const micro = voice >= 2 && tick % 2 ? .008 + voice * .003 : 0;
          this.playVoice(voice, Math.max(.35, .84 - repeat * .1), time + micro + repeat * step / repeats, (tick + voice + repeat) % 11);
        }
      }
      const shown = tick % this.recordingLength;
      setTimeout(() => {
        if (this.running) this.status.textContent = this.bpm + " BPM · " + (Math.floor(shown / 16) + 1) + "/16";
      }, Math.max(0, (time - this.ctx.currentTime) * 1000));
    }

    toggleRecord() {
      this.recording = !this.recording;
      this.recButton.setAttribute("aria-pressed", String(this.recording));
      this.recButton.textContent = this.recording ? "録音中" : "録音";
      if (this.recording && !this.running) this.startTransport();
      this.status.textContent = this.recording ? "REC · 16小節" : this.bpm + " BPM";
    }

    clearRecording() {
      this.manual.forEach(row => row.fill(0));
      this.status.textContent = "録音を消去";
    }
  }

  window.MappingDrumEngine = MappingDrumEngine;
})();
