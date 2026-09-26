# Final Quality-Control Checklist

## Outcome

**Status: PASS.** The raw source files, processed Tableau exports, Notebook workflow, Tableau workbook structure, and project documentation were checked on 2026-09-25. The project is ready for submission as a descriptive insurance-portfolio analysis. Dashboard visual previews are reproducible from the processed CSV files; the included Tableau Desktop guide describes the final manual interaction check.

## Data

- [x] **Frequency data inspected:** the raw Frequency source contains 677,991 rows and 12 fields; `IDpol` is unique and its `ClaimNb` total is 26,444.
- [x] **Severity data inspected:** the raw Severity source contains 26,444 claim rows and 2 fields; the largest observed claim is €4,075,400.56.
- [x] **Missing values checked:** neither raw source has missing values, and the critical exported fields (`IDpol`, Exposure, ClaimNb, claim cost, and technical claim key) have no missing values. Missing policy-level average/max claim amounts are retained only where a policy has no observed Severity row.
- [x] **Duplicate rows checked:** Frequency has no exact duplicate rows. Severity has 235 exact duplicate rows across 229 `IDpol`–`ClaimAmount` combinations; they are retained because the source has no insurer-issued claim ID and identical valid claim amounts are documented under the IRSA-IDA convention.
- [x] **Policy IDs validated:** Frequency and `tableau_portfolio.csv` each have 677,991 unique `IDpol` values; all claim-level IDs exist in the policy export.
- [x] **Extreme claims investigated:** 133 claims at or above the 99.5th-percentile threshold (€34,376.96) are flagged for review and retained, not deleted.
- [x] **Severity aggregated correctly:** policy-level `TotalClaimAmount`, `SeverityClaimCount`, `AverageClaimAmount`, and `MaxClaimAmount` are created before the join. The aggregate claim-row count is 26,444.
- [x] **Merge validated:** the left join retains all 677,991 Frequency policies. Claim count and total claim cost reconcile exactly between the policy and claim exports: 26,444 claims and €59,909,216.50.

## KPI Controls

The independent control calculation from `data/processed/tableau_portfolio.csv` returned the following portfolio totals.

| KPI | Controlled result | Definition checked |
|---|---:|---|
| Policy Count | 677,991 | Unique `IDpol` |
| Exposure | 358,482.834813 years | Sum of Exposure |
| Claim Count | 26,444 | Sum of `ClaimNb` |
| Claim Frequency | 0.073766 claims per exposure year | Claim Count / Exposure |
| Total Claim Cost | €59,909,216.50 | Sum of `TotalClaimAmount` |
| Average Severity | €2,265.51 per claim | Total Claim Cost / Severity claim rows |

- [x] **Policy Count** is calculated and documented.
- [x] **Exposure** is calculated and documented.
- [x] **Claim Count** is calculated and documented.
- [x] **Claim Frequency** is calculated and documented.
- [x] **Total Claim Cost** is calculated and documented.
- [x] **Average Severity** uses the claim-row denominator, not an average of policy averages.
- [x] **No Loss Ratio:** the Tableau workbook contains no Loss Ratio calculation, and the README explains that written premium is unavailable.

## Business Analysis

The Notebook contains a dedicated, validated answer cell for every management question. Conclusions are descriptive associations, with exposure and claim counts used as context.

- [x] **Q1 — Overall portfolio health:** portfolio KPI benchmark is reported.
- [x] **Q2 — Regional claim burden:** regions are compared by frequency, severity, cost, exposure, and claim count.
- [x] **Q3 — Driver and vehicle patterns:** driver-age and vehicle segments are compared.
- [x] **Q4 — Frequency versus severity:** the two measures are shown separately and compared without assuming they move together.
- [x] **Q5 — Claim-cost concentration:** Pareto analysis quantifies concentration; the top 1% of claims account for 38.01% of total cost.
- [x] **Q6 — Unusual claims or segments:** high-cost claims are flagged for investigation using the 99.5th percentile.
- [x] **Q7 — Monthly monitoring:** the required dashboard monitoring components are documented.
- [x] **Q8 — Recommendations:** three recommendations use the Evidence → Action → KPI format.

## Tableau

- [x] **Three coherent pages:** workbook XML contains Executive Portfolio Overview, Claims & Risk Segments, and Claim Cost Concentration.
- [x] **Executive KPI cards:** the overview contains the six core KPIs.
- [x] **Region and segment comparison:** regional bars, driver-age/vehicle-power views, and a driver/vehicle matrix are included.
- [x] **Frequency-versus-severity visual:** the driver-age scatter compares Claim Frequency and Average Severity, with Exposure encoded by marker size.
- [x] **Pareto analysis:** the claim-cost page includes a cumulative-cost curve and top-20 high-cost-claim view.
- [x] **Meaningful filters and actions:** five policy filters are restricted to decision-useful fields. Structural validation found the region filter action and driver-age highlight action, including valid source and target references.
- [x] **Three recommendations:** the claim-cost page and the business summary include the same three evidence-based recommendations.
- [x] **Labels, numbers, and explanations:** the same six KPI names are used across Python, Tableau, README, and business summary; number formats, subtitles, and tooltips specify units and interpretation.
- [x] **Visual evidence included:** three reproducible dashboard previews are in `figures/`. They are generated Python previews, not claimed as Tableau Desktop screenshots; use the interaction steps in `tableau/README.md` after opening the workbook in Tableau Desktop.

## Documentation and Reproducibility

- [x] **README complete:** it covers project overview, business problem, source, dictionary, cleaning, merge, features, KPIs, workflow, questions, Tableau, findings, recommendations, limitations, and reproduction.
- [x] **Data source cited:** source URLs, acquisition record, and SHA-256 checksums are in `data/README.md`.
- [x] **Merge logic explained:** grain, pre-join aggregation, left join, and control totals are documented.
- [x] **KPI definitions explained:** formulas and denominators are documented in the README, data notes, and Notebook.
- [x] **Limitations documented:** historical 2011–2013 data, anonymous insurer, absent premium/Loss Ratio, limited risk variables, and non-causal interpretation are explicitly stated.
- [x] **Reproduction instructions included:** `requirements.txt`, raw-data download commands, Notebook instructions, preview generation, workbook generation, and Tableau reconnection steps are in the README.

## Learning Workflow Review

The Notebook follows the expected sequence, with equivalent named sections rather than an artificial renumbering: imports and configuration; business understanding; source and dictionary; loading and inspection; quality checks; Severity aggregation and merge; feature engineering; KPI functions; EDA; regional and segment analysis; frequency versus severity; Pareto analysis; unusual claims; Tableau export; findings; recommendations; and limitations.

Recommended review order for learning is retained as the working sequence:

1. pandas basics and dataset inspection
2. missing values, duplicates, and policy-ID validation
3. `groupby`/aggregation and merge validation
4. `cut`/`qcut` segment design and insurance KPI logic
5. EDA, Pareto analysis, and high-cost-claim review
6. Tableau calculated fields, filters/actions, and dashboard design
7. evidence-based business storytelling

## Milestones and Definition of Done

- [x] **Milestone 1 — Data Ready:** raw data inspected, quality checks completed, Severity aggregated, and policy-level merge validated.
- [x] **Milestone 2 — Analysis Ready:** segments and KPIs implemented; EDA and Q1–Q6 completed.
- [x] **Milestone 3 — BI Ready:** Tableau-ready CSVs, three dashboard pages, filters/actions, and explanatory UX are present.
- [x] **Milestone 4 — Submission Ready:** Q7–Q8, business summary, README, requirements, visual previews, workbook, limitations, and reproducibility guidance are included.

The completed workflow is:

```text
Business Question → Data Understanding → Cleaning → Aggregation → Merge
→ Feature Engineering → KPI Design → EDA → Business Analysis
→ Tableau Dashboard → Recommendation
```

This confirms the project is more than a static dashboard: every displayed KPI and recommendation traces back to a documented data grain, transformation, control, and limitation.
