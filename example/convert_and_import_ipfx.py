from __future__ import annotations

from pathlib import Path
import sys

from ipfx.dataset.create import create_ephys_data_set

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from abf2nwb import convert_abf_to_nwb


def main() -> None:
    """Convert the bundled sample ABF file and load the result with IPFX."""

    abf_path = Path("data/2024_12_13_0020_for_nwb.abf")
    output_path = Path("data/example_output.nwb")

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
    first_sweep = data_set._data.get_sweep_data(1)

    print(f"Converted: {output_path}")
    print(f"Sweeps available: {len(data_set.sweep_table)}")
    print(f"First sweep stimulus unit: {first_sweep['stimulus_unit']}")
    print(f"First sweep sampling rate: {first_sweep['sampling_rate']}")


if __name__ == "__main__":
    main()
