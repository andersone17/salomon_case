"""Generate appendix deep-dive charts for the Vestal Pro readout deck.

Reproduces the main-analysis figures at a finer grain (baseline validation,
cannibalization baselines, channel economics, LTV assumption) using the same
mock data and the same deck palette as notebooks/campaign_analysis.ipynb.
PNGs are written to plots/ with an ``appendix_`` prefix.
"""
from pathlib import Path
import warnings

import numpy as np
import pandas as pd
import plotly.graph_objects as go

# --- Deck palette / typography (sampled from the readout deck) --------------
SALOMON_BLUE = "#0057B8"
BLUE_BRIGHT = "#3E8EDE"
BLUE_LIGHT = "#BFD5ED"
SALOMON_GREEN = "#1F7A4D"
SALOMON_RED = "#DA291C"
INK = "#333333"
MUTED = "#757575"
GRID = "#D9D9D9"
SURFACE = "#F5F6F7"
WHITE = "#FFFFFF"
SANS = "Arial, Helvetica, sans-serif"
SERIF = "Georgia, Times New Roman, serif"

import sys

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data" / "mock"
PLOTS_DIR = ROOT / "plots"
PLOTS_DIR.mkdir(exist_ok=True)

# Optional CLI flags:
#   --no-subtitle          drop the small gray sub-header under each chart title
#   --outdir <relpath>     write PNGs to this dir instead of plots/
_ARGV = sys.argv[1:]
NO_SUBTITLE = "--no-subtitle" in _ARGV
OUTDIR = ROOT / _ARGV[_ARGV.index("--outdir") + 1] if "--outdir" in _ARGV else PLOTS_DIR
OUTDIR.mkdir(parents=True, exist_ok=True)

# --- Analysis constants (match the notebook) --------------------------------
PRE_START = pd.Timestamp("2026-03-01")
PRE_END = pd.Timestamp("2026-05-31")
ACT_START = pd.Timestamp("2026-06-01")
ACT_END = pd.Timestamp("2026-06-20")
POST_END = pd.Timestamp("2026-07-20")
ACTIVE_DAYS = 20
EXISTING_FRANCHISES = ["Ultra Glide", "Genesis", "Speedcross"]
PAID_CHANNELS = ["Email", "SMS", "Paid Social", "Paid Search", "Affiliate"]
RNG = np.random.default_rng(7)
N_BOOT = 4000

ecommerce = pd.read_csv(DATA_DIR / "ecommerce_daily.csv", parse_dates=["date"])
products = pd.read_csv(DATA_DIR / "product_daily.csv", parse_dates=["date"])
channels = pd.read_csv(DATA_DIR / "channel_daily.csv", parse_dates=["date"])
orders = pd.read_csv(DATA_DIR / "customer_orders.csv", parse_dates=["order_date"])


def expected_baseline(frame, ycol, fit_through=PRE_END):
    """Trend + day-of-week OLS fit through ``fit_through`` (matches notebook)."""
    frame = frame.sort_values("date").reset_index(drop=True)
    X = pd.get_dummies(frame["date"].dt.dayofweek, prefix="dow", drop_first=True).astype(float)
    X.insert(0, "t", (frame["date"] - frame["date"].min()).dt.days)
    X.insert(0, "const", 1.0)
    fit = frame["date"] <= fit_through
    beta, *_ = np.linalg.lstsq(X[fit].to_numpy(), frame.loc[fit, ycol].to_numpy(), rcond=None)
    out = frame.copy()
    out["expected"] = X.to_numpy() @ beta
    resid = out.loc[fit, ycol].to_numpy() - out.loc[fit, "expected"].to_numpy()
    return out, resid


def style(fig, title, subtitle=None, *, height, width, legend=None, margin_t=92):
    fig.update_layout(
        template="plotly_white",
        font=dict(family=SANS, size=13, color=INK),
        paper_bgcolor=WHITE, plot_bgcolor=WHITE,
        title=dict(
            text=title,
            subtitle=dict(text=("" if NO_SUBTITLE else (subtitle or "")),
                          font=dict(family=SANS, size=12, color=MUTED)),
            font=dict(family=SERIF, size=19, color=INK),
            x=0, xref="paper", xanchor="left", y=0.97, yref="container", yanchor="top",
            pad=dict(b=10),
        ),
        width=width, height=height,
        margin=dict(l=64, r=30, t=(margin_t - 22 if NO_SUBTITLE else margin_t), b=52),
        hovermode="closest", bargap=0.3,
        showlegend=legend is not None,
    )
    if legend is not None:
        fig.update_layout(legend=legend)
    fig.update_xaxes(showline=True, linecolor=GRID, gridcolor=GRID, zerolinecolor=GRID,
                     ticks="outside", tickcolor=GRID, tickfont=dict(color=MUTED))
    fig.update_yaxes(showline=True, linecolor=GRID, gridcolor=GRID, zerolinecolor=GRID,
                     ticks="outside", tickcolor=GRID, tickfont=dict(color=MUTED))
    return fig


def save(fig, name, emu_w, emu_h, scale=3):
    """Export at pixel dims matching the EMU box aspect (no distortion in PPT)."""
    w = round(emu_w / 9525)
    h = round(emu_h / 9525)
    path = OUTDIR / name
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", message="Support for Kaleido versions less than 1.0.0")
        fig.write_image(path, width=w, height=h, scale=scale, format="png")
    print(f"saved {path.relative_to(ROOT)}  ({w*scale}x{h*scale}px)")


# Two-up box geometry shared across appendix slides (EMU).
BOX_W = 5_400_000
BOX_H = 4_180_000

# ============================================================================
# A1 — Baseline model validation
# ============================================================================
pre_only = ecommerce[ecommerce["date"] <= PRE_END]
backtest, _ = expected_baseline(pre_only, "footwear_revenue", fit_through=PRE_END - pd.Timedelta(days=14))
holdout = backtest[backtest["date"] > PRE_END - pd.Timedelta(days=14)].copy()
mape = (holdout["footwear_revenue"] - holdout["expected"]).abs().div(holdout["footwear_revenue"]).mean()
holdout["pct_err"] = (holdout["footwear_revenue"] - holdout["expected"]) / holdout["expected"]
fit_cut = PRE_END - pd.Timedelta(days=14)

# A1a: actual vs fitted over the pre-period, holdout shaded
fig = go.Figure()
fig.add_vrect(x0=fit_cut, x1=backtest["date"].max(), fillcolor=BLUE_LIGHT, opacity=0.28,
              line_width=0, layer="below")
fig.add_trace(go.Scatter(x=backtest["date"], y=backtest["footwear_revenue"], name="Actual",
                         mode="lines", line=dict(color=SALOMON_BLUE, width=2.2),
                         hovertemplate="%{x|%b %d}<br>Actual $%{y:,.0f}<extra></extra>"))
fig.add_trace(go.Scatter(x=backtest["date"], y=backtest["expected"], name="Model fit",
                         mode="lines", line=dict(color=MUTED, width=1.8, dash="dash"),
                         hovertemplate="%{x|%b %d}<br>Predicted $%{y:,.0f}<extra></extra>"))
fig.add_annotation(x=fit_cut + (backtest["date"].max() - fit_cut) / 2,
                   y=1.0, yref="paper", yanchor="bottom", showarrow=False,
                   text="14-DAY HOLDOUT", font=dict(size=10, color=MUTED))
fig.add_annotation(x=0.02, y=0.04, xref="paper", yref="paper", xanchor="left", yanchor="bottom",
                   text=f"Holdout MAPE <b>{mape:.1%}</b>", showarrow=False,
                   bgcolor="rgba(255,255,255,0.85)", borderpad=4,
                   font=dict(size=13, color=INK))
fig.update_yaxes(title="Daily footwear revenue", tickprefix="$", tickformat="~s", rangemode="tozero")
fig.update_xaxes(title=None)
style(fig, "Baseline backtest: actual vs predicted",
      "Trend + day-of-week fit; last 14 pre-campaign days held out",
      height=BOX_H, width=BOX_W, margin_t=104,
      legend=dict(orientation="h", x=0.01, y=1.02, xanchor="left", yanchor="bottom",
                  font=dict(color=INK)))
save(fig, "appendix_A1a_baseline_backtest.png", BOX_W, BOX_H)

# A1b: daily forecast error on the holdout
colors = [SALOMON_GREEN if abs(v) <= mape else SALOMON_BLUE for v in holdout["pct_err"]]
fig = go.Figure(go.Bar(x=holdout["date"], y=holdout["pct_err"],
                       marker=dict(color=SALOMON_BLUE), cliponaxis=False,
                       hovertemplate="%{x|%b %d}<br>Error %{y:+.1%}<extra></extra>"))
fig.add_hline(y=0, line=dict(color=INK, width=1))
fig.add_hline(y=mape, line=dict(color=MUTED, width=1.2, dash="dash"))
fig.add_hline(y=-mape, line=dict(color=MUTED, width=1.2, dash="dash"))
fig.add_annotation(x=holdout["date"].max(), y=mape, yshift=8, xanchor="right", showarrow=False,
                   text=f"±{mape:.1%} mean abs error", font=dict(size=11, color=MUTED))
fig.update_yaxes(title="Daily forecast error", tickformat="+.0%")
fig.update_xaxes(title=None)
style(fig, "Holdout forecast error by day",
      "Predicted vs actual over the 14-day holdout window",
      height=BOX_H, width=BOX_W)
save(fig, "appendix_A1b_holdout_error.png", BOX_W, BOX_H)

# ============================================================================
# A2 — Cannibalization: three baseline methods
# ============================================================================
vestal = products[products["franchise"] == "Vestal Pro"]
vestal_units = vestal[vestal["campaign_phase"] == "Active campaign"]["units_sold"].sum()


def unit_baselines(franchise):
    frame = products[products["franchise"] == franchise]
    pre = frame[frame["campaign_phase"] == "Pre-campaign"]
    active_units = frame[frame["campaign_phase"] == "Active campaign"]["units_sold"].sum()
    trend_frame, _ = expected_baseline(frame, "units_sold")
    return {
        "observed": active_units,
        "flat": pre["units_sold"].mean() * ACTIVE_DAYS,
        "recent": pre[pre["date"] > PRE_END - pd.Timedelta(days=28)]["units_sold"].mean() * ACTIVE_DAYS,
        "trend": trend_frame[trend_frame["campaign_phase"] == "Active campaign"]["expected"].sum(),
    }


specs = {fr: unit_baselines(fr) for fr in EXISTING_FRANCHISES}
spec_names = ["flat", "recent", "trend"]
spec_labels = {"flat": "Flat pre-avg", "recent": "Recent 4-wk", "trend": "Trend model"}
spec_colors = {"flat": BLUE_LIGHT, "recent": BLUE_BRIGHT, "trend": SALOMON_BLUE}

rates = {}
for spec in spec_names:
    displaced = sum(max(specs[fr][spec] - specs[fr]["observed"], 0) for fr in ["Genesis", "Ultra Glide"])
    gained = max(specs["Speedcross"]["observed"] - specs["Speedcross"][spec], 0)
    rates[spec] = (displaced - gained) / vestal_units

# A2a: per-franchise unit change under each baseline
fig = go.Figure()
for spec in spec_names:
    fig.add_trace(go.Bar(
        name=spec_labels[spec], x=EXISTING_FRANCHISES,
        y=[specs[fr]["observed"] / specs[fr][spec] - 1 for fr in EXISTING_FRANCHISES],
        marker_color=spec_colors[spec],
        hovertemplate="%{x}<br>" + spec_labels[spec] + ": %{y:+.1%}<extra></extra>",
    ))
fig.add_hline(y=0, line=dict(color=INK, width=1))
fig.update_yaxes(title="Campaign units vs baseline", tickformat="+.0%")
fig.update_xaxes(title=None, tickfont=dict(color=INK, size=13))
style(fig, "Existing-shoe unit change by baseline",
      "Each shoe under all three baseline methods",
      height=BOX_H, width=BOX_W, margin_t=104,
      legend=dict(orientation="h", x=0.01, y=1.02, xanchor="left", yanchor="bottom",
                  font=dict(color=INK)))
fig.update_layout(barmode="group")
save(fig, "appendix_A2a_franchise_by_baseline.png", BOX_W, BOX_H)

# A2b: overall cannibalization rate under each baseline vs guardrail
bar_colors = [spec_colors[s] for s in spec_names]
fig = go.Figure(go.Bar(
    x=[spec_labels[s] for s in spec_names], y=[rates[s] for s in spec_names],
    marker=dict(color=bar_colors), cliponaxis=False,
    text=[f"<b>{rates[s]:.0%}</b>" for s in spec_names], textposition="outside",
    textfont=dict(color=INK, size=14),
    hovertemplate="%{x}<br>Cannibalization %{y:.0%}<extra></extra>",
))
fig.add_hline(y=0.10, line=dict(color=SALOMON_RED, width=1.5, dash="dash"))
fig.add_annotation(x=2.4, y=0.10, yshift=9, xanchor="right", showarrow=False,
                   text="Guardrail 10%", font=dict(size=11, color=SALOMON_RED))
fig.update_yaxes(title="Share of Vestal Pro units", tickformat=".0%",
                 range=[0, max(rates.values()) * 1.25])
fig.update_xaxes(title=None, tickfont=dict(color=INK, size=13))
style(fig, "Cannibalization rate by baseline method",
      "All three estimates exceed the 10% guardrail",
      height=BOX_H, width=BOX_W)
save(fig, "appendix_A2b_rate_by_baseline.png", BOX_W, BOX_H)

# ============================================================================
# A3 — Channel economics
# ============================================================================
active_net = expected_baseline(ecommerce, "net_revenue")[0]
active_net = active_net[active_net["campaign_phase"] == "Active campaign"]
incremental_net = active_net["net_revenue"].sum() - active_net["expected"].sum()

active_channels = channels[channels["campaign_phase"] == "Active campaign"]
paid_summary = (active_channels[active_channels["channel"].isin(PAID_CHANNELS)]
                .groupby("channel")
                .agg(spend=("spend", "sum"), attributed=("attributed_revenue", "sum"),
                     new_customers=("new_customers", "sum")))
incrementality_factor = incremental_net / paid_summary["attributed"].sum()
paid_summary["roas"] = paid_summary["attributed"] / paid_summary["spend"]
paid_summary["iroas"] = paid_summary["roas"] * incrementality_factor
paid_summary["cac_new"] = paid_summary["spend"] / paid_summary["new_customers"]
paid_summary = paid_summary.sort_values("iroas", ascending=False)
chan_order = list(paid_summary.index)

# A3a: attributed ROAS vs incremental ROAS
fig = go.Figure()
fig.add_trace(go.Bar(name="Attributed ROAS", x=chan_order, y=paid_summary["roas"],
                     marker_color=BLUE_LIGHT,
                     text=[f"{v:.1f}×" for v in paid_summary["roas"]], textposition="outside",
                     textfont=dict(color=MUTED, size=11), cliponaxis=False,
                     hovertemplate="%{x}<br>Attributed %{y:.1f}×<extra></extra>"))
fig.add_trace(go.Bar(name="Incremental ROAS", x=chan_order, y=paid_summary["iroas"],
                     marker_color=SALOMON_BLUE,
                     text=[f"<b>{v:.1f}×</b>" for v in paid_summary["iroas"]], textposition="outside",
                     textfont=dict(color=INK, size=11), cliponaxis=False,
                     hovertemplate="%{x}<br>Incremental %{y:.2f}×<extra></extra>"))
fig.add_hline(y=1, line=dict(color=MUTED, width=1.2, dash="dash"))
fig.add_annotation(x=4.4, y=1, yshift=8, xanchor="right", showarrow=False,
                   text="Breakeven 1.0×", font=dict(size=11, color=MUTED))
fig.update_yaxes(title="Return on ad spend", ticksuffix="×", type="log",
                 tickvals=[0.3, 1, 3, 10, 30])
fig.update_xaxes(title=None, tickfont=dict(color=INK, size=12))
style(fig, "Attributed vs incremental ROAS",
      f"Incremental = attributed × {incrementality_factor:.2f} site factor · log scale",
      height=BOX_H, width=BOX_W, margin_t=104,
      legend=dict(orientation="h", x=0.01, y=1.02, xanchor="left", yanchor="bottom",
                  font=dict(color=INK)))
fig.update_layout(barmode="group")
save(fig, "appendix_A3a_roas_vs_iroas.png", BOX_W, BOX_H)

# A3b: new customers (bars) and CAC (markers, secondary axis)
by_new = paid_summary.sort_values("new_customers", ascending=False)
fig = go.Figure()
fig.add_trace(go.Bar(x=list(by_new.index), y=by_new["new_customers"], name="New customers",
                     marker_color=SALOMON_BLUE, yaxis="y",
                     text=[f"{int(v)}" for v in by_new["new_customers"]], textposition="outside",
                     textfont=dict(color=INK, size=12), cliponaxis=False,
                     hovertemplate="%{x}<br>%{y} new customers<extra></extra>"))
fig.add_trace(go.Scatter(x=list(by_new.index), y=by_new["cac_new"], name="CAC (new)",
                         mode="markers+text", yaxis="y2",
                         marker=dict(color=SALOMON_RED, size=11, symbol="diamond"),
                         text=[f"${v:,.0f}" for v in by_new["cac_new"]], textposition="top center",
                         textfont=dict(color=SALOMON_RED, size=11),
                         hovertemplate="%{x}<br>CAC $%{y:,.0f}<extra></extra>"))
# Decouple the two axis ranges so bar-top counts and CAC diamonds never collide:
# bars occupy the upper band, diamonds the lower band.
fig.update_yaxes(title="New customers acquired", range=[0, by_new["new_customers"].max() * 1.18])
fig.update_layout(yaxis2=dict(title=dict(text="CAC (new)", font=dict(color=SALOMON_RED)),
                              overlaying="y", side="right", tickprefix="$",
                              tickfont=dict(color=SALOMON_RED), showgrid=False,
                              range=[0, by_new["cac_new"].max() * 1.9]))
fig.update_xaxes(title=None, tickfont=dict(color=INK, size=12))
style(fig, "New customers vs cost to acquire",
      "Paid Social drives the most new customers at the highest CAC",
      height=BOX_H, width=BOX_W, margin_t=104,
      legend=dict(orientation="h", x=0.01, y=1.02, xanchor="left", yanchor="bottom",
                  font=dict(color=INK)))
save(fig, "appendix_A3b_new_customers_cac.png", BOX_W, BOX_H)

# ============================================================================
# A4 — New-customer LTV projection and its assumption
# ============================================================================
paid = channels[channels["channel"].isin(PAID_CHANNELS)]
active_spend = paid[paid["campaign_phase"] == "Active campaign"]["spend"].sum()
active_orders = orders[orders["campaign_phase"] == "Active campaign"]
new_ids = set(active_orders.loc[active_orders["customer_type"] == "New", "customer_id"])
first_orders = (active_orders[active_orders["customer_type"] == "New"]
                .sort_values(["order_date", "order_id"])
                .groupby("customer_id")["total_order_revenue"].first())
early_value = orders[orders["customer_id"].isin(new_ids)].groupby("customer_id")["total_order_revenue"].sum()
blended_cac = active_spend / len(new_ids)
first_order_new = first_orders.mean()
observed_value = early_value.mean()

CLV_HORIZON_M = 24
CLV_TAU = 9.0
month = np.arange(0, CLV_HORIZON_M + 1)


def clv_curve(mult_target):
    mult = 1 + (mult_target - 1) * (1 - np.exp(-month / CLV_TAU)) / (1 - np.exp(-CLV_HORIZON_M / CLV_TAU))
    return first_order_new * mult


clv = clv_curve(3.0)
clv_24m = clv[-1]

# A4a: projected cumulative value curve
fig = go.Figure()
fig.add_trace(go.Scatter(x=month, y=clv, mode="lines", name="Projected value",
                         line=dict(color=SALOMON_BLUE, width=2.6),
                         hovertemplate="Month %{x}<br>$%{y:,.0f}<extra></extra>"))
fig.add_hline(y=blended_cac, line=dict(color=MUTED, width=1.5, dash="dash"))
fig.add_annotation(x=CLV_HORIZON_M, y=blended_cac, yshift=-12, xanchor="right", showarrow=False,
                   text=f"Blended CAC ${blended_cac:,.0f}", font=dict(size=11, color=MUTED))
fig.add_trace(go.Scatter(x=[0], y=[first_order_new], mode="markers+text", showlegend=False,
                         marker=dict(color=SALOMON_BLUE, size=10),
                         text=[f"First order ${first_order_new:,.0f}"], textposition="top right",
                         textfont=dict(size=11, color=INK)))
fig.add_trace(go.Scatter(x=[1.3], y=[observed_value], mode="markers+text", showlegend=False,
                         marker=dict(color=SALOMON_GREEN, size=11, symbol="diamond"),
                         text=[f"  Observed to date ${observed_value:,.0f}"], textposition="middle right",
                         textfont=dict(size=11, color=SALOMON_GREEN)))
fig.add_annotation(x=CLV_HORIZON_M, y=clv_24m, yshift=14, xanchor="right", showarrow=False,
                   text=f"<b>${clv_24m:,.0f}</b> · 3.0× first order", font=dict(size=12, color=SALOMON_BLUE))
fig.update_xaxes(title="Months since first purchase", dtick=6, range=[-0.6, CLV_HORIZON_M + 0.6])
fig.update_yaxes(title="Cumulative value per new customer", tickprefix="$", rangemode="tozero")
style(fig, "Projected new-customer lifetime value",
      "Front-loaded curve to a 3.0× first-order return over 24 months",
      height=BOX_H, width=BOX_W)
save(fig, "appendix_A4a_ltv_curve.png", BOX_W, BOX_H)

# A4b: 24-month value under different return-multiple assumptions
mults = [2.5, 3.0, 3.5]
vals = [clv_curve(m)[-1] for m in mults]
mcolors = [BLUE_LIGHT, SALOMON_BLUE, BLUE_BRIGHT]
fig = go.Figure(go.Bar(
    x=[f"{m:.1f}× return" for m in mults], y=vals, marker_color=mcolors, cliponaxis=False,
    text=[f"<b>${v:,.0f}</b><br>{v/blended_cac:.1f}× CAC" for v in vals], textposition="outside",
    textfont=dict(color=INK, size=12),
    hovertemplate="%{x}<br>24-mo value $%{y:,.0f}<extra></extra>",
))
fig.add_hline(y=blended_cac, line=dict(color=SALOMON_RED, width=1.5, dash="dash"))
fig.add_annotation(x=2.45, y=blended_cac, yshift=9, xanchor="right", showarrow=False,
                   text=f"CAC ${blended_cac:,.0f}", font=dict(size=11, color=SALOMON_RED))
fig.update_yaxes(title="24-month value per new customer", tickprefix="$",
                 range=[0, max(vals) * 1.25])
fig.update_xaxes(title=None, tickfont=dict(color=INK, size=13))
style(fig, "Sensitivity to the return-multiple assumption",
      "Every scenario clears CAC; base case is 3.0×",
      height=BOX_H, width=BOX_W)
save(fig, "appendix_A4b_ltv_sensitivity.png", BOX_W, BOX_H)

# ============================================================================
# A5 — Inventory & unmet demand
# ============================================================================
vp_flight = products[(products["franchise"] == "Vestal Pro") & (products["date"] >= ACT_START)].copy()
vp_flight["week"] = (vp_flight["date"] - ACT_START).dt.days // 7 + 1
wk = vp_flight[vp_flight["week"] <= 7].groupby("week").agg(
    core_avail=("core_size_availability", "mean"), in_stock=("in_stock_rate", "mean"),
    sessions=("sessions", "sum"), units=("units_sold", "sum"), revenue=("net_revenue", "sum"))
campaign_st = wk.loc[1:3, "units"].sum() / wk.loc[1:3, "sessions"].sum()
asp_flight = wk["revenue"].sum() / wk["units"].sum()
wk["modeled_units"] = campaign_st * wk["sessions"]
late = wk.loc[4:]
unmet_units = late["modeled_units"].sum() - late["units"].sum()
unmet_revenue = unmet_units * asp_flight
wk_lbl = [f"Wk {w}" for w in wk.index]

# A5a: weekly availability
fig = go.Figure()
fig.add_trace(go.Scatter(x=wk_lbl, y=wk["in_stock"], name="Overall in-stock rate", mode="lines",
                         line=dict(color=MUTED, width=2.2),
                         hovertemplate="%{x}<br>In-stock %{y:.0%}<extra></extra>"))
fig.add_trace(go.Scatter(x=wk_lbl, y=wk["core_avail"], name="Core-size availability",
                         mode="lines+markers+text", line=dict(color=SALOMON_BLUE, width=2.8),
                         marker=dict(size=7), text=[f"{v:.0%}" for v in wk["core_avail"]],
                         textposition="bottom center", textfont=dict(color=SALOMON_BLUE, size=11),
                         cliponaxis=False, hovertemplate="%{x}<br>Core sizes %{y:.0%}<extra></extra>"))
fig.add_hline(y=0.9, line=dict(color=SALOMON_GREEN, width=1.3, dash="dash"))
fig.add_annotation(x=0.02, y=0.905, xref="paper", yref="y", text="90% HEALTHY", showarrow=False,
                   xanchor="left", yanchor="bottom", font=dict(size=10, color=SALOMON_GREEN))
fig.add_vline(x=2.5, line=dict(color=MUTED, width=1))
fig.add_annotation(x=2.5, y=1.0, xref="x", yref="y", text="CAMPAIGN ENDS", showarrow=False,
                   xanchor="left", font=dict(size=10, color=MUTED))
fig.update_yaxes(title=None, tickformat=".0%", range=[0.38, 1.06])
fig.update_xaxes(title=None, showgrid=False, tickfont=dict(color=INK, size=12))
style(fig, "Vestal Pro availability by week",
      "Core sizes fell below healthy within the campaign and kept sliding",
      height=BOX_H, width=BOX_W, margin_t=104,
      legend=dict(orientation="h", x=0.01, y=1.02, xanchor="left", yanchor="bottom", font=dict(color=INK)))
save(fig, "appendix_A5a_availability_weekly.png", BOX_W, BOX_H)

# A5b: actual vs modeled units (gap = unmet demand)
colors_a = [SALOMON_BLUE if w <= 3 else BLUE_LIGHT for w in wk.index]
fig = go.Figure()
fig.add_trace(go.Bar(x=wk_lbl, y=wk["units"], name="Actual units", marker_color=colors_a,
                     hovertemplate="%{x}<br>Actual %{y:,.0f} units<extra></extra>"))
fig.add_trace(go.Scatter(x=wk_lbl, y=wk["modeled_units"], name="Demand at campaign conversion",
                         mode="lines+markers", line=dict(color=SALOMON_RED, width=2.4, dash="dash"),
                         marker=dict(size=6),
                         hovertemplate="%{x}<br>Modeled %{y:,.0f} units<extra></extra>"))
fig.add_annotation(x=5, y=wk["modeled_units"].max() * 0.97, xref="x", yref="y", showarrow=False,
                   text=f"<b>Weeks 4-7 gap ≈{unmet_units:.0f} units · ≈${unmet_revenue/1e3:,.1f}K</b>",
                   font=dict(size=12, color=INK), bgcolor="rgba(255,255,255,0.85)", borderpad=3)
fig.update_yaxes(title="Vestal Pro units", rangemode="tozero")
fig.update_xaxes(title=None, showgrid=False, tickfont=dict(color=INK, size=12))
style(fig, "Demand left on the table after week 3",
      "Held campaign-period conversion against later PDP traffic",
      height=BOX_H, width=BOX_W, margin_t=104,
      legend=dict(orientation="h", x=0.01, y=1.02, xanchor="left", yanchor="bottom", font=dict(color=INK)))
save(fig, "appendix_A5b_unmet_demand.png", BOX_W, BOX_H)

# ============================================================================
# A6 — Returns & service quality
# ============================================================================
services = pd.read_csv(DATA_DIR / "consumer_services.csv", parse_dates=["contact_date"])
FR_ORDER = ["Vestal Pro", "Ultra Glide", "Genesis", "Speedcross", "Trail Apparel", "Trail Accessories"]
rr = orders.groupby("primary_product")["returned"].mean().reindex(FR_ORDER)
site_rr = orders["returned"].mean()

# A6a: return rate by franchise
rr_colors = [SALOMON_RED if fr == "Vestal Pro" else BLUE_LIGHT for fr in rr.index]
fig = go.Figure(go.Bar(x=rr.values, y=rr.index, orientation="h", marker_color=rr_colors,
                       text=[f"{v:.1%}" for v in rr.values], textposition="outside",
                       textfont=dict(color=INK, size=12), cliponaxis=False,
                       hovertemplate="%{y}<br>Return rate %{x:.1%}<extra></extra>"))
fig.add_vline(x=site_rr, line=dict(color=INK, width=1.3, dash="dash"))
fig.add_annotation(x=site_rr, y=5.4, yref="y", text=f"Site avg {site_rr:.1%}", showarrow=False,
                   xanchor="left", xshift=4, font=dict(size=11, color=INK))
fig.update_yaxes(autorange="reversed", title=None, showgrid=False, tickfont=dict(color=INK, size=12))
fig.update_xaxes(title="Order return rate", tickformat=".0%", range=[0, rr.max() * 1.22])
style(fig, "Return rate by product line",
      "Vestal Pro returns run well above the rest of the range",
      height=BOX_H, width=BOX_W)
save(fig, "appendix_A6a_return_by_franchise.png", BOX_W, BOX_H)

# A6b: service contact reasons, pre vs campaign per-day
DAYS = {"Pre-campaign": 92, "Active campaign": ACTIVE_DAYS}
reasons = (services[services["campaign_phase"].isin(DAYS)]
           .groupby(["contact_reason", "campaign_phase"]).size().unstack(fill_value=0))
reasons["pre"] = reasons.get("Pre-campaign", 0) / 92
reasons["act"] = reasons.get("Active campaign", 0) / ACTIVE_DAYS
reasons = reasons.sort_values("act", ascending=True)
fig = go.Figure()
fig.add_trace(go.Bar(y=reasons.index, x=reasons["pre"], name="Pre-campaign / day", orientation="h",
                     marker_color=BLUE_LIGHT, hovertemplate="%{y}<br>Pre %{x:.1f}/day<extra></extra>"))
fig.add_trace(go.Bar(y=reasons.index, x=reasons["act"], name="Campaign / day", orientation="h",
                     marker_color=SALOMON_BLUE, hovertemplate="%{y}<br>Campaign %{x:.1f}/day<extra></extra>"))
fig.update_layout(barmode="group")
fig.update_xaxes(title="Service contacts per day", rangemode="tozero")
fig.update_yaxes(title=None, tickfont=dict(color=INK, size=11))
style(fig, "Service contacts by reason",
      "Sizing & fit lead the rise; product defects stay near zero",
      height=BOX_H, width=BOX_W, margin_t=104,
      legend=dict(orientation="h", x=0.01, y=1.02, xanchor="left", yanchor="bottom", font=dict(color=INK)))
save(fig, "appendix_A6b_contact_reasons.png", BOX_W, BOX_H)

# ============================================================================
# A7 — Incrementality reconciliation bridge
# ============================================================================
vestal_direct = products[(products["franchise"] == "Vestal Pro") &
                         (products["campaign_phase"] == "Active campaign")]["net_revenue"].sum()
franchise_shift = 0.0
for fr in EXISTING_FRANCHISES:
    frame, _ = expected_baseline(products[products["franchise"] == fr], "net_revenue")
    act = frame[frame["campaign_phase"] == "Active campaign"]
    franchise_shift += -(act["net_revenue"].sum() - act["expected"].sum())
adj, _ = expected_baseline(ecommerce, "adjacent_category_revenue")
adj_act = adj[adj["campaign_phase"] == "Active campaign"]
halo_revenue = adj_act["adjacent_category_revenue"].sum() - adj_act["expected"].sum()
bottom_up = vestal_direct - franchise_shift + halo_revenue

# A7a: waterfall
fig = go.Figure(go.Waterfall(
    orientation="v", measure=["relative", "relative", "relative", "total"],
    x=["Vestal Pro<br>direct", "Cannibalization", "Halo", "Net<br>incremental"],
    y=[vestal_direct, -franchise_shift, halo_revenue, None],
    text=[f"+${vestal_direct/1e3:,.1f}K", f"-${franchise_shift/1e3:,.1f}K",
          f"+${halo_revenue/1e3:,.1f}K", f"${bottom_up/1e3:,.1f}K"],
    textposition="outside", textfont=dict(color=INK, size=12), cliponaxis=False,
    connector=dict(line=dict(color=GRID, width=1)),
    increasing=dict(marker=dict(color=SALOMON_BLUE)),
    decreasing=dict(marker=dict(color=SALOMON_RED)),
    totals=dict(marker=dict(color=INK)),
))
fig.update_yaxes(title="Revenue", tickprefix="$", tickformat="~s", rangemode="tozero")
fig.update_xaxes(title=None, tickfont=dict(color=INK, size=11))
style(fig, "Product-level build-up of net incremental revenue",
      "Direct sales, minus cannibalization, plus halo",
      height=BOX_H, width=BOX_W)
save(fig, "appendix_A7a_reconciliation_waterfall.png", BOX_W, BOX_H)

# A7b: two independent methods agree
diff = abs(bottom_up - incremental_net)
fig = go.Figure(go.Bar(
    x=["Product build-up<br>(direct − cannib. + halo)", "Site-level<br>(total revenue vs baseline)"],
    y=[bottom_up, incremental_net], marker_color=[SALOMON_BLUE, BLUE_BRIGHT], cliponaxis=False,
    text=[f"<b>${bottom_up/1e3:,.1f}K</b>", f"<b>${incremental_net/1e3:,.1f}K</b>"],
    textposition="outside", textfont=dict(color=INK, size=14),
    hovertemplate="%{x}<br>$%{y:,.0f}<extra></extra>", width=0.5,
))
fig.add_annotation(x=0.5, y=max(bottom_up, incremental_net) * 1.12, xref="x", yref="y", showarrow=False,
                   text=f"Two independent methods agree within ${diff/1e3:,.1f}K",
                   font=dict(size=12, color=SALOMON_GREEN))
fig.update_yaxes(title="Net incremental revenue", tickprefix="$", tickformat="~s",
                 range=[0, max(bottom_up, incremental_net) * 1.28])
fig.update_xaxes(title=None, tickfont=dict(color=INK, size=11))
style(fig, "Two estimates of the same number",
      "Cross-check on the headline incrementality figure",
      height=BOX_H, width=BOX_W)
save(fig, "appendix_A7b_two_methods.png", BOX_W, BOX_H)

# ============================================================================
# A8 — Brand-search persistence
# ============================================================================
search = pd.read_csv(DATA_DIR / "search_console_daily.csv", parse_dates=["date"])
search = search.sort_values("date")
search["brand_7d"] = search["brand_clicks"].rolling(7, min_periods=1).mean()
search["nonbrand_7d"] = search["nonbrand_clicks"].rolling(7, min_periods=1).mean()
phase_clicks = search.groupby("campaign_phase")["brand_clicks"].mean()
pre_b = phase_clicks["Pre-campaign"]; act_b = phase_clicks["Active campaign"]; post_b = phase_clicks["Post-campaign"]

# A8a: brand vs non-brand clicks over time
fig = go.Figure()
fig.add_vrect(x0=ACT_START, x1=ACT_END, fillcolor=BLUE_LIGHT, opacity=0.28, line_width=0, layer="below")
fig.add_annotation(x=ACT_START + (ACT_END - ACT_START) / 2, y=1.0, yref="paper", yanchor="bottom",
                   text="CAMPAIGN", showarrow=False, font=dict(size=10, color=MUTED))
fig.add_trace(go.Scatter(x=search["date"], y=search["brand_7d"], name="Branded", mode="lines",
                         line=dict(color=SALOMON_BLUE, width=2.6),
                         hovertemplate="%{x|%b %d}<br>Brand %{y:,.0f}<extra></extra>"))
fig.add_trace(go.Scatter(x=search["date"], y=search["nonbrand_7d"], name="Non-brand", mode="lines",
                         line=dict(color="#000000", width=2),
                         hovertemplate="%{x|%b %d}<br>Non-brand %{y:,.0f}<extra></extra>"))
fig.update_yaxes(title="Search clicks per day (7-day avg)", rangemode="tozero", tickformat="~s")
fig.update_xaxes(title=None)
style(fig, "Branded vs non-brand search demand",
      "Branded demand steps up and holds after media stops",
      height=BOX_H, width=BOX_W, margin_t=104,
      legend=dict(orientation="h", x=0.01, y=1.02, xanchor="left", yanchor="bottom", font=dict(color=INK)))
save(fig, "appendix_A8a_brand_search_trend.png", BOX_W, BOX_H)

# A8b: brand clicks/day by phase
phases = ["Pre-campaign", "Active campaign", "Post-campaign"]
vals = [pre_b, act_b, post_b]
labs = ["", f"+{act_b/pre_b-1:.0%} vs pre", f"+{post_b/pre_b-1:.0%} vs pre"]
fig = go.Figure(go.Bar(
    x=["Pre", "Campaign", "Post"], y=vals, marker_color=[BLUE_LIGHT, SALOMON_BLUE, SALOMON_BLUE],
    text=[f"<b>{v:,.0f}</b><br>{l}" if l else f"<b>{v:,.0f}</b>" for v, l in zip(vals, labs)],
    textposition="outside", textfont=dict(color=INK, size=13), cliponaxis=False,
    hovertemplate="%{x}<br>%{y:,.0f} brand clicks/day<extra></extra>", width=0.6,
))
fig.update_yaxes(title="Branded clicks per day", rangemode="tozero", range=[0, max(vals) * 1.25])
fig.update_xaxes(title=None, tickfont=dict(color=INK, size=13))
style(fig, "Branded search clicks by phase",
      "The post-campaign level stays above the campaign itself",
      height=BOX_H, width=BOX_W)
save(fig, "appendix_A8b_brand_by_phase.png", BOX_W, BOX_H)

# ============================================================================
# A9 — Assumptions & sensitivity register (single wide table)
# ============================================================================
rows = [
    ["Baseline model", "Trend + day-of-week OLS, fit on pre-period",
     "Backtest MAPE 8.0% on 14-day holdout", "Drives every incremental figure in the deck"],
    ["Site incrementality factor", "0.34, applied to all channels",
     "77.5K incremental ÷ 231K attributed rev.", "Per-channel holdout would reallocate channel credit"],
    ["Contribution margin", "60% on incremental revenue",
     "Assumed — no COGS in the data", "CM3 scales ~linearly; swings the profit read, not revenue"],
    ["New-customer LTV", "3.0× first order over 24 months",
     "Prior cohort analysis; not yet measured", "2.5×–3.5× → 323–452 per customer, all clear CAC"],
    ["Cannibalization guardrail", "< 10% of Vestal Pro sales",
     "Stakeholder-set threshold", "Result 19–32% flags under any reasonable threshold"],
    ["Returns maturity", "Post-campaign window still open",
     "Recent returns still landing", "Could raise return rate and trim net revenue"],
]
header = ["Assumption", "Value used", "Basis", "If it moves"]
cols = list(zip(*rows))
row_fill = [SURFACE if i % 2 else WHITE for i in range(len(rows))]
TBL_W, TBL_H = 11_186_160, 3_450_000
fig = go.Figure(go.Table(
    columnwidth=[1.15, 1.5, 1.6, 2.0],
    header=dict(values=[f"<b>{h}</b>" for h in header], fill_color=SALOMON_BLUE,
                font=dict(color=WHITE, size=13), align="left", height=40, line_color=SALOMON_BLUE),
    cells=dict(values=[list(c) for c in cols], fill_color=[row_fill] * 4,
               font=dict(color=INK, size=12), align="left", height=44, line_color=GRID),
))
fig.update_layout(template="plotly_white", paper_bgcolor=WHITE, plot_bgcolor=WHITE,
                  margin=dict(l=0, r=0, t=0, b=0),
                  width=round(TBL_W / 9525), height=round(TBL_H / 9525))
save(fig, "appendix_A9_assumptions_register.png", TBL_W, TBL_H)

print("\nReconciliation checks:")
print(f"  MAPE (holdout)                 = {mape:.1%}  (deck: 8.0%)")
print(f"  Cannibalization rates          = " + ", ".join(f"{s} {rates[s]:.0%}" for s in spec_names))
print(f"  Incrementality factor          = {incrementality_factor:.2f}  (deck: 0.34)")
print(f"  Blended CAC                    = ${blended_cac:,.0f}  (deck: $102)")
print(f"  24-mo LTV @3.0x                = ${clv_24m:,.0f}  (deck: $387)")
print(f"  Unmet demand wks 4-7           = {unmet_units:.0f} units / ${unmet_revenue/1e3:,.1f}K")
print(f"  Vestal Pro return rate         = {rr['Vestal Pro']:.1%}  (deck: ~15%)")
print(f"  Reconciliation: bottom-up ${bottom_up/1e3:,.1f}K vs site ${incremental_net/1e3:,.1f}K "
      f"(diff ${abs(bottom_up-incremental_net)/1e3:,.1f}K)")
print(f"  Brand clicks/day               = {pre_b:,.0f} pre / {act_b:,.0f} campaign / {post_b:,.0f} post")
