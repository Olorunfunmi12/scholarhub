**Subject:** Nontidal → tidal *Enterococcus* — results for the second section

---

Dear Professor [name],

Thank you for the feedback. Following up on your question, I explored whether
incorporating nontidal data adds predictive value for tidal *Enterococcus*, and the
short answer is **yes**.

Using the Blue Water Baltimore monitoring data (2013–2024), I compared a harbor-only
model (season, station, and the harbor's own in-situ water quality) against the same
model augmented with the upstream Gwynns Falls and Jones Falls stream-network
conditions, matched to each harbor sample within the same week and evaluated with
year-blocked cross-validation.

Key results, on harbor samples with a matching upstream survey:

- Regression skill for log *Enterococcus* rose from **R² 0.165 to 0.278**.
- Exceedance (>104 MPN/100 mL) **ROC-AUC rose from 0.746 to 0.802**.
- The added upstream block is highly significant (partial-F p < 0.001;
  likelihood-ratio χ² p < 0.001) and stable across models and random seeds.
- The strongest upstream predictor is the streams' own *Enterococcus* (Jones Falls in
  particular): harbor exceedance risk rises from ~1% when the streams are clean to ~38%
  when they are high — consistent with the streams delivering bacterial load to the harbor.

Two notes for how we frame it:

- Upstream data alone predicts harbor exceedance nearly as well as the harbor's own
  chemistry, which could be useful for nowcasting.
- Because upstream bacteria are rain-driven, the cleanest "purely hydrologic" version of
  this test adds the rainfall term to the baseline first; I can run that as soon as we
  fold in the NOAA rainfall record. The streamflow extension is also ready to run the
  moment the daily USGS discharge series is available.

I've put the full notebook, a draft write-up for the second section, and the figures
here: [link]. Happy to walk through any of it whenever works for you.

Best regards,
Olorunfunmi
