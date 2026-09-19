# Data Directory

## Raw Data

- `raw/freMTPL2freq.csv` — Policy-level frequency table (678,013 rows)
  - Source: [CASdatasets R Package](https://dutangc.github.io/CASdatasets/reference/freMTPL.html)
  - Variables: IDpol, ClaimNb, Exposure, VehPower, VehAge, DrivAge, BonusMalus, VehBrand, VehGas, Area, Density, Region

- `raw/freMTPL2sev.csv` — Individual claim severity table (26,639 rows)
  - Source: Same as above
  - Variables: IDpol, ClaimAmount

## Processed Data (Tableau-Ready)

- `processed/tableau_policy_level.csv` — Policy-level dataset with engineered segments
- `processed/tableau_regional_kpi.csv` — Regional KPI summary (21 regions)
- `processed/tableau_segment_analysis.csv` — Segment-level analysis (driver age, vehicle age, power, fuel, bonus-malus)
- `processed/tableau_individual_claims.csv` — Individual claims sorted for Pareto analysis
- `processed/tableau_portfolio_kpi.csv` — Portfolio-level KPI summary

## Data Source Citation

> Dutang, C. (2023). CASdatasets: Insurance Datasets. R package.
> https://dutangc.github.io/CASdatasets/reference/freMTPL.html

## Notes

- The dataset is from an anonymous French motor insurer (freMTPL2)
- Written premium is not available — Loss Ratio cannot be calculated
- Claims are exposure-adjusted (frequency = claims / exposure years)
