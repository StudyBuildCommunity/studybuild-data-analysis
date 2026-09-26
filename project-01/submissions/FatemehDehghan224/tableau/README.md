# Tableau Dashboard

Open `insurance_claims_dashboard.twb` in Tableau Desktop from this repository.

The workbook uses two CSV sources created in Phase 11:

- `../data/processed/tableau_portfolio.csv` — primary policy-level source.
- `../data/processed/tableau_claims.csv` — claim-level Pareto and high-cost-claim source.

The workbook contains three dashboard pages:

1. **Executive Portfolio Overview** — six KPI cards, regional comparison, and five policy-level filters.
2. **Claims & Risk Segments** — driver-age frequency versus severity scatter, vehicle-power comparison, and driver/vehicle highlight matrix.
3. **Claim Cost Concentration** — Pareto curve, top 20 claim amounts, high-cost vehicle-power segments, and the three evidence-based recommendations.

The Tableau calculated fields `Policy Count`, `Claim Frequency`, and `Average Severity` use the same definitions documented in the analysis notebook. The workbook intentionally excludes Loss Ratio because written premium is unavailable.

## Phase 13 interaction and UX

The workbook uses only portfolio filters that support a management comparison: **Region**, **Fuel Type**, **Driver Age Group**, **Vehicle Age Group**, and **Bonus–Malus Group**. They filter the policy-based sheets and KPI cards on the two portfolio dashboards. The Claim Cost Concentration page deliberately has no filter because it is designed as a portfolio-wide high-cost-claim review.

- Select a bar in **Claim Frequency by Region** on the Executive Portfolio Overview to filter the other overview sheets and KPI cards to that region. Clear the selection to restore the selected filter context.
- Select a circle in **Driver Age: Frequency vs Severity** to highlight the matching driver-age row in the driver/vehicle matrix. This preserves context by highlighting rather than hiding the other segments.

The labels are consistent across the notebook, Tableau workbook, root README, and business summary: **Policy Count**, **Exposure**, **Claim Count**, **Claim Frequency**, **Total Claim Cost**, and **Average Severity**.

Number formats are intentional: Exposure shows readable decimal years; Claim Frequency shows four decimal places and means claims per exposure year; Total Claim Cost, Average Severity, and claim-level amounts show euros without spurious decimals. Dashboard subtitles and worksheet tooltips define the measures, units, and interactions directly in the view.

## Phase 14 interpretation

The dashboard identifies observed associations for investigation, not causal explanations. Use [`../report/business_summary.md`](../report/business_summary.md) for the evidence-based interpretation of the young-driver cohort, regional patterns, fuel-type comparison, and claim-cost concentration. Each finding includes its observation, business meaning, possible management action, and limitation.

The generated workbook records the current repository path for these sources. If the repository is moved, use Tableau's **Data > Edit Connection** to relink the two CSV files in `data/processed/`.

To regenerate the workbook after changing CSV exports, run:

```powershell
.\.venv\Scripts\python.exe tableau\build_workbook.py
```
