# This script generates synthetic one-week flight movement data for Mumbai (BOM) and Delhi (DEL),
# analyzes peak-time delays and cascading disruptions, trains a simple ML model to predict delays,
# performs a capacity-aware slot re-timing optimization, identifies high-impact flights, and
# exposes a tiny rule-based NLP interface to query insights.
#
# It saves outputs (CSV, PNG charts, and a README) to /mnt/data/airport_opt_demo and zips the folder.

import os
import io
import zipfile
import math
import json
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Ensure output dir
outdir = "/mnt/data/airport_opt_demo"
os.makedirs(outdir, exist_ok=True)

rng = np.random.default_rng(42)

# ------------------------------
# 1) Synthetic data generation
# ------------------------------

def generate_synthetic_week(num_flights_per_airport_per_day=800, seed=42):
    rng = np.random.default_rng(seed)
    airports = ["BOM", "DEL"]
    airlines = ["AI", "6E", "UK", "SG", "G8", "IX"]
    ops = ["DEP", "ARR"]
    # Simplified runway config
    runway_cfg = {
        "BOM": ["09/27"],  # treat as one operational runway (real BOM constraints are complex)
        "DEL": ["09/27", "10/28"]  # treat as two parallel operational runways (simplified)
    }
    # create 7 days
    rows = []
    start_date = datetime(2025, 7, 14)  # pick a recent Monday (arbitrary, just consistent)
    for d in range(7):
        date = start_date + timedelta(days=d)
        for ap in airports:
            # generate a circadian demand curve for operations across the day (1440 minutes)
            minutes = np.arange(1440)
            # morning and evening peaks + noise; higher for DEL
            base = (1.0 +
                    0.6*np.exp(-((minutes-540)/120)**2) +  # ~9am peak
                    0.8*np.exp(-((minutes-1200)/120)**2)   # ~8pm peak
                   )
            if ap == "DEL":
                base *= 1.2
            # scale to expected total ops (arr+dep); ensure integer ops count
            total_ops = int(num_flights_per_airport_per_day * (1.2 if ap=="DEL" else 1.0))
            probs = base / base.sum()
            sched_minute_choices = rng.choice(minutes, size=total_ops, replace=True, p=probs)
            # split ARR/DEP roughly 50/50
            ops_choices = rng.choice(ops, size=total_ops, replace=True)
            # random airlines and aircraft types
            ac_types = ["A320", "B738", "A321", "AT76", "A20N"]
            airlines_choices = rng.choice(airlines, size=total_ops, replace=True)
            ac_choices = rng.choice(ac_types, size=total_ops, replace=True)
            # assign runways (round-robin by minute)
            runways = runway_cfg[ap]
            runway_assign = [runways[m % len(runways)] for m in sched_minute_choices]
            # schedule and baseline delay process
            # congestion factor: more operations per 5-min bucket -> more delay
            df_tmp = pd.DataFrame({
                "date": [date.strftime("%Y-%m-%d")] * total_ops,
                "airport": ap,
                "op": ops_choices,
                "airline": airlines_choices,
                "ac_type": ac_choices,
                "sched_minute_of_day": sched_minute_choices,
                "runway": runway_assign,
            })
            # baseline weather/day effects
            dow = date.weekday()
            weather_noise = rng.normal(loc=2 if dow in (0,5) else 0, scale=3, size=total_ops)  # Mondays & Saturdays a tad worse
            # compute 5-min bucket load as proxy for congestion
            df_tmp["bucket5"] = (df_tmp["sched_minute_of_day"] // 5).astype(int)
            load = df_tmp.groupby("bucket5")["op"].transform("count")
            # congestion delay model (minutes)
            cong_delay = np.maximum(0, (load - (18 if ap=="DEL" else 10)) * (0.6 if ap=="DEL" else 0.9))
            # op-specific baseline
            dep_bias = np.where(df_tmp["op"].values == "DEP", 3, 1)
            # total stochastic delay, truncated at 0
            raw_delay = weather_noise + cong_delay + rng.normal(0, 4, size=total_ops) + dep_bias
            delay = np.maximum(0, np.round(raw_delay).astype(int))
            df_tmp["sched_time"] = pd.to_datetime(df_tmp["date"]) + pd.to_timedelta(df_tmp["sched_minute_of_day"], unit="m")
            df_tmp["delay_min"] = delay
            df_tmp["act_time"] = df_tmp["sched_time"] + pd.to_timedelta(df_tmp["delay_min"], unit="m")
            rows.append(df_tmp)
    df = pd.concat(rows, ignore_index=True).sort_values(["date","airport","sched_minute_of_day"]).reset_index(drop=True)
    # Create simplistic tails to enable cascading disruptions: group by airline+ac_type and chain a few flights
    df["tail_id"] = (df["airline"] + "-" + df["ac_type"] + "-" + (rng.integers(1, 200, size=len(df))).astype(str))
    # Sort by tail timeline and propagate late arrivals to subsequent departures of same tail
    df["turn_min"] = rng.integers(35, 75, size=len(df))  # minimum turnaround
    # For simplicity, define a "next leg" within same day for a subset of tails
    df = df.sort_values(["tail_id","sched_time"]).reset_index(drop=True)
    df["prev_act_time_by_tail"] = df.groupby("tail_id")["act_time"].shift(1)
    df["op_prev"] = df.groupby("tail_id")["op"].shift(1)
    # If previous op is ARR, enforce that the next DEP cannot leave before prev_act + turnaround -> induced delay
    induced = (df["op"].eq("DEP")) & (df["op_prev"].eq("ARR")) & df["prev_act_time_by_tail"].notna()
    min_ready = df["prev_act_time_by_tail"] + pd.to_timedelta(df["turn_min"], unit="m")
    induced_delay = (min_ready - df["sched_time"]).dt.total_seconds() / 60.0
    induced_delay = induced_delay.where(induced, 0).clip(lower=0).round().astype(int)
    df["delay_min"] = df["delay_min"] + induced_delay
    df["act_time"] = df["sched_time"] + pd.to_timedelta(df["delay_min"], unit="m")
    # Save
    csv_path = os.path.join(outdir, "synthetic_week_movements.csv")
    df.to_csv(csv_path, index=False)
    return df, csv_path

df, csv_path = generate_synthetic_week()

# ------------------------------
# 2) Exploratory analysis: peaks, busiest slots, delays
# ------------------------------

def plot_busiest_slots(df, airport, window_min=15):
    dfa = df[df["airport"]==airport].copy()
    start = dfa["sched_time"].min().floor("D")
    end = dfa["sched_time"].max().ceil("D")
    # resample scheduled counts per window
    dfa = dfa.set_index("sched_time").sort_index()
    counts = dfa["op"].groupby([pd.Grouper(freq=f"{window_min}min")]).count()
    fig = plt.figure(figsize=(10,4))
    counts.plot()
    plt.title(f"{airport}: Movements per {window_min}-min window (scheduled)")
    plt.xlabel("Time")
    plt.ylabel("Movements")
    png = os.path.join(outdir, f"{airport}_busiest_slots_{window_min}min.png")
    plt.tight_layout()
    plt.savefig(png, dpi=140)
    plt.close(fig)
    return png

def plot_delay_by_hour(df, airport):
    dfa = df[df["airport"]==airport].copy()
    dfa["hour"] = dfa["sched_time"].dt.hour
    avg_delay = dfa.groupby("hour")["delay_min"].mean()
    fig = plt.figure(figsize=(8,4))
    avg_delay.plot(kind="bar")
    plt.title(f"{airport}: Average delay by hour (scheduled time)")
    plt.xlabel("Hour")
    plt.ylabel("Avg delay (min)")
    png = os.path.join(outdir, f"{airport}_avg_delay_by_hour.png")
    plt.tight_layout()
    plt.savefig(png, dpi=140)
    plt.close(fig)
    return png

bom_slots = plot_busiest_slots(df, "BOM", 15)
del_slots = plot_busiest_slots(df, "DEL", 15)
bom_delay = plot_delay_by_hour(df, "BOM")
del_delay = plot_delay_by_hour(df, "DEL")

# ------------------------------
# 3) Feature engineering for ML
# ------------------------------

# Features: airport, op, airline, ac_type, dayofweek, hour, bucket5 load (as a proxy for congestion), previous-tail delay, turnaround
work = df.copy()
work["dow"] = work["sched_time"].dt.weekday
work["hour"] = work["sched_time"].dt.hour
# approximate congestion feature: scheduled ops in same 5-min bucket at airport
work["bucket5"] = (work["sched_time"].view("int64") // (5*60*1_000_000_000)).astype(np.int64)
bucket_load = work.groupby(["airport","bucket5"])["op"].transform("count")
work["bucket_load"] = bucket_load
# previous tail delay feature
prev_delay = work.groupby("tail_id")["delay_min"].shift(1).fillna(0).astype(int)
work["prev_tail_delay"] = prev_delay
work["turn_min"] = work["turn_min"].fillna(0).astype(int)
# target
y = work["delay_min"].astype(float)

# Encode categoricals
cat_cols = ["airport","op","airline","ac_type"]
for c in cat_cols:
    work[c] = work[c].astype("category")
X_cats = pd.get_dummies(work[cat_cols], drop_first=False)
X_num = work[["dow","hour","bucket_load","prev_tail_delay","turn_min"]].astype(float)
X = pd.concat([X_num, X_cats], axis=1)

# Train/test split by time (last 2 days test)
split_time = work["sched_time"].min() + timedelta(days=5)
train_idx = work["sched_time"] < split_time
test_idx = ~train_idx

X_train, y_train = X[train_idx], y[train_idx]
X_test, y_test = X[test_idx], y[test_idx]

# Try to train RandomForest; if not available, fallback to linear regression
model = None
metrics = {}
try:
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.metrics import mean_absolute_error, r2_score
    model = RandomForestRegressor(n_estimators=120, random_state=42, n_jobs=-1)
    model.fit(X_train, y_train)
    preds = model.predict(X_test)
    metrics["model"] = "RandomForestRegressor"
    metrics["MAE"] = float(mean_absolute_error(y_test, preds))
    metrics["R2"] = float(r2_score(y_test, preds))
except Exception as e:
    from sklearn.linear_model import Ridge
    from sklearn.metrics import mean_absolute_error, r2_score
    model = Ridge(alpha=1.0, random_state=42) if "random_state" in Ridge().get_params() else Ridge(alpha=1.0)
    model.fit(X_train, y_train)
    preds = model.predict(X_test)
    metrics["model"] = "Ridge"
    metrics["MAE"] = float(mean_absolute_error(y_test, preds))
    metrics["R2"] = float(r2_score(y_test, preds))

# Save metrics
with open(os.path.join(outdir, "model_metrics.json"), "w") as f:
    json.dump(metrics, f, indent=2)

# ------------------------------
# 4) Capacity-aware slot re-timing optimization (greedy heuristic)
# ------------------------------
# Goal: within +/- 15 minutes of scheduled, assign each movement to a 1-minute slot
# subject to per-runway capacity per minute. Minimize (predicted delay + soft congestion penalty).

def predict_delay(df_subset):
    # Use the trained model to predict delay for df_subset rows
    tmp = df_subset.copy()
    tmp["dow"] = tmp["sched_time"].dt.weekday
    tmp["hour"] = tmp["sched_time"].dt.hour
    tmp["bucket5"] = (tmp["sched_time"].view("int64") // (5*60*1_000_000_000)).astype(np.int64)
    tmp["bucket_load"] = tmp.groupby(["airport","bucket5"])["op"].transform("count")
    tmp["prev_tail_delay"] = tmp.groupby("tail_id")["delay_min"].shift(1).fillna(0).astype(int) if "delay_min" in tmp else 0
    tmp["turn_min"] = tmp.get("turn_min", pd.Series(45, index=tmp.index))
    # encode
    enc = pd.get_dummies(tmp[cat_cols], drop_first=False)
    for c in X_cats.columns:
        if c not in enc.columns:
            enc[c] = 0
    enc = enc[X_cats.columns]
    num = tmp[["dow","hour","bucket_load","prev_tail_delay","turn_min"]].astype(float)
    feat = pd.concat([num, enc], axis=1)
    return model.predict(feat)

# per-airport per-minute capacity
cap_per_min = {
    "BOM": 1,   # effectively one movement per minute (simplified)
    "DEL": 2    # two movements per minute (simplified)
}

def greedy_assign_day(dfa, flex_min=15):
    # dfa: one day + one airport
    dfa = dfa.sort_values("sched_time").copy()
    # timeline minutes
    min_time = dfa["sched_time"].min().floor("T")
    max_time = dfa["sched_time"].max().ceil("T")
    minutes = pd.date_range(min_time - pd.Timedelta(minutes=flex_min),
                            max_time + pd.Timedelta(minutes=flex_min),
                            freq="T")
    capacity = pd.Series(cap_per_min.get(dfa["airport"].iloc[0], 1), index=minutes)
    assigned = []
    for idx, row in dfa.iterrows():
        ap = row["airport"]
        # candidate window
        window = pd.date_range(row["sched_time"] - pd.Timedelta(minutes=flex_min),
                               row["sched_time"] + pd.Timedelta(minutes=flex_min),
                               freq="T")
        # feasible minutes with remaining capacity
        feas = window[capacity.reindex(window, fill_value=0) > 0]
        if len(feas)==0:
            # push to the next minute with capacity
            feas = minutes[capacity.values > 0]
        # score each feasible minute: predicted delay at that minute + congestion penalty
        # For scoring, temporarily set sched_time to candidate minute
        scores = []
        for t in feas[:61]:  # limit search for speed
            tmp = row.to_frame().T.copy()
            tmp["sched_time"] = pd.to_datetime([t])
            pred = float(predict_delay(tmp)[0])
            # soft penalty if this minute is nearing capacity
            load_pen = 0.5 * (cap_per_min.get(ap,1) - capacity.loc[t])
            # prefer smaller move from original time
            shift_pen = 0.2 * abs(int((t - row["sched_time"]).total_seconds()/60))
            scores.append((pred + load_pen + shift_pen, t))
        best_score, best_t = min(scores, key=lambda x: x[0])
        assigned.append((idx, best_t, best_score))
        capacity.loc[best_t] -= 1
    res = pd.DataFrame(assigned, columns=["idx","opt_time","score"]).set_index("idx")
    dfa.loc[res.index, "opt_time"] = res["opt_time"].values
    dfa["opt_shift_min"] = (dfa["opt_time"] - dfa["sched_time"]).dt.total_seconds()/60.0
    return dfa

# Run greedy assignment per airport per day on last two days (test period)
opt_results = []
for (airport, date), dfg in work[test_idx].groupby([work["airport"], work["sched_time"].dt.date]):
    dfg_local = work.loc[dfg.index, ["airport","sched_time","delay_min","op","airline","ac_type","tail_id","turn_min"]].copy()
    dfg_local = greedy_assign_day(dfg_local, flex_min=15)
    opt_results.append(dfg_local)

opt_df = pd.concat(opt_results, ignore_index=False)
opt_df["opt_time"] = pd.to_datetime(opt_df["opt_time"])

# Evaluate improvement (proxy): predicted delay at scheduled vs at optimized
base_pred = predict_delay(opt_df.rename(columns={"sched_time":"sched_time"}))
opt_tmp = opt_df.copy()
opt_tmp = opt_tmp.rename(columns={"opt_time":"sched_time"})
opt_pred = predict_delay(opt_tmp)

improve = pd.DataFrame({
    "airport": opt_df["airport"].values,
    "base_pred_delay": base_pred,
    "opt_pred_delay": opt_pred,
    "shift_min": opt_df["opt_shift_min"].values
})
improve["delta"] = improve["base_pred_delay"] - improve["opt_pred_delay"]
summary_improve = improve.groupby("airport")[["base_pred_delay","opt_pred_delay","delta","shift_min"]].mean()

summary_csv = os.path.join(outdir, "optimization_summary.csv")
summary_improve.to_csv(summary_csv)

# ------------------------------
# 5) Identify high-impact flights
# ------------------------------
# Define "impact score" as: predicted downstream savings if we move this flight by <= 10 minutes
# We approximate downstream by same-tail next leg (if any).

def high_impact_flights(df_all, candidate_idx, minutes_to_move=10):
    row = df_all.loc[candidate_idx]
    # base predicted
    base = float(predict_delay(row.to_frame().T)[0])
    # try -10..+10 move
    deltas = []
    for m in range(-minutes_to_move, minutes_to_move+1, 5):
        tmp = row.to_frame().T.copy()
        tmp["sched_time"] = tmp["sched_time"] + pd.to_timedelta(m, unit="m")
        new = float(predict_delay(tmp)[0])
        deltas.append((m, base - new))
    best_shift, best_gain = max(deltas, key=lambda x: x[1])
    return best_gain, best_shift

# Compute a quick shortlist on test period
subset = work[test_idx].sample(500, random_state=42)
hi_rows = []
for idx in subset.index:
    try:
        gain, shift = high_impact_flights(work, idx, 10)
        hi_rows.append((idx, work.loc[idx,"airport"], work.loc[idx,"op"], work.loc[idx,"sched_time"], gain, shift))
    except Exception:
        continue

hi_df = pd.DataFrame(hi_rows, columns=["index","airport","op","sched_time","impact_gain_min","recommended_shift_min"]).sort_values("impact_gain_min", ascending=False).head(50)
hi_path = os.path.join(outdir, "high_impact_flights.csv")
hi_df.to_csv(hi_path, index=False)

# ------------------------------
# 6) NLP interface (very small rule-based demo)
# ------------------------------

class TinyNLP:
    def __init__(self, df, improvement_df, hi_df):
        self.df = df
        self.improv = improvement_df
        self.hi = hi_df

    def answer(self, q: str) -> str:
        ql = q.lower()
        if "busiest" in ql or "peak" in ql:
            # return busiest hour per airport
            ans = []
            for ap in ["BOM","DEL"]:
                dfa = self.df[self.df["airport"]==ap].copy()
                dfa["hour"] = dfa["sched_time"].dt.hour
                counts = dfa.groupby("hour")["op"].count()
                h = int(counts.idxmax())
                v = int(counts.max())
                ans.append(f"{ap}: busiest hour (scheduled) is {h:02d}:00 with ~{v} movements across the week.")
            return " | ".join(ans)
        if "average delay" in ql or "avg delay" in ql:
            parts = []
            for ap in ["BOM","DEL"]:
                avg = self.df[self.df["airport"]==ap]["delay_min"].mean()
                parts.append(f"{ap}: {avg:.1f} min")
            return "Average delay: " + " | ".join(parts)
        if "high impact" in ql:
            rows = self.hi.head(5).copy()
            rows["sched_time"] = rows["sched_time"].dt.strftime("%Y-%m-%d %H:%M")
            return rows.to_string(index=False)
        if "improvement" in ql or "optimiz" in ql:
            s = self.improv.copy()
            s = s[["base_pred_delay","opt_pred_delay","delta","shift_min"]].round(2)
            return "Optimization summary (means):\n" + s.to_string()
        if "when should i schedule" in ql or "best time" in ql:
            # suggest hours with lowest average predicted delay
            recs = []
            for ap in ["BOM","DEL"]:
                dfa = self.df[self.df["airport"]==ap].copy()
                dfa["hour"] = dfa["sched_time"].dt.hour
                avg = dfa.groupby("hour")["delay_min"].mean().sort_values().head(3)
                recs.append(f"{ap}: best hours (lower delay) -> {', '.join([str(int(h)) for h in avg.index.tolist()])}")
            return " | ".join(recs)
        return "Sorry, I can answer queries like: 'busiest slots', 'average delay', 'high impact flights', 'optimization improvement', or 'best time to schedule'."

tiny_nlp = TinyNLP(work, summary_improve, hi_df)

# Save a README with quick instructions
readme = f"""# Airport Schedule Optimization Demo

Files in this folder were generated from synthetic one-week data for BOM and DEL.

## What's inside
- synthetic_week_movements.csv — movement-level schedule with simulated delays
- BOM_* and DEL_* PNG charts — busiest slots and avg delay by hour
- model_metrics.json — ML model quality on the last two days
- optimization_summary.csv — mean predicted delay before/after greedy re-timing
- high_impact_flights.csv — top candidates whose small shift could save most minutes

## Quick NLP interface examples
- "busiest slots"
- "average delay"
- "high impact flights"
- "optimization improvement"
- "best time to schedule"

"""

with open(os.path.join(outdir, "README.txt"), "w") as f:
    f.write(readme)

# Display basic outputs to user (charts and metrics)
from caas_jupyter_tools import display_dataframe_to_user

# show a small preview of the dataset
preview = df.sample(10, random_state=7)
display_dataframe_to_user("Synthetic week preview (BOM/DEL)", preview)

# Plot images inline for user view
from IPython.display import Image, display
display(Image(filename=bom_slots))
display(Image(filename=del_slots))
display(Image(filename=bom_delay))
display(Image(filename=del_delay))

# Show metrics
metrics

