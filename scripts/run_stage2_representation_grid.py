from __future__ import annotations

import argparse
import json
import random
import re
import sys
import time
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import train_test_split
from sklearn.neighbors import NearestCentroid
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import LabelEncoder, StandardScaler

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.sequence_utils import inject_indel, mask_n, mutate_substitutions, trim_sequence
from src.stage2_features import build_feature_matrix, paired_retrieval_metrics

warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=RuntimeWarning)


def parse_csv_list(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def parse_int_list(value: str) -> list[int]:
    return [int(item.strip()) for item in value.split(",") if item.strip()]


def set_global_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    try:
        import torch  # type: ignore

        torch.manual_seed(seed)
        if hasattr(torch, "cuda"):
            torch.cuda.manual_seed_all(seed)
        if hasattr(torch, "use_deterministic_algorithms"):
            torch.use_deterministic_algorithms(True, warn_only=True)
    except Exception:
        pass


def apply_stage2_condition(row: pd.Series, condition: str, seed: int) -> dict[str, object]:
    seq = str(row["sequence"]).upper()
    rng = random.Random(f"{seed}:{row['clean_read_id']}:{condition}")
    profile: dict[str, object] = {"condition": condition}
    substitution_match = re.fullmatch(r"substitution_(\d+)pct", condition)
    n_match = re.fullmatch(r"N_(\d+)pct", condition)
    n_cluster_match = re.fullmatch(r"N_cluster_(\d+)pct", condition)
    combined_match = re.fullmatch(r"substitution_(\d+)pct_N_(\d+)pct", condition)
    trim_match = re.fullmatch(r"trim_(\d+)bp", condition)
    indel_match = re.fullmatch(r"short_indel_(\d+)pct", condition)
    local_mismatch_match = re.fullmatch(r"local_mismatch_(\d+)bp", condition)
    if condition == "clean":
        out_seq = seq
    elif condition == "short_indel":
        out_seq, events = inject_indel(seq, 0.01, rng)
        profile["indel_rate"] = 0.01
        profile["indel_events"] = events
    elif substitution_match:
        rate = int(substitution_match.group(1)) / 100.0
        out_seq, positions = mutate_substitutions(seq, rate, rng)
        profile["substitution_rate"] = rate
        profile["substitution_positions"] = positions
    elif n_match:
        rate = int(n_match.group(1)) / 100.0
        out_seq, positions = mask_n(seq, rate, rng)
        profile["N_rate"] = rate
        profile["N_positions"] = positions
    elif n_cluster_match:
        rate = int(n_cluster_match.group(1)) / 100.0
        out_seq, positions = mask_n(seq, rate, rng, mode="cluster")
        profile["N_rate"] = rate
        profile["N_mode"] = "cluster"
        profile["N_positions"] = positions
    elif combined_match:
        sub_rate = int(combined_match.group(1)) / 100.0
        n_rate = int(combined_match.group(2)) / 100.0
        mid_seq, sub_positions = mutate_substitutions(seq, sub_rate, rng)
        out_seq, n_positions = mask_n(mid_seq, n_rate, rng)
        profile["substitution_rate"] = sub_rate
        profile["N_rate"] = n_rate
        profile["substitution_positions"] = sub_positions
        profile["N_positions"] = n_positions
    elif trim_match:
        trim_bp = int(trim_match.group(1))
        out_seq = trim_sequence(seq, max(1, len(seq) - trim_bp), mode="right", rng=rng)
        profile["trim_bp"] = trim_bp
    elif indel_match:
        rate = int(indel_match.group(1)) / 100.0
        out_seq, events = inject_indel(seq, rate, rng)
        profile["indel_rate"] = rate
        profile["indel_events"] = events
    elif local_mismatch_match:
        chars = list(seq)
        block = min(int(local_mismatch_match.group(1)), len(chars))
        start = rng.randrange(0, max(1, len(chars) - block + 1))
        positions = []
        for pos in range(start, start + block):
            base = chars[pos]
            if base in "ACGT":
                choices = [b for b in "ACGT" if b != base]
                chars[pos] = rng.choice(choices)
                positions.append(pos)
        out_seq = "".join(chars)
        profile["local_mismatch_bp"] = block
        profile["local_mismatch_positions"] = positions
    else:
        raise ValueError(f"Unsupported condition: {condition}")
    out = row.to_dict()
    out["sequence"] = out_seq
    out["condition"] = condition
    out["length"] = len(out_seq)
    out["read_id"] = f"{row['clean_read_id']}_{condition}"
    out["mutation_profile"] = json.dumps(profile, ensure_ascii=False, sort_keys=True)
    return out


def derive_stage2_reads(
    clean_df: pd.DataFrame,
    lengths: list[int],
    conditions: list[str],
    seed: int,
    max_clean_per_length: int,
) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for length in lengths:
        subset = clean_df[(clean_df["source_length"] == length) & (clean_df["condition"] == "clean")].copy()
        if subset.empty:
            continue
        if max_clean_per_length > 0 and len(subset) > max_clean_per_length:
            subset = subset.sample(n=max_clean_per_length, random_state=seed + length)
        for _, row in subset.iterrows():
            for condition in conditions:
                rows.append(apply_stage2_condition(row, condition, seed))
    out = pd.DataFrame(rows)
    out["source_length"] = out["source_length"].astype(int)
    out["length"] = out["length"].astype(int)
    return out


def paired_subsets(df: pd.DataFrame, length: int, condition: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    clean = df[(df["source_length"] == length) & (df["condition"] == "clean")].copy()
    pert = df[(df["source_length"] == length) & (df["condition"] == condition)].copy()
    common = sorted(set(clean["clean_read_id"]) & set(pert["clean_read_id"]))
    clean = clean[clean["clean_read_id"].isin(common)].sort_values("clean_read_id").reset_index(drop=True)
    pert = pert[pert["clean_read_id"].isin(common)].sort_values("clean_read_id").reset_index(drop=True)
    return clean, pert


def run_stability_grid(
    df: pd.DataFrame,
    lengths: list[int],
    conditions: list[str],
    representations: list[str],
    max_pairs: int,
    seed: int,
    output_path: Path | None = None,
) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    perturbations = [condition for condition in conditions if condition != "clean"]
    for length in lengths:
        for condition in perturbations:
            clean, pert = paired_subsets(df, length, condition)
            if clean.empty:
                continue
            if max_pairs > 0 and len(clean) > max_pairs:
                keep = clean["clean_read_id"].drop_duplicates().sample(n=max_pairs, random_state=seed + length).tolist()
                clean = clean[clean["clean_read_id"].isin(keep)].sort_values("clean_read_id").reset_index(drop=True)
                pert = pert[pert["clean_read_id"].isin(keep)].sort_values("clean_read_id").reset_index(drop=True)
            all_seq = clean["sequence"].tolist() + pert["sequence"].tolist()
            train_idx = list(range(len(clean)))
            for rep in representations:
                try:
                    x, info = build_feature_matrix(all_seq, rep, length=length, train_indices=train_idx)
                    clean_x = x[: len(clean)]
                    pert_x = x[len(clean) :]
                    metric = paired_retrieval_metrics(clean_x, pert_x)
                    metric.update(
                        {
                            "length": length,
                            "condition": condition,
                            "representation": rep,
                            "n_pairs": int(len(clean)),
                            "n_features": info.n_features,
                            "density": info.density,
                            "avg_nnz_per_read": info.avg_nnz_per_read,
                        }
                    )
                    rows.append(metric)
                except Exception as exc:
                    rows.append(
                        {
                            "length": length,
                            "condition": condition,
                            "representation": rep,
                            "n_pairs": int(len(clean)),
                            "error": f"{type(exc).__name__}: {exc}",
                        }
                    )
                if output_path is not None and rows:
                    pd.DataFrame(rows).to_csv(output_path, index=False, encoding="utf-8-sig")
                    print(f"[stage2-grid] stability progress rows={len(rows)} length={length} condition={condition} rep={rep}", flush=True)
    return pd.DataFrame(rows)


def balanced_sample(frame: pd.DataFrame, label_col: str, max_per_class: int, seed: int) -> pd.DataFrame:
    parts = []
    for _, part in frame.groupby(label_col):
        parts.append(part.sample(n=min(max_per_class, len(part)), random_state=seed))
    return pd.concat(parts, ignore_index=True) if parts else frame.iloc[0:0].copy()


def evaluate_readout(
    subset: pd.DataFrame,
    rep: str,
    label_col: str,
    length: int,
    seed: int,
    classifiers: list[str],
) -> list[dict[str, object]]:
    labels = subset[label_col].astype(str).to_numpy()
    unique, counts = np.unique(labels, return_counts=True)
    if len(unique) < 2 or np.min(counts) < 3:
        return [{"error": "not enough labels", "representation": rep, "classifier": "all"}]
    y = LabelEncoder().fit_transform(labels)
    idx = np.arange(len(y))
    train_idx, test_idx = train_test_split(idx, test_size=0.3, random_state=seed, stratify=y)
    x, info = build_feature_matrix(subset["sequence"].tolist(), rep, length=length, train_indices=train_idx.tolist())
    models = {
        "nearest_centroid": NearestCentroid(),
        "logistic": make_pipeline(StandardScaler(), LogisticRegression(max_iter=3000, random_state=seed)),
        "mlp": make_pipeline(
            StandardScaler(),
            MLPClassifier(hidden_layer_sizes=(48,), max_iter=400, early_stopping=True, random_state=seed),
        ),
    }
    rows: list[dict[str, object]] = []
    for clf_name in classifiers:
        model = models[clf_name]
        try:
            model.fit(x[train_idx], y[train_idx])
            pred = model.predict(x[test_idx])
            rows.append(
                {
                    "representation": rep,
                    "classifier": clf_name,
                    "n_samples": int(len(subset)),
                    "n_classes": int(len(unique)),
                    "n_features": info.n_features,
                    "accuracy": float(accuracy_score(y[test_idx], pred)),
                    "macro_f1": float(f1_score(y[test_idx], pred, average="macro", zero_division=0)),
                }
            )
        except Exception as exc:
            rows.append({"representation": rep, "classifier": clf_name, "error": f"{type(exc).__name__}: {exc}"})
    return rows


def run_readout_grid(
    df: pd.DataFrame,
    lengths: list[int],
    conditions: list[str],
    representations: list[str],
    classifiers: list[str],
    seed: int,
    max_per_class: int,
) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for length in lengths:
        for condition in conditions:
            subset = df[(df["source_length"] == length) & (df["condition"] == condition)].copy()
            if subset.empty:
                continue
            for genus, genus_df in subset.groupby("genus"):
                for task, label_col in (("within_genus_species", "label"), ("target_background", "target_binary")):
                    if genus_df[label_col].nunique() < 2:
                        continue
                    sampled = balanced_sample(genus_df, label_col, max_per_class=max_per_class, seed=seed + length)
                    for rep in representations:
                        for row in evaluate_readout(sampled, rep, label_col, length, seed, classifiers):
                            row.update(
                                {
                                    "task": task,
                                    "genus": genus,
                                    "length": length,
                                    "condition": condition,
                                    "label_col": label_col,
                                }
                            )
                            rows.append(row)
    return pd.DataFrame(rows)


def write_summary(stability: pd.DataFrame, readout: pd.DataFrame, output_dir: Path) -> None:
    lines: list[str] = []
    lines.append("# Stage-2 Representation Grid Summary\n")
    lines.append("This run compares exact canonical k-mer evidence, canonical spaced counts, CSP and hybrid features under short-read perturbations.\n")
    valid = stability[~stability.get("error", pd.Series(index=stability.index, dtype=object)).notna()].copy() if not stability.empty else stability
    if not valid.empty:
        cols = ["condition", "length", "representation", "paired_cosine_mean", "l2_delta_mean", "retrieval_top1", "n_features", "density"]
        best = valid.sort_values(["condition", "length", "paired_cosine_mean"], ascending=[True, True, False]).groupby(["condition", "length"], as_index=False).first()
        lines.append("## Best perturbation stability by condition and length\n")
        lines.append(best[cols].to_markdown(index=False, floatfmt=".3f"))
        lines.append("")
        h = valid[valid["representation"].str.contains("hybrid", regex=False)]
        if not h.empty:
            lines.append("## Hybrid overview\n")
            lines.append(h.groupby(["condition", "length"], as_index=False).agg(paired_cosine_mean=("paired_cosine_mean", "mean"), l2_delta_mean=("l2_delta_mean", "mean"), retrieval_top1=("retrieval_top1", "mean")).to_markdown(index=False, floatfmt=".3f"))
            lines.append("")
    if not readout.empty and "macro_f1" in readout:
        valid_r = readout.dropna(subset=["macro_f1"])
        if not valid_r.empty:
            grouped = valid_r.groupby(["task", "condition", "length", "representation", "classifier"], as_index=False).agg(mean_macro_f1=("macro_f1", "mean"), mean_accuracy=("accuracy", "mean"))
            best_r = grouped.sort_values(["task", "condition", "length", "mean_macro_f1"], ascending=[True, True, True, False]).groupby(["task", "condition", "length"], as_index=False).first()
            lines.append("## Best readout probes\n")
            lines.append(best_r.to_markdown(index=False, floatfmt=".3f"))
            lines.append("")
    (output_dir / "stage2_representation_grid_summary.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run stage-2 representation advantage grid.")
    parser.add_argument("--input", default=str(PROJECT_ROOT / "data" / "real_slices" / "close_relative_reads.csv"))
    parser.add_argument("--output-dir", default=str(PROJECT_ROOT / "results" / "stage2" / "representation_grid"))
    parser.add_argument("--lengths", default="69,75,100,110,125,150,300")
    parser.add_argument("--readout-lengths", default="69,75,100,150")
    parser.add_argument("--conditions", default="clean,substitution_1pct,N_3pct,trim_5bp,substitution_1pct_N_3pct,short_indel,local_mismatch_6bp")
    parser.add_argument("--representations", default="ckmer5_count_l2,ckmer7_count_l2,cspaced_count_l2,cspaced_property_l2,hybrid_ckmer5_csp,hybrid_ckmer7_csp")
    parser.add_argument("--readout-representations", default="ckmer5_count_l2,cspaced_count_l2,cspaced_property_l2,hybrid_ckmer5_csp")
    parser.add_argument("--classifiers", default="nearest_centroid,logistic,mlp")
    parser.add_argument("--max-clean-per-length", type=int, default=900)
    parser.add_argument("--max-retrieval-pairs", type=int, default=600)
    parser.add_argument("--max-per-class", type=int, default=80)
    parser.add_argument("--seed", type=int, default=202)
    args = parser.parse_args()

    started = time.time()
    set_global_seed(args.seed)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    source = pd.read_csv(args.input)
    source["source_length"] = source["source_length"].astype(int)
    source["sequence"] = source["sequence"].astype(str).str.upper()
    lengths = parse_int_list(args.lengths)
    readout_lengths = parse_int_list(args.readout_lengths)
    conditions = parse_csv_list(args.conditions)
    reps = parse_csv_list(args.representations)
    readout_reps = parse_csv_list(args.readout_representations)
    classifiers = parse_csv_list(args.classifiers)

    print("[stage2-grid] deriving reads...", flush=True)
    stage2_reads = derive_stage2_reads(source, lengths, conditions, seed=args.seed, max_clean_per_length=args.max_clean_per_length)
    stage2_reads.to_csv(output_dir / "stage2_derived_reads.csv", index=False, encoding="utf-8-sig")
    print(f"[stage2-grid] derived {len(stage2_reads)} reads", flush=True)

    print("[stage2-grid] running stability grid...", flush=True)
    stability = run_stability_grid(
        stage2_reads,
        lengths=lengths,
        conditions=conditions,
        representations=reps,
        max_pairs=args.max_retrieval_pairs,
        seed=args.seed,
        output_path=output_dir / "stability_grid.csv",
    )
    stability.to_csv(output_dir / "stability_grid.csv", index=False, encoding="utf-8-sig")
    print(f"[stage2-grid] wrote {len(stability)} stability rows", flush=True)

    print("[stage2-grid] running readout grid...", flush=True)
    readout_conditions = [condition for condition in conditions if condition in {"clean", "substitution_1pct", "N_3pct", "trim_5bp", "substitution_1pct_N_3pct"}]
    readout = run_readout_grid(
        stage2_reads,
        lengths=readout_lengths,
        conditions=readout_conditions,
        representations=readout_reps,
        classifiers=classifiers,
        seed=args.seed,
        max_per_class=args.max_per_class,
    )
    readout.to_csv(output_dir / "readout_grid.csv", index=False, encoding="utf-8-sig")
    print(f"[stage2-grid] wrote {len(readout)} readout rows", flush=True)
    write_summary(stability, readout, output_dir)
    (output_dir / "stage2_representation_grid_run.json").write_text(
        json.dumps(
            {
                "elapsed_seconds": time.time() - started,
                "input": args.input,
                "lengths": lengths,
                "readout_lengths": readout_lengths,
                "conditions": conditions,
                "representations": reps,
                "readout_representations": readout_reps,
                "classifiers": classifiers,
                "n_stage2_reads": int(len(stage2_reads)),
                "n_stability_rows": int(len(stability)),
                "n_readout_rows": int(len(readout)),
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    print(f"Wrote stage-2 representation grid to {output_dir}")


if __name__ == "__main__":
    main()
