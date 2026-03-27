from __future__ import annotations

import unittest
from pathlib import Path

from abf2nwb import resolve_output_path


class TestOutputPathResolution(unittest.TestCase):
    def test_defaults_to_input_directory_when_output_missing(self) -> None:
        abf_path = Path("data/2024_12_13_0020_for_nwb.abf")
        self.assertEqual(
            resolve_output_path(abf_path, None),
            Path("data/2024_12_13_0020.nwb"),
        )

    def test_bare_output_filename_is_written_under_data(self) -> None:
        abf_path = Path("data/2024_12_13_0020_for_nwb.abf")
        self.assertEqual(
            resolve_output_path(abf_path, Path("custom_name.nwb")),
            Path("data/custom_name.nwb"),
        )

    def test_explicit_directory_is_respected(self) -> None:
        abf_path = Path("data/2024_12_13_0020_for_nwb.abf")
        explicit = Path("outputs/custom_name.nwb")
        self.assertEqual(resolve_output_path(abf_path, explicit), explicit)


if __name__ == "__main__":
    unittest.main()
