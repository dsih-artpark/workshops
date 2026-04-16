# DSIH-ARTPARK Workshop Repository

This repository contains materials for all workshops in this series, including slide decks, source files, and supporting assets.

## Available Workshop PDFs

1. [Workshop 1: Experiment Tracking](workshops/workshop-01-experiment-tracking/presentation.pdf)
2. [Workshop 2: Gen AI Workflows](workshops/workshop-02-gen-ai-workflows-01/presentation.pdf)

## Workshop 1: Experiment Tracking

This repository is a template for the workshop on experiment tracking. It is a simple example of how to use git to track experiments.

## System Level Requirements

- git (https://git-scm.com/)
- uv (https://docs.astral.sh/uv/)
- Python (https://www.python.org/ (Optional, uv will install it for you))

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

This will automatically create an .env file in the root of the repository.

> [!NOTE]
> The .env file is used to store the dataio API key. It is not committed to the repository.

Once this is done, you can run the script to fetch the data:

```bash
uv run get_data
```

One data file, the karnataka_districts.geojson, needs to be manually obtained from Sneha or Adish. Once done, you can configure it in the config.yaml file, in the files section of the relevant experiment.

> [!NOTE]
> This is a one-time setup. And don't worry about data being replicated across experiments. The script is set up to only download the data once, and then use the local copy for all experiments.

4. Run the experiments

```bash
uv run eda-baseline
```

```bash
uv run moran-spatial
```

## Results

The plots will be saved in the `plots/<experiment-name>/` directory.
