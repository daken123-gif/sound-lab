# Four-input Rotor coefficient measurements

- research-id: `20260828-things-motor`
- measured-at: 2026-08-28
- runtime: Python standard library
- sample-rate for Motor test: 48,000 Hz
- scope: coefficient and phase model only

## Executed checks

Command:

```text
python3 -m unittest -v test_rotor_measure.py
```

Observed result: 8 tests ran and all passed.

The tests covered:

- four-track adjacency and Track 4 to Track 1 wrap;
- equal-power squared-gain invariant;
- linear amplitude-sum invariant;
- no more than two active adjacent coefficients;
- coefficient continuity at one full phase wrap;
- rejection of an unknown curve;
- phase-continuous Motor stopping;
- reverse rotation.

## Measured values

| Measurement | Equal-power | Linear |
| --- | ---: | ---: |
| Maximum error from `g0² + g1² = 1` | `2.220446049250313e-16` | `0.5` |
| Maximum error from `g0 + g1 = 1` | `0.4142135623730949` | `0.0` |
| Correlated midpoint gain | `1.414213562373095` | `1.0` |
| Correlated midpoint gain | `+3.0102999566398116 dB` | `0.0 dB` |
| Maximum wrap coefficient jump at epsilon `1e-9` | `6.283185144565705e-09` | `3.999999886872274e-09` |

## Motor inertia measurement

Parameters:

- target run speed: `2.0 Hz`;
- inertia time constant: `0.15 s`;
- run before stop command: `1.0 s`;
- measured decay after stop command: `2.0 s`.

Observed values:

| Measurement | Value |
| --- | ---: |
| Speed before stop command | `1.997454732397325 Hz` |
| Speed on first sample after stop command | `1.9971773273936189 Hz` |
| First-sample phase advance after stop command | `4.1607860987391554e-05 rotations` |
| Residual speed after 2 seconds | `3.235071277374988e-06 Hz` |
| Maximum per-sample speed step | `0.00027775848854738605 Hz` |

The stop command does not reset phase or set speed to zero in one sample. The model therefore preserves coefficient continuity at the command boundary.

## What the measurement establishes

- Equal-power is internally consistent for uncorrelated energy: `g0² + g1²` remains one within floating-point error.
- Linear is internally consistent for perfectly correlated amplitude: `g0 + g1` remains one.
- Equal-power produces the predicted `+3.0103 dB` midpoint rise when both inputs carry the same signal.
- Linear produces a 50% power sum at the midpoint when inputs are uncorrelated.
- A single fixed curve cannot preserve both correlated amplitude and uncorrelated power.
- Four-track wrap can be coefficient-continuous when Track 4 hands back to Track 1.
- Exponential Motor inertia can stop without resetting the held mix position.

## What the measurement does not establish

- No microphone, recorded voice, music loop, or iPhone audio path was used.
- It does not establish perceived loudness across real material.
- It does not establish that the 150 ms inertia constant feels playable.
- It does not test `SKIP`, `HOLD`, or `HOLE` remapping during a live track-state change.
- It does not test audio-rate modulation, anti-aliasing, oversampling, CPU load, or AUv3 behaviour.
- It does not validate a UI or product integration.

## Design consequence

Do not place a hidden compressor or limiter after the Rotor to conceal the curve conflict. The next audio experiment must compare equal-power and linear with at least:

1. identical duplicated audio;
2. strongly correlated variations of one recording;
3. unrelated voice, environment, synth, and noise loops;
4. silence entering or leaving a pair.

The curve selector remains a research parameter and must not appear in the performance UI yet.
