# Tableau Dashboard Build Instructions

The `.twb` file in this directory is a **schema scaffold only** — it declares
datasources, field names, mark types, and dashboard zones, but does NOT contain
the full layout tree, pane/card blocks, encoding `attr` attributes, or internal
field IDs that Tableau requires to render correctly. It will open as blank
worksheets.

**To build the real dashboard**, follow these instructions in Tableau Desktop
(or Tableau Public). The 5 processed CSVs in `data/processed/` are the data
sources.

---

## Prerequisites

- Tableau Desktop 2023.x+ or Tableau Public (free)
- Files in `data/processed/`:
  - `tableau_portfolio_kpi.csv` (8 rows — KPI name/value pairs)
  - `tableau_regional_kpi.csv` (21 rows — one per region)
  - `tableau_segment_analysis.csv` (27 rows — 5 segment types × their groups)
  - `tableau_individual_claims.csv` (26,639 rows — one per claim)
  - `tableau_policy_level.csv` (678,013 rows — full policy-level data)

---

## Step 1: Connect Data Sources

1. Open Tableau Desktop → **Connect** → **Text file** → select
   `data/processed/tableau_portfolio_kpi.csv`. Rename the connection
   `Portfolio KPI`.
2. Repeat for each of the other 4 CSVs, renaming connections:
   - `tableau_regional_kpi.csv` → `Regional KPI`
   - `tableau_segment_analysis.csv` → `Segment Analysis`
   - `tableau_individual_claims.csv` → `Individual Claims`
   - `tableau_policy_level.csv` → `Policy Level`
3. In the **Data Source** tab, verify all 5 connections appear in the left
   sidebar. No joins are needed — each CSV is used independently.

---

## Step 2: Build Page 1 — Executive Portfolio Overview

### 2a. KPI Cards

1. Drag `Portfolio KPI` to the canvas.
2. Drag `KPI` to **Rows**, `Value` to **Text**.
3. Sort `KPI` ascending (so cards read: Policy Count, Total Exposure, etc.).
4. On the **Marks** card, set mark type to **Text**.
5. Format `Value` as number (custom: `$#,##0` for currency KPIs, `#,##0` for
   counts, `0.0000` for frequency). Use a **dashboard calculation** or
   separate sheets per KPI if you want individual formatting.
6. Title: "Portfolio KPIs".

### 2b. Regional Claim Frequency Bar

1. New sheet → drag `Regional KPI` to canvas.
2. `Region` → **Rows**, `SUM(ClaimFrequency)` → **Columns**.
3. Sort `Region` by `SUM(ClaimFrequency)` descending.
4. Marks: **Bar**. Color by `SUM(ClaimFrequency)` (blue palette).
5. Add **reference line**: constant at `0.1007`, label "Portfolio Avg".
6. Title: "Claim Frequency by Region".
7. Tooltip: Region, ClaimFrequency, PolicyCount, TotalExposure.

### 2c. Regional Cost-per-Exposure Bar

1. New sheet → `Regional KPI`.
2. `Region` → **Rows**, `SUM(CostPerExposure)` → **Columns**.
3. Sort descending by `SUM(CostPerExposure)`.
4. Marks: **Bar**. Color by `SUM(CostPerExposure)`.
5. Reference line: constant at `167`, label "Portfolio Avg".
6. Title: "Cost per Exposure Year by Region".
7. Format `CostPerExposure` as `$#,##0`.

### 2d. Highlight Table — Colored by Claim Frequency

1. New sheet → `Regional KPI`.
2. `Region` → **Rows**.
3. Drag `ClaimFrequency`, `AvgSeverity`, `CostPerExposure` → **Columns**.
4. On **Analytics** tab → drag **Highlight Table** to the view.
5. Color by `SUM(ClaimFrequency)` (red-white-blue diverging).
6. Title: "Highlight Table — Colored by Claim Frequency".
7. This shows all three metrics in a single grid, with color intensity
   driven by frequency.

### 2e. Assemble Dashboard 1

1. New dashboard, 1200×900.
2. Add a **Text** object at top: "INSURANCE CLAIMS & PORTFOLIO RISK
   DASHBOARD — French Motor Third-Party Liability (freMTPL2)".
3. Add the **KPI Cards** sheet below the title (height ~100px).
4. Add **Regional Frequency Bar** (left half) and **Cost-per-Exposure Bar**
   (right half), each ~350px tall.
5. Add **Highlight Table** below (~200px).
6. Add **filter controls**: Region (from Regional KPI), VehGas (from
   Policy Level), DensityGroup (from Policy Level).
7. Add a **dashboard filter action**: selecting a region in either bar chart
   filters the Highlight Table and KPI Cards.

---

## Step 3: Build Page 2 — Claims & Risk Segments

### 3a. Driver Age Frequency Bar

1. New sheet → `Segment Analysis`.
2. Filter `SegmentType` = `DrivAgeGroup`.
3. `Segment` → **Rows**, `SUM(ClaimFrequency)` → **Columns**.
4. Sort `Segment` ascending (18-25, 26-35, 36-45, 46-55, 56-65, 66+).
5. Marks: **Bar**. Color by `SUM(ClaimFrequency)`.
6. Reference line: 0.1007.
7. Title: "Claim Frequency by Driver Age".

### 3b. Driver Age Severity Bar

1. Same data source, filter `SegmentType` = `DrivAgeGroup`.
2. `Segment` → **Rows**, `SUM(AvgSeverity)` → **Columns**.
3. Sort ascending.
4. Marks: **Bar**. Color by `SUM(AvgSeverity)`.
5. Format as `$#,##0`.
6. Title: "Average Severity by Driver Age".

### 3c. Vehicle Age Frequency Bar

1. Filter `SegmentType` = `VehAgeGroup`.
2. `Segment` → **Rows**, `SUM(ClaimFrequency)` → **Columns**.
3. Sort ascending (New (0), 1-2, 3-5, 6-10, 11+).
4. Marks: **Bar**. Reference line at 0.1007.
5. Title: "Claim Frequency by Vehicle Age".

### 3d. Frequency vs. Severity Scatter (Regional)

1. New sheet → `Regional KPI`.
2. `SUM(ClaimFrequency)` → **Columns**, `SUM(AvgSeverity)` → **Rows**.
3. `Region` → **Detail** (each dot = one region).
4. `Region` → **Label**.
5. `PolicyCount` → **Size**.
6. `Region` → **Color**.
7. Add reference lines: vertical at 0.1007 (Avg Freq), horizontal at 2249
   (Avg Severity). This creates the quadrant view.
8. Title: "Frequency vs. Severity by Region".
9. Tooltip: Region, ClaimFrequency, AvgSeverity, PolicyCount, CostPerExposure.

### 3e. Segment Freq vs. Severity Scatter

1. New sheet → `Segment Analysis`.
2. `SUM(ClaimFrequency)` → **Columns**, `SUM(AvgSeverity)` → **Rows**.
3. `Segment` → **Detail** and **Label**.
4. `SegmentType` → **Color**.
5. `PolicyCount` → **Size**.
6. Reference lines at 0.1007 and 2249.
7. Title: "Frequency vs. Severity by Segment".

### 3f. Assemble Dashboard 2

1. New dashboard, 1200×900.
2. Title: "CLAIMS & RISK SEGMENTS".
3. Top row: Driver Age Frequency (left), Driver Age Severity (center),
   Vehicle Age Frequency (right) — each 400×280.
4. Middle: Freq vs. Severity Scatter (full width, ~400px).
5. Bottom: Segment Freq vs. Sev Scatter (full width, ~170px).
6. Add filter: `SegmentType` from Segment Analysis.
7. Add **highlight action**: clicking a region in the scatter highlights
   corresponding segments.

---

## Step 4: Build Page 3 — Claim Cost Concentration

### 4a. Pareto Chart (Dual-Axis Combo)

1. New sheet → `Individual Claims`.
2. `ClaimRankPct` → **Columns** (continuous, range 0–100).
3. `SUM(ClaimAmount)` → **Rows**. Marks: **Bar**. Sort descending by
   `ClaimAmount`. This is the individual claim amount bars.
4. Create a **calculated field** `CumCostPct`:
   `RUNNING_SUM(SUM([ClaimAmount])) / TOTAL(SUM([ClaimAmount])) * 100`
5. Drag `CumCostPct` → **Rows** (right axis). Right-click → **Dual Axis**.
6. On the secondary axis marks: **Line**. Color: orange or red.
7. Synchronize axes if needed.
8. Add **reference line** on the secondary axis at 80%, label "80% of cost".
9. Title: "Pareto: Cumulative Cost by Claim Rank".
10. Format primary Y-axis as `$#,##0`, secondary Y-axis as `0%`.

**Why bars + line instead of pure line:** A classic Pareto shows individual
claim magnitudes as bars (the "Pareto bars") with a cumulative line on top.
This lets management see both the individual claim sizes AND the cumulative
concentration simultaneously.

### 4b. Top Claims Table

1. New sheet → `Individual Claims`.
2. Sort descending by `ClaimAmount`.
3. Show top 20: **Analysis** → **Filter** → Top → By Field → Top 20 by
   `ClaimAmount` (Sum) descending.
4. Drag `IDpol`, `ClaimAmount`, `CumCostPct`, `ClaimRank` to **Rows**.
5. On the Marks card for `ClaimAmount`, use **ATTR(ClaimAmount)** (not SUM)
   since each row is one claim — SUM is a pass-through but semantically
   misleading.
6. Format `ClaimAmount` as `$#,##0`, `CumCostPct` as `0.0%`.
7. Title: "Top 20 Most Expensive Claims".

### 4c. Cost Distribution by Region

1. New sheet → `Regional KPI`.
2. `Region` → **Rows**, `SUM(TotalClaimCost)` → **Columns**.
3. Sort descending.
4. Marks: **Bar**. Color by `SUM(TotalClaimCost)`.
5. Format as `$#,##0`.
6. Title: "Total Claim Cost by Region".

### 4d. Recommendations Text Zone

1. On the Page 3 dashboard, add a **Text** object (not a worksheet).
2. Paste the following text (formatting with bold headers):

```
RECOMMENDATION 1: Target Underwriting Review in High-Cost Regions
Champagne-Ardenne ranks #1 in both average severity (€3,230) and cost
per exposure year (€399), despite being #2 in claim frequency (0.133,
behind Corse at 0.143). Its real signal is severity and cost, not
frequency alone.
Action: Conduct focused underwriting review — examine pricing adequacy.
KPI: Monthly claim frequency and cost per exposure year by region.

RECOMMENDATION 2: Strengthen Monitoring of Young Driver Segment
Drivers aged 18–25 show claim frequency 0.175 (75% above avg) and
severity €4,692 (167% above avg). Implement enhanced monitoring; review
bonus-malus and vehicle-power differentiation.
KPI: Monthly frequency and severity for 18–25 group vs. portfolio avg.

RECOMMENDATION 3: Focus Claims Management on High-Cost Tail Claims
Top 10% of individual claims account for 60% of total cost. Establish
structured review for claims above the 95th percentile (~€4,862).
KPI: Monthly count and cost contribution of claims above 95th percentile.
```

### 4e. Assemble Dashboard 3

1. New dashboard, 1200×900.
2. Title: "CLAIM COST CONCENTRATION & RECOMMENDATIONS".
3. Top: Pareto Chart (left, 800×350) + Top Claims Table (right, 400×350).
4. Middle: Cost Distribution by Region (full width, ~180px).
5. Bottom: Recommendations text zone (full width, ~320px).

---

## Step 5: Save & Publish

### Save as .twbx

1. **File** → **Save As** → choose `.twbx` (packaged workbook).
   This bundles the data + workbook into a single file.
2. Save as `tableau/insurance_claims_dashboard.twbx`.

### Publish to Tableau Public (optional)

1. **Server** → **Tableau Public** → **Save to Tableau Public As…**
2. Name: "Insurance Claims & Portfolio Risk Dashboard".
3. Once published, copy the URL and add it to README.md:
   ```
   Tableau Public link: https://public.tableau.com/views/...
   ```

### Tableau Public Publishing Checklist

- [ ] All 5 data sources load without errors
- [ ] Page 1: 6 KPI values display correctly
- [ ] Page 1: Both regional bars render with reference lines
- [ ] Page 1: Highlight table shows all 21 regions × 3 measures
- [ ] Page 1: Region / Fuel Type / Density filters work
- [ ] Page 2: Driver age bars show 6 groups with correct frequencies
- [ ] Page 2: Vehicle age bars show 5 groups
- [ ] Page 2: Both scatter plots show labeled dots with size encoding
- [ ] Page 2: SegmentType filter works
- [ ] Page 3: Pareto shows bars + cumulative line + 80% reference
- [ ] Page 3: Top claims table shows 20 rows sorted by amount
- [ ] Page 3: Cost distribution shows 21 regions
- [ ] Page 3: Recommendations text is readable
- [ ] Dashboard actions: region click filters across charts
- [ ] Tooltips show correct fields on all charts
- [ ] No "unknown field" errors in the data pane

---

## Notes

- The generated `insurance_claims_dashboard.twb` is a **schema scaffold** that
  declares the intended structure but cannot render in Tableau. Use it as a
  reference for field names and chart types when building manually.
- The `scripts/generate_twb.py` generator exists for documentation purposes
  only — it is NOT a valid Tableau workbook.
- All KPI definitions, data cleaning, and analysis are in
  `notebooks/analysis.ipynb`. Do not modify the underlying data or KPI
  calculations.
