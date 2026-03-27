# ABF to NWB for IPFX

This repository converts Axon Binary Format (`.abf`) electrophysiology recordings into NWB files
that can be loaded by the Allen Institute's `ipfx` package.

The main use case is:

- start with an `.abf` recording in [data](/Users/dmoracze/uv/abf2nwb/data)
- convert it to NWB with [abf2nwb.py](/Users/dmoracze/uv/abf2nwb/abf2nwb.py)
- load the NWB file with `ipfx` for downstream analysis

The converter writes a single-electrode current-clamp NWB file with:

- `CurrentClampSeries` response data
- `CurrentClampStimulusSeries` command data
- icephys intracellular recording tables
- the deprecated `sweep_table` that `ipfx` still expects

## Basic Use

Convert an ABF file into an NWB file:

```bash
# Activate your environment first (Conda or uv/.venv), then run:
python abf2nwb.py data/2024_12_13_0020_for_nwb.abf -o 2024_12_13_0020_ipfx.nwb
```

The command above writes `data/2024_12_13_0020_ipfx.nwb`. Bare output filenames are placed in
`data/`; provide a path with a directory if you want a different location.

For the bundled `data/2024_12_13_0020_for_nwb.abf`, the converter auto-detects channel 0 as the
current-clamp response channel.

Optional flags:

- `--response-channel N` to force a specific ABF channel
- `--stimulus-description CODE` to set the IPFX stimulus code written to NWB metadata
- `--timezone America/New_York` to localize the ABF recording timestamp

## Example

An end-to-end example that converts the bundled sample ABF file and imports it with `ipfx` lives
at [example/convert_and_import_ipfx.py](/Users/dmoracze/uv/abf2nwb/example/convert_and_import_ipfx.py).

Run it with:

```bash
# Activate your environment first (Conda or uv/.venv), then run:
python example/convert_and_import_ipfx.py
```

Run the integration test with:

```bash
# Activate your environment first (Conda or uv/.venv), then run:
python -m unittest tests.test_ipfx_import
```

## From Scratch

Use one of the complete setups below.

### Windows + Conda (Anaconda/Miniconda)

1. Open Anaconda Prompt (or Command Prompt with Conda initialized).
2. Clone the repository and enter it.
3. Create and activate the Conda environment from `environment.yml`.
4. Run the integration test.
5. Run a sample conversion.

```bat
git clone <your-repo-url>
cd abf2nwb
conda env create -f environment.yml
conda activate abf2nwb
python -m unittest tests.test_ipfx_import
python abf2nwb.py data/2024_12_13_0020_for_nwb.abf -o 2024_12_13_0020_ipfx.nwb
```

### macOS/Linux + uv

1. Install `uv` (if needed).
2. Clone the repository and enter it.
3. Create and sync the local environment.
4. Activate `.venv`.
5. Run the integration test.
6. Run a sample conversion.

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
git clone <your-repo-url>
cd abf2nwb
uv sync
source .venv/bin/activate
python -m unittest tests.test_ipfx_import
python abf2nwb.py data/2024_12_13_0020_for_nwb.abf -o 2024_12_13_0020_ipfx.nwb
```

For a step-by-step notebook walkthrough, see
[example/convert_and_import_ipfx.ipynb](/Users/dmoracze/uv/abf2nwb/example/convert_and_import_ipfx.ipynb).
