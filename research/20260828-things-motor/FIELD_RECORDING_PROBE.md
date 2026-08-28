# External field-recording probe

Status: harness verified; no actual user recording has been measured.

## What is now executable

`rotor_field_probe.py` accepts exactly four external audio files and runs the
moving `HOLD` participation-switch comparison already established by the
synthetic probes. It produces:

- source names, decoded lengths, trimmed lengths, RMS, and peaks;
- immediate-switch and 5 ms ramp coefficient metrics;
- optional WAV renders of both versions for direct listening;
- a JSON report suitable for preserving the exact test conditions.

The decoder uses ffmpeg, so WAV and AAC/M4A inputs have both been exercised in
the automated tests. Every input is explicitly downmixed to mono and resampled
to the requested analysis rate, 48 kHz by default. All tracks are trimmed to the
shortest decoded recording; the report exposes both the original decoded frame
count and the common trimmed count. These transformations are not silent or
presented as original-capture measurements.

## Default run

```bash
python3 rotor_field_probe.py \
  voice.m4a room.m4a transient.m4a texture.m4a \
  --mode hold \
  --speed-hz 0.5 \
  --phase-at-switch 0.8 \
  --switch-seconds 0.2 \
  --ramp-ms 5 \
  --output-immediate field-immediate.wav \
  --output-ramped field-ramped.wav \
  > field-report.json
```

The four labels describe useful test roles, not required musical content:

| Track | Stress being exposed |
|---|---|
| voice | correlated harmonics and breath transients |
| room | low-level noise and diffuse ambience |
| transient | clicks, taps, or percussion near a hard edge |
| texture | sustained material crossing adjacent sectors |

## Verification

- PCM WAV decode is tested.
- An AAC/M4A file is generated, decoded, and amplitude-checked in the test.
- Four-file validation, shortest-track trimming, report fields, 5 ms ramp
  reduction, and both output WAVs are tested.
- The complete research suite passes 37 tests.

## Remaining evidence boundary

No voice memo, field recording, iPhone microphone capture, or other actual user
audio was available in this workspace. Therefore this work verifies the input
and measurement path, not click audibility or the musical quality of `HOLD` on
real material. Those conclusions remain open until four recordings are supplied
or captured by the application itself.
