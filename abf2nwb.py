from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np
import pyabf
from pynwb import NWBHDF5IO, NWBFile
from pynwb.icephys import CurrentClampSeries, CurrentClampStimulusSeries, SweepTable


UNIT_TO_SI = {
    "mV": ("volts", 1e-3),
    "V": ("volts", 1.0),
    "pA": ("amperes", 1e-12),
    "nA": ("amperes", 1e-9),
    "A": ("amperes", 1.0),
}


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments for the ABF-to-NWB converter."""

    parser = argparse.ArgumentParser(
        description=(
            "Convert an ABF file into a single-electrode current-clamp NWB file "
            "that is compatible with IPFX's NWB loader."
        )
    )
    parser.add_argument("abf_path", type=Path, help="Input ABF file.")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Output NWB path. Defaults to the ABF filename with .nwb extension.",
    )
    parser.add_argument(
        "--response-channel",
        type=int,
        default=None,
        help=(
            "ABF channel to export as the current-clamp response. Defaults to "
            "auto-detecting the channel with mV response and a non-zero command trace."
        ),
    )
    parser.add_argument(
        "--stimulus-description",
        default="C1LSCOARSE",
        help=(
            "Stimulus code written into the NWB PatchClampSeries metadata. "
            "Use an IPFX-recognized code such as 'C1LSCOARSE' when possible."
        ),
    )
    parser.add_argument(
        "--session-description",
        default="Intracellular electrophysiology experiment.",
        help="NWB session description.",
    )
    parser.add_argument(
        "--experimenter",
        default=None,
        help="Optional NWB experimenter name.",
    )
    parser.add_argument(
        "--institution",
        default=None,
        help="Optional NWB institution value.",
    )
    parser.add_argument(
        "--lab",
        default=None,
        help="Optional NWB lab value.",
    )
    parser.add_argument(
        "--timezone",
        default="America/New_York",
        help=(
            "Timezone used to localize the ABF recording timestamp when the ABF "
            "contains a naive datetime."
        ),
    )
    return parser.parse_args()


def default_output_path(abf_path: Path) -> Path:
    """Return the default NWB output path for an input ABF path."""

    stem = abf_path.stem.removesuffix("_for_nwb")
    return abf_path.with_name(f"{stem}.nwb")


def ensure_timezone(dt: datetime, timezone_name: str) -> datetime:
    """Attach a timezone to a naive datetime, leaving aware datetimes unchanged."""

    if dt.tzinfo is not None:
        return dt
    return dt.replace(tzinfo=ZoneInfo(timezone_name))


def si_unit_and_conversion(unit: str) -> tuple[str, float]:
    """Map an ABF unit string to its NWB SI unit name and conversion factor."""

    try:
        return UNIT_TO_SI[unit]
    except KeyError as exc:
        raise ValueError(f"Unsupported ABF unit {unit!r}.") from exc


def infer_response_channel(abf: pyabf.ABF) -> int:
    """Infer the current-clamp response channel from the first ABF sweep."""

    candidates: list[int] = []
    for channel_index in range(abf.channelCount):
        abf.setSweep(sweepNumber=0, channel=channel_index)
        has_command = bool(np.any(abf.sweepC))
        if abf.sweepUnitsY == "mV" and has_command:
            candidates.append(channel_index)
    if len(candidates) == 1:
        return candidates[0]
    if not candidates:
        raise ValueError(
            "Could not infer a current-clamp response channel. "
            "Pass --response-channel explicitly."
        )
    raise ValueError(
        f"Found multiple candidate response channels {candidates}. "
        "Pass --response-channel explicitly."
    )


def build_nwbfile(
    abf: pyabf.ABF,
    *,
    abf_path: Path,
    response_channel: int,
    stimulus_description: str,
    session_description: str,
    timezone_name: str,
    experimenter: str | None,
    institution: str | None,
    lab: str | None,
) -> NWBFile:
    """Build an NWBFile containing one current-clamp recording series per ABF sweep."""

    session_start_time = ensure_timezone(abf.abfDateTime, timezone_name)
    nwbfile = NWBFile(
        session_description=session_description,
        identifier=abf.abfID,
        session_start_time=session_start_time,
        experimenter=experimenter,
        institution=institution,
        lab=lab,
        notes=f"Converted from {abf_path.name}",
        protocol=abf.protocol or None,
        source_script=Path(__file__).read_text(),
        source_script_file_name=Path(__file__).name,
    )

    device = nwbfile.create_device(
        name="DeviceIcephys",
        description=f"{abf.creator} (ABF {abf.abfVersionString})",
    )
    electrode = nwbfile.create_icephys_electrode(
        name=f"electrode-{response_channel}",
        device=device,
        description="Whole-cell patch clamp electrode",
    )
    sweep_table = SweepTable.__new__(SweepTable, parent=nwbfile, in_construct_mode=True)
    sweep_table.__init__(name="sweep_table")
    sweep_table._in_construct_mode = False
    nwbfile.sweep_table = sweep_table

    for sweep_number in range(abf.sweepCount):
        abf.setSweep(sweepNumber=sweep_number, channel=response_channel)
        nwb_sweep_number = np.uint32(sweep_number + 1)

        response_unit, response_conversion = si_unit_and_conversion(abf.sweepUnitsY)
        stimulus_unit, stimulus_conversion = si_unit_and_conversion(abf.sweepUnitsC)

        response = CurrentClampSeries(
            name=f"current_clamp-response-{sweep_number + 1:02d}",
            data=np.asarray(abf.sweepY, dtype=np.float32),
            unit=response_unit,
            conversion=response_conversion,
            electrode=electrode,
            gain=np.nan,
            rate=float(abf.dataRate),
            starting_time=float(abf.sweepX[0]),
            stimulus_description=stimulus_description,
            description=f"Response to: {stimulus_description}",
            sweep_number=nwb_sweep_number,
            bias_current=None,
            bridge_balance=None,
            capacitance_compensation=None,
        )
        stimulus = CurrentClampStimulusSeries(
            name=f"stimulus-{sweep_number + 1:02d}",
            data=np.asarray(abf.sweepC, dtype=np.float32),
            unit=stimulus_unit,
            conversion=stimulus_conversion,
            electrode=electrode,
            gain=np.nan,
            rate=float(abf.dataRate),
            starting_time=float(abf.sweepX[0]),
            stimulus_description=stimulus_description,
            description=f"Stim type: {stimulus_description}",
            sweep_number=nwb_sweep_number,
        )

        nwbfile.add_stimulus(stimulus, use_sweep_table=True)
        nwbfile.add_acquisition(response, use_sweep_table=True)
        recording_id = nwbfile.add_intracellular_recording(
            electrode=electrode,
            stimulus=stimulus,
            stimulus_start_index=0,
            stimulus_index_count=len(abf.sweepC),
            response=response,
            response_start_index=0,
            response_index_count=len(abf.sweepY),
        )
        simultaneous_id = nwbfile.add_icephys_simultaneous_recording(
            recordings=[recording_id]
        )
        nwbfile.add_icephys_sequential_recording(
            stimulus_type=stimulus_description,
            simultaneous_recordings=[simultaneous_id],
        )

    return nwbfile


def convert_abf_to_nwb(
    *,
    abf_path: Path,
    output_path: Path,
    response_channel: int | None,
    stimulus_description: str,
    session_description: str,
    timezone_name: str,
    experimenter: str | None,
    institution: str | None,
    lab: str | None,
) -> Path:
    """Convert an ABF recording to an IPFX-readable NWB file on disk."""

    abf = pyabf.ABF(str(abf_path))
    selected_channel = response_channel
    if selected_channel is None:
        selected_channel = infer_response_channel(abf)
    if not 0 <= selected_channel < abf.channelCount:
        raise ValueError(
            f"--response-channel must be between 0 and {abf.channelCount - 1}."
        )

    nwbfile = build_nwbfile(
        abf,
        abf_path=abf_path,
        response_channel=selected_channel,
        stimulus_description=stimulus_description,
        session_description=session_description,
        timezone_name=timezone_name,
        experimenter=experimenter,
        institution=institution,
        lab=lab,
    )

    with NWBHDF5IO(str(output_path), "w") as io:
        io.write(nwbfile)

    return output_path


def main() -> None:
    """Run the command-line converter and print the written NWB path."""

    args = parse_args()
    output_path = args.output or default_output_path(args.abf_path)
    written_path = convert_abf_to_nwb(
        abf_path=args.abf_path,
        output_path=output_path,
        response_channel=args.response_channel,
        stimulus_description=args.stimulus_description,
        session_description=args.session_description,
        timezone_name=args.timezone,
        experimenter=args.experimenter,
        institution=args.institution,
        lab=args.lab,
    )
    print(written_path)


if __name__ == "__main__":
    main()
