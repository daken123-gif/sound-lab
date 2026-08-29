# Effect-specific DRIFT experiment

## Question

Can one DRIFT macro remain quiet at low settings while exposing a different
failure mode in each effect at high settings, without reducing every effect to
the same random LFO?

## Scope

This is a deterministic control-domain design hypothesis. It is not a Chroma
Console hardware emulation and does not claim the published product uses these
curves or distributions.

The model runs for 60 seconds at a 100 Hz control rate with seed `20260828`.
DRIFT is tested at `0.2`, `0.5`, and `0.8`.

## Model

| Effect | DRIFT controls | Failure character |
|---|---|---|
| Vibrato | random-wave blend, stereo divergence, pitch depth | continuous unstable motion |
| Reels | wow plus loss accumulated by repeat index | each recycle degrades further |
| Collage | nonlinear event hazard, duration, speed state, refractory time | rare double-/half-speed readout |
| Generic LFO | one continuous mono random value | no stereo, repeat, or discrete-event state |

The exponent choices are design hypotheses: continuous motion grows earlier,
while Collage event probability grows approximately with `DRIFT^3` so the low
range remains sparse.

## Results

| Metric | DRIFT 0.2 | DRIFT 0.5 | DRIFT 0.8 |
|---|---:|---:|---:|
| Vibrato random component RMS | 0.193 cents | 1.216 cents | 3.593 cents |
| Vibrato L/R difference RMS | 0.098 cents | 0.530 cents | 1.457 cents |
| Vibrato L/R correlation | 0.9997 | 0.9949 | 0.9549 |
| Reels loss per repeat | 0.374 dB | 0.882 dB | 1.459 dB |
| Reels brightness loss per repeat | 0.476 dB | 1.200 dB | 2.104 dB |
| Reels level after 12 repeats | -4.484 dB | -10.581 dB | -17.507 dB |
| Collage events in 60 s | 1 | 3 | 5 |
| Collage event occupancy | 0.783% | 1.933% | 4.817% |

From low to high DRIFT:

- Vibrato random motion increased `18.63x` and its stereo difference increased
  `14.83x`.
- Reels loss per recycle increased `3.90x`.
- Collage event occupancy increased by `4.03` percentage points; the high run
  contained four double-speed events and one half-speed event.

## Interpretation

The experiment supports an effect-specific macro architecture. A low setting
can remain a slight instability, while a high setting exposes three recognizably
different failure types. The generic LFO reference has perfect left/right
correlation, no repeat-indexed degradation, and no discrete playback state. A
generic LFO can become useful only after effect-specific state and mappings are
added; at that point it is no longer the whole DRIFT design.

This result does not establish perceptual quality, correspondence with Chroma
Console hardware, or safe real-time parameter transitions. Those require audio
renders, listening tests, and implementation profiling.

## Reproduction

```sh
python3 experiments/effect_specific_drift.py \
  --output experiments/effect-specific-drift-metrics.json
```

Validation performed:

- two runs produced byte-identical JSON;
- Python byte-code compilation succeeded;
- the JSON SHA-256 is
  `07a4d70bf38b2305173d656ae46bfc54054ccbf76961f4dd76cdc3461127d979`.

