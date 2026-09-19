# Insurance Claims & Portfolio Risk Analytics — Python + Tableau

**StudyBuild — Project 01 | Data Analysis & Business Intelligence Track**

Author: [Arad Pilevar Javid](https://github.com/AradPilevarJavid)

This project uses the French Motor Third-Party Liability (freMTPL2) dataset to explore insurance claims and portfolio risk patterns. The analysis is mainly done in Python, with Tableau used for the final visual analysis and dashboard.

---

## Business Problem

A motor insurance company needs a clear view of its portfolio:

* Where do claims occur most frequently?
* Where are claim costs highest?
* Which segments show noticeably different claim patterns?
* Which patterns are worth monitoring further?

This is a **descriptive analytics / BI project**, not a pricing or underwriting model. Claim counts alone are not enough to compare groups, so exposure, portfolio size, frequency, and severity are considered together.

---

## Dataset

* **Name:** French Motor Third-Party Liability (freMTPL2)
* **Source:** [CASdatasets R Package](https://dutangc.github.io/CASdatasets/reference/freMTPL.html)
* **Policies:** 678,000+ motor third-party liability policies, mainly covering 2011–2013
* **Claims:** 26,639 individual claim records
* **Original insurer:** Unknown / anonymous dataset

The dataset does **not** contain written premium, so **Loss Ratio is not calculated**. Instead, the analysis focuses on claim frequency, claim severity, and total claim cost.

I went through the project in several main steps. Some of the smaller steps are self-explanatory from the notebook, so I did not document every individual operation here.

1. Data cleaning and quality checks
2. Merging the frequency and severity datasets
3. Feature engineering and segment creation
4. Exploratory data analysis
5. Portfolio and segment analysis
6. Claim-cost concentration and outlier analysis
7. Preparing the data for Tableau
8. Final Tableau dashboard

---

## Portfolio Health Summary

| KPI                    |                     Value |
| ---------------------- | ------------------------: |
| Policy Count           |                   678,013 |
| Total Exposure         |             358,499 years |
| Total Claim Count      |                    36,102 |
| Policies with Claims   |             34,060 (5.0%) |
| Claim Frequency        |  0.1007 per exposure year |
| Total Claim Cost       |               €59,909,216 |
| Average Claim Severity | €2,249 per observed claim |
| Cost per Exposure Year |                      €167 |

Raw claim counts can be misleading when comparing regions or segments. A group with more policies or longer exposure will naturally accumulate more claims. Claim frequency normalises the number of claims by exposure and provides a more useful basis for comparison.

### Severity note

Average Claim Severity is calculated as:

`Total Claim Cost / Number of observed claims`

The denominator is the **26,639 individual claim records** in the severity dataset, not the 34,060 policies with claims. This makes the metric an average cost per observed claim.

There is also a known gap between the policy-level claim counts and the severity records: `ClaimNb` totals 36,102, while the severity dataset contains 26,639 claim records. Therefore, the €2,249 figure should be interpreted as the average cost of the recorded claims in the severity dataset rather than an estimate of the cost of every claim implied by `ClaimNb`.

---

# Analysis & Findings

## Regional Claim Burden

* **Champagne-Ardenne** has the highest observed average severity (€3,230) and cost per exposure year (€399), while its claim frequency is 0.133.
* **Corse** has the highest claim frequency (0.143) but a more moderate severity, showing that high frequency does not necessarily mean high severity.
* **Île-de-France** contributes the largest absolute claim cost (€4.6M), largely because of its large portfolio, while its frequency is only slightly above the portfolio average.

This is why regional comparisons use both exposure-adjusted frequency and severity rather than absolute claim cost alone.

---

## Driver & Vehicle Segment Patterns

Several segments show noticeably different observed claim patterns:

* **Young drivers (18–25)** have the highest claim frequency (0.175) and the highest average severity (€4,692).
* **New vehicles (`VehAge = 0`)** show a high frequency (0.311) but relatively low severity (€476).
* **Older vehicles (11+)** have a lower frequency (0.080) but higher severity (€2,607).
* **Bonus-Malus** shows a strong relationship with claim frequency: drivers with scores above 100 have substantially higher observed frequency than drivers at 50.

These are observed associations in the dataset and should not be interpreted as proof that any individual characteristic causes higher claim costs.

---

## Frequency vs. Severity

Frequency and severity do not always move together.

The regional frequency-versus-severity analysis shows most regions clustering around the portfolio average, while Champagne-Ardenne stands out with both relatively high frequency and severity.

Other segments show different combinations. For example, new vehicles have high observed frequency but relatively low severity.

This makes frequency and severity useful as separate dimensions rather than reducing portfolio risk to a single metric.

---

## Claim Cost Concentration

Claim amounts have a very long right tail.

The largest claims account for a disproportionately large share of total claim cost:

* The **top 10% of individual claims** account for approximately **60%** of total claim cost.
* The **top 1%** account for approximately **38%**.
* The maximum observed claim is **€4,075,401**.
* The median claim is approximately **€1,172**.
* The 99.9th percentile is approximately **€162,784**.

I also use claim-cost rankings, cumulative cost shares, Lorenz curves, and the Gini coefficient to examine this concentration.

Extreme values are not automatically removed. Insurance claim distributions are naturally skewed, so large claims are part of the problem being analysed rather than simply data points to delete.

---

## Unusual Segments

One segment that stood out during the analysis was **young drivers with more powerful vehicles** (driver age ≤25 and vehicle power ≥10).

This group is relatively small, so the observation should not be treated as a portfolio-wide conclusion. It is better viewed as a segment worth investigating further.

---

# Recommendations

The recommendations below are based on the observed patterns in this dataset. They are areas for further investigation rather than direct pricing decisions.

### 1. Review High-Cost Regions

**Evidence:** Champagne-Ardenne has the highest observed average severity (€3,230) and cost per exposure year (€399), while its claim frequency is 0.133.

**Action:** Review the region in more detail and investigate whether the observed severity and cost patterns are consistent across its different policy segments.

**KPI:** Average severity and claim cost per exposure year by region.

### 2. Monitor the Young Driver Segment

**Evidence:** Drivers aged 18–25 have an observed claim frequency of 0.175 and average severity of €4,692.

**Action:** Examine how this segment interacts with other variables such as Bonus-Malus, vehicle power, and vehicle age.

**KPI:** Claim frequency and severity for drivers aged 18–25 compared with the portfolio average.

### 3. Monitor High-Cost Claims

**Evidence:** The largest claims account for a disproportionately large share of total claim cost, with the top 10% contributing around 60%.

**Action:** Pay particular attention to claims in the upper tail of the distribution and investigate unusual or extreme observations.

**KPI:** Number of claims and share of total cost above selected severity thresholds.

---

## Limitations

1. **Anonymous insurer** — The original insurer is not identified, so the results may not generalise to other portfolios.
2. **Historical data** — The dataset mainly covers 2011–2013, so current insurance patterns may differ.
3. **No premium data** — Loss Ratio cannot be calculated.
4. **Limited features** — The dataset does not contain every factor that could affect insurance claims, such as driving behaviour, telematics, weather, or road conditions.
5. **Descriptive analysis** — The observed relationships do not establish causation.
6. **Claim count discrepancy** — `ClaimNb` totals 36,102 claims, while the severity dataset contains 26,639 individual claim records. The frequency table counts claim multiplicity at the policy level, while the severity table contains recorded claim amounts. These two sources therefore need to be interpreted separately.

---

# Tableau Dashboard

The final visual analysis is being built in Tableau around three main areas.

### Portfolio Overview

* Total policies
* Total exposure
* Total claims
* Claim frequency
* Total claim cost
* Average claim severity
* Regional comparisons

### Frequency & Severity

* Claim frequency by region
* Claim frequency by driver age
* Claim frequency by vehicle characteristics
* Claim severity by region
* Claim severity by driver age
* Frequency vs. severity

### Claim Cost Analysis

* Claim severity distribution
* High-cost claims
* Regional claim costs
* Claim-cost concentration

The dashboard also uses filters such as region, vehicle age, fuel type, and Bonus-Malus where appropriate.

---

## Repository Structure

```text
insurance_final/
├── README.md
├── figures/
│   ├── q2_regional_comparison.png
│   ├── q3_segment_patterns.png
│   ├── q4_frequency_vs_severity.png
│   ├── q5_pareto_analysis.png
│   ├── q6_claim_distribution.png
│   └── q7_executive_dashboard_preview.png
├── notebooks/
│   └── analysis.ipynb
├── report/
│   └── business_summary.md
├── requirements.txt
├── scripts/
│   └── generate_twb.py
└── tableau/
    ├── BUILD_INSTRUCTIONS.md
    └── insurance_claims_dashboard.twb
```

---

Big thanks to the StudyBuild community for preparing the projects, sharing knowledge, and giving constructive feedback.

If you are interested in joining the community, feel free to message me on [Telegram](https://t.me/nerdysamurai).

*[StudyBuild](https://github.com/StudyBuildCommunity) — Learn • Build • Apply*
