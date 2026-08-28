# Direct-touch and Motor phase handoff

Status: interaction-model research, not an adopted UI specification.

## Question

Manual drag and automatic Motor rotation must not own separate positions. If
they do, touching or releasing the Rotor can recall a stale phase and jump to a
different track. This probe gives both paths one phase state and tests the two
handoff boundaries.

## Implemented candidate

1. Motor motion advances the shared phase.
2. Touch-down grabs the current Rotor phase without snapping it to the finger.
3. Pointer movement changes the phase by relative circular motion.
4. Every pointer event is interpolated across its corresponding audio samples.
5. Release continues at the last manual angular velocity; a very slow release
   holds the current position.
6. Reverse flick uses the same signed speed axis as reverse Motor motion.

This model intentionally does not implement the earlier provisional
"tap anywhere to seek immediately" gesture. An absolute seek can jump between
tracks. It needs a separate audible seek-ramp experiment before it can return as
a candidate.

## Circular boundary

Raw normalized angles cannot be subtracted directly. A pointer moving from
0.98 to 0.03 crossed the wrap in the positive direction:

```text
circularDelta(0.98, 0.03) = +0.05 rotations
```

It was not interpreted as `-0.95` rotations. The same shortest-path calculation
is used for reverse movement.

## Measurement

The test Motor ran at 0.5 rotations/s, was grabbed after 0.25 seconds, then the
pointer moved +0.05 rotations over 50 ms at 48 kHz.

| Observation | Result |
|---|---:|
| Touch-down phase jump | 0 |
| Drag frames | 2,400 |
| Maximum drag phase step/sample | 0.0000208333 |
| Derived release speed | 1.0 rotations/s |
| First Motor step after release | 0.0000208333 |
| Expected step at 1 rotation/s | 0.0000208333 |

The manual-to-Motor derivative matched at release within floating-point error.
Tests also cover slow-release hold, reverse flick, 4 rotations/s clamping, and
audio-rate interpolation of lower-rate pointer events.

## Research parameters, not product controls

- maximum flick speed: 4 rotations/s
- hold threshold: 0.05 rotations/s

These values exist to bound the prototype. They are not approved UI settings
and should not become visible controls without a separate need.

## Remaining boundary

- Touch-down sets Motor velocity to zero without changing phase. The resulting
  velocity discontinuity has not been checked with actual audio.
- Pointer event timing, multitouch contention, missed events, and iPhone touch
  latency have not been measured.
- Absolute tap-to-seek and long-press behaviour remain unimplemented.
- No interface appearance or layout was produced by this work.
- The complete research suite passes 44 tests.

Run:

```bash
python3 -m unittest -v test_rotor_gesture.py
python3 rotor_gesture.py
```
