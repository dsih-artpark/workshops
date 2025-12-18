"""
Spatial Autocorrelation: FMD Vaccination Coverage in Karnataka

Goal: Test if vaccination coverage exhibits spatial clustering using Moran's I

Usage:
    uv run moran-spatial
    uv run moran-spatial --config config.yaml
"""

import argparse
import os

import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from esda.moran import Moran
from libpysal.weights import Queen
from splot.esda import moran_scatterplot

from example import load_config

EXPERIMENT_NAME = "moran-spatial-autocorrelation"


def main():
    """Run Moran's I spatial autocorrelation analysis on vaccination coverage"""

    # Parse arguments
    parser = argparse.ArgumentParser(
        description="Spatial autocorrelation analysis of FMD vaccination coverage"
    )
    parser.add_argument(
        "--config",
        type=str,
        default="config.yaml",
        help="Path to config file (default: config.yaml)",
    )
    args = parser.parse_args()

    # Set style
    sns.set_style("whitegrid")
    plt.rcParams["figure.figsize"] = (12, 8)

    # Load config
    config = load_config(args.config)
    experiment_config = config["experiments"][EXPERIMENT_NAME]

    # Construct file paths
    data_dir = config["meta"]["directories"]["data"]
    plots_dir = os.path.join(config["meta"]["directories"]["plots"], EXPERIMENT_NAME)
    os.makedirs(plots_dir, exist_ok=True)

    vax_file = os.path.join(data_dir, experiment_config["files"]["vax"])
    pop_file = os.path.join(data_dir, experiment_config["files"]["population"])
    geo_file = os.path.join(
        data_dir, experiment_config["files"]["ka_districts_geojson"]
    )

    print("=" * 60)
    print("SPATIAL AUTOCORRELATION: FMD Vaccination Coverage")
    print("=" * 60)

    # Load data
    print("\n📂 Loading data...")
    vax_df = pd.read_csv(vax_file)
    pop_df = pd.read_csv(pop_file)
    geo_df = gpd.read_file(geo_file)

    print(f"Vaccination records: {len(vax_df):,}")
    print(f"Population records: {len(pop_df):,}")
    print(f"Geographic features: {len(geo_df):,}")

    # Filter for Karnataka and aggregate vaccinations
    print("\n🔄 Processing vaccination data...")
    ka_vax = vax_df[vax_df["state.name"] == "Karnataka"].copy()

    district_vax = (
        ka_vax.groupby("district.name")["totalVaccinations.count"].sum().reset_index()
    )
    district_vax.columns = ["district_name", "total_vaccinations"]
    print(f"Districts with vaccination data: {len(district_vax)}")

    # Calculate total livestock population (cattle + buffalo)
    print("\n🐄 Processing livestock population...")
    pop_df["total_livestock"] = (
        pop_df["population.cattle"] + pop_df["population.buffalo"]
    )
    pop_df_clean = pop_df[["district.name", "total_livestock"]].copy()
    pop_df_clean.columns = ["district_name", "total_livestock"]
    print(f"Districts with population data: {len(pop_df_clean)}")

    # Normalize district names for merging (case differences!)
    print("\n🔧 Normalizing district names...")
    district_vax["district_name_clean"] = (
        district_vax["district_name"].str.upper().str.strip()
    )
    pop_df_clean["district_name_clean"] = (
        pop_df_clean["district_name"].str.upper().str.strip()
    )

    print(
        f"Vaccination districts (unique): {district_vax['district_name_clean'].nunique()}"
    )
    print(
        f"Population districts (unique): {pop_df_clean['district_name_clean'].nunique()}"
    )

    # Merge vaccination and population data
    print("\n🔗 Merging datasets...")
    merged_data = district_vax.merge(
        pop_df_clean,
        left_on="district_name_clean",
        right_on="district_name_clean",
        how="inner",
        suffixes=("_vax", "_pop"),
    )

    # Calculate vaccination coverage (vaccinations per 1000 livestock)
    merged_data["coverage"] = (
        merged_data["total_vaccinations"] / merged_data["total_livestock"] * 1000
    )

    print(f"Districts with both vax and population data: {len(merged_data)}")

    if len(merged_data) == 0:
        print(
            "\n❌ ERROR: No districts matched between vaccination and population data!"
        )
        print(
            "Sample vaccination districts:",
            district_vax["district_name_clean"].head(3).tolist(),
        )
        print(
            "Sample population districts:",
            pop_df_clean["district_name_clean"].head(3).tolist(),
        )
        return

    # Check for districts in vaccination data but not in population data
    vax_only = set(district_vax["district_name_clean"]) - set(
        pop_df_clean["district_name_clean"]
    )
    pop_only = set(pop_df_clean["district_name_clean"]) - set(
        district_vax["district_name_clean"]
    )

    if vax_only:
        print(
            f"\n⚠️  Districts in vaccination data but not in population data: {vax_only}"
        )
    if pop_only:
        print(
            f"\n⚠️  Districts in population data but not in vaccination data: {pop_only}"
        )

    print("\nCoverage Statistics (vaccinations per 1000 livestock):")
    print(merged_data["coverage"].describe())

    # Merge with geographic data
    print("\n🗺️  Merging with geographic data...")
    # GeoJSON uses 'name' field (not 'DISTRICT'), already in uppercase
    if "name" not in geo_df.columns:
        print("❌ ERROR: GeoJSON doesn't have 'name' column!")
        print("Available columns:", geo_df.columns.tolist())
        return

    geo_df["district_name_clean"] = geo_df["name"].str.upper().str.strip()

    geo_merged = geo_df.merge(merged_data, on="district_name_clean", how="left")

    print(f"Districts in final geodataframe: {len(geo_merged)}")
    print(f"Districts with coverage data: {geo_merged['coverage'].notna().sum()}")

    if geo_merged["coverage"].isna().any():
        print("\n⚠️  Districts without coverage data:")
        missing = geo_merged[geo_merged["coverage"].isna()]["name"].tolist()
        print(missing)

    # Create spatial weights matrix
    print("\n⚙️  Creating spatial weights matrix...")
    # Drop districts without coverage for Moran's I calculation
    geo_analysis = geo_merged[geo_merged["coverage"].notna()].copy()

    w = Queen.from_dataframe(geo_analysis)
    w.transform = "r"  # Row-standardize
    print(f"Spatial weights matrix created: {w.n} observations")

    # Run Moran's I test
    print("\n📊 Running Moran's I test...")
    moran = Moran(geo_analysis["coverage"].values, w, permutations=999)

    print("=" * 60)
    print(f"Moran's I statistic: {moran.I:.4f}")
    print(f"Expected I (null): {moran.EI:.4f}")
    print(f"P-value: {moran.p_sim:.4f}")
    print(f"Z-score: {moran.z_sim:.4f}")
    print("=" * 60)

    if moran.p_sim < 0.05:
        if moran.I > 0:
            interpretation = "Significant POSITIVE spatial autocorrelation detected"
            explanation = "(Districts with similar coverage cluster together)"
        else:
            interpretation = "Significant NEGATIVE spatial autocorrelation detected"
            explanation = "(Districts with dissimilar coverage are neighbors)"
    else:
        interpretation = "No significant spatial autocorrelation detected"
        explanation = "(Coverage appears randomly distributed across space)"

    print(f"\n🔍 Interpretation: {interpretation}")
    print(f"   {explanation}")

    # Create visualizations
    print("\n📈 Creating visualizations...")

    # 1. Choropleth map of vaccination coverage
    fig, axes = plt.subplots(1, 2, figsize=(16, 8))

    ax1 = axes[0]
    geo_merged.plot(
        column="coverage",
        cmap="YlOrRd",
        legend=True,
        ax=ax1,
        missing_kwds={"color": "lightgrey", "label": "No data"},
        legend_kwds={"label": "Vaccinations per 1000 livestock"},
    )
    ax1.set_title(
        "FMD Vaccination Coverage by District\n(Karnataka)",
        fontsize=14,
        fontweight="bold",
    )
    ax1.axis("off")

    # 2. Moran scatter plot
    ax2 = axes[1]

    moran_scatterplot(moran, ax=ax2)
    ax2.set_title(
        f"Moran's I Scatter Plot\n(I = {moran.I:.4f}, p = {moran.p_sim:.4f})",
        fontsize=14,
        fontweight="bold",
    )

    plt.tight_layout()
    output_file = os.path.join(plots_dir, "spatial_autocorrelation.png")
    plt.savefig(output_file, dpi=150, bbox_inches="tight")
    print(f"✅ Saved plot: {output_file}")

    # Additional: Coverage distribution histogram
    fig, ax = plt.subplots(figsize=(10, 6))
    merged_data["coverage"].hist(bins=20, ax=ax, edgecolor="black")
    ax.set_title(
        "Distribution of Vaccination Coverage Across Districts",
        fontsize=14,
        fontweight="bold",
    )
    ax.set_xlabel("Vaccinations per 1000 livestock")
    ax.set_ylabel("Number of Districts")
    ax.axvline(
        merged_data["coverage"].mean(),
        color="red",
        linestyle="--",
        label=f"Mean: {merged_data['coverage'].mean():.1f}",
    )
    ax.legend()

    output_file_dist = os.path.join(plots_dir, "coverage_distribution.png")
    plt.savefig(output_file_dist, dpi=150, bbox_inches="tight")
    print(f"✅ Saved plot: {output_file_dist}")

    # Summary statistics
    print("\n📋 Summary Results:")
    print("-" * 60)
    print(f"Districts analyzed: {len(geo_analysis)}")
    print(f"Mean coverage: {merged_data['coverage'].mean():.2f} vax/1000 livestock")
    print(f"Median coverage: {merged_data['coverage'].median():.2f} vax/1000 livestock")
    print(f"Std deviation: {merged_data['coverage'].std():.2f}")
    print(
        f"Range: {merged_data['coverage'].min():.2f} - {merged_data['coverage'].max():.2f}"
    )
    print(f"\nMoran's I: {moran.I:.4f} (p = {moran.p_sim:.4f})")
    print(f"Interpretation: {interpretation}")

    print("\n✅ Spatial Analysis Complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
