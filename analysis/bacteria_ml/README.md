# Enterococcus prediction — rainfall & streamflow

Reproducible ML analysis testing whether NOAA rainfall and USGS streamflow improve
prediction of *Enterococcus* bacteria in Baltimore's tidal harbor and nontidal streams
(Blue Water Baltimore AWQMP, 2013–2024).

## Run
```bash
pip install -r requirements.txt
jupyter notebook Enterococcus_rainfall_streamflow_ML.ipynb   # Run All
```
The notebook is already executed (outputs + figures embedded); re-run to reproduce.

## Files
- `Enterococcus_rainfall_streamflow_ML.ipynb` — the analysis (narrative + code + results)
- `data/BWB_AWQMP_Data.xlsx` — bacteria + in-situ water quality
- `data/NOAA_BWI_precip_2013_2026.csv` — daily rainfall (BWI airport)
- `data/usgs_discharge_summary.csv` — USGS gauge summary (NOT the daily series — see §11)

## Headline
Rainfall is a large, robust win in the harbor (AUC 0.74 → 0.84) and ~neutral in the
streams (in-situ turbidity/phosphorus/DO already carry the storm signal). Streamflow is
pending the daily discharge series — §11 runs it automatically once supplied.
