# Does incorporating nontidal data improve prediction of tidal Enterococcus?

Blue Water Baltimore Ambient Water Quality Monitoring Program, 2013-2024. Draft results section, following the rainfall and streamflow analysis.

## Question

I tested whether nontidal (upstream stream) monitoring data helps predict Enterococcus at the tidal harbor stations (BWB-PATMH, Patapsco / Baltimore Harbor). Gwynns Falls (BWB-GWN) and Jones Falls (BWB-JON) drain into the harbor, so their water quality could be an early indicator of harbor bacteria.

## Approach

A nested-model comparison, holding the samples, cross-validation folds, and model fixed:

| Model | Predictors | Purpose |
|---|---|---|
| T1 (base) | season, station location and site, and the harbor's own in-situ panel (nutrient chemistry plus surface sonde: temperature, pH, conductance, salinity, DO) | harbor-only baseline |
| T2 (+ nontidal) | T1 plus the upstream stream network: stream Enterococcus (network mean and max, and per-watershed), plus stream turbidity, total phosphorus, DO, nitrate, conductance, temperature | test of added value |
| T3 (nontidal only) | season, location, and upstream stream data (no harbor chemistry) | can upstream data alone predict the harbor? |

- Target: harmonized Enterococcus (A2LA value where present, otherwise the BWB value converted to its A2LA equivalent), modeled as log10(MPN+1) for regression and as exceedance of the 104 MPN/100 mL single-sample standard for classification.
- Matching: harbor and stream samples rarely fall on the same day, but the nearest stream survey is within 1 day for the median harbor sample and within 7 days for about 87% of them. Each harbor sample is matched to the nearest stream reading within 7 days. A backward-only match (streams on or before the harbor date) gives the same result.
- Validation: year-blocked cross-validation, holding out whole calendar years so no sampling week is split across train and test. All metrics are out-of-fold.

## Results

Adding upstream data improves the harbor model on every metric. On the matched subset (harbor samples with an upstream survey within 7 days; n = 3,121, exceedance rate 16.6%):

| Model | R2 (log10) | RMSE | ROC-AUC | PR-AUC |
|---|---|---|---|---|
| T1, harbor in-situ WQ (base) | 0.165 | 0.904 | 0.746 | 0.357 |
| T2, plus nontidal data | 0.278 | 0.841 | 0.802 | 0.496 |
| T3, nontidal only | 0.224 | 0.872 | 0.788 | 0.450 |
| Change (T2 minus T1) | +0.113 | -0.063 | +0.056 | +0.139 |

On the full harbor sample (n = 3,581), where unmatched rows keep an imputed upstream block so the sample size and folds match, the improvement is smaller but in the same direction: R2 +0.024, AUC +0.053, PR-AUC +0.121.

The added block is significant. With year fixed effects, regression of log10(Enterococcus) rises from adjusted R2 0.335 to 0.386 (partial-F = 22.4, p < 0.001), and exceedance pseudo-R2 rises from 0.273 to 0.344 (likelihood-ratio chi2 = 200, p < 0.001). The improvement is stable across random seeds and models (Random Forest change in R2 = +0.116, Gradient Boosting +0.072).

What drives it is the upstream Enterococcus itself. The strongest added predictors are stream Enterococcus (Jones Falls network mean first, then the pooled stream mean and max), followed by stream turbidity and phosphorus. Rank correlations with harbor log Enterococcus are about +0.20 to +0.26 for upstream bacteria and +0.14 to +0.15 for stream turbidity and TP; conductance is negatively related (about -0.18), which fits fresh stormwater runoff lowering harbor salinity while raising bacteria. Harbor exceedance rises steadily with same-week upstream bacteria, from about 1% when the streams are clean (below 10 MPN/100 mL) to about 38% when they are high (above 1000).

## Interpretation

Adding nontidal stream data clearly improves prediction of harbor Enterococcus, and upstream data alone (T3) predicts almost as well as the harbor's own chemistry, which is useful where harbor chemistry is limited. The strongest signal is the streams' own bacteria, consistent with the streams carrying a load that the harbor then registers.

One caveat: upstream bacteria are rain-driven, so some of this improvement may overlap with the antecedent-rainfall signal that was strong in the harbor in Section 1. Adding the rainfall term to the baseline before comparing T1 and T2 would separate the stream-transport effect from shared weather, and is the recommended next step. The daily USGS discharge series, once available, plugs into the same upstream feature set to test whether streamflow adds anything on top of stream chemistry.
