from __future__ import annotations

import argparse
import json
import sys
import time
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.decomposition import NMF, PCA, TruncatedSVD
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import train_test_split
from sklearn.neighbors import NearestCentroid
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import LabelEncoder, StandardScaler, normalize


def _find_project_root(start: Path) -> Path:
    for candidate in [start.parent, *start.parents]:
        if (candidate / "methods").is_dir() and (candidate / "configs").is_dir():
            return candidate
    raise RuntimeError("Could not locate the release repository root.")


PROJECT_ROOT = _find_project_root(Path(__file__).resolve())
sys.path.insert(0, str(PROJECT_ROOT))

from experiments.main.run_stage2_representation_grid import balanced_sample, paired_subsets, parse_csv_list, parse_int_list, set_global_seed  # noqa: E402
from src.stage2_features import build_feature_matrix, paired_retrieval_metrics  # noqa: E402


REP_LABELS = {
    "ckmer4_property_multiscale_mean_l2": "CK4P-MSP",
    "ckmer4_property_l2": "CK4+P",
    "ckmer4_count_l2": "CK4",
    "ckmer5_count_l2": "CK5",
    "ckmer7_count_l2": "CK7",
}


@dataclass(frozen=True)
class ReducedSpec:
    base_rep: str
    reducer: str
    target_dim: int

    @property
    def name(self) -> str:
        short = self.base_rep.replace("ckmer", "ck").replace("_count_l2", "")
        return f"{short}_{self.reducer}{self.target_dim}"

    @property
    def label(self) -> str:
        base = REP_LABELS.get(self.base_rep, self.base_rep)
        return f"{base} {self.reducer.upper()}-{self.target_dim}"


def make_reducer(kind: str, n_components: int, seed: int):
    if kind == "pca":
        return PCA(n_components=n_components, svd_solver="randomized", random_state=seed)
    if kind == "svd":
        return TruncatedSVD(n_components=n_components, random_state=seed)
    if kind == "nmf":
        return NMF(n_components=n_components, init="nndsvda", random_state=seed, max_iter=500)
    raise ValueError(f"Unsupported reducer: {kind}")


def reduced_features(
    sequences: list[str],
    length: int,
    train_indices: list[int],
    spec: ReducedSpec,
    seed: int,
) -> tuple[np.ndarray, int]:
    x, _ = build_feature_matrix(sequences, spec.base_rep, length=length, train_indices=train_indices)
    x = np.nan_to_num(np.asarray(x, dtype=np.float64), nan=0.0, posinf=0.0, neginf=0.0)
    train_x = x[train_indices]
    max_components = min(spec.target_dim, train_x.shape[0] - 1, train_x.shape[1])
    if max_components < 1:
        raise ValueError(f"Cannot fit {spec.name}: too few samples or features")
    reducer = make_reducer(spec.reducer, max_components, seed)
    z_train = train_x
    z_all = x
    if spec.reducer == "nmf":
        z_train = np.clip(z_train, 0.0, None)
        z_all = np.clip(z_all, 0.0, None)
    reducer.fit(z_train)
    z = reducer.transform(z_all)
    z = normalize(np.nan_to_num(z, nan=0.0, posinf=0.0, neginf=0.0), norm="l2", axis=1)
    return z, int(max_components)


def build_named_features(
    sequences: list[str],
    length: int,
    train_indices: list[int],
    representation: str,
    specs: dict[str, ReducedSpec],
    seed: int,
) -> tuple[np.ndarray, int, str]:
    if representation in specs:
        x, n_components = reduced_features(sequences, length, train_indices, specs[representation], seed=seed)
        return x, n_components, specs[representation].label
    x, info = build_feature_matrix(sequences, representation, length=length, train_indices=train_indices)
    x = normalize(np.nan_to_num(np.asarray(x, dtype=np.float64), nan=0.0, posinf=0.0, neginf=0.0), norm="l2", axis=1)
    return x, int(info.n_features), REP_LABELS.get(representation, representation)


def run_stability(
    reads: pd.DataFrame,
    lengths: list[int],
    conditions: list[str],
    representations: list[str],
    specs: dict[str, ReducedSpec],
    max_pairs: int,
    seed: int,
) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    perturbations = [condition for condition in conditions if condition != "clean"]
    for length in lengths:
        for condition in perturbations:
            clean, pert = paired_subsets(reads, length, condition)
            if clean.empty:
                continue
            if max_pairs > 0 and len(clean) > max_pairs:
                keep = clean["clean_read_id"].drop_duplicates().sample(n=max_pairs, random_state=seed + length).tolist()
                clean = clean[clean["clean_read_id"].isin(keep)].sort_values("clean_read_id").reset_index(drop=True)
                pert = pert[pert["clean_read_id"].isin(keep)].sort_values("clean_read_id").reset_index(drop=True)
            sequences = clean["sequence"].astype(str).tolist() + pert["sequence"].astype(str).tolist()
            train_indices = list(range(len(clean)))
            for rep in representations:
                try:
                    x, n_features, label = build_named_features(sequences, length, train_indices, rep, specs, seed + length)
                    clean_x = x[: len(clean)]
                    pert_x = x[len(clean) :]
                    metrics = paired_retrieval_metrics(clean_x, pert_x)
                    metrics.update(
                        {
                            "length": int(length),
                            "condition": condition,
                            "representation": rep,
                            "representation_label": label,
                            "n_pairs": int(len(clean)),
                            "n_features": int(n_features),
                        }
                    )
                    if rep in specs:
                        metrics.update(
                            {
                                "base_representation": specs[rep].base_rep,
                                "reducer": specs[rep].reducer,
                                "target_dim": specs[rep].target_dim,
                            }
                        )
                    rows.append(metrics)
                except Exception as exc:
                    rows.append(
                        {
                            "length": int(length),
                            "condition": condition,
                            "representation": rep,
                            "error": f"{type(exc).__name__}: {exc}",
                        }
                    )
    return pd.DataFrame(rows)


def classifier_registry(seed: int) -> dict[str, object]:
    return {
        "nearest_centroid": NearestCentroid(),
        "logistic": make_pipeline(StandardScaler(), LogisticRegression(max_iter=4000, random_state=seed)),
    }


def evaluate_readout(
    subset: pd.DataFrame,
    representation: str,
    specs: dict[str, ReducedSpec],
    label_col: str,
    length: int,
    seed: int,
    classifiers: list[str],
) -> list[dict[str, object]]:
    labels = subset[label_col].astype(str).to_numpy()
    unique, counts = np.unique(labels, return_counts=True)
    if len(unique) < 2 or np.min(counts) < 3:
        return [{"representation": representation, "classifier": "all", "error": "not enough labels"}]
    y = LabelEncoder().fit_transform(labels)
    idx = np.arange(len(y))
    train_idx, test_idx = train_test_split(idx, test_size=0.3, random_state=seed, stratify=y)
    x, n_features, label = build_named_features(
        subset["sequence"].astype(str).tolist(),
        length=length,
        train_indices=train_idx.tolist(),
        representation=representation,
        specs=specs,
        seed=seed + length,
    )
    rows: list[dict[str, object]] = []
    models = classifier_registry(seed)
    for clf_name in classifiers:
        model = models[clf_name]
        try:
            model.fit(x[train_idx], y[train_idx])
            pred = model.predict(x[test_idx])
            rows.append(
                {
                    "representation": representation,
                    "representation_label": label,
                    "classifier": clf_name,
                    "n_samples": int(len(subset)),
                    "n_classes": int(len(unique)),
                    "n_features": int(n_features),
                    "accuracy": float(accuracy_score(y[test_idx], pred)),
                    "macro_f1": float(f1_score(y[test_idx], pred, average="macro", zero_division=0)),
                }
            )
        except Exception as exc:
            rows.append({"representation": representation, "classifier": clf_name, "error": f"{type(exc).__name__}: {exc}"})
    return rows


def run_readout(
    reads: pd.DataFrame,
    lengths: list[int],
    conditions: list[str],
    representations: list[str],
    specs: dict[str, ReducedSpec],
    classifiers: list[str],
    seed: int,
    max_per_class: int,
) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for length in lengths:
        for condition in conditions:
            subset = reads[(reads["source_length"].eq(length)) & (reads["condition"].eq(condition))].copy()
            if subset.empty:
                continue
            for genus, genus_df in subset.groupby("genus"):
                for task, label_col in (("within_genus_species", "label"), ("target_background", "target_binary")):
                    if genus_df[label_col].nunique() < 2:
                        continue
                    sampled = balanced_sample(genus_df, label_col, max_per_class=max_per_class, seed=seed + length)
                    for rep in representations:
                        for row in evaluate_readout(sampled, rep, specs, label_col, length, seed, classifiers):
                            row.update(
                                {
                                    "task": task,
                                    "genus": genus,
                                    "length": int(length),
                                    "condition": condition,
                                    "label_col": label_col,
                                }
                            )
                            rows.append(row)
    return pd.DataFrame(rows)


def summarize(stability: pd.DataFrame, readout: pd.DataFrame, out_dir: Path) -> None:
    lines = [
        "# Same-dimension dimensionality-reduction baselines",
        "",
        "High-dimensional canonical k-mer features were projected to the same dimensional ranges as the compact property-aware representations. Reducers were fitted on the clean/train portion within each analysis cell, then applied to paired perturbed reads or readout test examples.",
        "",
    ]
    valid = stability[~stability.get("error", pd.Series(index=stability.index, dtype=object)).notna()].copy() if not stability.empty else stability
    if not valid.empty:
        stab = (
            valid.groupby(["representation", "representation_label"], as_index=False)
            .agg(
                n_cells=("paired_cosine_mean", "count"),
                paired_cosine=("paired_cosine_mean", "mean"),
                l2_drift=("l2_delta_mean", "mean"),
                retrieval_top1=("retrieval_top1", "mean"),
                median_features=("n_features", "median"),
            )
            .sort_values(["paired_cosine", "l2_drift"], ascending=[False, True])
        )
        stab.to_csv(out_dir / "dimension_reduction_stability_summary.csv", index=False, encoding="utf-8-sig")
        lines.extend(["## Stability summary", "", stab.to_markdown(index=False, floatfmt=".3f"), ""])
    valid_r = readout.dropna(subset=["macro_f1"]).copy() if not readout.empty and "macro_f1" in readout else pd.DataFrame()
    if not valid_r.empty:
        read = (
            valid_r.groupby(["representation", "representation_label", "classifier"], as_index=False)
            .agg(
                n_cells=("macro_f1", "count"),
                macro_f1=("macro_f1", "mean"),
                accuracy=("accuracy", "mean"),
                median_features=("n_features", "median"),
            )
            .sort_values(["macro_f1", "accuracy"], ascending=False)
        )
        read.to_csv(out_dir / "dimension_reduction_readout_summary.csv", index=False, encoding="utf-8-sig")
        lines.extend(["## Readout summary", "", read.to_markdown(index=False, floatfmt=".3f"), ""])
    (out_dir / "dimension_reduction_summary.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run same-dimension PCA/SVD/NMF k-mer reduction baselines for reviewer response.")
    parser.add_argument("--input", default=str(PROJECT_ROOT / "results" / "stage3" / "position_property_ablation" / "stage3_compact_baseline_reads.csv"))
    parser.add_argument("--output-dir", default=str(PROJECT_ROOT / "results" / "stage3" / "reviewer_response" / "dimension_reduction_baselines"))
    parser.add_argument("--lengths", default="69,75,100,150")
    parser.add_argument("--stability-conditions", default="substitution_1pct,N_3pct,trim_5bp,substitution_1pct_N_3pct,local_mismatch_6bp,short_indel")
    parser.add_argument("--readout-conditions", default="clean,substitution_1pct,N_3pct")
    parser.add_argument("--base-representations", default="ckmer5_count_l2,ckmer7_count_l2")
    parser.add_argument("--reducers", default="pca,svd")
    parser.add_argument("--target-dims", default="147,222")
    parser.add_argument("--comparators", default="ckmer4_count_l2,ckmer4_property_l2,ckmer4_property_multiscale_mean_l2,ckmer5_count_l2")
    parser.add_argument("--classifiers", default="nearest_centroid,logistic")
    parser.add_argument("--max-pairs", type=int, default=250)
    parser.add_argument("--max-per-class", type=int, default=40)
    parser.add_argument("--seed", type=int, default=20260624)
    args = parser.parse_args()

    started = time.time()
    set_global_seed(args.seed)
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    reads = pd.read_csv(args.input)
    reads["source_length"] = reads["source_length"].astype(int)
    reads["sequence"] = reads["sequence"].astype(str).str.upper()

    specs_list = [
        ReducedSpec(base_rep=base, reducer=reducer, target_dim=target_dim)
        for base in parse_csv_list(args.base_representations)
        for reducer in parse_csv_list(args.reducers)
        for target_dim in parse_int_list(args.target_dims)
    ]
    specs = {spec.name: spec for spec in specs_list}
    reduced_names = list(specs.keys())
    comparators = parse_csv_list(args.comparators)
    representations = comparators + reduced_names
    lengths = parse_int_list(args.lengths)

    stability = run_stability(
        reads,
        lengths=lengths,
        conditions=parse_csv_list(args.stability_conditions),
        representations=representations,
        specs=specs,
        max_pairs=args.max_pairs,
        seed=args.seed,
    )
    stability.to_csv(out_dir / "dimension_reduction_stability.csv", index=False, encoding="utf-8-sig")

    readout = run_readout(
        reads,
        lengths=lengths,
        conditions=parse_csv_list(args.readout_conditions),
        representations=representations,
        specs=specs,
        classifiers=parse_csv_list(args.classifiers),
        seed=args.seed,
        max_per_class=args.max_per_class,
    )
    readout.to_csv(out_dir / "dimension_reduction_readout.csv", index=False, encoding="utf-8-sig")
    summarize(stability, readout, out_dir)
    (out_dir / "dimension_reduction_run.json").write_text(
        json.dumps(
            {
                "elapsed_seconds": time.time() - started,
                "input": args.input,
                "lengths": lengths,
                "stability_conditions": parse_csv_list(args.stability_conditions),
                "readout_conditions": parse_csv_list(args.readout_conditions),
                "base_representations": parse_csv_list(args.base_representations),
                "reducers": parse_csv_list(args.reducers),
                "target_dims": parse_int_list(args.target_dims),
                "comparators": comparators,
                "max_pairs": args.max_pairs,
                "max_per_class": args.max_per_class,
                "n_stability_rows": int(len(stability)),
                "n_readout_rows": int(len(readout)),
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    print(f"Wrote dimension-reduction reviewer analyses to {out_dir}")


if __name__ == "__main__":
    main()

