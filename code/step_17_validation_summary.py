"""Supplementary validation summaries for the final LR model.

Post-processing only: reads the saved subject-held-out validation predictions
(step_13_lr_predictions.csv), the validation patient identifiers
(PPMI_9_test.csv) and the fixed training-derived Youden threshold
(step_13_lr_test_performance.csv). No model is fitted or tuned.

Reported quantities:
- reference (prevalence-only) Brier score and scaled Brier score;
- mean calibration: mean predicted probability, observed prevalence,
  observed/expected ratio and calibration-in-the-large (logistic intercept
  with the predicted log-odds as offset, slope fixed at 1);
- decision-curve net benefit at the Youden threshold and the threshold range
  on the plotted grid (0.00-0.99, step 0.01) where the model exceeds both
  treat-all and treat-none.
Percentile 95% CIs use 2,000 patient-clustered bootstrap resamples with the
same sampling scheme and seed as step_14_bootstrap_ci.py.
"""

from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm

BASE_DIR = Path(__file__).resolve().parent
N_BOOTSTRAP = 2000
RANDOM_SEED = 42
DCA_GRID = np.round(np.arange(0.0, 1.0, 0.01), 2)


def citl(y: np.ndarray, p: np.ndarray) -> float:
    """Calibration-in-the-large: intercept of logit P(Y=1) = a + logit(p)."""
    p = np.clip(p, 1e-12, 1 - 1e-12)
    offset = np.log(p / (1 - p))
    fit = sm.GLM(y, np.ones_like(y), family=sm.families.Binomial(), offset=offset).fit()
    return float(fit.params[0])


def net_benefit(y: np.ndarray, p: np.ndarray, t: float) -> float:
    high = p >= t
    n = len(y)
    tp = np.sum(high & (y == 1)) / n
    fp = np.sum(high & (y == 0)) / n
    return float(tp - fp * t / (1 - t))


def treat_all(y: np.ndarray, t: float) -> float:
    prev = float(np.mean(y))
    return prev - (1 - prev) * t / (1 - t)


def summary(y: np.ndarray, p: np.ndarray, youden: float) -> dict:
    prev = float(np.mean(y))
    brier = float(np.mean((p - y) ** 2))
    ref = prev * (1 - prev)
    return {
        "Prevalence": prev,
        "Mean_predicted": float(np.mean(p)),
        "OE_ratio": prev / float(np.mean(p)),
        "Brier": brier,
        "Reference_Brier": ref,
        "Scaled_Brier": 1 - brier / ref,
        "CITL": citl(y, p),
        "NB_model_Youden": net_benefit(y, p, youden),
        "NB_treat_all_Youden": treat_all(y, youden),
    }


def cluster_samples(subjects: np.ndarray, y: np.ndarray) -> list[np.ndarray]:
    unique_subjects = np.unique(subjects)
    index = {s: np.flatnonzero(subjects == s) for s in unique_subjects}
    rng = np.random.RandomState(RANDOM_SEED)
    samples = []
    for _ in range(N_BOOTSTRAP):
        chosen = rng.choice(unique_subjects, size=len(unique_subjects), replace=True)
        idx = np.concatenate([index[s] for s in chosen])
        if np.unique(y[idx]).size == 2:
            samples.append(idx)
    return samples


def main() -> None:
    validation = pd.read_csv(BASE_DIR / "PPMI_9_test.csv")
    predictions = pd.read_csv(BASE_DIR / "step_13_lr_predictions.csv")
    y = predictions["y_true"].to_numpy(dtype=float)
    p = predictions["y_prob"].to_numpy(dtype=float)
    if len(validation) != len(predictions) or not np.array_equal(
        validation["MCI"].to_numpy(dtype=float), y
    ):
        raise SystemExit("Validation rows and saved predictions are not aligned")
    subjects = validation["PATNO"].to_numpy()
    performance = pd.read_csv(BASE_DIR / "step_13_lr_test_performance.csv", index_col=0)
    youden = float(performance.loc["Optimal Threshold", "test_youden"])

    point = summary(y, p, youden)
    boot = {k: [] for k in point}
    for idx in cluster_samples(subjects, y):
        for k, v in summary(y[idx], p[idx], youden).items():
            boot[k].append(v)
    rows = []
    for k, v in point.items():
        values = np.asarray(boot[k], dtype=float)
        rows.append(
            {
                "Metric": k,
                "Point_Estimate": v,
                "CI_Lower": float(np.percentile(values, 2.5)),
                "CI_Upper": float(np.percentile(values, 97.5)),
                "N_Bootstrap": int(values.size),
            }
        )
    better = [
        t
        for t in DCA_GRID
        if t < 1 and net_benefit(y, p, t) > max(0.0, treat_all(y, t))
    ]
    rows.append({"Metric": "Youden_threshold", "Point_Estimate": youden})
    rows.append(
        {
            "Metric": "DCA_grid_min_threshold_model_above_both",
            "Point_Estimate": min(better),
        }
    )
    rows.append(
        {
            "Metric": "DCA_grid_max_threshold_model_above_both",
            "Point_Estimate": max(better),
        }
    )
    rows.append(
        {"Metric": "DCA_grid_points_model_above_both", "Point_Estimate": len(better)}
    )
    rows.append(
        {
            "Metric": "DCA_grid_contiguous",
            "Point_Estimate": int(
                len(better) == int(round((max(better) - min(better)) / 0.01)) + 1
            ),
        }
    )
    out = pd.DataFrame(rows)
    out.to_csv(BASE_DIR / "step_17_validation_summary.csv", index=False)
    print(out.to_string(index=False))


if __name__ == "__main__":
    main()
