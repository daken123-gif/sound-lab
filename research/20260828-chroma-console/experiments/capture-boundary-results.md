# Capture boundary experiment

## Question

How should Capture turn an arbitrary button-release point into a repeatable
loop without treating a 180 ms grain and a 2.4 s phrase as the same object?

## Scope

This is a deterministic 48 kHz audio experiment and a product-design
hypothesis. It is not a reconstruction of Chroma Console firmware. Synthetic
captures deliberately end at waveform values that do not match their starts.

## Compared boundary policies

1. Hard loop: jump directly from the final sample to the first sample.
2. Fixed 120 ms overlap: included as a sizing reference.
3. Duration-adaptive overlap:
   - 180 ms capture: 45 ms overlap (`25%`)
   - 650 ms capture: 30 ms overlap (`4.62%`)
   - 2.4 s capture: 10 ms overlap (`0.42%`)

A 120 ms overlap consumes `66.67%` of a 180 ms capture and exceeds half its
length, so it cannot be used by this symmetric overlap algorithm. The boundary
must depend on the captured duration.

## Results

| Capture | Hard seam / ordinary step | Adaptive seam / ordinary step | Jump reduction | Effective loop |
|---|---:|---:|---:|---:|
| 180 ms | 21.63x | 1.05x | 26.03 dB | 135 ms |
| 650 ms | 41.58x | 0.75x | 34.74 dB | 620 ms |
| 2.4 s | 44.61x | 0.17x | 48.47 dB | 2.39 s |

The hard seams are 22–45 times larger than an ordinary adjacent-sample step.
After adaptive overlap, every seam is at or below roughly one normal waveform
step. The 8 kHz-and-above energy fraction around each seam also falls by several
orders of magnitude in these synthetic cases.

## Interpretation

One Capture mechanism can support two behaviors if duration changes the
boundary policy rather than selecting a separate looper:

- very short material gives up a substantial portion of its literal phrase
  length to become a dense overlapping cycle;
- long material receives only enough overlap to hide the release seam, so its
  phrase duration remains nearly intact.

The experiment supports the structural precondition for a short sustain/drone,
but it does not prove that the result sounds musically sustained. Listening
tests with voice, room tone, percussion, and pitched instruments are still
required.

## Data model consequence

Keep three durations distinct:

```text
recorded duration = button press to button release
overlap duration  = function(recorded duration)
playback duration = recorded duration - overlap duration
```

The displayed Capture length should remain the recorded duration. Quietly
reporting the shortened playback period as if it were the user's recording
would make timing appear inaccurate.

## Reproduction

```sh
python3 experiments/capture_boundary_model.py \
  --output experiments/capture-boundary-metrics.json
```

Validation performed:

- two runs produced byte-identical JSON;
- Python byte-code compilation succeeded;
- JSON SHA-256:
  `9e66c6ee873785b1f87e8d74e30d00568b1c19600ecf671e40bbda246df377c8`.

Not yet verified: perceptual quality, stereo phase, zero-length taps, recording
replacement, PRE/POST routing, live input safety, hardware correspondence, and
iPhone real-time load.

