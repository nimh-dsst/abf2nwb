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

Choose one environment manager.

### Option A: Conda (Anaconda/Miniconda)

Clone the repository and enter it:

```bash
git clone <your-repo-url>
cd abf2nwb
```

Create the environment:

```bash
conda env create -f environment.yml
conda activate abf2nwb
```

### Option B: uv

Create and sync the uv environment:

```bash
uv sync
```

Activate it:

macOS/Linux:

```bash
source .venv/bin/activate
```

Windows PowerShell:

```bat
.venv\Scripts\activate.bat
```

Then verify setup with:

```bash
python -m unittest tests.test_ipfx_import
```

For a step-by-step notebook walkthrough, see
[example/convert_and_import_ipfx.ipynb](/Users/dmoracze/uv/abf2nwb/example/convert_and_import_ipfx.ipynb).
