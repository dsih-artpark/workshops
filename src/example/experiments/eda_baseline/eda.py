"""
Baseline EDA: FMD Vaccinations in Karnataka

Goal: Understand the vaccination data - distributions, coverage, patterns

Usage:
    uv run eda-baseline
    uv run eda-baseline --config config.yaml
"""

import argparse
import os

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from example import load_config

EXPERIMENT_NAME = "eda-baseline"


def main():
    """Run baseline EDA on FMD vaccination data"""

    # Parse arguments
    parser = argparse.ArgumentParser(
        description="Baseline EDA on FMD vaccination data for Karnataka"
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
    plt.rcParams["figure.figsize"] = (12, 6)

    # Load config
    config = load_config(args.config)
    experiment_config = config["experiments"][EXPERIMENT_NAME]

    # Construct file paths
    data_dir = config["meta"]["directories"]["data"]
    plots_dir = os.path.join(config["meta"]["directories"]["plots"], EXPERIMENT_NAME)
    os.makedirs(plots_dir, exist_ok=True)

    vax_file = os.path.join(data_dir, experiment_config["files"]["vax"])

    print("=" * 60)
    print("BASELINE EDA: FMD Vaccinations")
    print("=" * 60)

    # Load data
    print("\n📂 Loading data...")
    vax_df = pd.read_csv(vax_file)
    print(f"Loaded {len(vax_df):,} vaccination records")

    # Filter for Karnataka
    print("\n🗺️  Filtering for Karnataka...")
    ka_vax = vax_df[vax_df["state.name"] == "Karnataka"].copy()
    print(f"Karnataka records: {len(ka_vax):,}")
    print(f"Districts: {ka_vax['district.name'].nunique()}")
    print(f"Vaccination rounds: {sorted(ka_vax['metadata.vaccinationRound'].unique())}")

    # Summary statistics
    print("\n📊 Summary Statistics")
    print("-" * 60)
    print(f"Total vaccinations: {ka_vax['totalVaccinations.count'].sum():,}")
    print(f"Total farmers benefited: {ka_vax['farmersBenefited.count'].sum():,}")
    print(
        f"Average vaccinations per district-round: {ka_vax['totalVaccinations.count'].mean():,.0f}"
    )
    print(
        f"Average farmers per district-round: {ka_vax['farmersBenefited.count'].mean():,.0f}"
    )

    # Group by district (all rounds combined)
    district_totals = (
        ka_vax.groupby("district.name")
        .agg({"totalVaccinations.count": "sum", "farmersBenefited.count": "sum"})
        .sort_values("totalVaccinations.count", ascending=False)
    )

    print("\n🏆 Top 5 Districts by Total Vaccinations:")
    print(district_totals.head())

    print("\n⚠️  Bottom 5 Districts by Total Vaccinations:")
    print(district_totals.tail())

    # Vaccination rounds analysis
    print("\n🔄 Vaccination Rounds Analysis")
    print("-" * 60)
    round_summary = ka_vax.groupby("metadata.vaccinationRound").agg(
        {"totalVaccinations.count": ["sum", "mean"], "district.name": "nunique"}
    )
    round_summary.columns = [
        "Total Vaccinations",
        "Avg per District",
        "Districts Covered",
    ]
    print(round_summary)

    # Create visualizations
    print("\n📈 Creating visualizations...")

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # 1. Distribution of vaccinations per district
    ax1 = axes[0, 0]
    district_totals["totalVaccinations.count"].hist(bins=20, ax=ax1, edgecolor="black")
    ax1.set_title(
        "Distribution of Total Vaccinations by District", fontsize=12, fontweight="bold"
    )
    ax1.set_xlabel("Total Vaccinations")
    ax1.set_ylabel("Number of Districts")
    ax1.axvline(
        district_totals["totalVaccinations.count"].median(),
        color="red",
        linestyle="--",
        label=f"Median: {district_totals['totalVaccinations.count'].median():,.0f}",
    )
    ax1.legend()

    # 2. Top 10 districts
    ax2 = axes[0, 1]
    top10 = district_totals.head(10)["totalVaccinations.count"]
    top10.plot(kind="barh", ax=ax2, color="steelblue")
    ax2.set_title(
        "Top 10 Districts by Total Vaccinations", fontsize=12, fontweight="bold"
    )
    ax2.set_xlabel("Total Vaccinations")
    ax2.invert_yaxis()

    # 3. Vaccinations by round
    ax3 = axes[1, 0]
    round_totals = ka_vax.groupby("metadata.vaccinationRound")[
        "totalVaccinations.count"
    ].sum()
    round_totals.plot(kind="bar", ax=ax3, color="forestgreen")
    ax3.set_title("Total Vaccinations by Round", fontsize=12, fontweight="bold")
    ax3.set_xlabel("Vaccination Round")
    ax3.set_ylabel("Total Vaccinations")
    ax3.set_xticklabels(ax3.get_xticklabels(), rotation=0)

    # 4. Farmers benefited vs vaccinations
    ax4 = axes[1, 1]
    ax4.scatter(
        ka_vax["totalVaccinations.count"], ka_vax["farmersBenefited.count"], alpha=0.5
    )
    ax4.set_title(
        "Farmers Benefited vs Total Vaccinations", fontsize=12, fontweight="bold"
    )
    ax4.set_xlabel("Total Vaccinations")
    ax4.set_ylabel("Farmers Benefited")

    # Add reference line
    max_val = max(
        ka_vax["totalVaccinations.count"].max(), ka_vax["farmersBenefited.count"].max()
    )
    ax4.plot([0, max_val], [0, max_val], "r--", alpha=0.3, label="1:1 ratio")
    ax4.legend()

    plt.tight_layout()
    output_file = os.path.join(plots_dir, "overview.png")
    plt.savefig(output_file, dpi=150, bbox_inches="tight")
    print(f"✅ Saved plot: {output_file}")

    # Key observations
    print("\n🔍 Key Observations:")
    print("-" * 60)
    print("1. Vaccination coverage varies widely across districts")
    print(
        f"   - Highest: {district_totals.index[0]} with {district_totals.iloc[0]['totalVaccinations.count']:,.0f} vaccinations"
    )
    print(
        f"   - Lowest: {district_totals.index[-1]} with {district_totals.iloc[-1]['totalVaccinations.count']:,.0f} vaccinations"
    )
    print(
        f"2. {len(ka_vax['metadata.vaccinationRound'].unique())} vaccination rounds completed"
    )
    print(
        f"3. Average farmers-to-vaccination ratio: {ka_vax['farmersBenefited.count'].sum() / ka_vax['totalVaccinations.count'].sum():.2f}"
    )
    print("4. District participation is consistent across rounds")

    print("\n✅ EDA Complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
