# Nontidal predictors of tidal Enterococcus

Added predictive value of upstream stream monitoring data for *Enterococcus* at the
tidal harbor stations of the Blue Water Baltimore AWQMP (2013-2024).

## Data (not committed)

Place in `data/`:

- `BWB_AWQMP_Data_2009-2024-analyse061026.xlsx` — harbor and stream monitoring
- `usgs_daily_mean_discharge_clean_combined.csv` — USGS gauge reference

## Run

```
pip install -r requirements.txt
jupyter nbconvert --to notebook --execute Enterococcus_nontidal_predicts_tidal_ML.ipynb
```

## Result

A harbor-only baseline (`T1`) is compared against the same model plus upstream stream
features (`T2`) under year-blocked cross-validation. Upstream data raises out-of-fold
skill (R2 0.165 -> 0.278, exceedance AUC 0.746 -> 0.802 on the matched subset); the
added block is significant (OLS partial-F and logistic LR tests, p < 0.001) and stable
across seeds and estimators. Figures in `figures/`.
