# Insurance Claims & Portfolio Risk Dashboard

## Project Overview

This project is an end-to-end descriptive analytics and business-intelligence study of a French motor-insurance portfolio. Python prepares and validates the data, Tableau provides interactive exploration, and the business summary translates results into management actions. Phases 1–19 are complete.

## Business Problem

Management needs a consistent view of where observed claims occur most frequently, where costs are highest, which segments merit review, whether frequency and severity move together, and how concentrated claim costs are. The project supports monitoring and investigation. It does not build a pricing model, make underwriting decisions, or establish causal relationships.

## Dataset Source

The project uses the anonymized French Motor Third-Party Liability (`freMTPL2`) dataset from [CASdatasets](https://github.com/dutangc/CASdatasets). It contains 677,991 policies observed mostly over one year, during approximately 2011–2013. The insurer is not identified.

- [Dataset documentation](https://dutangc.github.io/CASdatasets/reference/freMTPL.html)
- [Frequency source file](https://raw.githubusercontent.com/dutangc/CASdatasets/master/data/freMTPL2freq.rda)
- [Severity source file](https://raw.githubusercontent.com/dutangc/CASdatasets/master/data/freMTPL2sev.rda)
- [Download record, checksums, and detailed data notes](data/README.md)

The source consists of a policy-level Frequency table and a claim-level Severity table. `IDpol` is the policy key linking them.

## Data Dictionary

- `IDpol`: policy identifier used to link the two source tables.
- `ClaimNb`: reported claim count during the policy exposure period.
- `Exposure`: observed policy time in years.
- `VehPower`, `VehAge`, `DrivAge`: vehicle power, vehicle age, and driver age.
- `BonusMalus`: French bonus/malus coefficient; values below 100 indicate a bonus and values above 100 a malus.
- `VehBrand`, `VehGas`, `Area`, `Density`, `Region`: vehicle, fuel, geography, and density attributes.
- `ClaimAmount`: observed claim cost in the Severity table.
- `TotalClaimAmount`, `SeverityClaimCount`, `AverageClaimAmount`, `MaxClaimAmount`: policy-level Severity aggregates created during preparation.

The complete source, derived-field, KPI, and Tableau-export dictionary is in [data/README.md](data/README.md).

## Project Structure

```text
insurance-claims-tableau-analysis/
├── notebooks/insurance_analysis.ipynb  # Python analysis and validation
├── data/
│   ├── raw/                            # Downloaded RDA source files, not committed
│   ├── processed/                      # Validated Tableau CSV exports
│   └── README.md                       # Source record and data dictionary
├── tableau/
│   ├── insurance_claims_dashboard.twb  # Tableau workbook
│   ├── build_workbook.py               # Rebuilds the workbook
│   └── README.md                       # Dashboard guide
├── report/business_summary.md          # Management summary
├── report/final_quality_control.md     # Auditable final QC checklist
├── figures/
│   ├── build_dashboard_previews.py     # Rebuilds dashboard visual previews
│   └── *.png                           # Analysis figures and dashboard previews
└── requirements.txt                    # Python dependencies
```

## Data Cleaning

The notebook inspects completeness, data types, duplicate rows, identifier uniqueness, exposure, claim counts, claim amounts, age ranges, and bonus/malus values. No row or value is removed without evidence of invalidity.

The 235 exact duplicate Severity rows across 229 `IDpol`–`ClaimAmount` combinations are retained. The source has no insurer-issued claim identifier and identical amounts may represent distinct claims under the documented French IRSA-IDA convention. High claim amounts are also retained for review rather than treated as errors.

## Merge Logic

Frequency is one row per policy, while Severity is one row per observed claim. The notebook first aggregates Severity by `IDpol` to calculate total claim cost, claim-row count, average claim amount, and maximum claim amount. It then performs a validated one-to-one left join to retain every Frequency policy.

This prevents multiple Severity rows from duplicating policy-level Exposure or attributes. The validated result contains 677,991 policies, matches 24,944 claim-bearing policies, retains 653,047 policies without an observed Severity row, and reconciles the original, aggregated, and merged claim-cost total of €59,909,216.50.

## Feature Engineering

The original source fields are preserved. The notebook adds stable business segments using fixed `pd.cut` thresholds:

- `DriverAgeGroup`: Young (18–24), Early Career (25–34), Mid-age (35–49), Mature (50–64), Senior (65+).
- `VehicleAgeGroup`: New (0–1), Recent (2–5), Mid-age (6–10), Old (11–20), Very old (21+).
- `VehiclePowerGroup`: Low (4–5), Medium (6–7), High (8–9), Very high (10+).
- `BonusMalusGroup`: Bonus (50–99), Standard (100), Malus (101+).

## KPI Definitions

- **Policy Count:** number of unique policies in the selected population.
- **Exposure:** sum of observed policy time in years.
- **Claim Count:** sum of `ClaimNb`.
- **Claim Frequency:** Claim Count divided by Exposure, expressed as claims per exposure year.
- **Total Claim Cost:** sum of policy-level total claim amounts.
- **Average Severity:** Total Claim Cost divided by observed Severity claim rows.

Frequency and severity are always interpreted with Exposure and Claim Count. Loss Ratio is deliberately excluded because written premium is not available.

## Python Analysis Workflow

The [analysis notebook](notebooks/insurance_analysis.ipynb) loads the unchanged RDA files with `rdata`, profiles and validates both source tables, documents cleaning decisions, aggregates Severity, validates the merge, creates segments, computes reusable KPIs, answers the business questions, and exports Tableau-ready CSV files.

The exported tables are re-opened and checked after writing:

- `data/processed/tableau_portfolio.csv`: 677,991 policy-level rows; primary Tableau source.
- `data/processed/tableau_claims.csv`: 26,444 claim-level rows; Pareto and high-cost-claim source.

## Business Questions

The analysis answers eight management questions:

1. What is the overall portfolio benchmark?
2. Which regions show the greatest observed claim burden?
3. Which driver and vehicle segments show different claim patterns?
4. Are frequent-claim segments also expensive-claim segments?
5. Is claim cost concentrated in a small number of claims or policies?
6. Which unusual claims or segments warrant investigation?
7. What should management monitor monthly?
8. What three evidence-based actions should management consider?

## Tableau Dashboard

Open [tableau/insurance_claims_dashboard.twb](tableau/insurance_claims_dashboard.twb) in Tableau Desktop. The workbook has three pages:

- **Executive Portfolio Overview:** portfolio KPI cards, regional comparison, and five meaningful filters.
- **Claims & Risk Segments:** frequency-versus-severity comparison and segment exploration.
- **Claim Cost Concentration:** Pareto analysis and high-cost-claim review.

The dashboard includes a regional filter action, a driver-age highlight action, readable number formats, consistent KPI labels, and explanatory subtitles and tooltips. See [tableau/README.md](tableau/README.md) for interaction and reconnection instructions.

## Key Findings

- The portfolio has 358,482.83 exposure years, 26,444 claims, Claim Frequency of 0.0738, Total Claim Cost of €59.91 million, and Average Severity of €2,265.51.
- Rhone-Alpes has the highest observed regional Claim Frequency at 0.0934 and €10.28 million of Total Claim Cost. Centre has the largest Total Claim Cost (€19.07 million) because it also has the largest Exposure.
- Young (18–24) drivers have observed Claim Frequency of 0.1610 and Average Severity of €5,838.56.
- Mid-age (6–10) vehicles have the highest observed vehicle-age Claim Frequency (0.0809), while Old (11–20) vehicles have the highest Average Severity (€2,917.02).
- The top 1% of observed claims contribute 38.01% of Total Claim Cost. The 133 claims at or above €34,376.96 contribute 32.96% of cost.

See the concise [business summary](report/business_summary.md) for management interpretation.

## Three Recommendations

1. **Monitor Young (18–24) drivers:** review Claim Frequency, Average Severity, Exposure, and Claim Count together; investigate portfolio and claim-mix differences before proposing an intervention.
2. **Review Rhone-Alpes monthly:** compare its claim mix and claims handling with portfolio benchmarks while retaining frequency, severity, cost, exposure, and claim-count context.
3. **Maintain a high-cost claim review queue:** review claim-file validity, reserving, claims handling, and recurring operational themes without automatically excluding valid high-cost observations.

## Limitations

- **Historical data:** the portfolio reflects approximately 2011–2013. It may not represent current claims patterns, regulations, vehicle technology, repair costs, or the current market.
- **Anonymous insurer:** the insurer is not identified, so the portfolio's underwriting strategy, claims practices, coverage terms, and market position cannot be assessed.
- **No premium information:** written premium is unavailable. Therefore, Loss Ratio and profitability cannot be calculated.
- **Limited risk variables:** the dataset does not contain every factor that may influence insurance outcomes, such as detailed driving behaviour, journey purpose, coverage terms, or claims-process information.
- **Descriptive analytics:** observed relationships are associations, not proof of causation. A segment comparison does not show that a region, vehicle, fuel type, or driver characteristic caused an outcome.
- Small groups can produce volatile rates; Exposure and Claim Count must accompany segment comparisons.
- The Severity source has no insurer-issued claim identifier. `ClaimRowID` is a technical export key, not proof of claim validity or cause.

## How to Reproduce the Project

1. Clone the repository and open PowerShell in its root directory.
2. Create and activate the virtual environment, then install dependencies:

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   python -m ipykernel install --user --name insurance-claims-dashboard --display-name "Python (.venv - Insurance Claims)"
   ```

3. Download the raw sources into `data/raw/` if they are not already present:

   ```powershell
   New-Item -ItemType Directory -Force data/raw
   Invoke-WebRequest https://raw.githubusercontent.com/dutangc/CASdatasets/master/data/freMTPL2freq.rda -OutFile data/raw/freMTPL2freq.rda
   Invoke-WebRequest https://raw.githubusercontent.com/dutangc/CASdatasets/master/data/freMTPL2sev.rda -OutFile data/raw/freMTPL2sev.rda
   ```

   Verify the downloaded files against the SHA-256 values in [data/README.md](data/README.md).

4. Start Jupyter and run all cells in the analysis notebook to regenerate validated processed CSV files and figures:

   ```powershell
   python -m jupyter notebook notebooks/insurance_analysis.ipynb
   ```

5. Generate the dashboard visual previews from the processed CSV files:

   ```powershell
   python figures/build_dashboard_previews.py
   ```

6. Rebuild the Tableau workbook from the processed CSV files:

   ```powershell
   python tableau/build_workbook.py
   ```

7. Open `tableau/insurance_claims_dashboard.twb` in Tableau Desktop. If the repository was moved, use **Data > Edit Connection** to relink the CSV files in `data/processed/`.

## Reproducibility Check

- [x] Raw data sources, download dates, and SHA-256 checksums are documented in [data/README.md](data/README.md).
- [x] Python dependencies, including the Notebook kernel dependency, are pinned in `requirements.txt`.
- [x] The Notebook runs from top to bottom with the documented `insurance-claims-dashboard` kernel.
- [x] Python and workbook-builder paths are derived from the repository location; no project-specific drive path is required to regenerate outputs.
- [x] Cleaning decisions, merge logic, segmentation thresholds, and KPI formulas are documented in this README, [data/README.md](data/README.md), and the Notebook.
- [x] The Notebook regenerates the Tableau-ready CSV files, and `tableau/build_workbook.py` regenerates the Tableau workbook.
- [x] Reproducible dashboard visual previews are included in `figures/`; they are generated from the validated CSV exports and are not represented as Tableau Desktop captures.
- [x] The Tableau workbook and its interaction guide are included in [tableau/](tableau/).

The detailed, evidence-linked final review is in [report/final_quality_control.md](report/final_quality_control.md).
