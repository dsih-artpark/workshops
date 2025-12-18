# Example Repository for the Workshop on Experiment Tracking

This repository is a template for the workshop on experiment tracking. It is a simple example of how to use git to track experiments.

## System Level Requirements

- git (https://git-scm.com/)
- Python (https://www.python.org/)
- uv (https://docs.astral.sh/uv/)

## Usage

1. Clone the repository

```bash
git clone https://github.com/dsih-artpark/example.git
```

2. Install the dependencies using uv

```bash
uv sync
```

3. Get the data

Before you do, ensure you have the dataio client configured. To do this, have your dataio API key handy. Then run:

```bash
uv run dataio init
```

Once this is done, you can run the script to fetch the data:

```bash
uv run get_data
```

One data file, the karnataka_districts.geojson, needs to be manually obtained from Sneha or Adish. Once done, you can configure it in the config.yaml file, in the files section of the relevant experiment.

> [!NOTE]
> This is a one-time setup. And don't worry about data being replicated across experiments. The script is set up to only download the data once, and then use the local copy for all experiments.
