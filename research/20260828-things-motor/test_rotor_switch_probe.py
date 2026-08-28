import tempfile
import unittest
import wave
from pathlib import Path

from rotor_audio_probe import material_cases
from rotor_layout import layout_coefficients
from rotor_switch_probe import probe, render_switch


class MovingSwitchTests(unittest.TestCase):
    def setUp(self) -> None:
        self.sample_rate = 4_000
        self.tracks = material_cases(self.sample_rate, 1.0)["unrelated"]
        self.switch_frame = 800

    def test_ramp_ends_on_live_moving_target(self) -> None:
        frames = 20
        _, history = render_switch(
            self.tracks,
            sample_rate=self.sample_rate,
            mode="hold",
            switch_frame=self.switch_frame,
            phase_at_switch=0.8,
            speed_hz=0.5,
            transition_frames=frames,
        )
        final_frame = self.switch_frame + frames - 1
        final_phase = (0.8 + (frames - 1) * 0.5 / self.sample_rate) % 1.0
        self.assertEqual(
            history[final_frame],
            layout_coefficients(final_phase, [True, True, True, False], "hold"),
        )

    def test_phase_continues_through_switch(self) -> None:
        _, history = render_switch(
            self.tracks,
            sample_rate=self.sample_rate,
            mode="hold",
            switch_frame=self.switch_frame,
            phase_at_switch=0.1,
            speed_hz=0.5,
            transition_frames=20,
        )
        self.assertNotEqual(history[self.switch_frame - 2], history[self.switch_frame - 1])
        self.assertNotEqual(history[self.switch_frame + 19], history[self.switch_frame + 20])

    def test_unaffected_hold_arc_keeps_unramped_motion(self) -> None:
        _, immediate = render_switch(
            self.tracks,
            sample_rate=self.sample_rate,
            mode="hold",
            switch_frame=self.switch_frame,
            phase_at_switch=0.1,
            speed_hz=0.5,
            transition_frames=1,
        )
        _, ramped = render_switch(
            self.tracks,
            sample_rate=self.sample_rate,
            mode="hold",
            switch_frame=self.switch_frame,
            phase_at_switch=0.1,
            speed_hz=0.5,
            transition_frames=20,
        )
        self.assertEqual(
            immediate[self.switch_frame : self.switch_frame + 20],
            ramped[self.switch_frame : self.switch_frame + 20],
        )

    def test_hold_avoids_nonlocal_switch_jump(self) -> None:
        report = probe(sample_rate=self.sample_rate, seconds=1.0, ramp_frames=20)
        case = report["scenarios"]["nonlocal_phase_0_10"]
        self.assertGreater(
            case["skip"]["immediate"]["coefficient_step_at_switch"], 0.1
        )
        self.assertLess(
            case["hold"]["immediate"]["coefficient_step_at_switch"], 0.001
        )
        self.assertLess(
            case["hole"]["immediate"]["coefficient_step_at_switch"], 0.001
        )

    def test_ramp_reduces_audible_track_switch_step(self) -> None:
        report = probe(sample_rate=self.sample_rate, seconds=1.0, ramp_frames=20)
        case = report["scenarios"]["audible_track4_phase_0_80"]
        for mode in ("skip", "hold", "hole"):
            self.assertLess(
                case[mode]["ramp_5ms"]["coefficient_step_at_switch"],
                case[mode]["immediate"]["coefficient_step_at_switch"] / 10,
            )

    def test_wav_render_writes_twelve_valid_files(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            probe(
                sample_rate=self.sample_rate,
                seconds=1.0,
                ramp_frames=20,
                wav_dir=Path(directory),
            )
            files = list(Path(directory).glob("*.wav"))
            self.assertEqual(len(files), 12)
            for path in files:
                with wave.open(str(path), "rb") as rendered:
                    self.assertEqual(rendered.getnchannels(), 1)
                    self.assertEqual(rendered.getframerate(), self.sample_rate)
                    self.assertEqual(rendered.getnframes(), self.sample_rate)


if __name__ == "__main__":
    unittest.main()
