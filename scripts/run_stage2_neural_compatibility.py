from __future__ import annotations

import argparse
import hashlib
import json
import os
import random
import sys
import time
from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.base_encodings import EIIP, GC, HYDROGEN, PURINE, pad_or_trim
from src.stage2_features import build_feature_matrix


def parse_csv_list(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def parse_int_list(value: str) -> list[int]:
    return [int(item.strip()) for item in value.split(",") if item.strip()]


def set_global_seed(seed: int) -> None:
    os.environ.setdefault("PYTHONHASHSEED", str(seed))
    random.seed(seed)
    np.random.seed(seed)
    import torch

    torch.manual_seed(seed)
    torch.set_num_threads(1)
    if hasattr(torch, "use_deterministic_algorithms"):
        torch.use_deterministic_algorithms(True, warn_only=True)
    if hasattr(torch.backends, "cudnn"):
        torch.backends.cudnn.benchmark = False
        torch.backends.cudnn.deterministic = True


def channel_matrix(seq: str, length: int, encoding: str) -> np.ndarray:
    seq = pad_or_trim(seq, length)
    if encoding == "onehot":
        rows = np.zeros((5, length), dtype=np.float32)
        for i, base in enumerate(seq):
            idx = {"A": 0, "C": 1, "G": 2, "T": 3}.get(base, 4)
            rows[idx, i] = 1.0
        return rows
    if encoding == "property":
        rows = np.zeros((5, length), dtype=np.float32)
        for i, base in enumerate(seq):
            rows[0, i] = HYDROGEN.get(base, 0.0) / 3.0
            rows[1, i] = GC.get(base, 0.0)
            rows[2, i] = PURINE.get(base, 0.0)
            rows[3, i] = EIIP.get(base, 0.0) / 0.1340
            rows[4, i] = 1.0 if base == "N" else 0.0
        return rows
    raise ValueError(f"Unsupported channel encoding: {encoding}")


@dataclass(frozen=True)
class ModelSpec:
    name: str
    family: str
    input_name: str
    input_kind: str


MODEL_SPECS = {
    "mlp_ckmer5": ModelSpec("mlp_ckmer5", "tabular_mlp", "ckmer5_count_l2", "vector"),
    "mlp_csp": ModelSpec("mlp_csp", "tabular_mlp", "cspaced_property_l2", "vector"),
    "mlp_hybrid": ModelSpec("mlp_hybrid", "tabular_mlp", "hybrid_ckmer5_csp", "vector"),
    "cnn_onehot": ModelSpec("cnn_onehot", "cnn1d", "onehot", "channels"),
    "cnn_property": ModelSpec("cnn_property", "cnn1d", "property", "channels"),
    "tiny_transformer_onehot": ModelSpec("tiny_transformer_onehot", "tiny_transformer", "onehot", "channels"),
    "tiny_transformer_property": ModelSpec("tiny_transformer_property", "tiny_transformer", "property", "channels"),
}


def balanced_sample(frame: pd.DataFrame, label_col: str, max_per_class: int, seed: int) -> pd.DataFrame:
    parts = []
    for label, part in frame.groupby(label_col, sort=True):
        if len(part) < 3:
            continue
        n = min(max_per_class, len(part))
        label_digest = hashlib.md5(str(label).encode("utf-8")).hexdigest()
        label_seed = int(label_digest[:8], 16) % 10000
        parts.append(part.sample(n=n, random_state=seed + label_seed))
    if not parts:
        return frame.iloc[0:0].copy()
    return pd.concat(parts, ignore_index=True)


def make_task_frames(
    df: pd.DataFrame,
    length: int,
    condition: str,
    tasks: list[str],
    seed: int,
    target_max_per_class: int,
    species_max_per_class: int,
    within_genus: str,
) -> list[tuple[str, str, pd.DataFrame]]:
    subset = df[(df["source_length"] == length) & (df["condition"] == condition)].copy()
    out: list[tuple[str, str, pd.DataFrame]] = []
    if subset.empty:
        return out
    if "target_background" in tasks:
        sampled = balanced_sample(subset, "target_binary", target_max_per_class, seed + length)
        if sampled["target_binary"].nunique() >= 2:
            out.append(("target_background", "target_binary", sampled))
    if "global_species" in tasks:
        sampled = balanced_sample(subset, "label", species_max_per_class, seed + length + 11)
        if sampled["label"].nunique() >= 2:
            out.append(("global_species", "label", sampled))
    if "within_genus_species" in tasks:
        genera = [g.strip() for g in within_genus.split(",") if g.strip()]
        if not genera or genera == ["all"]:
            genera = sorted(str(g) for g in subset["genus"].dropna().unique())
        for genus in genera:
            gdf = subset[subset["genus"] == genus].copy()
            sampled = balanced_sample(gdf, "label", species_max_per_class, seed + length + len(genus))
            if sampled["label"].nunique() >= 2:
                out.append((f"within_genus_species:{genus}", "label", sampled))
    return out


def encode_input(frame: pd.DataFrame, spec: ModelSpec, length: int, train_idx: np.ndarray) -> tuple[np.ndarray, dict[str, float | int | str]]:
    sequences = frame["sequence"].astype(str).str.upper().tolist()
    if spec.input_kind == "vector":
        x, info = build_feature_matrix(sequences, spec.input_name, length=length, train_indices=train_idx.tolist())
        x = np.asarray(x, dtype=np.float32)
        mean = x[train_idx].mean(axis=0, keepdims=True)
        std = x[train_idx].std(axis=0, keepdims=True)
        std[std < 1e-6] = 1.0
        x = (x - mean) / std
        meta: dict[str, float | int | str] = {
            "input_shape": f"{x.shape[1]}",
            "n_features": int(info.n_features),
            "density": float(info.density),
        }
        return x, meta
    if spec.input_kind == "channels":
        arr = np.stack([channel_matrix(seq, length, spec.input_name) for seq in sequences]).astype(np.float32)
        meta = {
            "input_shape": f"{arr.shape[1]}x{arr.shape[2]}",
            "n_features": int(arr.shape[1] * arr.shape[2]),
            "density": float(np.count_nonzero(arr) / arr.size),
        }
        return arr, meta
    raise ValueError(f"Unsupported input kind: {spec.input_kind}")


def make_model(spec: ModelSpec, input_shape: tuple[int, ...], n_classes: int):
    import torch
    from torch import nn

    if spec.family == "tabular_mlp":
        n_features = int(input_shape[0])
        hidden = min(96, max(24, n_features // 4))
        return nn.Sequential(
            nn.Linear(n_features, hidden),
            nn.ReLU(),
            nn.Linear(hidden, n_classes),
        )
    if spec.family == "cnn1d":
        channels, _length = input_shape
        return nn.Sequential(
            nn.Conv1d(channels, 24, kernel_size=7, padding=3),
            nn.ReLU(),
            nn.Conv1d(24, 32, kernel_size=5, padding=2),
            nn.ReLU(),
            nn.AdaptiveMaxPool1d(1),
            nn.Flatten(),
            nn.Linear(32, n_classes),
        )
    if spec.family == "tiny_transformer":
        channels, length = input_shape

        class TinyTransformer(nn.Module):
            def __init__(self) -> None:
                super().__init__()
                d_model = 32
                self.proj = nn.Linear(channels, d_model)
                self.pos = nn.Parameter(torch.zeros(1, length, d_model))
                layer = nn.TransformerEncoderLayer(
                    d_model=d_model,
                    nhead=4,
                    dim_feedforward=64,
                    dropout=0.0,
                    batch_first=True,
                    activation="relu",
                )
                self.encoder = nn.TransformerEncoder(layer, num_layers=1)
                self.head = nn.Linear(d_model, n_classes)

            def forward(self, x):
                x = x.transpose(1, 2)
                z = self.proj(x) + self.pos
                z = self.encoder(z)
                return self.head(z.mean(dim=1))

        return TinyTransformer()
    raise ValueError(f"Unsupported model family: {spec.family}")


def split_indices(y: np.ndarray, seed: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    indices = np.arange(len(y))
    train_val, test = train_test_split(indices, test_size=0.3, random_state=seed, stratify=y)
    y_train_val = y[train_val]
    _, counts = np.unique(y_train_val, return_counts=True)
    if len(counts) >= 2 and counts.min() >= 3:
        train, val = train_test_split(train_val, test_size=0.25, random_state=seed + 1, stratify=y_train_val)
    else:
        train, val = train_val, test
    return np.asarray(train), np.asarray(val), np.asarray(test)


def train_probe(
    x: np.ndarray,
    y: np.ndarray,
    spec: ModelSpec,
    seed: int,
    epochs: int,
    patience: int,
    batch_size: int,
    lr: float,
) -> tuple[dict[str, object], list[dict[str, object]]]:
    import torch
    from torch import nn

    set_global_seed(seed)
    train_idx, val_idx, test_idx = split_indices(y, seed)
    model = make_model(spec, tuple(x.shape[1:]), int(np.max(y) + 1))
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    loss_fn = nn.CrossEntropyLoss()
    x_t = torch.as_tensor(x, dtype=torch.float32)
    y_t = torch.as_tensor(y, dtype=torch.long)
    best_state = None
    best_val = float("inf")
    bad_epochs = 0
    history: list[dict[str, object]] = []

    for epoch in range(1, epochs + 1):
        model.train()
        rng = np.random.default_rng(seed + epoch)
        order = rng.permutation(train_idx)
        batch_losses = []
        for start in range(0, len(order), batch_size):
            batch = order[start : start + batch_size]
            optimizer.zero_grad(set_to_none=True)
            logits = model(x_t[batch])
            loss = loss_fn(logits, y_t[batch])
            loss.backward()
            optimizer.step()
            batch_losses.append(float(loss.detach().cpu()))

        model.eval()
        with torch.no_grad():
            val_loss = float(loss_fn(model(x_t[val_idx]), y_t[val_idx]).detach().cpu())
        train_loss = float(np.mean(batch_losses)) if batch_losses else float("nan")
        history.append({"epoch": epoch, "train_loss": train_loss, "val_loss": val_loss})
        if val_loss + 1e-6 < best_val:
            best_val = val_loss
            best_state = {k: v.detach().cpu().clone() for k, v in model.state_dict().items()}
            bad_epochs = 0
        else:
            bad_epochs += 1
            if bad_epochs >= patience:
                break

    if best_state is not None:
        model.load_state_dict(best_state)
    model.eval()
    with torch.no_grad():
        logits = model(x_t[test_idx])
        pred = torch.argmax(logits, dim=1).cpu().numpy()
    y_true = y[test_idx]
    result = {
        "n_samples": int(len(y)),
        "n_train": int(len(train_idx)),
        "n_val": int(len(val_idx)),
        "n_test": int(len(test_idx)),
        "n_classes": int(np.max(y) + 1),
        "epochs_ran": int(len(history)),
        "best_val_loss": float(best_val),
        "final_train_loss": float(history[-1]["train_loss"]) if history else float("nan"),
        "final_val_loss": float(history[-1]["val_loss"]) if history else float("nan"),
        "accuracy": float(accuracy_score(y_true, pred)),
        "macro_f1": float(f1_score(y_true, pred, average="macro", zero_division=0)),
    }
    return result, history


def completed_keys(path: Path) -> set[tuple[str, int, str, str, str, int]]:
    if not path.exists():
        return set()
    df = pd.read_csv(path)
    required = {"task", "length", "condition", "model", "input_name", "seed"}
    if not required.issubset(df.columns):
        return set()
    return set(
        (
            str(row.task),
            int(row.length),
            str(row.condition),
            str(row.model),
            str(row.input_name),
            int(row.seed),
        )
        for row in df.itertuples(index=False)
    )


def append_rows(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        return
    frame = pd.DataFrame(rows)
    if path.exists():
        old = pd.read_csv(path)
        frame = pd.concat([old, frame], ignore_index=True)
    frame.to_csv(path, index=False, encoding="utf-8-sig")


def write_summary(results: pd.DataFrame, output_dir: Path) -> None:
    lines: list[str] = []
    lines.append("# Stage-2 Neural Compatibility Probe\n")
    lines.append(
        "This deterministic probe tests whether compact tabular features, one-hot channels and DNA property channels can be read by small local neural models. It is not a clinical classifier benchmark.\n"
    )
    if results.empty:
        (output_dir / "neural_compatibility_summary.md").write_text("\n".join(lines), encoding="utf-8")
        return
    valid = results.dropna(subset=["macro_f1"]).copy()
    aggregate = (
        valid.groupby(["task", "model", "family", "input_name"], as_index=False)
        .agg(
            mean_macro_f1=("macro_f1", "mean"),
            mean_accuracy=("accuracy", "mean"),
            mean_epochs=("epochs_ran", "mean"),
            mean_features=("n_features", "mean"),
            n_runs=("macro_f1", "size"),
        )
        .sort_values(["task", "mean_macro_f1"], ascending=[True, False])
    )
    aggregate.to_csv(output_dir / "neural_compatibility_aggregate.csv", index=False, encoding="utf-8-sig")
    lines.append("## Aggregate by task and model\n")
    lines.append(aggregate.to_markdown(index=False, floatfmt=".3f"))
    lines.append("")

    clean = valid[valid["condition"] == "clean"][
        ["task", "length", "model", "input_name", "macro_f1", "accuracy"]
    ].rename(columns={"macro_f1": "clean_macro_f1", "accuracy": "clean_accuracy"})
    pert = valid[valid["condition"] != "clean"][
        ["task", "length", "condition", "model", "family", "input_name", "macro_f1", "accuracy"]
    ].copy()
    drop = pert.merge(clean, on=["task", "length", "model", "input_name"], how="left")
    if not drop.empty:
        drop["macro_f1_drop_vs_clean"] = drop["clean_macro_f1"] - drop["macro_f1"]
        drop["accuracy_drop_vs_clean"] = drop["clean_accuracy"] - drop["accuracy"]
        drop.to_csv(output_dir / "neural_compatibility_clean_drop.csv", index=False, encoding="utf-8-sig")
        drop_summary = (
            drop.groupby(["task", "condition", "model", "family", "input_name"], as_index=False)
            .agg(mean_macro_f1_drop=("macro_f1_drop_vs_clean", "mean"), mean_accuracy_drop=("accuracy_drop_vs_clean", "mean"))
            .sort_values(["task", "condition", "mean_macro_f1_drop"], ascending=[True, True, True])
        )
        drop_summary.to_csv(output_dir / "neural_compatibility_drop_summary.csv", index=False, encoding="utf-8-sig")
        lines.append("## Mean degradation versus clean\n")
        lines.append(drop_summary.to_markdown(index=False, floatfmt=".3f"))
        lines.append("")

    fig, axes = plt.subplots(1, min(3, valid["task"].nunique()), figsize=(13, 4.2), sharey=True)
    if not isinstance(axes, np.ndarray):
        axes = np.array([axes])
    for ax, (task, sub) in zip(axes.ravel(), aggregate.groupby("task", sort=True)):
        top = sub.sort_values("mean_macro_f1", ascending=False).head(8)
        labels = [f"{m}\n({inp})" for m, inp in zip(top["model"], top["input_name"])]
        ax.bar(labels, top["mean_macro_f1"], color="#3b5b92")
        ax.set_title(task.replace("_", " "))
        ax.set_ylim(0, 1.02)
        ax.tick_params(axis="x", rotation=35)
    axes[0].set_ylabel("Mean macro-F1")
    fig.suptitle("Deterministic lightweight neural probes are representation-dependent")
    fig.tight_layout(rect=[0, 0, 1, 0.90])
    fig.savefig(output_dir / "fig_stage2_neural_compatibility.png", dpi=260, bbox_inches="tight")
    plt.close(fig)

    (output_dir / "neural_compatibility_summary.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run deterministic lightweight neural compatibility probes for stage-2 representations.")
    parser.add_argument("--input", default=str(PROJECT_ROOT / "results" / "stage2" / "representation_grid" / "stage2_derived_reads.csv"))
    parser.add_argument("--output-dir", default=str(PROJECT_ROOT / "results" / "stage2" / "neural_compatibility"))
    parser.add_argument("--lengths", default="69,75,100,150")
    parser.add_argument("--conditions", default="clean,N_3pct,substitution_1pct_N_3pct")
    parser.add_argument("--tasks", default="target_background,global_species,within_genus_species")
    parser.add_argument("--within-genus", default="Enterobacter")
    parser.add_argument("--models", default="mlp_ckmer5,mlp_csp,mlp_hybrid,cnn_onehot,cnn_property,tiny_transformer_onehot,tiny_transformer_property")
    parser.add_argument("--target-max-per-class", type=int, default=160)
    parser.add_argument("--species-max-per-class", type=int, default=35)
    parser.add_argument("--epochs", type=int, default=24)
    parser.add_argument("--patience", type=int, default=5)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--lr", type=float, default=1e-3)
    parser.add_argument("--seed", type=int, default=606)
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()

    started = time.time()
    set_global_seed(args.seed)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    results_path = output_dir / "neural_compatibility_results.csv"
    history_path = output_dir / "neural_training_history.csv"
    done = completed_keys(results_path) if args.resume else set()

    df = pd.read_csv(args.input)
    df["source_length"] = df["source_length"].astype(int)
    df["sequence"] = df["sequence"].astype(str).str.upper()
    lengths = parse_int_list(args.lengths)
    conditions = parse_csv_list(args.conditions)
    tasks = parse_csv_list(args.tasks)
    models = parse_csv_list(args.models)

    rows: list[dict[str, object]] = []
    history_rows: list[dict[str, object]] = []
    total = 0
    for length in lengths:
        for condition in conditions:
            task_frames = make_task_frames(
                df,
                length=length,
                condition=condition,
                tasks=tasks,
                seed=args.seed,
                target_max_per_class=args.target_max_per_class,
                species_max_per_class=args.species_max_per_class,
                within_genus=args.within_genus,
            )
            for task, label_col, frame in task_frames:
                labels = frame[label_col].astype(str).to_numpy()
                unique, counts = np.unique(labels, return_counts=True)
                if len(unique) < 2 or counts.min() < 3:
                    continue
                y = LabelEncoder().fit_transform(labels)
                for model_name in models:
                    if model_name not in MODEL_SPECS:
                        raise ValueError(f"Unsupported model: {model_name}")
                    spec = MODEL_SPECS[model_name]
                    key = (task, int(length), condition, model_name, spec.input_name, int(args.seed))
                    if key in done:
                        continue
                    combo_seed = args.seed + length * 17 + len(task) * 13 + len(condition) * 7 + len(model_name)
                    train_idx, _, _ = split_indices(y, combo_seed)
                    try:
                        x, meta = encode_input(frame, spec, length=length, train_idx=train_idx)
                        result, history = train_probe(
                            x,
                            y,
                            spec,
                            seed=combo_seed,
                            epochs=args.epochs,
                            patience=args.patience,
                            batch_size=args.batch_size,
                            lr=args.lr,
                        )
                        row: dict[str, object] = {
                            "task": task,
                            "label_col": label_col,
                            "length": int(length),
                            "condition": condition,
                            "model": model_name,
                            "family": spec.family,
                            "input_name": spec.input_name,
                            "input_kind": spec.input_kind,
                            "seed": int(args.seed),
                            "combo_seed": int(combo_seed),
                            **meta,
                            **result,
                        }
                        for item in history:
                            history_rows.append(
                                {
                                    "task": task,
                                    "length": int(length),
                                    "condition": condition,
                                    "model": model_name,
                                    "input_name": spec.input_name,
                                    "seed": int(args.seed),
                                    "combo_seed": int(combo_seed),
                                    **item,
                                }
                            )
                        rows.append(row)
                        total += 1
                        append_rows(results_path, [row])
                        append_rows(history_path, history_rows)
                        history_rows = []
                        print(
                            f"[neural] {total:04d} task={task} length={length} condition={condition} model={model_name} "
                            f"f1={row['macro_f1']:.3f} epochs={row['epochs_ran']} val={row['best_val_loss']:.3f}",
                            flush=True,
                        )
                    except Exception as exc:
                        row = {
                            "task": task,
                            "label_col": label_col,
                            "length": int(length),
                            "condition": condition,
                            "model": model_name,
                            "family": spec.family,
                            "input_name": spec.input_name,
                            "input_kind": spec.input_kind,
                            "seed": int(args.seed),
                            "combo_seed": int(combo_seed),
                            "error": f"{type(exc).__name__}: {exc}",
                        }
                        rows.append(row)
                        append_rows(results_path, [row])
                        print(f"[neural] ERROR {task} {length} {condition} {model_name}: {row['error']}", flush=True)

    results = pd.read_csv(results_path) if results_path.exists() else pd.DataFrame(rows)
    write_summary(results, output_dir)
    run_info = {
        "elapsed_seconds": time.time() - started,
        "input": args.input,
        "lengths": lengths,
        "conditions": conditions,
        "tasks": tasks,
        "within_genus": args.within_genus,
        "models": models,
        "target_max_per_class": args.target_max_per_class,
        "species_max_per_class": args.species_max_per_class,
        "epochs": args.epochs,
        "patience": args.patience,
        "batch_size": args.batch_size,
        "lr": args.lr,
        "seed": args.seed,
        "n_result_rows": int(len(results)),
    }
    (output_dir / "neural_compatibility_run.json").write_text(json.dumps(run_info, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote neural compatibility results to {output_dir}")


if __name__ == "__main__":
    main()
