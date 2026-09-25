"""
Walk-forward training + evaluation (LightGBM + Ridge baseline).

v2 prep:
- Cross-sectional z-score by day (stock ranking curve)
- Drop highly correlated features (fit on train only)
- Focus horizon: 1y (others optional)
- Smaller / more regularized LightGBM
"""

from __future__ import annotations

from pathlib import Path

import joblib
import lightgbm as lgb
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from pinky.config import HORIZONS, PROJECT_ROOT
from pinky.dataset import load_dataset
from pinky.metrics import (
    brier_score,
    calibration_table,
    daily_rank_ic,
    top_decile_hit_rate,
    top_n_basket_excess,
    universe_mean_excess,
)
from pinky.preprocess import prepare_fold_frames
from pinky.walkforward import WalkForwardFold, iter_walk_forward_folds

ARTIFACTS_DIR = PROJECT_ROOT / "artifacts"
MODELS_DIR = PROJECT_ROOT / "models"

# Primary focus after v1 failure
DEFAULT_HORIZONS = ["1y"]


def _xy_return(df: pd.DataFrame, fcols: list[str], horizon: str):
    x = df[fcols].to_numpy(dtype=float)
    y = df[f"excess_{horizon}"].to_numpy(dtype=float)
    return x, y


def _xy_beat(df: pd.DataFrame, fcols: list[str], horizon: str):
    x = df[fcols].to_numpy(dtype=float)
    y = df[f"beat_{horizon}"].to_numpy(dtype=float)
    return x, y


def _fit_return_models(x_train, y_train):
    # Ridge = simple baseline we must beat
    ridge = Pipeline(
        [
            ("scaler", StandardScaler()),
            ("model", Ridge(alpha=1.0, random_state=42)),
        ]
    )
    ridge.fit(x_train, y_train)

    # Smaller, more regularized LightGBM (fix #5)
    lgbm = lgb.LGBMRegressor(
        n_estimators=120,
        learning_rate=0.03,
        num_leaves=15,
        max_depth=4,
        min_child_samples=40,
        subsample=0.7,
        colsample_bytree=0.5,
        reg_lambda=5.0,
        reg_alpha=0.1,
        random_state=42,
        verbosity=-1,
    )
    lgbm.fit(x_train, y_train)
    return ridge, lgbm


def _fit_beat_models(x_train, y_train):
    logit = Pipeline(
        [
            ("scaler", StandardScaler()),
            (
                "model",
                LogisticRegression(
                    max_iter=500,
                    random_state=42,
                    class_weight="balanced",
                ),
            ),
        ]
    )
    logit.fit(x_train, y_train)

    lgbm = lgb.LGBMClassifier(
        n_estimators=120,
        learning_rate=0.03,
        num_leaves=15,
        max_depth=4,
        min_child_samples=40,
        subsample=0.7,
        colsample_bytree=0.5,
        reg_lambda=5.0,
        reg_alpha=0.1,
        random_state=42,
        verbosity=-1,
    )
    lgbm.fit(x_train, y_train)
    return logit, lgbm


def _eval_prepared(
    horizon: str,
    fold: WalkForwardFold,
    test: pd.DataFrame,
    fcols: list[str],
    ridge,
    lgbm_ret,
    logit,
    lgbm_beat,
    n_train: int,
) -> dict:
    x_test = test[fcols].to_numpy(dtype=float)
    test = test.copy()
    test["pred_excess_ridge"] = ridge.predict(x_test)
    test["pred_excess_lgbm"] = lgbm_ret.predict(x_test)
    test["pred_beat_logit"] = logit.predict_proba(x_test)[:, 1]
    test["pred_beat_lgbm"] = lgbm_beat.predict_proba(x_test)[:, 1]

    excess_col = f"excess_{horizon}"
    beat_col = f"beat_{horizon}"

    row = {
        "fold_id": fold.fold_id,
        "horizon": horizon,
        "test_start": fold.test_start.date().isoformat(),
        "test_end": fold.test_end.date().isoformat(),
        "n_train": n_train,
        "n_test": len(test),
        "n_purged": fold.n_purged,
        "n_features": len(fcols),
        "beat_rate_test": float(test[beat_col].mean()),
        "ic_ridge": daily_rank_ic(test, "pred_excess_ridge", excess_col),
        "ic_lgbm": daily_rank_ic(test, "pred_excess_lgbm", excess_col),
        "top_decile_hit_ridge": top_decile_hit_rate(test, "pred_excess_ridge", beat_col),
        "top_decile_hit_lgbm": top_decile_hit_rate(test, "pred_excess_lgbm", beat_col),
        "top5_excess_ridge": top_n_basket_excess(test, "pred_excess_ridge", excess_col, n=5),
        "top5_excess_lgbm": top_n_basket_excess(test, "pred_excess_lgbm", excess_col, n=5),
        "universe_mean_excess": universe_mean_excess(test, excess_col),
        "brier_logit": brier_score(test[beat_col].to_numpy(), test["pred_beat_logit"].to_numpy()),
        "brier_lgbm": brier_score(test[beat_col].to_numpy(), test["pred_beat_lgbm"].to_numpy()),
    }
    row["ic_lgbm_beats_ridge"] = (
        row["ic_lgbm"] > row["ic_ridge"]
        if not (np.isnan(row["ic_lgbm"]) or np.isnan(row["ic_ridge"]))
        else False
    )
    row["top5_lgbm_beats_ridge"] = (
        row["top5_excess_lgbm"] > row["top5_excess_ridge"]
        if not (np.isnan(row["top5_excess_lgbm"]) or np.isnan(row["top5_excess_ridge"]))
        else False
    )
    return row


def run_horizon(df: pd.DataFrame, horizon: str) -> tuple[pd.DataFrame, dict]:
    """Train/eval all folds for one horizon with CS prep + tuned LightGBM."""
    rows = []
    last_models: dict = {}

    for fold in iter_walk_forward_folds(df, horizon):
        train_cs, test_cs, fcols = prepare_fold_frames(fold.train, fold.test)
        x_tr, y_tr = _xy_return(train_cs, fcols, horizon)
        x_tb, y_tb = _xy_beat(train_cs, fcols, horizon)

        ridge, lgbm_ret = _fit_return_models(x_tr, y_tr)
        logit, lgbm_beat = _fit_beat_models(x_tb, y_tb)

        metrics = _eval_prepared(
            horizon,
            fold,
            test_cs,
            fcols,
            ridge,
            lgbm_ret,
            logit,
            lgbm_beat,
            n_train=len(train_cs),
        )
        rows.append(metrics)
        last_models = {
            "feature_cols": fcols,
            "ridge": ridge,
            "lgbm_return": lgbm_ret,
            "logit": logit,
            "lgbm_beat": lgbm_beat,
            "fold": fold,
            "test_cs": test_cs,
        }
        print(
            f"[{horizon}] fold {fold.fold_id}: "
            f"feats={len(fcols)} | "
            f"IC lgbm={metrics['ic_lgbm']:.3f} ridge={metrics['ic_ridge']:.3f} | "
            f"top5 lgbm={metrics['top5_excess_lgbm']:.3f} "
            f"ridge={metrics['top5_excess_ridge']:.3f} "
            f"univ={metrics['universe_mean_excess']:.3f}"
        )

    return pd.DataFrame(rows), last_models


def _write_summary(all_metrics: pd.DataFrame, path: Path) -> None:
    lines = [
        "# Pinky Walk-Forward Training Report (v2 prep)",
        "",
        "Prep: cross-sectional z-score + correlated-feature drop + regularized LightGBM.",
        "Validation: expanding walk-forward + label purge (no random splits).",
        "Baseline to beat: **Ridge**.",
        "",
    ]
    for horizon in list(HORIZONS):
        m = all_metrics[all_metrics["horizon"] == horizon]
        if m.empty:
            continue
        ic_lgbm = m["ic_lgbm"].mean()
        ic_ridge = m["ic_ridge"].mean()
        top5_lgbm = m["top5_excess_lgbm"].mean()
        top5_ridge = m["top5_excess_ridge"].mean()
        univ = m["universe_mean_excess"].mean()
        beat_ic = m["ic_lgbm_beats_ridge"].mean()
        beat_top = m["top5_lgbm_beats_ridge"].mean()

        pass_ic = ic_lgbm > ic_ridge
        pass_top = top5_lgbm > top5_ridge
        soft = "PASS" if pass_ic and pass_top else "FAIL / MIXED"

        lines += [
            f"## Horizon `{horizon}` ({len(m)} folds)",
            "",
            f"- Mean rank IC — LightGBM: **{ic_lgbm:.3f}** | Ridge: **{ic_ridge:.3f}**",
            f"- LightGBM beats Ridge on IC in **{100 * beat_ic:.0f}%** of folds",
            f"- Mean top-5 excess — LightGBM: **{top5_lgbm:.3f}** | Ridge: **{top5_ridge:.3f}** | Universe: **{univ:.3f}**",
            f"- LightGBM beats Ridge on top-5 in **{100 * beat_top:.0f}%** of folds",
            f"- Avg features used: **{m['n_features'].mean():.1f}**",
            f"**Soft bar vs Ridge:** **{soft}**",
            "",
        ]

    path.write_text("\n".join(lines))


def run_all(
    horizons: list[str] | None = None,
    save: bool = True,
) -> pd.DataFrame:
    """Run walk-forward training. Default focus: 1y."""
    horizons = horizons or list(DEFAULT_HORIZONS)
    df = load_dataset()
    parts = []
    last_by_h = {}

    for h in horizons:
        print(f"\n=== Training horizon {h} (v2 prep) ===")
        metrics, last = run_horizon(df, h)
        parts.append(metrics)
        last_by_h[h] = last

    all_metrics = pd.concat(parts, ignore_index=True)

    if save:
        ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
        MODELS_DIR.mkdir(parents=True, exist_ok=True)
        metrics_path = ARTIFACTS_DIR / "walkforward_metrics_v2.csv"
        all_metrics.to_csv(metrics_path, index=False)
        summary_path = ARTIFACTS_DIR / "walkforward_summary_v2.md"
        _write_summary(all_metrics, summary_path)

        for h, pack in last_by_h.items():
            out = MODELS_DIR / h
            out.mkdir(parents=True, exist_ok=True)
            joblib.dump(pack["lgbm_return"], out / "lgbm_return.joblib")
            joblib.dump(pack["lgbm_beat"], out / "lgbm_beat.joblib")
            joblib.dump(pack["ridge"], out / "ridge_return.joblib")
            joblib.dump(pack["logit"], out / "logit_beat.joblib")
            (out / "feature_cols.txt").write_text("\n".join(pack["feature_cols"]))

        if "1y" in last_by_h:
            pack = last_by_h["1y"]
            test = pack["test_cs"]
            fcols = pack["feature_cols"]
            x = test[fcols].to_numpy(dtype=float)
            p = pack["lgbm_beat"].predict_proba(x)[:, 1]
            y = test["beat_1y"].to_numpy(dtype=float)
            calibration_table(y, p).to_csv(
                ARTIFACTS_DIR / "calibration_1y_last_fold_v2.csv", index=False
            )

        print(f"\nWrote {metrics_path}")
        print(f"Wrote {summary_path}")
        print(f"Wrote models under {MODELS_DIR}")

    return all_metrics


if __name__ == "__main__":
    run_all()
