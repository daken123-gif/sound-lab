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
- a separate four-line feedback delay network candidate;
- normalized Hadamard feedback mixing;
- independent fractional delay coordinates for the four network lines;
- per-line damping, DC blocking, and soft clipping;
- a stereo return derived from two line pairs.
- independent dual-head delay-time jumps on all four FDN lines.

## Deliberately absent

- any claim about Dedalus's unpublished internal line count or matrix;
- stereo crossfeed and random panning;
- Scrub/Drift modulation, pitch mode, ducking, or gate behavior;
- Loopy track routing, Skulptur ordering, UI, AUv3, and iPhone integration.

The four-line network now contains the dual-head transition mechanism on each
line. The original mono cell remains as the smaller reference experiment; the
network does not instantiate four copies of its independent feedback loop.

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

The second test executable checks normalized-Hadamard energy preservation,
per-line impulse timing, reset behavior, parameter clamps, and 200,000 samples
of the four-line network at feedback `1.2`. It also checks that changing one
line's delay creates no amplitude hole, completes in the requested number of
samples, and does not move the other three read coordinates.

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

The four-line network was subsequently built with the same C++17 warning
policy. Its host assertions and UndefinedBehaviorSanitizer run also passed.

The dual-head mechanism was then integrated per line. Host and undefined-
behavior tests passed again, including simultaneous delay jumps inside the
200,000-sample high-feedback run. Retargeting a line before its current
crossfade completes remains explicitly unverified.

These results verify only the host-side prototype and its listed assertions.
Audio quality, click energy on real material, CPU cost, iPhone behavior, and
the musical fit between Loopy, temporal memory, and Skulptur remain unverified.
