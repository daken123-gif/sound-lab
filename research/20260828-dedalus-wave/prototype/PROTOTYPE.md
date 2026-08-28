# Temporal Memory DSP prototype

This directory advances `20260828-dedalus-wave` from a research note to an
isolated, executable DSP experiment. It is not product integration and does
not change the research state from `active`.

## Implemented in this experiment

- one mono circular delay buffer;
- fractional delay reads with linear interpolation;
- two simultaneous read heads during a delay-time jump;
- equal-power crossfade between the old and new read positions;
- feedback adjustable from `0.0` to the research ceiling `1.5`;
- a DC blocker and `tanh` soft clipping inside the feedback loop;
- deterministic reset and parameter clamping.

## Deliberately absent

- the proposed four-line feedback delay network;
- any claim about Dedalus's unpublished internal line count or matrix;
- stereo crossfeed and random panning;
- Scrub/Drift modulation, pitch mode, ducking, or gate behavior;
- Loopy track routing, Skulptur ordering, UI, AUv3, and iPhone integration.

The absence of those parts keeps the first experiment on the narrow question:
can a delay-time jump be made without an amplitude hole while recursive audio
remains finite?

## Run

```sh
cmake -S . -B build
cmake --build build
ctest --test-dir build --output-on-failure
```

The test executable checks impulse timing, fractional interpolation, the
equal-power transition envelope, transition completion, parameter clamps, and
100,000 samples at feedback `1.2` for non-finite or unbounded output.

## Result on 2026-08-28

The isolated host test passed with GCC under C++17 and warnings treated as
errors:

```sh
g++ -std=c++17 -Wall -Wextra -Wpedantic -Werror \
  TemporalMemoryPrototype.cpp TemporalMemoryPrototypeTests.cpp \
  -o temporal_memory_tests
./temporal_memory_tests
```

The same assertions also passed with UndefinedBehaviorSanitizer. The CMake
wrapper was not executed because CMake is unavailable in the test environment.
AddressSanitizer was inconclusive because LeakSanitizer cannot inspect `/proc`
under the environment's tracing boundary; no AddressSanitizer pass is claimed.

These results verify only the host-side prototype and its listed assertions.
Audio quality, click energy on real material, CPU cost, iPhone behavior, and
the musical fit between Loopy, temporal memory, and Skulptur remain unverified.
