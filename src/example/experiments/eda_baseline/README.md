# Experiment: Baseline EDA on FMD Vaccinations

**Date:** 2025-12-18  
**Experiment ID:** `eda-baseline`

## Goal

Understand the FMD vaccination data for Karnataka - distributions, coverage patterns, and identify gaps for further analysis.

## What I'm Testing

- How many districts have vaccination data?
- What's the distribution of vaccinations per district?
- Are there patterns across vaccination rounds?
- What's the farmers-to-vaccination ratio?

## Data Sources

1. **FMD Vaccinations**: NDLM Bharat Pashudhan (dataset 86)
   - Districts, vaccination rounds, counts
2. **Livestock Census**: 20th Livestock Census (dataset 41)
   - Population by species for context

## Running the Experiment

```bash
# Run with default config
uv run eda-baseline

# Run with custom config
uv run eda-baseline --config path/to/config.yaml
```

**Required in `pyproject.toml`:**

```toml
[project.scripts]
eda-baseline = "experiments.eda_baseline:main"
```

## Method

1. Load Karnataka vaccination records
2. Calculate summary statistics by district and round
3. Visualize distributions and patterns
4. Identify top/bottom performing districts

## Expected Outcome

- Summary statistics table
- Distribution plots showing variation
- Identification of districts for deeper spatial analysis

## Results

### Summary Statistics

- Total vaccinations: [Fill after run]
- Districts covered: [Fill after run]
- Vaccination rounds: [Fill after run]

### Key Observations

- [Add observations here after running]

### Plots Generated

- `plots/eda_baseline_overview.png`: 4-panel overview
  - Vaccination distribution histogram
  - Top 10 districts bar chart
  - Vaccinations by round
  - Farmers vs vaccinations scatter

## Next Steps

- [ ] Calculate vaccination coverage (vaccinations / livestock population)
- [ ] Merge with geospatial data for spatial analysis
- [ ] Run Moran's I test for spatial autocorrelation
- [ ] Investigate why certain districts have low coverage
