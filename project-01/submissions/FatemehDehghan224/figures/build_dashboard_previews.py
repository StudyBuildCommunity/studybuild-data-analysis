"""Generate reproducible visual previews of the three Tableau dashboard pages.

The images are evidence for the repository and are derived from the same validated
CSV exports as the Tableau workbook. They are previews, not Tableau Desktop
screenshots.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
FIGURES_DIR = Path(__file__).resolve().parent
PORTFOLIO_PATH = PROJECT_ROOT / "data" / "processed" / "tableau_portfolio.csv"
CLAIMS_PATH = PROJECT_ROOT / "data" / "processed" / "tableau_claims.csv"

BLUE = "#2F75B5"
ORANGE = "#ED7D31"
GREY = "#6B7280"


def save_overview(portfolio: pd.DataFrame) -> None:
    total_exposure = portfolio["Exposure"].sum()
    total_claims = portfolio["ClaimNb"].sum()
    total_cost = portfolio["TotalClaimAmount"].sum()
    total_severity_count = portfolio["SeverityClaimCount"].sum()
    frequency = total_claims / total_exposure
    severity = total_cost / total_severity_count
    region = portfolio.groupby("Region", as_index=False).agg(
        Exposure=("Exposure", "sum"),
        ClaimCount=("ClaimNb", "sum"),
    )
    region["ClaimFrequency"] = region["ClaimCount"] / region["Exposure"]
    region = region.sort_values("ClaimFrequency", ascending=False).head(10).sort_values("ClaimFrequency")

    figure = plt.figure(figsize=(16, 9), constrained_layout=True)
    grid = figure.add_gridspec(2, 1, height_ratios=(1, 2))
    kpi_axis = figure.add_subplot(grid[0])
    kpi_axis.axis("off")
    kpis = [
        ("Policy Count", f"{portfolio['IDpol'].nunique():,}"),
        ("Exposure", f"{total_exposure:,.1f}"),
        ("Claim Count", f"{total_claims:,}"),
        ("Claim Frequency", f"{frequency:.4f}"),
        ("Total Claim Cost", f"€{total_cost / 1_000_000:.2f}m"),
        ("Average Severity", f"€{severity:,.0f}"),
    ]
    for index, (label, value) in enumerate(kpis):
        x = (index + 0.5) / len(kpis)
        kpi_axis.text(x, 0.65, value, ha="center", va="center", fontsize=20, fontweight="bold", color=BLUE)
        kpi_axis.text(x, 0.30, label, ha="center", va="center", fontsize=11, color=GREY)
    kpi_axis.set_title("Executive Portfolio Overview — reproducible preview", loc="left", fontsize=18, fontweight="bold")

    axis = figure.add_subplot(grid[1])
    axis.barh(region["Region"], region["ClaimFrequency"], color=BLUE)
    axis.axvline(frequency, color=ORANGE, linestyle="--", label=f"Portfolio: {frequency:.4f}")
    axis.set_xlabel("Claim Frequency (claims per exposure year)")
    axis.set_title("Top 10 regions by observed Claim Frequency")
    axis.legend()
    figure.savefig(FIGURES_DIR / "tableau_dashboard_executive_overview_preview.png", dpi=160)
    plt.close(figure)


def save_segments(portfolio: pd.DataFrame) -> None:
    driver = portfolio.groupby("DriverAgeGroup", as_index=False).agg(
        Exposure=("Exposure", "sum"),
        ClaimCount=("ClaimNb", "sum"),
        TotalClaimCost=("TotalClaimAmount", "sum"),
        SeverityClaimCount=("SeverityClaimCount", "sum"),
    )
    driver["ClaimFrequency"] = driver["ClaimCount"] / driver["Exposure"]
    driver["AverageSeverity"] = driver["TotalClaimCost"] / driver["SeverityClaimCount"]
    vehicle = portfolio.groupby("VehicleAgeGroup", as_index=False).agg(
        Exposure=("Exposure", "sum"), ClaimCount=("ClaimNb", "sum")
    )
    vehicle["ClaimFrequency"] = vehicle["ClaimCount"] / vehicle["Exposure"]
    vehicle = vehicle.sort_values("ClaimFrequency")

    figure, axes = plt.subplots(1, 2, figsize=(16, 7), constrained_layout=True)
    axes[0].scatter(
        driver["ClaimFrequency"],
        driver["AverageSeverity"],
        s=driver["Exposure"] / driver["Exposure"].max() * 1_200,
        color=BLUE,
        alpha=0.75,
    )
    label_offsets = {
        "Young (18-24)": (5, 5),
        "Early Career (25-34)": (8, 8),
        "Mid-age (35-49)": (8, -16),
        "Mature (50-64)": (-35, 5),
        "Senior (65+)": (5, 5),
    }
    for row in driver.itertuples():
        axes[0].annotate(
            row.DriverAgeGroup,
            (row.ClaimFrequency, row.AverageSeverity),
            xytext=label_offsets[row.DriverAgeGroup],
            textcoords="offset points",
        )
    axes[0].set_xlabel("Claim Frequency")
    axes[0].set_ylabel("Average Severity (€)")
    axes[0].set_title("Driver Age: frequency versus severity")

    axes[1].barh(vehicle["VehicleAgeGroup"], vehicle["ClaimFrequency"], color=ORANGE)
    axes[1].set_xlabel("Claim Frequency (claims per exposure year)")
    axes[1].set_title("Vehicle Age: observed Claim Frequency")
    figure.suptitle("Claims & Risk Segments — reproducible preview", x=0.01, ha="left", fontsize=18, fontweight="bold")
    figure.savefig(FIGURES_DIR / "tableau_dashboard_claims_risk_segments_preview.png", dpi=160)
    plt.close(figure)


def save_concentration(claims: pd.DataFrame) -> None:
    ordered = claims.sort_values("ClaimAmount", ascending=False).reset_index(drop=True)
    cumulative_cost_share = ordered["ClaimAmount"].cumsum() / ordered["ClaimAmount"].sum()
    cumulative_claim_share = (ordered.index + 1) / len(ordered)

    figure, axes = plt.subplots(1, 2, figsize=(16, 7), constrained_layout=True)
    axes[0].plot(cumulative_claim_share * 100, cumulative_cost_share * 100, color=BLUE, linewidth=2.5)
    axes[0].plot([0, 100], [0, 100], color=GREY, linestyle="--", linewidth=1)
    axes[0].set_xlabel("Observed claims included (%)")
    axes[0].set_ylabel("Cumulative Claim Cost (%)")
    axes[0].set_title("Claim Cost Pareto curve")

    top_claims = ordered.head(20).sort_values("ClaimAmount")
    axes[1].barh(top_claims["ClaimRowID"].astype(str), top_claims["ClaimAmount"], color=ORANGE)
    axes[1].set_xscale("log")
    axes[1].set_xlabel("Claim Amount (€; logarithmic scale)")
    axes[1].set_ylabel("Claim Row ID")
    axes[1].set_title("Largest 20 observed claims")
    figure.suptitle("Claim Cost Concentration — reproducible preview", x=0.01, ha="left", fontsize=18, fontweight="bold")
    figure.savefig(FIGURES_DIR / "tableau_dashboard_claim_cost_concentration_preview.png", dpi=160)
    plt.close(figure)


def main() -> None:
    portfolio = pd.read_csv(PORTFOLIO_PATH)
    claims = pd.read_csv(CLAIMS_PATH)
    save_overview(portfolio)
    save_segments(portfolio)
    save_concentration(claims)
    print("Created reproducible dashboard previews in figures/.")


if __name__ == "__main__":
    main()
