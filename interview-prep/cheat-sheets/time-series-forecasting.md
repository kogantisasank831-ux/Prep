---
layout: "week"
status: "approved"
version: "1.0.0"
last_reviewed: "2026-11-10"
header_context: "Interview preparation"
back_label: "Interview prep"
back_url: "/interview-prep/"
toc_heading: "Interview sections"
pagination_label: "Interview prep hub"
pagination_url: "/interview-prep/"
title: "Time series and forecasting interview cheat sheet"
description: "Forecasting contracts, temporal audits, baselines, ETS, ARIMA, lagged ML, global and foundation models, rolling-origin evaluation, metrics, uncertainty, hierarchy, and production."
summary: "Revise forecast-origin correctness, model and baseline choices, horizon-aware backtests, probabilistic decisions, special demand patterns, and production operations."
permalink: "/interview-prep/cheat-sheets/time-series-forecasting/"
kicker_primary: "Interview preparation"
kicker_secondary: "Batch 8 · Time series and forecasting"
current_label: "Revision guide"
alternate_label: "Interview prep hub"
alternate_url: "/interview-prep/"
---
> **Batch 8 source:** This page integrates the prepared `27_Time_Series_Forecasting_Interview_Cheat_Sheet.md` artifact in the Prep site. It is separate from the Week 1–20 learning assessments.

**Target roles:** Data Scientist, Lead Data Scientist, Applied Scientist, ML Engineer, Forecasting Scientist  
**Use:** statistical modeling, demand/capacity forecasting, temporal ML, system-design, and leadership interviews  
**Interview rule:** define the forecast origin, horizon, information set, decision, and evaluation simulation before naming ARIMA, boosting, a transformer, or a foundation model.

## 1. Thirty-second revision

- Specify target, frequency, horizon, lead time, decision, series granularity, known-future covariates, forecast cadence, and cost of over/under prediction.
- Keep naive, seasonal-naive, and domain baselines. A complex model must beat them across relevant horizons and series.
- Time order is part of the data-generating process. Use rolling-origin evaluation; never shuffle ordinary forecasting rows.
- A lag is safe only when it was available at the forecast origin. Forecasted weather is different from realized future weather.
- Separate local models per series from global models trained across many series.
- Use ETS for evolving level/trend/seasonality; ARIMA/SARIMAX for autocorrelation/differencing and exogenous structure; boosting for nonlinear lag/covariate relationships.
- Deep/global models can share information across series; time-series foundation models are candidates, not automatic winners. Benchmark accuracy, calibration, latency, memory, license, and adaptation.
- Evaluate per horizon, series, segment, and business weight. MAPE fails near zero; RMSE emphasizes large errors; MASE supports cross-series comparison.
- Point forecasts are incomplete when decisions need uncertainty. Evaluate interval/quantile coverage and sharpness.
- Intermittent demand, hierarchy, censoring, stockouts, structural breaks, and regime changes require explicit treatment.
- Monitor data timeliness, bias, residuals, interval coverage, business cost, and forecast value add—not only average error.
- Retraining on corrupted or unrepresentative recent data can make a model worse; distinguish model staleness from pipeline failure and regime change.

## 2. Forecasting contract

Write:

> At forecast origin `t`, using information available by `t`, predict target `y` for horizons `t+1 … t+H` at frequency `f` so that decision-maker `D` can take action `A` under asymmetric cost and operational constraints.

Record:

- target semantics and unit;
- stock versus flow measurement;
- entity/series identifiers and hierarchy;
- timestamp, timezone, calendar, and sampling interval;
- forecast origin, horizon, lead time, and update frequency;
- history/context length;
- static, observed-past, and known-future covariates;
- point, quantile, distribution, or scenario output;
- decision loss, capacity limits, and guardrails;
- retraining and publication cadence.

Do not train on realized covariates that will be unknown at prediction time. If weather or price must itself be forecast, evaluate the end-to-end information set rather than using perfect future values.

## 3. Temporal data audit

Check:

- duplicate timestamps and overlapping records;
- expected interval, gaps, and irregular sampling;
- timezone, daylight-saving transitions, and local holidays;
- late arrivals, corrections, backfills, and revisions;
- unit/currency changes and sensor recalibration;
- censoring and stockouts: observed sales may be lower than latent demand;
- zeros versus missing versus not applicable;
- series births/deaths and changing identifiers;
- outliers, outages, promotions, strikes, and one-off events;
- aggregation consistency across product, store, region, and total.

Keep an “as known then” snapshot for backtesting. Reconstructing history from a corrected latest table can overstate real-time performance.

## 4. Components and diagnostics

- **Level:** current central magnitude.
- **Trend:** long-run direction, possibly damped.
- **Seasonality:** repeating pattern with known/estimated period.
- **Cycle:** longer, less fixed oscillation.
- **Autocorrelation:** dependence between observations at different lags.
- **Structural break:** persistent change in level, trend, variance, or relationship.
- **Noise/innovation:** unpredictable component under the model.

Use plots, seasonal subseries, decomposition, ACF/PACF, residuals, missingness, and change-point diagnostics as evidence—not a mechanical model-selection oracle.

Stationarity means distributional properties used by the model remain stable. Differencing can remove trend/seasonal dependence:

$$
\nabla y_t = y_t-y_{t-1}
\nabla_m y_t = y_t-y_{t-m}
$$

Over-differencing increases noise and damages long-run information. Logs/Box–Cox can stabilize variance and enforce positivity, but back-transformation may require bias adjustment.

## 5. Baselines first

| Baseline | Forecast | Good for |
|---|---|---|
| Mean | historical mean | stationary level |
| Naive | `ŷ_(T+h) = y_T` | random-walk-like series |
| Seasonal naive | `ŷ_(T+h) = y_(T+h−m)` | strong stable seasonality |
| Drift | extend average historical slope | trending series |
| Moving average | recent-window mean | smooth local level |
| Domain rule | operational planning rule | business comparison and fallback |

Report model improvement over the relevant baseline by horizon and business segment. Forecast value add can be more actionable than a standalone error score.

## 6. Classical statistical models

### Exponential smoothing / ETS

Updates level, trend, and seasonal states with recency weights. Variants support additive/multiplicative errors and components, damping, and probabilistic forecasts.

Use when components evolve smoothly and interpretability/fast fitting matter. Watch multiplicative models near zero, structural breaks, and multiple/complex seasonalities.

### ARIMA/SARIMA

ARIMA$(p,d,q)$ combines autoregression, differencing, and moving-average errors:

$$
\phi(B)(1-B)^d y_t = c + \theta(B)\epsilon_t
$$

SARIMA adds seasonal AR, differencing, and MA terms. SARIMAX/dynamic regression adds exogenous predictors.

Use residual diagnostics and rolling performance, not ACF/PACF alone. Verify parameter stability, invertibility/stationarity assumptions as implemented, and future covariate availability.

### State-space models

Represent latent states and observation equations; Kalman filtering updates estimates as data arrives. Useful for missing observations, time-varying components, structural models, and uncertainty propagation.

### Decomposable/Prophet-style models

Trend + seasonality + holiday/event components can be convenient for business series. They still require realistic backtests, changepoint/seasonality control, known-future events, and comparison with simpler baselines.

## 7. ML with lagged features

Tree/boosting models can learn nonlinear relationships from:

- lags $y_{t-1}, y_{t-7}, y_{t-28}$;
- rolling/expanding statistics that end before the origin;
- calendar and cyclic encodings;
- price, promotion, inventory, weather forecast, and events;
- static item/store attributes;
- cross-series and hierarchy features.

Build features separately for every forecast origin. A rolling mean computed on the full table can include the target or future. Use a pipeline that makes cutoff semantics explicit.

Multi-step strategies:

| Strategy | Description | Trade-off |
|---|---|---|
| Recursive | one-step model feeds its predictions back | compact; error accumulation |
| Direct | separate model per horizon | no recursion; more models/data |
| Multi-output | one model predicts all horizons | captures horizon relation; larger output |
| DirRec | combines direct and recursive inputs | complex training/serving |
| Seq2seq | encoder produces a forecast sequence | flexible; data/compute intensive |

## 8. Global, deep, and foundation models

**Local model:** fitted per series. Strong when series have long histories and distinct dynamics.  
**Global model:** trained across many series using identity/static/covariate features. Shares statistical strength and can help sparse/new series.

Deep families to recognize:

- DeepAR: autoregressive probabilistic global model;
- N-BEATS/N-HiTS: feed-forward basis/hierarchical interpolation approaches;
- Temporal Fusion Transformer: multi-horizon model with static and temporal covariates;
- TCN, RNN/LSTM/GRU, PatchTST, TiDE, TSMixer, and related architectures.

Time-series foundation models in the current ecosystem include Google TimesFM, Amazon Chronos/Chronos-2, and Salesforce Moirai/Uni2TS. Evaluate them as pretrained forecasting candidates:

- zero-shot versus fine-tuned/adapted performance;
- univariate/multivariate/covariate support;
- context/horizon/frequency limits;
- probabilistic calibration;
- domain/dataset contamination risk;
- compute, batch latency, memory, and deployment environment;
- license, model-card limitations, and reproducibility.

Do not compare a foundation model only against a weak baseline. Use the same rolling origins, information set, metrics, and tuning budget; include statistical/global ML alternatives.

## 9. Rolling-origin evaluation

At each origin:

1. train or update using data available up to the origin;
2. respect feature and label availability;
3. leave a gap if operational latency or overlapping labels require it;
4. forecast the real deployment horizon;
5. advance the origin and repeat;
6. aggregate by horizon, series, slice, and business weights.

Choices:

- expanding versus fixed/sliding training window;
- number and spacing of origins;
- refit every origin versus deployment-like update cadence;
- cold-start series handling;
- hyperparameter selection nested within past data;
- locked final period/regime.

Random train/test splitting gives future patterns to the model and usually produces optimistic results.

## 10. Point forecast metrics

Let `e_t = y_t − ŷ_t`.

$$
MAE = \frac{1}{n}\sum |e_t|
RMSE = \sqrt{\frac{1}{n}\sum e_t^2}
$$

- MAE is robust and matches median-optimal point forecasts.
- RMSE penalizes large errors and is scale-dependent.
- MAPE is undefined/unstable near zero and asymmetric.
- sMAPE reduces but does not eliminate percentage-metric pathologies.
- WAPE aggregates absolute error over total actual magnitude; it can be distorted by trend, mix, or zero-total slices.

MASE scales error by an in-sample naive benchmark:

$$
MASE =
\frac{\frac{1}{n}\sum |e_t|}
{\frac{1}{T-m}\sum_{t=m+1}^{T}|y_t-y_{t-m}|}
$$

Use $m=1$ for non-seasonal or the relevant seasonal period when justified. MASE below 1 indicates improvement over that scaling baseline, but still inspect each horizon and segment.

Select metrics from the decision cost. Inventory may penalize stockouts differently from overstock; capacity planning may care about peaks and upper quantiles.

## 11. Probabilistic forecasts

A prediction interval describes uncertainty in a future observation, not uncertainty only in a mean parameter. Evaluate:

- empirical coverage at each nominal level;
- sharpness/width conditional on coverage;
- calibration by horizon, season, and slice;
- pinball loss for quantile $q$:

$$
L_q(y,\hat{y}_q)=
\begin{cases}
q(y-\hat{y}_q), & y\ge\hat{y}_q \\
(1-q)(\hat{y}_q-y), & y<\hat{y}_q
\end{cases}
$$

- CRPS or proper scoring rules for full distributions;
- quantile crossing and non-negative/support constraints.

Intervals often widen with horizon. Narrow but under-covering intervals are not high quality. Conformal methods can calibrate intervals under their assumptions; temporal dependence and regime change need careful calibration design.

## 12. Special forecasting problems

### Intermittent demand

Many zeros with irregular non-zero demand. Compare seasonal/naive and aggregate approaches with Croston/SBA/TSB-style methods, count/zero-inflated models, or global models. Evaluate inventory decisions and zero/non-zero timing, not MAPE.

### Hierarchical/grouped series

Forecasts across SKU → category → region → total should reconcile. Approaches:

- bottom-up;
- top-down;
- middle-out;
- optimal reconciliation such as MinT using error covariance.

Evaluate accuracy at every decision level; coherence alone does not ensure accuracy.

### Structural breaks and regimes

Use rolling diagnostics, change-point/domain events, shorter windows, adaptive states, scenario models, or ensembles. Avoid immediately retraining on a temporary outage or promotion spike.

### Censored demand

Sales during stockouts underestimate demand. Incorporate availability, censoring, substitution, lost-sales estimation, or causal/operational assumptions explicitly.

## 13. Production forecasting system

Typical flow:

1. versioned historical snapshot and as-of availability;
2. temporal validation and hierarchy reconciliation;
3. feature/covariate generation at each origin;
4. baseline and candidate backtests;
5. model/ensemble selection with horizon and segment policy;
6. scheduled fit/update and forecast generation;
7. constraints, reconciliation, quantiles, and scenario output;
8. publication with model/data/origin/version;
9. actuals arrival and error attribution;
10. monitoring, exceptions, retraining, and fallback.

Monitor:

- source freshness, gaps, corrections, and future-covariate delivery;
- bias and error by horizon/series/segment;
- interval coverage and width;
- baseline-relative performance and forecast value add;
- stockout/capacity/business cost;
- model/data version, runtime, failures, and latency;
- regime and hierarchy changes.

## 14. Library and model map

| Tool | Good fit | Boundary |
|---|---|---|
| statsmodels | ARIMA/SARIMAX, state space, ETS and diagnostics | production orchestration is separate |
| sktime | unified forecasting interfaces, reduction, evaluation | estimator capabilities vary |
| StatsForecast | scalable statistical/global benchmark models | benchmark claims need workload validation |
| MLForecast | lag-feature ML across many series | cutoff/covariate correctness remains yours |
| NeuralForecast | global neural forecasting models | tune/benchmark compute and stability |
| GluonTS | probabilistic forecasting datasets/models/evaluation | backend/model support varies |
| Darts | broad forecasting experimentation API | abstraction does not prevent leakage |
| Prophet | decomposable trend/seasonality/holiday workflow | not a universal default |
| TimesFM/Chronos/Moirai | pretrained/foundation forecasting | verify model version, license, limits, calibration |

## 15. Minimal rolling-origin splitter

```python
from __future__ import annotations

from typing import Iterator


def rolling_origins(
    n_observations: int,
    *,
    min_train_size: int,
    horizon: int,
    step: int = 1,
    gap: int = 0,
) -> Iterator[tuple[range, range]]:
    """Yield expanding train and fixed-horizon test index ranges."""
    values = (n_observations, min_train_size, horizon, step)
    if any(value <= 0 for value in values) or gap < 0:
        raise ValueError("sizes must be positive and gap must be non-negative")

    origin = min_train_size
    while origin + gap + horizon <= n_observations:
        train = range(0, origin)
        test = range(origin + gap, origin + gap + horizon)
        yield train, test
        origin += step


splits = list(
    rolling_origins(12, min_train_size=6, horizon=2, step=2, gap=1)
)
assert [(len(train), list(test)) for train, test in splits] == [
    (6, [7, 8]),
    (8, [9, 10]),
]
```

In real backtests, rebuild features and known-future covariates separately at each origin and match the actual refit cadence.

## 16. Rapid interview questions

**Why is a seasonal-naive model important?** It is a strong, cheap baseline for seasonal series and exposes complex models that merely rediscover last season.

**What is the difference between forecast horizon and lead time?** Horizon is how far ahead predictions extend; lead time is how early the decision requires the forecast. Operational lead time determines the usable information set.

**Why not shuffle a time series?** It lets future regimes and lag relationships influence training, producing an unrealistic evaluation.

**When use ETS versus ARIMA?** ETS models evolving components directly; ARIMA models differenced autocorrelation/error structure. Compare assumptions, diagnostics, and rolling performance.

**How do you use future covariates?** Only if their future values are truly known or generated by a separately evaluated forecast/scenario at the origin.

**Why can MAPE mislead?** It explodes near zero, is undefined at zero, and penalizes over/under forecasts asymmetrically.

**What is a global forecasting model?** One model learns across many related series, sharing patterns through series identity, static features, and covariates.

**How do you evaluate prediction intervals?** Coverage and sharpness by nominal level, horizon, season, and slice, plus a proper loss such as pinball/CRPS.

**How do you handle stockouts?** Treat observed sales as censored demand; include availability and use an explicit lost-sales/censoring assumption rather than learning stockouts as low demand.

**Would you use a time-series foundation model?** Benchmark the exact version against strong statistical/global baselines under identical origins, covariates, metrics, resource limits, and license constraints.

## 17. Lead-level case

**Prompt:** Forecast weekly SKU–store demand for replenishment across thousands of series.

Cover:

1. replenishment decision, order lead time, horizon, service-level/holding/stockout costs;
2. sales versus latent demand, stockout censoring, returns, substitutions, promotions, and new items;
3. SKU–store hierarchy, calendar, units, timezone, late corrections, and immutable as-of snapshots;
4. seasonal-naive and current planner forecast as baselines;
5. rolling origins spanning promotions, holidays, and recent regimes with a lead-time gap;
6. local statistical versus global boosting/neural/foundation candidates;
7. known-future price/promotion/calendar features and separately forecast weather;
8. intermittent-demand and cold-start policy using product/store attributes;
9. MAE/MASE plus asymmetric inventory cost, bias, service level, interval coverage, and horizon breakdown;
10. hierarchical reconciliation and operational constraints such as pack size and capacity;
11. staged shadow/pilot rollout against planner decisions, with overrides and reason logging;
12. monitoring actuals delay, stockouts, source gaps, forecast value add, coverage, drift, and fallback.

## 18. Final checklist

- [ ] I can define origin, horizon, lead time, frequency, series grain, and decision loss.
- [ ] I can audit temporal gaps, duplicates, timezone/DST, revisions, stockouts, and hierarchy.
- [ ] I can explain naive/seasonal-naive/drift baselines.
- [ ] I can compare ETS, ARIMA/SARIMAX, state-space, lagged boosting, global, deep, and foundation models.
- [ ] I can build lag/rolling features without future leakage.
- [ ] I can design rolling-origin evaluation that matches deployment refits and covariates.
- [ ] I can compare MAE, RMSE, MAPE, WAPE, MASE, pinball loss, and business cost.
- [ ] I can evaluate prediction intervals for coverage and sharpness.
- [ ] I can handle intermittent demand, hierarchy, structural breaks, and censored demand.
- [ ] I can design publication, monitoring, retraining, and safe fallback for production forecasts.

## 19. Primary references

- Hyndman and Athanasopoulos, [Forecasting: Principles and Practice](https://otexts.com/fpp3/)
- scikit-learn, [Lagged features for time-series forecasting](https://scikit-learn.org/stable/auto_examples/applications/plot_time_series_lagged_features.html)
- statsmodels, [State-space time-series analysis](https://www.statsmodels.org/stable/statespace.html)
- Nixtla, [StatsForecast documentation](https://nixtlaverse.nixtla.io/statsforecast/)
- Google Research, [TimesFM](https://github.com/google-research/timesfm)
- Amazon Science, [Chronos forecasting](https://github.com/amazon-science/chronos-forecasting)
- Salesforce AI Research, [Uni2TS and Moirai](https://github.com/SalesforceAIResearch/uni2ts)

Model families and APIs evolve. Pin the candidate, retain the full backtest identity, and compare it against strong deployment-relevant baselines.
