# Rotor participation layouts and state transitions

Status: active research, not an adopted product decision.

## Question

When a performer removes one of four tracks from the Rotor, should the remaining
tracks be redistributed around the circle (`SKIP`), should the removed sector
keep sounding its preceding track (`HOLD`), or should it become silent (`HOLE`)?

The decisive issue is not only click suppression. It is whether a participation
toggle silently changes the meaning of rotor angle elsewhere on the circle.

## Implemented models

| Mode | Sector geometry | Removed sector | Consequence |
|---|---|---|---|
| `SKIP` | Re-divides the circle among enabled tracks | Removed | Every enabled track can move |
| `HOLD` | Keeps four fixed sectors | Previous enabled track dwells | Stable angle map without a forced silence |
| `HOLE` | Keeps four fixed sectors | Silence | Stable angle map with an intentional gap |

`HOLD` treats adjacent sectors owned by the same track as one unity-gain dwell.
It does **not** add two equal-power coefficients; doing so would create an
unintended gain rise of up to +3.01 dB at the midpoint.

## Measurement

Test transition: all four tracks enabled, then track 4 disabled. The rotor phase
is held fixed to isolate layout remapping from normal motor motion. Equal-power
crossfades are used.

| Measurement | `SKIP` | `HOLD` | `HOLE` |
|---|---:|---:|---:|
| Jump at phase 0.10, outside track 4's region | 0.133795 | 0 | 0 |
| Maximum jump over the unaffected fixed half-circle | 0.707107 | 0 | 0 |
| Worst immediate jump anywhere on circle | 1.0 | 1.0 | 1.0 |

The worst-case value of 1.0 is unavoidable when the currently audible track is
removed. The structural difference is that `SKIP` can also jump where the
removed track was not contributing, because it globally re-quantizes the circle.

A 5 ms state-change ramp at 48 kHz spans 240 samples. For the phase-0.10 `SKIP`
case it reduces the maximum per-sample coefficient step from 0.133795 to
0.00055748. In the absolute worst case, the linear bound is 1 / 240 = 0.00416667.
This ramp is only for discontinuity suppression; it does not change the Rotor's
motor inertia or its musical crossfade curve.

## Current judgment

`HOLD` is the leading default candidate. It preserves the performer's learned
track-to-angle map and does not impose silence. `HOLE` is coherent only when an
empty sector is an explicit performance gesture. `SKIP` should not be the hidden
default because a local participation change produces a global angular remap.

This supersedes the earlier provisional preference for `SKIP`; that preference
was made before transition geometry was measured.

## Verification and remaining boundary

- `rotor_layout.py` contains the three mappings and the transition ramp.
- `test_rotor_layout.py` checks cyclic ownership, silent holes, single-track
  unity, no duplicated `HOLD` gain, fixed-map stability, and the ramp bound.
- The complete study suite currently passes 26 tests.
- These are coefficient-domain measurements. Live switching with actual field
  recordings, a moving rotor, and iPhone output remains unverified.

Run:

```bash
python3 -m unittest -v \
  test_rotor_measure.py test_rotor_audio_probe.py test_rotor_layout.py
python3 rotor_layout.py
```
