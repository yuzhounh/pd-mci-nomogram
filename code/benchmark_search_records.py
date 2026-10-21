"""Persist the selected parameters and complete trials of a benchmark search."""

import json
from pathlib import Path


def duration(seconds):
    seconds = max(0, int(seconds))
    hours, rest = divmod(seconds, 3600)
    minutes, seconds = divmod(rest, 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


def save_benchmark_search(study, selected_params, model_label, random_state):
    """Record the existing search without changing sampling or model fitting."""
    prefix = Path(f"step_14_{model_label.lower()}")
    record = {
        "model_label": model_label,
        "objective": "mean subject-level cross-validation AUPRC",
        "best_value": float(study.best_value),
        "best_trial_number": int(study.best_trial.number),
        "best_params": selected_params,
        "tuned_params": study.best_trial.params,
        "random_state": int(random_state),
        "n_trials": len(study.trials),
    }
    destination = Path(str(prefix) + "_best_params.json")
    temporary = destination.with_suffix(".json.tmp")
    temporary.write_text(
        json.dumps(record, indent=2, ensure_ascii=False, allow_nan=False),
        encoding="utf-8",
    )
    temporary.replace(destination)
    study.trials_dataframe().to_csv(
        str(prefix) + "_optuna_trials.csv", index=False, encoding="utf-8"
    )
    return record
