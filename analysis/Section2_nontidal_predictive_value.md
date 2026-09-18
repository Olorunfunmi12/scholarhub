# Does incorporating nontidal data improve prediction of tidal *Enterococcus*?

**Blue Water Baltimore Ambient Water-Quality Monitoring Program, 2013–2024**
Draft results section — follow-up to the rainfall/streamflow analysis.

## Question

We tested whether **nontidal (upstream stream) monitoring data adds predictive value for *Enterococcus* at the
tidal harbor stations** (`BWB-PATMH-*`, Patapsco/Baltimore Harbor). Gwynns Falls (`BWB-GWN-*`) and Jones Falls
(`BWB-JON-*`) drain into the harbor, so their water quality is a plausible leading indicator of harbor bacteria.

## Approach

A nested-model comparison holding the samples, folds, and estimator fixed:

| Model | Predictors | Purpose |
|---|---|---|
| **T1 (base)** | season + station location/site + the harbor's own in-situ panel (nutrient chemistry + surface sonde: temperature, pH, conductance, salinity, DO) | best harbor-only baseline |
| **T2 (+ nontidal)** | T1 **+** upstream stream-network state: stream *Enterococcus* (network mean & max, and per-watershed for Gwynns and Jones), plus stream turbidity, total phosphorus, DO, nitrate, conductance, temperature | test of added value |
| **T3 (nontidal only)** | season + location + upstream stream data (no harbor chemistry) | can upstream data alone nowcast the harbor? |

- **Target:** harmonized *Enterococcus* (A2LA value, else BWB→A2LA-equivalent), modeled as log₁₀(MPN+1) for
  regression and as exceedance of the 104 MPN/100 mL single-sample standard for classification.
- **Temporal join:** harbor and stream surveys rarely fall on the exact same day, but the nearest stream survey is
  within 1 day (median) and within 7 days for **87%** of harbor samples. Each harbor sample was matched to the
  nearest stream-network state within ±7 days (a strictly-causal backward-only join gave the same conclusion).
- **Validation:** year-blocked cross-validation (`GroupKFold` by calendar year) so no survey week is split across
  train and test. All metrics are out-of-fold. Missing predictors imputed from training folds only.

## Results

**Adding upstream data improves the harbor model on every metric.** On the matched subset (harbor samples with an
upstream survey within 7 days; n = 3,121, exceedance base rate 16.6%):

| Model | R² (log₁₀) | RMSE | ROC-AUC | PR-AUC |
|---|---|---|---|---|
| T1 — harbor in-situ WQ (base) | 0.165 | 0.904 | 0.746 | 0.357 |
| **T2 — + nontidal data** | **0.278** | **0.841** | **0.802** | **0.496** |
| T3 — nontidal only | 0.224 | 0.872 | 0.788 | 0.450 |
| **Lift (T2 − T1)** | **+0.113** | **−0.063** | **+0.056** | **+0.139** |

On the full harbor sample (n = 3,581; unmatched rows keep an imputed upstream block, a conservative lower bound)
the lift is smaller but in the same direction: R² +0.024, AUC +0.053, PR-AUC +0.121.

**The added block is highly significant.** In linear/logistic models with year fixed effects on the matched subset:

- Regression of log₁₀(*Enterococcus*): adjusted R² **0.335 → 0.386**; partial-F(12, 3081) = **22.4, p ≈ 0**.
- Exceedance (>104): McFadden pseudo-R² **0.273 → 0.344**; likelihood-ratio χ²(12) = **200, p ≈ 0**.

**The lift is stable**, not a lucky fold: ΔR² = +0.116 ± 0.001 (Random Forest) and +0.072 ± 0.001 (Gradient
Boosting) across seeds; ΔAUC = +0.057 for both.

**What carries the signal — upstream bacteria themselves.** The strongest added predictors are stream
*Enterococcus* (Jones Falls network mean first, pooled stream mean/max next), followed by stream turbidity, total
phosphorus, conductance and nitrate. Rank correlations with harbor log-*Enterococcus* are ρ ≈ +0.20–0.26 for
upstream bacteria and +0.14–0.15 for stream turbidity/TP; conductance is negatively associated (ρ ≈ −0.18),
consistent with fresh stormwater runoff lowering harbor salinity while raising bacteria.

**Dose–response.** Harbor exceedance rises monotonically with same-week upstream bacteria — from ~1% of harbor
samples when upstream streams are clean (<10 MPN/100 mL) to ~38% when upstream streams are high (>1000), providing
the physical basis for the statistical result.

## Interpretation and caveat

Incorporating nontidal stream data materially improves nowcasting of harbor *Enterococcus*, and upstream data
alone (T3) nearly matches the harbor-only baseline — a useful result where harbor chemistry is unavailable. The
one caveat: upstream bacteria are themselves rain-driven, so part of this lift may overlap with the
antecedent-rainfall signal that Section 1 found strong in the harbor. Re-running T1 vs T2 with the NOAA rainfall
block already in the base isolates the purely hydrologic (stream-transport) contribution, and is the recommended
next step when the two analyses are combined. The daily USGS discharge series (still pending) then slots directly
into the same upstream feature set to test whether streamflow adds value on top of stream chemistry.
