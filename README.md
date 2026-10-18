# Disney Analytics Team | Park Operations Dashboard

A compact Streamlit dashboard for a **Walt Disney World park operations manager** making historical staffing and attraction-priority decisions. 

## Step 1 — Dataset and decision-maker

- **Source:** [Walt Disney World Wait Times and Crowd Calendar (Kaggle)](https://www.kaggle.com/datasets/chadwambles/walt-disney-world-wait-times), uploaded by chadwambles.
- **Files used:** `calendar_enriched.csv` (16,682 park-date records) and `ride_stats.csv` (2,022 park-year-attraction-metric summary records).
- **Coverage:** Four parks from **January 1, 2015 to September 30, 2026** for the park-date dataset. Date range and attraction coverage depend on selection.
- **What one row means:** In `calendar_enriched.csv`, one row is one park on one date. In `ride_stats.csv`, one row is one attraction, park, year (or all-time), and wait statistic.
- **Origin and limitations:** The Kaggle files provide historical crowd scores and summarized attraction waits. The underlying observation method and exact construction of the crowd score are not independently verified here; do not treat it as literal capacity utilization. The files are not a live feed. This analysis uses the provided data as a historical snapshot, not a forecast.
- **Audience:** A manager responsible for staffing and attraction operations in a selected Disney World park.

## Step 2 — Why a dashboard?

**Use:** The manager reviews historical demand patterns when planning staff schedules and deciding which attractions deserve operational attention. If the share of observed days with crowd scores at or above 80% is high in a planning period, the manager should examine staffing coverage for that period rather than automatically raise staffing based on one outlier. If particular attractions routinely show longer average waits, they should receive closer operational review.

**Without it:** The manager would need to compare separate date records and yearly ride summaries manually, making it slower to identify patterns and easier to confuse dates or mix parks.

**Why an interactive dashboard:** Planning questions recur every week and change by park and year. Filters allow repeated, consistent comparisons without generating a separate slide deck for each request. A weekly email is useful for a fixed summary but less convenient for exploring an individual park and year. It is not intended to replace real-time operational alerts.

## Step 3 — Exploratory analysis and display decisions

The EDA notebook (`eda.ipynb`) reviews shapes, types, missing values, distributions, and relationships in the supplied data. The key design choices are:

1. **Three KPIs:** Mean historical crowd score, share of high-crowd observed days (score >= 80), and number of observed dates. Together these show pressure, frequency, and sample size.
2. **Chart 1:** 14-observation rolling crowd score across the year. A smoothed time trend makes sustained crowded periods easier to see than daily noise.
3. **Chart 2:** Eight highest mean attraction waits among the selected park's non-archived attractions in the selected year. This supports prioritization and avoids overwhelming the manager with a large table.
4. **Filters:** Park and year. These match the decisions the manager can make and prevent combining incomparable parks and years.
5. **Reading order:** KPIs first, temporal explanation next, attraction ranking last.

**Excluded:** A weather breakdown, because the file's `is_rainy` indicator has no measured rainfall intensity and would distract from staffing decisions. Also excluded the Lightning Lane split analysis, since matched-group comparisons need methodological context and do not directly answer this dashboard's staffing question.

**Potential misunderstandings:** The crowd score is not a verified percentage of park capacity. Annual attraction average waits cannot be interpreted as live or day-specific waits. The attraction list changes across years, and some dates or operating minutes may be missing. The dashboard excludes archived attractions and labels the historical and annual data separately. There are 630 missing `operating_minutes` values in the complete calendar file; that field is intentionally not used. The 80% review threshold is illustrative, not an official park rule.

## Step 4 — Refresh and action rules

For a production version focused on **planning rather than live queue management**, new daily crowd records would be ingested **once per day**, and attraction wait summaries would be recomputed nightly from underlying ride observations, if those observations were available. The operations manager would review trends **once per week**, ahead of staffing planning. Daily refresh and weekly review serve different purposes.

The **share of days with crowd score >= 80** would be tracked by park across comparable periods. A proposed review trigger is **more than 25%** of observed dates in a planning period crossing 80; it prompts a staffing discussion, not an automatic staffing change. The threshold needs calibration against actual staffing costs and service levels.

If data were a week old, a staffing review could miss recent demand shifts, new ride closures, and special events, increasing the risk of scheduling too few employees or allocating them to the wrong attractions. For same-day queue decisions, this historical dashboard is insufficient: that would require a separate verified live data source and a faster refresh rate.

**Current deployed version:** Frozen Kaggle snapshot through September 30, 2026. It does **not** auto-refresh; the proposed frequency describes a future production system.
