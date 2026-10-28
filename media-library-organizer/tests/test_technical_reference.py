from __future__ import annotations

import re
import subprocess
import types
import unittest
from pathlib import Path
from unittest.mock import patch


DOCUMENT = Path(__file__).resolve().parents[1] / "technical-reference.md"


def helpers() -> types.ModuleType:
    module = types.ModuleType("technical_reference")
    for source in re.findall(r"```python\n(.*?)```", DOCUMENT.read_text(), re.S):
        exec(compile(source, str(DOCUMENT), "exec"), module.__dict__)
    return module


class TechnicalReferenceTest(unittest.TestCase):
    def setUp(self) -> None:
        self.module = helpers()

    def test_probe_failure_never_fabricates_default_values(self) -> None:
        with patch.object(self.module.subprocess, "run", side_effect=FileNotFoundError):
            result = self.module.collect_technical_info("Untitled.mkv")
        self.assertTrue(all(field == {"value": None, "source": "unknown"} for field in result.values()))

    def test_nonzero_exit_invalid_json_and_missing_streams_are_unknown(self) -> None:
        outcomes = [
            subprocess.CalledProcessError(1, "ffprobe"),
            types.SimpleNamespace(stdout="not JSON"),
            types.SimpleNamespace(stdout='{"streams": []}'),
            types.SimpleNamespace(stdout='{"streams": [{"codec_type": "video"}, {"codec_type": "audio"}]}'),
        ]
        for outcome in outcomes:
            with self.subTest(outcome=outcome):
                module = helpers()
                arguments = {"side_effect": outcome} if isinstance(outcome, Exception) else {"return_value": outcome}
                with patch.object(module.subprocess, "run", **arguments):
                    result = module.collect_technical_info("Untitled.mkv")
                self.assertTrue(all(field["value"] is None for field in result.values()))

    def test_explicit_filename_values_are_guesses(self) -> None:
        with patch.object(self.module.subprocess, "run", side_effect=FileNotFoundError):
            result = self.module.collect_technical_info("Show.1080p.HEVC.SDR.WEB-DL.2.0.mkv")
        self.assertEqual({"value": "SDR", "source": "filename"}, result["hdr"])
        self.assertEqual({"value": "2.0", "source": "filename"}, result["audio"])
        self.assertTrue(all(field["source"] == "filename" for field in result.values()))

    def test_measured_values_win_and_probe_runs_once(self) -> None:
        output = types.SimpleNamespace(stdout='{"streams": [{"codec_type": "video", "height": 2160, "codec_name": "hevc", "color_transfer": "smpte2084"}, {"codec_type": "audio", "channels": 6}]}')
        with patch.object(self.module.subprocess, "run", return_value=output) as probe:
            result = self.module.collect_technical_info("Show.1080p.AVC.SDR.2.0.mkv")
        self.assertEqual({"value": "2160p", "source": "ffprobe"}, result["resolution"])
        self.assertEqual({"value": "HDR10", "source": "ffprobe"}, result["hdr"])
        self.assertEqual({"value": "5.1", "source": "ffprobe"}, result["audio"])
        self.assertEqual(1, probe.call_count)
        self.assertTrue(probe.call_args.kwargs["check"])


if __name__ == "__main__":
    unittest.main()
