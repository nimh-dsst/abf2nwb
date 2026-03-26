from __future__ import annotations

import unittest
from pathlib import Path

from ipfx.dataset.create import create_ephys_data_set

from abf2nwb import convert_abf_to_nwb


class TestIPFXImport(unittest.TestCase):
    """Integration tests for loading converted NWB files with IPFX."""

    def test_ipfx_can_import_converted_nwb(self) -> None:
        """Convert the sample ABF and verify that IPFX can load sweep data from it."""

        abf_path = Path("data/2024_12_13_0020_for_nwb.abf")
        output_path = Path("data/test_converted_for_ipfx.nwb")
        try:
            convert_abf_to_nwb(
                abf_path=abf_path,
                output_path=output_path,
                response_channel=None,
                stimulus_description="C1LSCOARSE",
                session_description="Intracellular electrophysiology experiment.",
                timezone_name="America/New_York",
                experimenter=None,
                institution=None,
                lab=None,
            )

            data_set = create_ephys_data_set(str(output_path))

            self.assertTrue(output_path.exists())
            self.assertEqual(len(data_set.sweep_table), 25)
            self.assertEqual(
                data_set.sweep_table.iloc[0]["clamp_mode"],
                data_set.CURRENT_CLAMP,
            )

            first_sweep = data_set._data.get_sweep_data(1)
            self.assertEqual(first_sweep["stimulus_unit"], "Amps")
            self.assertEqual(first_sweep["sampling_rate"], 20000.0)
            self.assertGreater(len(first_sweep["response"]), 0)
        finally:
            output_path.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
