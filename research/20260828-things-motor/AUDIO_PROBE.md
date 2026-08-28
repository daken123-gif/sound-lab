# Synthetic audio probe

- research-id: `20260828-things-motor`
- measured-at: 2026-08-28
- sample-rate: 48,000 Hz
- duration: 4 seconds per render
- rotor travel: one complete four-track rotation
- source amplitude: 0.25 peak per non-silent track

## Purpose

The coefficient-only measurement established a conflict between equal-power and linear crossfades. This probe runs actual sample streams through three candidate laws:

1. `equal_power`;
2. `linear`;
3. `correlation_compensated`.

The third law begins with equal-power gains and divides them by the expected output power for the measured adjacent-track correlation:

```text
expectedPower = g0² + g1² + 2 * rho * g0 * g1
normalizer = sqrt(max(0.25, expectedPower))
out0 = g0 / normalizer
out1 = g1 / normalizer
```

The `0.25` power floor bounds the gain near anti-correlation. This is an experimental measurement law, not a product decision.

## Material

| Case | Construction | Adjacent correlation |
| --- | --- | --- |
| identical | Four copies of a 220 Hz sine | `1.0` on all edges |
| strongly correlated | 220 Hz sine with phase offsets `0`, `0.25`, `0.50`, `0.75` radians | three edges `0.9689`; wrap edge `0.7317` |
| unrelated | 173, 257, 389, 541 Hz sines | approximately zero |
| silence mixed | 220 Hz, silence, 331 Hz, silence | zero because one side of every edge is silent |

These are controlled synthetic signals. They are not substitutes for voice, environment, synth, noise, or iPhone microphone recordings.

## Observed RMS relative to one non-silent track

| Case | Equal-power | Linear | Correlation compensated |
| --- | ---: | ---: | ---: |
| identical | `+2.139480 dB` | `0.000000 dB` | `0.000000 dB` |
| strongly correlated | `+1.984025 dB` | `-0.132870 dB` | `+0.000000414 dB` |
| unrelated | `-0.000041 dB` | `-1.760954 dB` | `-0.000041 dB` |
| silence mixed | `-3.010300 dB` | `-4.771215 dB` | `-3.010300 dB` |

## Observed peaks

| Case | Equal-power | Linear | Correlation compensated |
| --- | ---: | ---: | ---: |
| identical | `0.3535289` | `0.2500000` | `0.2500000` |
| strongly correlated | `0.3507920` | `0.2499908` | `0.2500000` |
| unrelated | `0.3531241` | `0.2500000` | `0.3531241` |
| silence mixed | `0.2499850` | `0.2497974` | `0.2499850` |

## What was established

- Equal-power behaves correctly for unrelated inputs but lifts correlated material by about 2 dB RMS in this full-rotation test.
- Linear behaves correctly for identical inputs but loses about 1.76 dB RMS for unrelated material.
- Correlation compensation reproduced equal-power for unrelated inputs and linear-like level preservation for identical inputs.
- On the strongly correlated case, correlation compensation held global RMS within approximately `0.000000414 dB` of the source-track RMS.
- Correlation compensation cannot restore energy when one input is silence because correlation is undefined and treated as zero. Silence remains an intentional fade-out case.

## Risks not hidden by the result

### Whole-loop correlation is static

The probe calculates one correlation value for each adjacent pair over the complete buffer. A real voice or field recording may change correlation throughout the loop. A single number can therefore be wrong locally.

### Moving correlation can pump

Recalculating correlation continuously and changing the denominator would modulate gain independently of the performer's Rotor motion. That would let the machine reshape the gesture. If this approach continues, correlation must update slowly, freeze during a touch gesture, or be calculated at recording completion.

### Anti-correlation needs a hard boundary

Near opposite polarity, the theoretical normalization approaches infinite gain while the signals cancel. The probe floors expected power at `0.25`, limiting midpoint coefficient gain to about `1.4142` per input. This bound is protective but not perceptually validated.

### Level preservation is not musical preservation

Flat RMS does not prove that the transition sounds natural. Correlation compensation changes the crossfade law according to source content, so it may remove an audible swell that the performer wanted.

## WAV generation check

The probe generated twelve mono PCM WAV files: four materials multiplied by three curves. A transient zero-byte file was observed on the first filesystem listing. The same render command was repeated, after which all twelve files were `384,044` bytes. The automated WAV test was strengthened to require:

- exactly twelve files;
- size greater than the 44-byte WAV header;
- one channel;
- expected sample rate;
- expected frame count.

The strengthened test passed. Generated WAV files are reproducible outputs and are not stored in Git in this step.

## Current judgment

Keep `equal_power`, `linear`, and `correlation_compensated` as research modes. Do not expose three curve choices in the performance UI. Do not silently select correlation compensation as the product default yet.

The next evidence must come from actual loop material and listening, not another synthetic curve refinement.
