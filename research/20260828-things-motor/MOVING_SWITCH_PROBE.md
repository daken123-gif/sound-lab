# Moving Rotor participation-switch probe

Status: active research, not an adopted product decision.

## Purpose

The earlier layout test held phase still. This probe keeps the Rotor moving while
Track 4 changes from enabled to disabled, so the state-change ramp cannot hide a
phase reset or freeze.

## Test setup

- sample rate: 48 kHz
- Rotor speed: 0.5 rotations per second
- input: four unrelated synthetic sine tracks at 0.25 amplitude
- state change: `[1, 1, 1, 1]` to `[1, 1, 1, 0]`
- immediate switch: 1 sample
- smoothed switch: 5 ms / 240 samples
- scenarios: phase 0.10, where Track 4 is not contributing; phase 0.80,
  where Track 4 is strongly contributing

## Correct transition construction

A ramp from one captured coefficient vector to a later target is insufficient
when phase keeps moving: it briefly distorts normal Rotor motion, even on an arc
whose ownership did not change.

Instead, every transition sample evaluates both layouts at the current phase:

```text
old = coefficients(currentPhase, oldParticipation)
new = coefficients(currentPhase, newParticipation)
outputCoefficients = old + progress * (new - old)
```

Only the layout difference is ramped. Rotor phase and ordinary crossfade motion
continue throughout the state change. The last ramp sample lands on the current,
not previously captured, destination.

## Results

Maximum single-sample coefficient changes:

| Switch position | Mode | Immediate | 5 ms ramp |
|---|---|---:|---:|
| phase 0.10, Track 4 absent from mix | `SKIP` | 0.133742 | 0.000523 |
| phase 0.10, Track 4 absent from mix | `HOLD` | 0.00005295 | 0.00005295 |
| phase 0.10, Track 4 absent from mix | `HOLE` | 0.00005295 | 0.00005295 |
| phase 0.80, Track 4 strongly audible | `SKIP` | 0.951077 | 0.003983 |
| phase 0.80, Track 4 strongly audible | `HOLD` | 0.951077 | 0.003983 |
| phase 0.80, Track 4 strongly audible | `HOLE` | 0.951077 | 0.003983 |

At phase 0.10, the small `HOLD/HOLE` value is ordinary 0.5 Hz Rotor motion;
the switch adds no extra coefficient jump and the 5 ms mechanism leaves that
motion exactly unchanged. `SKIP` still remaps the unrelated part of the circle.

At phase 0.80, the performer removes a track that is actually sounding. No
layout can avoid the intended change, but the 5 ms ramp reduces the coefficient
step by about 239 times without stopping phase.

The maximum output peak in this synthetic 0.25-amplitude test was 0.35355, with
no clipping. This is not a general headroom result: actual recordings may have
different peaks, correlations, DC offsets, and transients.

## Current judgment

The moving-phase result supports the earlier `HOLD` default candidacy. It also
narrows the implementation rule: participation smoothing must interpolate the
old and new **layouts at the live phase**, not freeze the Rotor at the command
point and not slew all coefficients indiscriminately.

## Verification boundary

- `rotor_switch_probe.py` implements the moving-phase renderer and optional WAV
  output for all 12 scenario/mode/ramp combinations.
- `test_rotor_switch_probe.py` checks live-target landing, phase continuation,
  unaffected-arc identity, ramp reduction, and WAV integrity.
- External WAV/M4A input is covered by
  [`FIELD_RECORDING_PROBE.md`](FIELD_RECORDING_PROBE.md).
- The complete study suite passes 37 tests.
- The inputs remain synthetic. Click audibility with voice, room sound, hard
  transients, iPhone microphone capture, and iPhone playback is still untested.

Run:

```bash
python3 -m unittest -v \
  test_rotor_measure.py test_rotor_audio_probe.py \
  test_rotor_layout.py test_rotor_switch_probe.py
python3 rotor_switch_probe.py
```
