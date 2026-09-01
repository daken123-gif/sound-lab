# Cross-model sensitivity audit — 2026-09-01

## Outcome

The two drum findings reproduce across two separately trained weight sets in the same MDX-Net family:

| Preview | Model A BPM | Model B BPM | A/B waveform cosine | Model A triplet score | Model B triplet score | Decision |
|---|---:|---:|---:|---:|---:|---|
| Billy Jack | 141.14 | 141.78 | 0.9465 | 0.005 | 0.016 | stable pulse; no triplet-spacing claim |
| Sweet Exorcist | 111.59 | 111.63 | 0.9123 | 0.657 | 0.715 | triplet-spaced onset structure reproduced |

The Sweet Exorcist drum result also survives windowing:

| Window | Model A | Model B |
|---|---:|---:|
| 0–10 s | 0.537 | 0.625 |
| 10–20 s | 0.762 | 0.684 |
| 20–end | 0.911 | 0.747 |

These scores measure rotation-invariant onset spacing around the estimated beat. They do not by themselves identify syncopation, downbeats, microtiming feel, or a particular performed drum pattern.

## Calibration gate

Before using Model A on real previews, it was tested on a synthetic mixture whose drum and bass stems are known.

| Target | Target cosine | SI-SDR | A/B cosine | Gate |
|---|---:|---:|---:|---|
| Drums | 0.8214 | 3.169 dB | 0.8018 | pass, but marginal |
| Bass | 0.9673 | 11.631 dB | 0.9928 | pass |

The predefined gate was target cosine ≥ 0.8 and SI-SDR ≥ 3.0 dB. The drum separator only narrowly passes, so the real-track comparison is used as a direction-of-effect sensitivity check, not as ground-truth transcription.

## Bass decision

The bass waveforms are similar across A/B weights, but their beat-phase descriptions are not reliable enough for musical conclusions. Billy Jack has low full-excerpt beat confidence (A 0.322; B 0.368). Sweet Exorcist changes to roughly 75 BPM in the first ten-second window and roughly 111 BPM later. Bass-derived phase claims remain rejected.

## Independence limit

This is not independent architectural replication. `kuielab_a_*` and `kuielab_b_*` are different weight sets in the same MDX-Net architecture family. The result rules out a simple single-weight accident more strongly than the original one-model run, but it does not rule out a family-wide separation bias.

An independent Demucs run was attempted. The model and configuration downloaded, but inference never began: PyTorch state-dictionary loading failed because this sandbox has no readable `/proc/cpuinfo` and CPU feature initialization failed. Setting `ATEN_CPU_CAPABILITY=default` did not remove that failure. This is recorded as a blocked test, not a negative model result.

## Reproducibility

- Full machine-readable result: `cross-model-results-20260901.json`
- Reproduction and gate logic: `cross_model_audit.py`
- Inputs: the existing 30-second Apple Music previews and synthetic fixture
- Outputs intentionally excluded from Git: copyrighted preview audio, derived WAV stems, model binaries, virtual environments

Model SHA-256 values used locally:

- `kuielab_a_drums.onnx`: `40f586b7091934dd6f5563f0cba8f14bad57ce88440da1098bf388ea716c2901`
- `kuielab_a_bass.onnx`: `0c3e77b9963185b1ea6bb46a4b8924137d9370fc1ccdefec7b1b416ef550dcaa`
- `kuielab_b_drums.onnx`: `a6fecee758059b33ed99f6dabba297439b3e7cacfac4b1097bd324aff8052208`
- `kuielab_b_bass.onnx`: `b4b7080fe501d0bece62076c5d4eda4d6590c5207ed78ec84a57bac0740a061d`

## Current claim boundary

Supported: within these two 30-second previews, two MDX weight sets recover mutually similar drum estimates, and the same contrast in beat-phase spacing appears in both estimates.

Not supported: full-song characterization, causal attribution to a musician, exact notation, isolated multitrack truth, or equivalence to listening-based criticism.
