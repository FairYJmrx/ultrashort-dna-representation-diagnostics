"""Screen positional k-mer candidate blocks across the manuscript evidence layers."""

from __future__ import annotations

import argparse
import json
import platform
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


def _find_project_root(start: Path) -> Path:
    for candidate in [start.parent, *start.parents]:
        if (candidate / "methods").is_dir() and (candidate / "configs").is_dir():
            return candidate
    raise RuntimeError("Could not locate the release repository root.")


PROJECT_ROOT = _find_project_root(Path(__file__).resolve())
sys.path.insert(0, str(PROJECT_ROOT))

from methods.ck4p_msp import CK4PMSPConfig, build_ck4_block  # noqa: E402
from methods.experimental_positional_kmer import (  # noqa: E402
    CANDIDATE_LABELS,
    build_positional_kmer_candidate,
    build_positional_kmer_candidates,
    candidate_dimensions,
)
from methods.stage2_features import paired_retrieval_metrics  # noqa: E402


REPRESENTATION_LABELS = {
    "ck4": "CK4",
    "ck5": "CK5",
    **CANDIDATE_LABELS,
}
DEFAULT_REPRESENTATIONS = list(REPRESENTATION_LABELS)


def parse_csv_list(text: str) -> list[str]:
    return [item.strip() for item in text.split(",") if item.strip()]


def parse_int_list(text: str) -> list[int]:
    return [int(item) for item in parse_csv_list(text)]


def build_all_matrices(sequences: list[str], representations: list[str]) -> dict[str, np.ndarray]:
    candidates = build_positional_kmer_candidates(sequences)
    matrices: dict[str, np.ndarray] = {}
    for name in representations:
        if name == "ck4":
            matrices[name] = candidates.ck4
        elif name == "ck5":
            matrices[name], _ = build_ck4_block(sequences, config=CK4PMSPConfig(k=5))
        elif name in candidates.matrices:
            matrices[name] = candidates.matrices[name]
        else:
            raise ValueError(f"Unsupported representation: {name}")
    return matrices


def _complete_ids(frame: pd.DataFrame, id_col: str, condition_col: str, conditions: list[str]) -> list[str]:
    counts = frame.groupby(id_col)[condition_col].agg(lambda values: set(values.astype(str)))
    required = set(conditions)
    return sorted(str(index) for index, values in counts.items() if required.issubset(values))


def _sample_ids(ids: list[str], maximum: int, seed: int) -> list[str]:
    if maximum <= 0 or len(ids) <= maximum:
        return ids
    rng = np.random.default_rng(seed)
    return sorted(rng.choice(ids, size=maximum, replace=False).tolist())


def stability_audit(
    reads: pd.DataFrame,
    *,
    lengths: list[int],
    conditions: list[str],
    representations: list[str],
    max_pairs: int,
    seed: int,
) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    length_column = "source_length" if "source_length" in reads.columns else "length"
    for length in lengths:
        subset = reads[reads[length_column].eq(length)].copy()
        ids = _complete_ids(subset, "clean_read_id", "condition", ["clean", *conditions])
        ids = _sample_ids(ids, max_pairs, seed + length)
        if not ids:
            continue
        sequences: list[str] = []
        for condition in ["clean", *conditions]:
            part = subset[subset["condition"].eq(condition)].set_index("clean_read_id").loc[ids]
            sequences.extend(part["sequence"].astype(str).tolist())
        n = len(ids)
        matrices = build_all_matrices(sequences, representations)
        for representation, matrix in matrices.items():
            clean = matrix[:n]
            for condition_index, condition in enumerate(conditions, start=1):
                perturbed = matrix[condition_index * n : (condition_index + 1) * n]
                metrics = paired_retrieval_metrics(clean, perturbed)
                rows.append(
                    {
                        "length": length,
                        "condition": condition,
                        "representation": representation,
                        "representation_label": REPRESENTATION_LABELS[representation],
                        "n_features": int(matrix.shape[1]),
                        "n_pairs": n,
                        **metrics,
                    }
                )
    return pd.DataFrame(rows)


def grouped_delta_readout(
    clean: np.ndarray,
    noise: np.ndarray,
    local: np.ndarray,
    sample_ids: list[str],
    *,
    seed: int,
    cv_folds: int,
    standardize: bool = True,
) -> tuple[float, float, float]:
    features = np.vstack([np.abs(noise - clean), np.abs(local - clean)])
    labels = np.asarray([0] * len(clean) + [1] * len(clean), dtype=int)
    groups = np.asarray(sample_ids + sample_ids)
    splitter = StratifiedGroupKFold(n_splits=cv_folds, shuffle=True, random_state=seed)
    scores: list[float] = []
    accuracies: list[float] = []
    for train, test in splitter.split(features, labels, groups):
        if standardize:
            model = make_pipeline(
                StandardScaler(),
                LogisticRegression(max_iter=5000, random_state=seed),
            )
        else:
            model = LogisticRegression(max_iter=5000, random_state=seed)
        model.fit(features[train], labels[train])
        prediction = model.predict(features[test])
        scores.append(float(f1_score(labels[test], prediction, average="macro", zero_division=0)))
        accuracies.append(float(accuracy_score(labels[test], prediction)))
    return float(np.mean(scores)), float(np.std(scores)), float(np.mean(accuracies))


def local_audit(
    triplets: pd.DataFrame,
    *,
    lengths: list[int],
    representations: list[str],
    max_triplets: int,
    cv_folds: int,
    seed: int,
    standardize: bool = True,
) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for length in lengths:
        length_frame = triplets[triplets["source_length"].eq(length)]
        for mode in sorted(length_frame["local_mode"].astype(str).unique()):
            subset = length_frame[length_frame["local_mode"].eq(mode)].copy()
            ids = _complete_ids(
                subset,
                "sample_id",
                "variant",
                ["clean", "random_noise", "local_property_shift"],
            )
            ids = _sample_ids(ids, max_triplets, seed + length + len(mode))
            if not ids:
                continue
            sequences: list[str] = []
            for variant in ["clean", "random_noise", "local_property_shift"]:
                part = subset[subset["variant"].eq(variant)].set_index("sample_id").loc[ids]
                sequences.extend(part["sequence"].astype(str).tolist())
            n = len(ids)
            matrices = build_all_matrices(sequences, representations)
            for representation, matrix in matrices.items():
                clean, noise, local = matrix[:n], matrix[n : 2 * n], matrix[2 * n : 3 * n]
                macro_f1, macro_f1_sd, accuracy = grouped_delta_readout(
                    clean,
                    noise,
                    local,
                    ids,
                    seed=seed + length,
                    cv_folds=cv_folds,
                    standardize=standardize,
                )
                rows.append(
                    {
                        "length": length,
                        "local_mode": mode,
                        "representation": representation,
                        "representation_label": REPRESENTATION_LABELS[representation],
                        "n_features": int(matrix.shape[1]),
                        "n_triplets": n,
                        "noise_l2_mean": float(np.linalg.norm(noise - clean, axis=1).mean()),
                        "local_l2_mean": float(np.linalg.norm(local - clean, axis=1).mean()),
                        "macro_f1": macro_f1,
                        "macro_f1_sd": macro_f1_sd,
                        "accuracy": accuracy,
                    }
                )
    return pd.DataFrame(rows)


def motif_audit(
    reads: pd.DataFrame,
    *,
    representations: list[str],
    cv_folds: int,
    seed: int,
) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for length in sorted(reads["length"].unique()):
        subset = reads[reads["length"].eq(length)].reset_index(drop=True)
        labels = subset["position_label"].astype(str).to_numpy()
        groups = subset["source_id"].astype(str).to_numpy()
        matrices = build_all_matrices(subset["sequence"].astype(str).tolist(), representations)
        splitter = StratifiedGroupKFold(n_splits=cv_folds, shuffle=True, random_state=seed + int(length))
        folds = list(splitter.split(np.arange(len(subset)), labels, groups))
        for representation, matrix in matrices.items():
            for fold, (train, test) in enumerate(folds, start=1):
                model = LogisticRegression(max_iter=5000, random_state=seed + fold)
                model.fit(matrix[train], labels[train])
                prediction = model.predict(matrix[test])
                rows.append(
                    {
                        "length": int(length),
                        "fold": fold,
                        "representation": representation,
                        "representation_label": REPRESENTATION_LABELS[representation],
                        "n_features": int(matrix.shape[1]),
                        "macro_f1": float(f1_score(labels[test], prediction, average="macro", zero_division=0)),
                        "accuracy": float(accuracy_score(labels[test], prediction)),
                    }
                )
    return pd.DataFrame(rows)


def art_audit(
    reads: pd.DataFrame,
    *,
    representations: list[str],
    max_pairs_per_length: int,
    seed: int,
) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for length in sorted(reads["length"].unique()):
        subset = reads[reads["length"].eq(length)].copy()
        ids = _complete_ids(subset, "clean_read_id", "condition", ["clean", "art_illumina"])
        ids = _sample_ids(ids, max_pairs_per_length, seed + int(length))
        if not ids:
            continue
        clean_part = subset[subset["condition"].eq("clean")].set_index("clean_read_id").loc[ids]
        art_part = subset[subset["condition"].eq("art_illumina")].set_index("clean_read_id").loc[ids]
        sequences = clean_part["sequence"].astype(str).tolist() + art_part["sequence"].astype(str).tolist()
        n = len(ids)
        matrices = build_all_matrices(sequences, representations)
        for representation, matrix in matrices.items():
            metrics = paired_retrieval_metrics(matrix[:n], matrix[n:])
            rows.append(
                {
                    "length": int(length),
                    "representation": representation,
                    "representation_label": REPRESENTATION_LABELS[representation],
                    "n_features": int(matrix.shape[1]),
                    "n_pairs": n,
                    **metrics,
                }
            )
    return pd.DataFrame(rows)


def _balanced_cami_sources(shifted: pd.DataFrame, maximum_per_class: int, seed: int) -> list[str]:
    source = shifted[["source_id", "binary_label"]].drop_duplicates().sort_values("source_id")
    selected: list[str] = []
    for label, part in source.groupby("binary_label"):
        ids = part["source_id"].astype(str).tolist()
        selected.extend(_sample_ids(ids, maximum_per_class, seed + int(label)))
    return sorted(selected)


def cami_fixed_head_audit(
    shifted: pd.DataFrame,
    *,
    representations: list[str],
    max_sources_per_class: int,
    cv_folds: int,
    seed: int,
) -> pd.DataFrame:
    source_ids = _balanced_cami_sources(shifted, max_sources_per_class, seed)
    subset = shifted[shifted["source_id"].astype(str).isin(source_ids)].copy().reset_index(drop=True)
    source = subset[["source_id", "binary_label"]].drop_duplicates().sort_values("source_id")
    source_names = source["source_id"].astype(str).to_numpy()
    source_labels = source["binary_label"].to_numpy(dtype=int)
    splitter = StratifiedGroupKFold(n_splits=cv_folds, shuffle=True, random_state=seed)
    fold_map: dict[str, int] = {}
    for fold, (_, test) in enumerate(splitter.split(source_names, source_labels, source_names), start=1):
        for source_id in source_names[test]:
            fold_map[str(source_id)] = fold
    subset["fold"] = subset["source_id"].astype(str).map(fold_map).astype(int)
    matrices = build_all_matrices(subset["sequence"].astype(str).tolist(), representations)
    prediction_rows: list[dict[str, object]] = []

    for representation, matrix in matrices.items():
        for fold in range(1, cv_folds + 1):
            train_mask = (
                subset["fold"].ne(fold)
                & subset["length"].eq(100)
                & subset["condition"].eq("clean")
            ).to_numpy()
            model = LogisticRegression(max_iter=5000, class_weight="balanced", random_state=seed + fold)
            model.fit(matrix[train_mask], subset.loc[train_mask, "binary_label"].to_numpy(dtype=int))
            for (length, condition), cell in subset[subset["fold"].eq(fold)].groupby(["length", "condition"]):
                indices = cell.index.to_numpy(dtype=int)
                truth = cell["binary_label"].to_numpy(dtype=int)
                prediction = model.predict(matrix[indices])
                prediction_rows.append(
                    {
                        "representation": representation,
                        "representation_label": REPRESENTATION_LABELS[representation],
                        "n_features": int(matrix.shape[1]),
                        "fold": fold,
                        "length": int(length),
                        "condition": str(condition),
                        "macro_f1": float(f1_score(truth, prediction, average="macro", zero_division=0)),
                        "accuracy": float(accuracy_score(truth, prediction)),
                        "n_test_sources": int(len(cell)),
                    }
                )
    metrics = pd.DataFrame(prediction_rows)
    baseline = (
        metrics[(metrics["length"].eq(100)) & (metrics["condition"].eq("clean"))]
        .groupby("representation")["macro_f1"]
        .mean()
        .to_dict()
    )
    metrics["baseline_macro_f1"] = metrics["representation"].map(baseline)
    metrics["retention_ratio"] = metrics["macro_f1"] / metrics["baseline_macro_f1"]
    return metrics


def runtime_audit(sequences: list[str], representations: list[str], repeats: int) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for representation in representations:
        if representation in {"ck4", "ck5"}:
            continue
        for repeat in range(repeats):
            started = time.perf_counter()
            matrix = build_positional_kmer_candidate(sequences, representation)
            elapsed = time.perf_counter() - started
            rows.append(
                {
                    "representation": representation,
                    "representation_label": REPRESENTATION_LABELS[representation],
                    "repeat": repeat + 1,
                    "n_reads": len(sequences),
                    "n_features": int(matrix.shape[1]),
                    "seconds": float(elapsed),
                }
            )
    return pd.DataFrame(rows)


def build_decision_table(
    stability: pd.DataFrame,
    local: pd.DataFrame,
    motif: pd.DataFrame,
    art: pd.DataFrame,
    cami: pd.DataFrame,
    runtime: pd.DataFrame,
) -> pd.DataFrame:
    required_frames = {
        "stability": stability,
        "local": local,
        "motif": motif,
        "art": art,
        "cami": cami,
        "runtime": runtime,
    }
    empty = [name for name, frame in required_frames.items() if frame.empty]
    if empty:
        raise ValueError(f"Candidate decision table requires non-empty layers: {empty}")
    wgs = stability.groupby("representation", as_index=False).agg(
        wgs_l2=("l2_delta_mean", "mean"),
        wgs_retrieval=("retrieval_top1", "mean"),
    )
    local_summary = local.groupby("representation", as_index=False).agg(local_macro_f1=("macro_f1", "mean"))
    motif_summary = motif.groupby("representation", as_index=False).agg(motif_macro_f1=("macro_f1", "mean"))
    art_summary = art.groupby("representation", as_index=False).agg(art_l2=("l2_delta_mean", "mean"))
    shifted = cami[~((cami["length"].eq(100)) & (cami["condition"].eq("clean")))]
    cami_summary = shifted.groupby("representation", as_index=False).agg(cami_mean_retention=("retention_ratio", "mean"))
    runtime_summary = runtime.groupby("representation", as_index=False).agg(runtime_seconds=("seconds", "median"))
    dimensions = candidate_dimensions()
    dimensions.update({"ck4": 136, "ck5": 512})
    table = pd.DataFrame(
        {
            "representation": list(REPRESENTATION_LABELS),
            "representation_label": [REPRESENTATION_LABELS[name] for name in REPRESENTATION_LABELS],
            "n_features": [dimensions[name] for name in REPRESENTATION_LABELS],
        }
    )
    for frame in [wgs, local_summary, motif_summary, art_summary, cami_summary, runtime_summary]:
        table = table.merge(frame, on="representation", how="left")
    baseline = table[table["representation"].eq("ck4p_msp")].iloc[0]
    table["motif_gain_vs_main"] = table["motif_macro_f1"] - baseline["motif_macro_f1"]
    table["wgs_l2_change_vs_main"] = table["wgs_l2"] - baseline["wgs_l2"]
    table["wgs_retrieval_change_vs_main"] = table["wgs_retrieval"] - baseline["wgs_retrieval"]
    table["local_f1_change_vs_main"] = table["local_macro_f1"] - baseline["local_macro_f1"]
    table["art_l2_change_vs_main"] = table["art_l2"] - baseline["art_l2"]
    table["cami_retention_change_vs_main"] = table["cami_mean_retention"] - baseline["cami_mean_retention"]
    table["runtime_ratio_vs_main"] = table["runtime_seconds"] / baseline["runtime_seconds"]
    candidate_mask = table["representation"].str.startswith("candidate_")
    table["screen_pass_motif"] = table["motif_gain_vs_main"].ge(0.02)
    table["screen_pass_wgs_l2"] = table["wgs_l2_change_vs_main"].le(0.01)
    table["screen_pass_retrieval"] = table["wgs_retrieval_change_vs_main"].ge(-0.01)
    table["screen_pass_local"] = table["local_f1_change_vs_main"].ge(-0.01)
    table["screen_pass_art"] = table["art_l2_change_vs_main"].le(0.01)
    table["screen_pass_cami"] = table["cami_retention_change_vs_main"].ge(-0.02)
    table["screen_pass_runtime"] = table["runtime_ratio_vs_main"].le(2.0)
    pass_columns = [column for column in table.columns if column.startswith("screen_pass_")]
    table["eligible_for_independent_confirmation"] = candidate_mask & table[pass_columns].all(axis=1)
    table.loc[table["representation"].eq("candidate_dual_augment"), "eligible_for_independent_confirmation"] = False
    return table


def write_summary(decision: pd.DataFrame, output_dir: Path, metadata: dict[str, object]) -> None:
    eligible = decision[decision["eligible_for_independent_confirmation"]]
    lines = [
        "# Positional k-mer candidate screen",
        "",
        "This is a prespecified engineering screen, not a confirmatory superiority test.",
        "The current CK4P-MSP method remains unchanged unless a candidate passes all gates and then reproduces on an independent seed or template split.",
        "",
        decision.to_markdown(index=False, floatfmt=".4f"),
        "",
        "## Screen outcome",
        "",
        (
            "Eligible candidates: " + ", ".join(eligible["representation"].tolist())
            if not eligible.empty
            else "No candidate passed every prespecified gate."
        ),
        "",
        "ART and CAMI are lightweight screening subsets at this stage; a passing candidate requires full-layer reruns.",
        "",
        "## Run metadata",
        "",
        "```json",
        json.dumps(metadata, indent=2, ensure_ascii=False),
        "```",
    ]
    (output_dir / "positional_kmer_candidate_summary.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--stability-reads",
        default=str(PROJECT_ROOT / "results" / "stage3" / "contract_v2" / "compact_baselines" / "stage3_compact_baseline_reads.csv"),
    )
    parser.add_argument(
        "--local-triplets",
        default=str(PROJECT_ROOT / "results" / "stage3" / "contract_v2" / "local_mutation_sensitivity" / "local_mutation_triplets.csv"),
    )
    parser.add_argument(
        "--motif-reads",
        default=str(PROJECT_ROOT / "results" / "stage3" / "external_motif_position_probe" / "external_motif_position_probe_reads.csv"),
    )
    parser.add_argument(
        "--art-reads",
        default=str(PROJECT_ROOT / "results" / "stage3" / "contract_v2" / "art_current_contract" / "art_paired_reads.csv"),
    )
    parser.add_argument(
        "--cami-shifted",
        default=str(PROJECT_ROOT / "results" / "stage3" / "contract_v2" / "cami_fixed_head_transfer" / "cami_fixed_head_shifted_rows.csv"),
    )
    parser.add_argument(
        "--output-dir",
        default=str(PROJECT_ROOT / "results" / "stage3" / "candidate_positional_kmer"),
    )
    parser.add_argument("--representations", default=",".join(DEFAULT_REPRESENTATIONS))
    parser.add_argument("--lengths", default="69,75,100,150")
    parser.add_argument("--conditions", default="substitution_1pct,N_3pct,trim_5bp,substitution_1pct_N_3pct,local_mismatch_6bp,short_indel")
    parser.add_argument("--max-pairs", type=int, default=500)
    parser.add_argument("--max-triplets", type=int, default=400)
    parser.add_argument("--max-art-pairs-per-length", type=int, default=2000)
    parser.add_argument("--max-cami-sources-per-class", type=int, default=600)
    parser.add_argument("--runtime-reads", type=int, default=10000)
    parser.add_argument("--runtime-repeats", type=int, default=2)
    parser.add_argument("--cv-folds", type=int, default=5)
    parser.add_argument("--seed", type=int, default=20260805)
    args = parser.parse_args()

    started = time.time()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    representations = parse_csv_list(args.representations)
    lengths = parse_int_list(args.lengths)
    conditions = parse_csv_list(args.conditions)

    stability_reads = pd.read_csv(args.stability_reads)
    local_triplets = pd.read_csv(args.local_triplets)
    motif_reads = pd.read_csv(args.motif_reads)
    art_reads = pd.read_csv(args.art_reads)
    cami_shifted = pd.read_csv(args.cami_shifted)

    stability = stability_audit(
        stability_reads,
        lengths=lengths,
        conditions=conditions,
        representations=representations,
        max_pairs=args.max_pairs,
        seed=args.seed,
    )
    stability.to_csv(output_dir / "candidate_wgs_stability.csv", index=False, encoding="utf-8-sig")
    print("[candidate-audit] WGS stability complete", flush=True)

    local = local_audit(
        local_triplets,
        lengths=[length for length in lengths if length in set(local_triplets["source_length"])],
        representations=representations,
        max_triplets=args.max_triplets,
        cv_folds=args.cv_folds,
        seed=args.seed,
    )
    local.to_csv(output_dir / "candidate_local_readout.csv", index=False, encoding="utf-8-sig")
    print("[candidate-audit] grouped local readout complete", flush=True)

    motif = motif_audit(
        motif_reads,
        representations=representations,
        cv_folds=args.cv_folds,
        seed=args.seed,
    )
    motif.to_csv(output_dir / "candidate_motif_position.csv", index=False, encoding="utf-8-sig")
    print("[candidate-audit] motif-position complete", flush=True)

    art = art_audit(
        art_reads,
        representations=representations,
        max_pairs_per_length=args.max_art_pairs_per_length,
        seed=args.seed,
    )
    art.to_csv(output_dir / "candidate_art_stability.csv", index=False, encoding="utf-8-sig")
    print("[candidate-audit] ART screen complete", flush=True)

    cami = cami_fixed_head_audit(
        cami_shifted,
        representations=representations,
        max_sources_per_class=args.max_cami_sources_per_class,
        cv_folds=args.cv_folds,
        seed=args.seed,
    )
    cami.to_csv(output_dir / "candidate_cami_fixed_head.csv", index=False, encoding="utf-8-sig")
    print("[candidate-audit] CAMI fixed-head screen complete", flush=True)

    runtime_pool = art_reads[art_reads["condition"].eq("clean")]["sequence"].astype(str).tolist()
    if len(runtime_pool) < args.runtime_reads:
        runtime_pool.extend(stability_reads[stability_reads["condition"].eq("clean")]["sequence"].astype(str).tolist())
    runtime_sequences = runtime_pool[: args.runtime_reads]
    runtime = runtime_audit(runtime_sequences, representations, args.runtime_repeats)
    runtime.to_csv(output_dir / "candidate_runtime.csv", index=False, encoding="utf-8-sig")
    print("[candidate-audit] runtime complete", flush=True)

    decision = build_decision_table(stability, local, motif, art, cami, runtime)
    decision.to_csv(output_dir / "candidate_decision_table.csv", index=False, encoding="utf-8-sig")
    metadata = {
        "elapsed_seconds": round(time.time() - started, 3),
        "representations": representations,
        "lengths": lengths,
        "conditions": conditions,
        "max_pairs": args.max_pairs,
        "max_triplets": args.max_triplets,
        "max_art_pairs_per_length": args.max_art_pairs_per_length,
        "max_cami_sources_per_class": args.max_cami_sources_per_class,
        "runtime_reads": len(runtime_sequences),
        "runtime_repeats": args.runtime_repeats,
        "cv_folds": args.cv_folds,
        "seed": args.seed,
        "python": sys.version,
        "platform": platform.platform(),
        "processor": platform.processor(),
    }
    (output_dir / "candidate_run.json").write_text(json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8")
    write_summary(decision, output_dir, metadata)
    print(f"Wrote positional k-mer candidate screen to {output_dir}")


if __name__ == "__main__":
    main()
