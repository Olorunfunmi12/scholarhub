"""
Enterococcus Bacteria ML Prediction – BWB Nontidal 2013–2024
Based on methodology from Ali et al. (2026) Water Research
4 Scenarios: Real-time, Same day, Same day + Lag, Next day
Model: Random Forest Regressor
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import warnings, math
warnings.filterwarnings('ignore')

from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, r2_score

# ─────────────────────────────────────────────────────────────
# 1. LOAD & CLEAN DATA
# ─────────────────────────────────────────────────────────────
RAW_PATH = '/root/.claude/uploads/828f0ffd-65f0-5b07-8c29-77e2e012e459/459a9b21-box4_BWB.xlsx'
df = pd.read_excel(RAW_PATH)
df.columns = df.columns.str.strip()

df['Collection Date'] = pd.to_datetime(df['Collection Date'], origin='1899-12-30', unit='D')

for col in ['Enterococcus Bacteria (MPN/100mL) - BWB Lab',
            'Total Nitrogen (mg/L)', 'Total Phosphorus (mg/L)']:
    df[col] = pd.to_numeric(df[col], errors='coerce')

# Combine both lab measurements; prefer A2LA Lab
df['Entero'] = (
    df['Enterococcus Bacteria (MPN/100mL) - A2LA Lab']
    .combine_first(df['Enterococcus Bacteria (MPN/100mL) - BWB Lab'])
)

df = df[df['Entero'].notna()].copy()
df['Entero'] = df['Entero'].replace(0, 0.01)   # avoid log(0)

print(f"Raw rows with Enterococcus: {len(df):,}  |  Stations: {df['Station ID'].nunique()}")

# ─────────────────────────────────────────────────────────────
# 2. AGGREGATE TO SAMPLING-DATE LEVEL (mean across stations)
# ─────────────────────────────────────────────────────────────
FEATURE_COLS = [
    'Dissolved Oxygen (mg/L)',
    'Barometric Pressure (mmHg)',
    'Temperature (°C)',
    'Specific Conductance (µS/cm)',
    'pH (SU)',
    'Turbidity (NTU)',
    'Optical Brighteners (ppm)',
    'Total Nitrogen (mg/L)',
    'Total Phosphorus (mg/L)',
    'Nitrate/Nitrite (mg/L)',
]

agg = {c: 'mean' for c in FEATURE_COLS}
agg['Entero'] = 'mean'

samp = (df.groupby('Collection Date').agg(agg)
          .reset_index()
          .sort_values('Collection Date')
          .reset_index(drop=True))

samp['log10_Entero'] = np.log10(samp['Entero'])

# Add calendar features
samp['month']      = samp['Collection Date'].dt.month
samp['day_of_year']= samp['Collection Date'].dt.dayofyear
samp['sin_doy']    = np.sin(2 * np.pi * samp['day_of_year'] / 365)
samp['cos_doy']    = np.cos(2 * np.pi * samp['day_of_year'] / 365)

CALENDAR_FEATS = ['sin_doy', 'cos_doy']
ALL_FEATS_BASE = FEATURE_COLS + CALENDAR_FEATS

print(f"\nSampling dates: {len(samp)}  |  Range: {samp['Collection Date'].min().date()} – {samp['Collection Date'].max().date()}")

# ─────────────────────────────────────────────────────────────
# 3. LAG FEATURES (sample-based: prev sample, 2 samples ago, …)
# ─────────────────────────────────────────────────────────────
LAG_SAMPLES = [1, 2, 3, 4]  # previous 1–4 sampling events

for lag in LAG_SAMPLES:
    samp[f'log10_Entero_lag{lag}'] = samp['log10_Entero'].shift(lag)
    for col in FEATURE_COLS:
        samp[f'{col}_lag{lag}'] = samp[col].shift(lag)

LAG_TARGET_FEATS = [f'log10_Entero_lag{l}' for l in LAG_SAMPLES]
LAG_WQ_1         = [f'{c}_lag1' for c in FEATURE_COLS]
LAG_WQ_1_2_3     = [f'{c}_lag{l}' for l in [1, 2, 3] for c in FEATURE_COLS]

# ─────────────────────────────────────────────────────────────
# 4. SCENARIO DEFINITIONS  (mirrors Ali et al. 4-scenario design)
# ─────────────────────────────────────────────────────────────
#  Scenario 1 – Real-time   : current-day WQ + lagged target + lag-1 WQ
#  Scenario 2 – Same day    : current-day WQ only (no history)
#  Scenario 3 – Same day + Lag: current WQ + lagged WQ (no target lag)
#  Scenario 4 – Next day    : lag-1 WQ + lagged target → predict next sample
SCENARIOS = {
    'Scenario 1\n(Real-time)':
        ALL_FEATS_BASE + LAG_TARGET_FEATS + LAG_WQ_1,
    'Scenario 2\n(Same day)':
        ALL_FEATS_BASE,
    'Scenario 3\n(Same day + Lag)':
        ALL_FEATS_BASE + LAG_WQ_1_2_3,
    'Scenario 4\n(Next day)':
        LAG_WQ_1 + LAG_TARGET_FEATS + CALENDAR_FEATS,
}

SCENARIO_COLORS = {
    'Scenario 1\n(Real-time)':        '#5B9BD5',
    'Scenario 2\n(Same day)':         '#70AD47',
    'Scenario 3\n(Same day + Lag)':   '#ED7D31',
    'Scenario 4\n(Next day)':         '#E05C7B',
}

# ─────────────────────────────────────────────────────────────
# 5. TRAIN / TEST SPLIT  (temporal 80 / 20)
# ─────────────────────────────────────────────────────────────
TARGET = 'log10_Entero'

# Use rows that have at least the target + core WQ (after lag shift)
core_needed = FEATURE_COLS[:6]   # DO, BP, Temp, SpCond, pH, Turb
samp_valid = samp.dropna(subset=[TARGET] + core_needed + LAG_TARGET_FEATS).reset_index(drop=True)

split_idx = int(len(samp_valid) * 0.80)
train_df  = samp_valid.iloc[:split_idx]
test_df   = samp_valid.iloc[split_idx:]

print(f"\nTrain: {train_df['Collection Date'].min().date()} – {train_df['Collection Date'].max().date()}  ({len(train_df)} samples)")
print(f"Test : {test_df['Collection Date'].min().date()} – {test_df['Collection Date'].max().date()}  ({len(test_df)} samples)")

# ─────────────────────────────────────────────────────────────
# 6. HELPER METRICS
# ─────────────────────────────────────────────────────────────
def rmse(yt, yp):   return np.sqrt(np.mean((yt - yp)**2))
def mape(yt, yp):
    m = yt != 0
    return np.mean(np.abs((yt[m] - yp[m]) / yt[m])) * 100

# ─────────────────────────────────────────────────────────────
# 7. TRAIN RANDOM FOREST FOR EACH SCENARIO
# ─────────────────────────────────────────────────────────────
results     = {}
predictions = {}

for name, feat_list in SCENARIOS.items():
    feats = [f for f in feat_list if f in samp_valid.columns]

    # Fill remaining NaN with training medians
    train_med = train_df[feats].median()
    X_train = train_df[feats].fillna(train_med).values
    y_train = train_df[TARGET].values
    X_test  = test_df[feats].fillna(train_med).values
    y_test  = test_df[TARGET].values

    scaler   = StandardScaler()
    X_tr_s   = scaler.fit_transform(X_train)
    X_te_s   = scaler.transform(X_test)

    rf = RandomForestRegressor(
        n_estimators=500,
        max_depth=None,
        min_samples_leaf=2,
        max_features='sqrt',
        random_state=42,
        n_jobs=-1,
    )
    rf.fit(X_tr_s, y_train)

    y_pred_train = rf.predict(X_tr_s)
    y_pred_test  = rf.predict(X_te_s)

    mae_v  = mean_absolute_error(y_test, y_pred_test)
    mape_v = mape(y_test, y_pred_test)
    rmse_v = rmse(y_test, y_pred_test)
    r2_v   = r2_score(y_test, y_pred_test)

    results[name] = dict(MAE=mae_v, MAPE=mape_v, RMSE=rmse_v, R2=r2_v)
    predictions[name] = dict(
        train_dates = train_df['Collection Date'].values,
        test_dates  = test_df['Collection Date'].values,
        y_train_obs = y_train,
        y_pred_train= y_pred_train,
        y_test_obs  = y_test,
        y_pred_test = y_pred_test,
        feats       = feats,
        model       = rf,
    )

    short = name.replace('\n', ' ')
    print(f"  {short:<32}  MAE={mae_v:.3f}  MAPE={mape_v:.1f}%  RMSE={rmse_v:.3f}  R²={r2_v:.3f}")

# ─────────────────────────────────────────────────────────────
# 8. MAIN FIGURE  (mirrors sample image: TS | Radar | Scatter)
# ─────────────────────────────────────────────────────────────
SNAMES = list(SCENARIOS.keys())
n_sc   = len(SNAMES)

fig = plt.figure(figsize=(18, 5.2 * n_sc))
fig.patch.set_facecolor('white')

outer = gridspec.GridSpec(
    n_sc, 3, figure=fig,
    hspace=0.65, wspace=0.38,
    left=0.06, right=0.97, top=0.95, bottom=0.03
)

# ── Radar helper ────────────────────────────────────────────
max_mae  = max(v['MAE']  for v in results.values()) * 1.05
max_mape = max(v['MAPE'] for v in results.values()) * 1.05
max_rmse = max(v['RMSE'] for v in results.values()) * 1.05

def draw_radar(ax, res, color, title):
    n_mae  = res['MAE']  / max_mae
    n_mape = res['MAPE'] / max_mape
    n_rmse = res['RMSE'] / max_rmse
    n_r2   = res['R2']   / 1.0       # higher is better

    # Diamond: top=MAE, right=R², bottom=RMSE, left=MAPE
    angles = [np.pi/2, 0, -np.pi/2, np.pi]
    norms  = [n_mae, n_r2, n_rmse, n_mape]
    xs = [v * np.cos(a) for v, a in zip(norms, angles)] + [norms[0]*np.cos(angles[0])]
    ys = [v * np.sin(a) for v, a in zip(norms, angles)] + [norms[0]*np.sin(angles[0])]

    ax.fill(xs, ys, alpha=0.30, color=color)
    ax.plot(xs, ys, color=color, lw=1.8)

    th = np.linspace(0, 2*np.pi, 300)
    for r in [0.25, 0.50, 0.75, 1.0]:
        ax.plot(np.cos(th)*r, np.sin(th)*r, color='grey', lw=0.4, ls='--', alpha=0.45)
    for a in angles:
        ax.plot([0, np.cos(a)], [0, np.sin(a)], color='grey', lw=0.6)

    labels = ['MAE', 'R²', 'RMSE', 'MAPE']
    raw_vals = [res['MAE'], res['R2'], res['RMSE'], res['MAPE']]
    fmts     = ['{:.2f}', '{:.3f}', '{:.3f}', '{:.0f}%']
    for (a, lbl, rv, fmt) in zip(angles, labels, raw_vals, fmts):
        ax.text(np.cos(a)*1.22, np.sin(a)*1.22, lbl,
                ha='center', va='center', fontsize=7.5, fontweight='bold')
        ax.text(np.cos(a)*0.92, np.sin(a)*0.92, fmt.format(rv),
                ha='center', va='center', fontsize=6.5, color='#333333')

    for r_tick in [0.25, 0.50]:
        ax.text(0.02, r_tick+0.03, f'{r_tick:.2f}', ha='left',
                va='bottom', fontsize=5.5, color='grey')

    ax.set_xlim(-1.5, 1.5); ax.set_ylim(-1.5, 1.5)
    ax.set_aspect('equal'); ax.axis('off')
    ax.set_title(title, fontsize=9, fontweight='bold', pad=6)

# ── Row plots ───────────────────────────────────────────────
for i, name in enumerate(SNAMES):
    color = SCENARIO_COLORS[name]
    pred  = predictions[name]
    res   = results[name]
    short = name.replace('\n', ' ')

    all_dates = np.concatenate([pred['train_dates'], pred['test_dates']])
    all_obs   = np.concatenate([pred['y_train_obs'], pred['y_test_obs']])
    all_pred  = np.concatenate([pred['y_pred_train'], pred['y_pred_test']])

    split_date = pred['test_dates'][0]

    # ── A: Time Series ──────────────────────────────────────
    ax_ts = fig.add_subplot(outer[i, 0])
    ax_ts.plot(all_dates, all_obs,  color='#2776B4', lw=1.0, label='Observed',  zorder=3)
    ax_ts.plot(all_dates, all_pred, color='#FF7F0E', lw=1.0, ls='--',
               label='Predicted', zorder=3)
    ax_ts.axvspan(all_dates[0], split_date, alpha=0.06, color='steelblue')
    ax_ts.axvspan(split_date, all_dates[-1], alpha=0.06, color='darkorange')
    ax_ts.axvline(split_date, color='grey', lw=0.8, ls=':')
    ax_ts.set_ylabel('log₁₀ Enterococcus\n(MPN/100mL)', fontsize=8)
    ax_ts.set_xlabel('Year', fontsize=8)
    ax_ts.set_title(short, fontsize=9, fontweight='bold')
    ax_ts.legend(fontsize=6.5, loc='upper right', framealpha=0.75)
    ax_ts.tick_params(labelsize=7)
    ax_ts.yaxis.set_major_locator(plt.MaxNLocator(5))
    # Panel letter
    if i == 0:
        ax_ts.text(-0.11, 1.07, 'a.', transform=ax_ts.transAxes,
                   fontsize=13, fontweight='bold')

    # ── B: Radar ────────────────────────────────────────────
    ax_r = fig.add_subplot(outer[i, 1])
    draw_radar(ax_r, res, color, short)
    if i == 0:
        ax_r.text(-0.10, 1.08, 'b.', transform=ax_r.transAxes,
                  fontsize=13, fontweight='bold')

    # ── C: Scatter (test set) ───────────────────────────────
    ax_sc = fig.add_subplot(outer[i, 2])
    y_obs  = pred['y_test_obs']
    y_pred = pred['y_pred_test']

    ax_sc.scatter(y_obs, y_pred, s=22, color='#FFA500',
                  alpha=0.70, edgecolors='none', zorder=3)

    lo = min(y_obs.min(), y_pred.min()) - 0.15
    hi = max(y_obs.max(), y_pred.max()) + 0.15
    ax_sc.plot([lo, hi], [lo, hi], color='#7B2D8B', ls='--', lw=1.2,
               label='1:1 Line', zorder=2)

    coeffs = np.polyfit(y_obs, y_pred, 1)
    x_line = np.linspace(lo, hi, 200)
    ax_sc.plot(x_line, np.polyval(coeffs, x_line),
               color='#2CA02C', lw=1.2, label='Regression Line', zorder=2)

    ax_sc.set_xlabel('Observed Enterococcus (log₁₀ MPN/100mL)', fontsize=8)
    ax_sc.set_ylabel('Predicted Enterococcus (log₁₀ MPN/100mL)', fontsize=8)
    ax_sc.legend(fontsize=6.5, loc='upper left', framealpha=0.75)
    ax_sc.tick_params(labelsize=7)
    ax_sc.text(0.04, 0.91,
               f"R² = {res['R2']:.3f}\nRMSE = {res['RMSE']:.3f}\nMAE = {res['MAE']:.3f}",
               transform=ax_sc.transAxes, fontsize=7,
               bbox=dict(boxstyle='round,pad=0.3', fc='white', alpha=0.75))
    if i == 0:
        ax_sc.text(-0.20, 1.07, 'c.', transform=ax_sc.transAxes,
                   fontsize=13, fontweight='bold')

plt.suptitle(
    'Enterococcus Bacteria ML Prediction (Random Forest)\n'
    'BWB Nontidal Watershed – 2013 to 2024',
    fontsize=11, fontweight='bold', y=0.982
)

OUT_FIG = '/home/user/scholarhub/enterococcus_ml_prediction.png'
plt.savefig(OUT_FIG, dpi=150, bbox_inches='tight', facecolor='white')
print(f"\nMain figure → {OUT_FIG}")
plt.close()

# ─────────────────────────────────────────────────────────────
# 9. FEATURE IMPORTANCE (Scenario 1)
# ─────────────────────────────────────────────────────────────
fi_name  = 'Scenario 1\n(Real-time)'
fi_model = predictions[fi_name]['model']
fi_feats = predictions[fi_name]['feats']
imps     = fi_model.feature_importances_
TOP_N    = 15
idx      = np.argsort(imps)[::-1][:TOP_N]

fig2, ax2 = plt.subplots(figsize=(11, 5))
bars = ax2.bar(range(TOP_N), imps[idx], color=SCENARIO_COLORS[fi_name], alpha=0.85)
ax2.set_xticks(range(TOP_N))
labels_fi = [fi_feats[j].replace(' (mg/L)', '\n(mg/L)').replace(' (', '\n(') for j in idx]
ax2.set_xticklabels(labels_fi, rotation=35, ha='right', fontsize=7.5)
ax2.set_ylabel('Feature Importance (Mean Decrease Impurity)', fontsize=9)
ax2.set_title('Top-15 Feature Importances – Scenario 1 (Real-time)\nRandom Forest | Enterococcus Prediction', fontsize=10)
ax2.grid(axis='y', alpha=0.3)

# Annotate bars
for bar, val in zip(bars, imps[idx]):
    ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.001,
             f'{val:.3f}', ha='center', va='bottom', fontsize=6.5)

fig2.tight_layout()
OUT_FI = '/home/user/scholarhub/enterococcus_feature_importance.png'
fig2.savefig(OUT_FI, dpi=150, bbox_inches='tight', facecolor='white')
print(f"Feature importance → {OUT_FI}")
plt.close(fig2)

# ─────────────────────────────────────────────────────────────
# 10. METRICS SUMMARY
# ─────────────────────────────────────────────────────────────
print("\n" + "="*67)
print(f"{'Scenario':<32}  {'MAE':>6}  {'MAPE%':>7}  {'RMSE':>6}  {'R²':>6}")
print("="*67)
for name, res in results.items():
    s = name.replace('\n', ' ')
    print(f"{s:<32}  {res['MAE']:>6.3f}  {res['MAPE']:>7.2f}  {res['RMSE']:>6.3f}  {res['R2']:>6.3f}")
print("="*67)

# Save CSV
metrics_df = pd.DataFrame([
    {'Scenario': k.replace('\n', ' '), **v} for k, v in results.items()
])
OUT_CSV = '/home/user/scholarhub/enterococcus_ml_metrics.csv'
metrics_df.to_csv(OUT_CSV, index=False)
print(f"\nMetrics CSV → {OUT_CSV}")
