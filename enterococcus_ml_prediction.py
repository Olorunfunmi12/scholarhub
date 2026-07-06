import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import warnings
warnings.filterwarnings('ignore')

from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, r2_score


RAW_PATH = '/root/.claude/uploads/828f0ffd-65f0-5b07-8c29-77e2e012e459/459a9b21-box4_BWB.xlsx'
df = pd.read_excel(RAW_PATH)
df.columns = df.columns.str.strip()
df['Collection Date'] = pd.to_datetime(df['Collection Date'], origin='1899-12-30', unit='D')

for col in ['Enterococcus Bacteria (MPN/100mL) - BWB Lab',
            'Total Nitrogen (mg/L)', 'Total Phosphorus (mg/L)']:
    df[col] = pd.to_numeric(df[col], errors='coerce')

df['Entero'] = (
    df['Enterococcus Bacteria (MPN/100mL) - A2LA Lab']
    .combine_first(df['Enterococcus Bacteria (MPN/100mL) - BWB Lab'])
)
df = df[df['Entero'].notna()].copy()
df['Entero'] = df['Entero'].replace(0, 0.01)


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
samp['sin_doy'] = np.sin(2 * np.pi * samp['Collection Date'].dt.dayofyear / 365)
samp['cos_doy'] = np.cos(2 * np.pi * samp['Collection Date'].dt.dayofyear / 365)

CALENDAR_FEATS = ['sin_doy', 'cos_doy']
ALL_FEATS_BASE = FEATURE_COLS + CALENDAR_FEATS

for lag in [1, 2, 3, 4]:
    samp[f'log10_Entero_lag{lag}'] = samp['log10_Entero'].shift(lag)
    for col in FEATURE_COLS:
        samp[f'{col}_lag{lag}'] = samp[col].shift(lag)

LAG_TARGET = [f'log10_Entero_lag{l}' for l in [1, 2, 3, 4]]
LAG_WQ_1   = [f'{c}_lag1' for c in FEATURE_COLS]
LAG_WQ_123 = [f'{c}_lag{l}' for l in [1, 2, 3] for c in FEATURE_COLS]

SCENARIOS = {
    'Scenario 1\n(Real-time)':        ALL_FEATS_BASE + LAG_TARGET + LAG_WQ_1,
    'Scenario 2\n(Same day)':         ALL_FEATS_BASE,
    'Scenario 3\n(Same day + Lag)':   ALL_FEATS_BASE + LAG_WQ_123,
    'Scenario 4\n(Next day)':         LAG_WQ_1 + LAG_TARGET + CALENDAR_FEATS,
}

COLORS = {
    'Scenario 1\n(Real-time)':        '#5B9BD5',
    'Scenario 2\n(Same day)':         '#70AD47',
    'Scenario 3\n(Same day + Lag)':   '#ED7D31',
    'Scenario 4\n(Next day)':         '#E05C7B',
}

TARGET = 'log10_Entero'
core   = FEATURE_COLS[:6]
samp_valid = samp.dropna(subset=[TARGET] + core + LAG_TARGET).reset_index(drop=True)

split      = int(len(samp_valid) * 0.80)
train_df   = samp_valid.iloc[:split]
test_df    = samp_valid.iloc[split:]


def rmse(yt, yp):
    return np.sqrt(np.mean((yt - yp) ** 2))

def mape(yt, yp):
    m = yt != 0
    return np.mean(np.abs((yt[m] - yp[m]) / yt[m])) * 100


results, predictions = {}, {}

for name, feat_list in SCENARIOS.items():
    feats = [f for f in feat_list if f in samp_valid.columns]
    med   = train_df[feats].median()

    X_tr = train_df[feats].fillna(med).values
    y_tr = train_df[TARGET].values
    X_te = test_df[feats].fillna(med).values
    y_te = test_df[TARGET].values

    sc     = StandardScaler()
    X_tr_s = sc.fit_transform(X_tr)
    X_te_s = sc.transform(X_te)

    rf = RandomForestRegressor(
        n_estimators=500, min_samples_leaf=2,
        max_features='sqrt', random_state=42, n_jobs=-1
    )
    rf.fit(X_tr_s, y_tr)

    yp_tr = rf.predict(X_tr_s)
    yp_te = rf.predict(X_te_s)

    results[name] = dict(
        MAE=mean_absolute_error(y_te, yp_te),
        MAPE=mape(y_te, yp_te),
        RMSE=rmse(y_te, yp_te),
        R2=r2_score(y_te, yp_te),
    )
    predictions[name] = dict(
        train_dates=train_df['Collection Date'].values,
        test_dates=test_df['Collection Date'].values,
        y_tr_obs=y_tr, y_tr_pred=yp_tr,
        y_te_obs=y_te, y_te_pred=yp_te,
        feats=feats, model=rf,
    )


SNAMES  = list(SCENARIOS.keys())
n_sc    = len(SNAMES)
max_mae  = max(v['MAE']  for v in results.values()) * 1.05
max_mape = max(v['MAPE'] for v in results.values()) * 1.05
max_rmse = max(v['RMSE'] for v in results.values()) * 1.05


def draw_radar(ax, res, color, title):
    angles = [np.pi/2, 0, -np.pi/2, np.pi]
    norms  = [res['MAE']/max_mae, res['R2'], res['RMSE']/max_rmse, res['MAPE']/max_mape]
    xs = [v*np.cos(a) for v, a in zip(norms, angles)] + [norms[0]*np.cos(angles[0])]
    ys = [v*np.sin(a) for v, a in zip(norms, angles)] + [norms[0]*np.sin(angles[0])]

    ax.fill(xs, ys, alpha=0.30, color=color)
    ax.plot(xs, ys, color=color, lw=1.8)

    th = np.linspace(0, 2*np.pi, 300)
    for r in [0.25, 0.50, 0.75, 1.0]:
        ax.plot(np.cos(th)*r, np.sin(th)*r, color='grey', lw=0.4, ls='--', alpha=0.45)
    for a in angles:
        ax.plot([0, np.cos(a)], [0, np.sin(a)], color='grey', lw=0.6)

    for a, lbl, rv, fmt in zip(
        angles,
        ['MAE', 'R²', 'RMSE', 'MAPE'],
        [res['MAE'], res['R2'], res['RMSE'], res['MAPE']],
        ['{:.2f}', '{:.3f}', '{:.3f}', '{:.0f}%'],
    ):
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


fig   = plt.figure(figsize=(18, 5.2 * n_sc))
fig.patch.set_facecolor('white')
outer = gridspec.GridSpec(n_sc, 3, figure=fig,
                          hspace=0.65, wspace=0.38,
                          left=0.06, right=0.97, top=0.95, bottom=0.03)

for i, name in enumerate(SNAMES):
    color = COLORS[name]
    pred  = predictions[name]
    res   = results[name]
    short = name.replace('\n', ' ')

    all_dates = np.concatenate([pred['train_dates'], pred['test_dates']])
    all_obs   = np.concatenate([pred['y_tr_obs'],    pred['y_te_obs']])
    all_pred  = np.concatenate([pred['y_tr_pred'],   pred['y_te_pred']])
    split_date = pred['test_dates'][0]

    ax_ts = fig.add_subplot(outer[i, 0])
    ax_ts.plot(all_dates, all_obs,  color='#2776B4', lw=1.0, label='Observed',  zorder=3)
    ax_ts.plot(all_dates, all_pred, color='#FF7F0E', lw=1.0, ls='--', label='Predicted', zorder=3)
    ax_ts.axvspan(all_dates[0], split_date,  alpha=0.06, color='steelblue')
    ax_ts.axvspan(split_date,  all_dates[-1], alpha=0.06, color='darkorange')
    ax_ts.axvline(split_date, color='grey', lw=0.8, ls=':')
    ax_ts.set_ylabel('log₁₀ Enterococcus\n(MPN/100mL)', fontsize=8)
    ax_ts.set_xlabel('Year', fontsize=8)
    ax_ts.set_title(short, fontsize=9, fontweight='bold')
    ax_ts.legend(fontsize=6.5, loc='upper right', framealpha=0.75)
    ax_ts.tick_params(labelsize=7)
    ax_ts.yaxis.set_major_locator(plt.MaxNLocator(5))
    if i == 0:
        ax_ts.text(-0.11, 1.07, 'a.', transform=ax_ts.transAxes, fontsize=13, fontweight='bold')

    ax_r = fig.add_subplot(outer[i, 1])
    draw_radar(ax_r, res, color, short)
    if i == 0:
        ax_r.text(-0.10, 1.08, 'b.', transform=ax_r.transAxes, fontsize=13, fontweight='bold')

    ax_sc = fig.add_subplot(outer[i, 2])
    y_obs  = pred['y_te_obs']
    y_pred = pred['y_te_pred']

    ax_sc.scatter(y_obs, y_pred, s=22, color='#FFA500', alpha=0.70, edgecolors='none', zorder=3)

    lo = min(y_obs.min(), y_pred.min()) - 0.15
    hi = max(y_obs.max(), y_pred.max()) + 0.15
    ax_sc.plot([lo, hi], [lo, hi], color='#7B2D8B', ls='--', lw=1.2, label='1:1 Line', zorder=2)

    coeffs = np.polyfit(y_obs, y_pred, 1)
    x_line = np.linspace(lo, hi, 200)
    ax_sc.plot(x_line, np.polyval(coeffs, x_line), color='#2CA02C', lw=1.2,
               label='Regression Line', zorder=2)

    ax_sc.set_xlabel('Observed Enterococcus (log₁₀ MPN/100mL)', fontsize=8)
    ax_sc.set_ylabel('Predicted Enterococcus (log₁₀ MPN/100mL)', fontsize=8)
    ax_sc.legend(fontsize=6.5, loc='upper left', framealpha=0.75)
    ax_sc.tick_params(labelsize=7)
    ax_sc.text(0.04, 0.91,
               f"R² = {res['R2']:.3f}\nRMSE = {res['RMSE']:.3f}\nMAE = {res['MAE']:.3f}",
               transform=ax_sc.transAxes, fontsize=7,
               bbox=dict(boxstyle='round,pad=0.3', fc='white', alpha=0.75))
    if i == 0:
        ax_sc.text(-0.20, 1.07, 'c.', transform=ax_sc.transAxes, fontsize=13, fontweight='bold')

plt.suptitle(
    'Enterococcus Bacteria Prediction (Random Forest)\nBWB Nontidal Watershed 2013 to 2024',
    fontsize=11, fontweight='bold', y=0.982
)

OUT_FIG = '/home/user/scholarhub/enterococcus_ml_prediction.png'
plt.savefig(OUT_FIG, dpi=150, bbox_inches='tight', facecolor='white')
plt.close()


fi_name  = 'Scenario 1\n(Real-time)'
fi_model = predictions[fi_name]['model']
fi_feats = predictions[fi_name]['feats']
imps     = fi_model.feature_importances_
idx      = np.argsort(imps)[::-1][:15]

fig2, ax2 = plt.subplots(figsize=(11, 5))
bars = ax2.bar(range(15), imps[idx], color=COLORS[fi_name], alpha=0.85)
ax2.set_xticks(range(15))
ax2.set_xticklabels(
    [fi_feats[j].replace(' (mg/L)', '\n(mg/L)').replace(' (', '\n(') for j in idx],
    rotation=35, ha='right', fontsize=7.5
)
ax2.set_ylabel('Feature Importance', fontsize=9)
ax2.set_title('Top 15 Feature Importances, Scenario 1 (Real-time)', fontsize=10)
ax2.grid(axis='y', alpha=0.3)
for bar, val in zip(bars, imps[idx]):
    ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.001,
             f'{val:.3f}', ha='center', va='bottom', fontsize=6.5)
fig2.tight_layout()
fig2.savefig('/home/user/scholarhub/enterococcus_feature_importance.png',
             dpi=150, bbox_inches='tight', facecolor='white')
plt.close(fig2)


metrics_df = pd.DataFrame([
    {'Scenario': k.replace('\n', ' '), **v} for k, v in results.items()
])
metrics_df.to_csv('/home/user/scholarhub/enterococcus_ml_metrics.csv', index=False)

for name, res in results.items():
    print(f"{name.replace(chr(10), ' '):<32}  MAE={res['MAE']:.3f}  MAPE={res['MAPE']:.1f}%  RMSE={res['RMSE']:.3f}  R²={res['R2']:.3f}")
