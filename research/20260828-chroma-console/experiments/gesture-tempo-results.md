# Gesture tempo and separation experiment

## Question

Can a recorded hand movement survive tempo stretching, loop without a control
discontinuity, and remain distinct from effect-specific DRIFT?

## Scope

This is a deterministic control-domain design experiment, not a reconstruction
of Chroma Console firmware. The 4.8-second test gesture contains pauses,
direction changes, small hand-scale detail, and deliberately different start
and release values.

## Results

### Loop boundary

| Metric | Result |
|---|---:|
| Raw release-to-start jump | 0.541815 |
| Closed playback-loop jump | 0.000000 |
| Closure window | 120 ms |
| Portion touched by closure | 2.5% |
| Full-record closure error RMS | 0.052593 |

An immediate raw loop would create a large parameter step. A short closure
removes the seam, but it also changes the final 120 ms materially. Therefore
the raw recorded take and the playback-safe loop should remain separate data:
editing the playback edge must not erase the hand movement that was recorded.

### Tempo scaling

| Playback rate | Cycle duration | Shape correlation | Shape error RMS |
|---:|---:|---:|---:|
| 0.5x | 9.6 s | 1.0000000 | effectively zero |
| 1.0x | 4.8 s | 1.0000000 | effectively zero |
| 2.0x | 2.4 s | 0.9999997 | 0.000138 |
| 4.0x | 1.2 s | 0.9999907 | 0.000715 |

Normalized-phase playback preserves the hand-drawn shape through 4x speed.
The small high-speed error is control-rate interpolation error rather than a
change of the stored gesture.

### Gesture and DRIFT separation

At DRIFT `0.75`, the composite signal still correlates `0.995066` with the
repeating Gesture, while stored-Gesture mutation remains exactly zero. DRIFT
runs continuously over three Gesture cycles; adjacent DRIFT-cycle correlation
is `-0.0391`, so the instability does not become a second identical loop.

This supports two clocks and two state paths:

1. Gesture uses normalized loop phase and follows tempo.
2. DRIFT uses the effect engine's continuing time and does not rewrite or
   restart with Gesture.

## Design consequence

The playback parameter should be assembled from separate layers:

```text
raw hand take
  -> playback-only loop closure
  -> normalized-phase tempo playback
  -> effect-specific DRIFT on an independent clock
  -> bounded parameter output
```

Recording DRIFT into Gesture, restarting its random stream at every Gesture
boundary, or destructively replacing the raw tail with closure processing would
collapse these roles.

## Reproduction

```sh
python3 experiments/gesture_tempo_model.py \
  --output experiments/gesture-tempo-metrics.json
```

Validation performed:

- two runs produced byte-identical JSON;
- Python byte-code compilation succeeded;
- JSON SHA-256:
  `c3c1e22a0077ee856aebafdc30ce4ef6d3cef5f9ad4744a0f867e3c48115aa6b`.

Not yet verified: audio-rate smoothing, audible zipper noise, real-time tempo
changes inside a cycle, overwrite behavior during playback, multi-parameter
recording, hardware correspondence, and iPhone CPU cost.

