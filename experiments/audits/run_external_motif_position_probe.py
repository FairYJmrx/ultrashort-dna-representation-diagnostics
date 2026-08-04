"""Run a public motif-position readability probe on known Dorsal sites.

The task is deliberately narrow: extract short windows containing a known
binding site from public CRM sequences, label the site's relative position in
the window, and evaluate fixed representations with grouped cross-validation.
The task tests position-related readability; it is not a motif discovery or
binding-affinity benchmark.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.neighbors import NearestCentroid


def _find_project_root(start: Path) -> Path:
    for candidate in [start.parent, *start.parents]:
        if (candidate / "methods").is_dir() and (candidate / "configs").is_dir():
            return candidate
    raise RuntimeError("Could not locate the release repository root.")


PROJECT_ROOT = _find_project_root(Path(__file__).resolve())
sys.path.insert(0, str(PROJECT_ROOT))

from methods.stage2_features import build_feature_matrix  # noqa: E402


DEFAULT_REPRESENTATIONS = ["ck4", "ckmer5_count_l2", "p", "msp", "p_msp", "ck4p_msp"]
DEFAULT_LENGTHS = [50, 75, 100, 150]


def parse_fasta(path: Path) -> dict[str, str]:
    records: dict[str, str] = {}
    header: str | None = None
    chunks: list[str] = []
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith(">"):
            if header is not None:
                records[header] = "".join(chunks).upper()
            header = line[1:].strip().split()[0]
            chunks = []
        else:
            chunks.append(line)
    if header is not None:
        records[header] = "".join(chunks).upper()
    return records


def position_bin(relative_start: int, window_length: int, motif_length: int) -> str:
    max_relative_start = window_length - motif_length
    if max_relative_start <= 0:
        return "middle"
    fraction = relative_start / max_relative_start
    if fraction < 1 / 3:
        return "left"
    if fraction < 2 / 3:
        return "middle"
    return "right"


def select_evenly(values: list[int], n: int) -> list[int]:
    if len(values) <= n:
        return values
    indices = np.linspace(0, len(values) - 1, n).round().astype(int).tolist()
    return [values[index] for index in indices]


def build_probe_table(
    site_path: Path,
    crm_path: Path,
    lengths: list[int],
    windows_per_bin: int,
) -> pd.DataFrame:
    sites = parse_fasta(site_path)
    crms = parse_fasta(crm_path)
    rows: list[dict[str, object]] = []

    for source_id in sorted(set(sites).intersection(crms)):
        motif = sites[source_id]
        crm = crms[source_id]
        motif_start = crm.find(motif)
        if motif_start < 0:
            continue
        motif_length = len(motif)
        for length in lengths:
            if length <= motif_length or len(crm) < length:
                continue
            min_window_start = max(0, motif_start + motif_length - length)
            max_window_start = min(motif_start, len(crm) - length)
            candidates: dict[str, list[tuple[int, int]]] = {"left": [], "middle": [], "right": []}
            for window_start in range(min_window_start, max_window_start + 1):
                relative_start = motif_start - window_start
                label = position_bin(relative_start, length, motif_length)
                candidates[label].append((window_start, relative_start))
            if any(not values for values in candidates.values()):
                continue
            for label, values in candidates.items():
                for index, (window_start, relative_start) in enumerate(select_evenly(values, windows_per_bin)):
                    sequence = crm[window_start : window_start + length]
                    rows.append(
                        {
                            "read_id": f"{source_id}_L{length}_{label}_{index:02d}",
                            "source_id": source_id,
                            "sequence": sequence,
                            "length": length,
                            "motif": motif,
                            "motif_length": motif_length,
                            "motif_relative_start": relative_start,
                            "position_label": label,
                        }
                    )
    result = pd.DataFrame(rows)
    if result.empty:
        raise RuntimeError("No valid motif-position windows were generated.")
    return result.sort_values(["length", "source_id", "position_label", "motif_relative_start"]).reset_index(drop=True)


def classifiers(seed: int) -> dict[str, object]:
    return {
        "contract_logistic": LogisticRegression(max_iter=5000, random_state=seed),
        "nearest_centroid": NearestCentroid(),
    }


def evaluate_representation(
    subset: pd.DataFrame,
    representation: str,
    cv_folds: int,
    seed: int,
    labels_override: np.ndarray | None = None,
) -> list[dict[str, object]]:
    sequences = subset["sequence"].astype(str).tolist()
    labels = (
        subset["position_label"].astype(str).to_numpy()
        if labels_override is None
        else np.asarray(labels_override, dtype=str)
    )
    groups = subset["source_id"].astype(str).to_numpy()
    unique_labels = np.unique(labels)
    if len(unique_labels) != 3:
        return [{"error": f"expected three position classes, got {unique_labels.tolist()}"}]

    splitter = StratifiedGroupKFold(n_splits=cv_folds, shuffle=True, random_state=seed)
    rows: list[dict[str, object]] = []
    for fold, (train_idx, test_idx) in enumerate(splitter.split(sequences, labels, groups), start=1):
        matrix, info = build_feature_matrix(
            sequences,
            representation,
            length=int(subset["length"].iloc[0]),
            train_indices=train_idx.tolist(),
        )
        for classifier_name, classifier in classifiers(seed).items():
            classifier.fit(matrix[train_idx], labels[train_idx])
            predictions = classifier.predict(matrix[test_idx])
            rows.append(
                {
                    "fold": fold,
                    "classifier": classifier_name,
                    "accuracy": float(accuracy_score(labels[test_idx], predictions)),
                    "macro_f1": float(f1_score(labels[test_idx], predictions, average="macro", zero_division=0)),
                    "n_features": int(info.n_features),
                    "n_train": int(len(train_idx)),
                    "n_test": int(len(test_idx)),
                    "n_train_groups": int(len(np.unique(groups[train_idx]))),
                    "n_test_groups": int(len(np.unique(groups[test_idx]))),
                }
            )
    return rows


def permute_labels_within_source(subset: pd.DataFrame, seed: int) -> np.ndarray:
    """Preserve source-level class counts while removing label-feature linkage."""
    rng = np.random.default_rng(seed)
    labels = subset["position_label"].astype(str).to_numpy(copy=True)
    groups = subset["source_id"].astype(str).to_numpy()
    for source_id in np.unique(groups):
        indices = np.flatnonzero(groups == source_id)
        shuffled = labels[indices].copy()
        rng.shuffle(shuffled)
        labels[indices] = shuffled
    return labels


def summarize_metrics(metrics: pd.DataFrame) -> pd.DataFrame:
    group_cols = ["length", "representation", "classifier"]
    summary = (
        metrics.groupby(group_cols, as_index=False)
        .agg(
            mean_accuracy=("accuracy", "mean"),
            sd_accuracy=("accuracy", "std"),
            mean_macro_f1=("macro_f1", "mean"),
            sd_macro_f1=("macro_f1", "std"),
            n_features=("n_features", "first"),
            n_folds=("fold", "nunique"),
        )
        .sort_values(group_cols)
    )
    return summary


def plot_summary(summary: pd.DataFrame, output_path: Path) -> None:
    plot_data = summary[summary["classifier"] == "contract_logistic"].copy()
    labels = {
        "ck4": "CK4",
        "ckmer5_count_l2": "CK5",
        "p": "P",
        "msp": "MSP",
        "p_msp": "P+MSP",
        "ck4p_msp": "CK4P-MSP",
    }
    colors = {
        "ck4": "#566573",
        "ckmer5_count_l2": "#8e44ad",
        "p": "#e67e22",
        "msp": "#16a085",
        "p_msp": "#2980b9",
        "ck4p_msp": "#1f9d55",
    }
    fig, ax = plt.subplots(figsize=(7.2, 4.2))
    for representation in labels:
        group = plot_data[plot_data["representation"] == representation].sort_values("length")
        if group.empty:
            continue
        ax.errorbar(
            group["length"],
            group["mean_macro_f1"],
            yerr=group["sd_macro_f1"].fillna(0),
            marker="o",
            linewidth=1.6,
            markersize=4,
            color=colors[representation],
            label=labels[representation],
            capsize=2,
        )
    ax.axhline(1 / 3, color="#777777", linestyle="--", linewidth=1, label="3-class chance")
    ax.set_xlabel("Window length (bp)")
    ax.set_ylabel("Grouped-CV macro-F1")
    ax.set_xticks(sorted(plot_data["length"].unique()))
    ax.set_ylim(0.25, 0.75)
    ax.legend(frameon=False, ncol=2, fontsize=8)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(output_path, dpi=300)
    fig.savefig(output_path.with_suffix(".pdf"))
    fig.savefig(output_path.with_suffix(".svg"))
    plt.close(fig)


def write_summary(
    output_path: Path,
    reads: pd.DataFrame,
    summary: pd.DataFrame,
    null_summary: pd.DataFrame,
    source_url: str,
) -> None:
    lines = [
        "# External motif-position probe summary",
        "",
        "This is a grouped external readability probe using public Dorsal binding-site and CRM sequences.",
        "The label is the relative position of a known site within a 50/75/100/150 bp window.",
        "It is not a TFBS discovery, affinity, species classification or clinical validation task.",
        "",
        f"Source: {source_url}",
        f"Samples: {len(reads)} windows; CRM groups: {reads['source_id'].nunique()}; lengths: {sorted(reads['length'].unique().tolist())}",
        "",
        "## Class counts",
        "",
        reads.groupby(["length", "position_label"]).size().unstack(fill_value=0).to_markdown(),
        "",
        "## Grouped-CV results",
        "",
        summary.to_markdown(index=False, floatfmt=".3f"),
        "",
        "## Within-source label-permutation null",
        "",
        null_summary.to_markdown(index=False, floatfmt=".3f"),
        "",
        "Chance macro-F1 is 1/3 for the three-class position label.",
        "A result above chance indicates external position-label readability under this probe; it does not establish general natural position semantics.",
    ]
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the public external motif-position readability probe.")
    parser.add_argument("--site-fasta", default=str(PROJECT_ROOT / "data" / "external" / "mibbs_dorsal" / "Data" / "CoreDorsalOrthologsites.fa"))
    parser.add_argument("--crm-fasta", default=str(PROJECT_ROOT / "data" / "external" / "mibbs_dorsal" / "Data" / "CRMs.fa"))
    parser.add_argument("--output-dir", default=str(PROJECT_ROOT / "results" / "stage3" / "external_motif_position_probe"))
    parser.add_argument("--lengths", default="50,75,100,150")
    parser.add_argument("--windows-per-bin", type=int, default=3)
    parser.add_argument("--cv-folds", type=int, default=5)
    parser.add_argument("--null-repeats", type=int, default=5)
    parser.add_argument("--seed", type=int, default=1205)
    parser.add_argument("--representations", default=",".join(DEFAULT_REPRESENTATIONS))
    args = parser.parse_args()

    started = time.time()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    lengths = [int(value.strip()) for value in args.lengths.split(",") if value.strip()]
    representations = [value.strip() for value in args.representations.split(",") if value.strip()]
    reads = build_probe_table(Path(args.site_fasta), Path(args.crm_fasta), lengths, args.windows_per_bin)
    reads.to_csv(output_dir / "external_motif_position_probe_reads.csv", index=False, encoding="utf-8-sig")

    metric_rows: list[dict[str, object]] = []
    null_rows: list[dict[str, object]] = []
    for length in lengths:
        subset = reads[reads["length"] == length].reset_index(drop=True)
        for representation in representations:
            rows = evaluate_representation(subset, representation, args.cv_folds, args.seed)
            for row in rows:
                row.update(
                    {
                        "length": length,
                        "representation": representation,
                        "n_samples": int(len(subset)),
                        "n_groups": int(subset["source_id"].nunique()),
                        "n_classes": int(subset["position_label"].nunique()),
                    }
                )
                metric_rows.append(row)
        for permutation in range(args.null_repeats):
            shuffled_labels = permute_labels_within_source(subset, args.seed + length * 100 + permutation)
            for representation in representations:
                rows = evaluate_representation(
                    subset,
                    representation,
                    args.cv_folds,
                    args.seed,
                    labels_override=shuffled_labels,
                )
                for row in rows:
                    row.update(
                        {
                            "length": length,
                            "representation": representation,
                            "n_samples": int(len(subset)),
                            "n_groups": int(subset["source_id"].nunique()),
                            "n_classes": int(subset["position_label"].nunique()),
                            "label_control": "within_source_permutation",
                            "permutation": permutation,
                        }
                    )
                    null_rows.append(row)
    metrics = pd.DataFrame(metric_rows)
    metrics.to_csv(output_dir / "external_motif_position_probe_metrics.csv", index=False, encoding="utf-8-sig")
    summary = summarize_metrics(metrics.dropna(subset=["macro_f1"]))
    summary.to_csv(output_dir / "external_motif_position_probe_summary.csv", index=False, encoding="utf-8-sig")
    null_metrics = pd.DataFrame(null_rows)
    null_metrics.to_csv(output_dir / "external_motif_position_probe_null_metrics.csv", index=False, encoding="utf-8-sig")
    null_summary = summarize_metrics(null_metrics.dropna(subset=["macro_f1"]))
    null_summary.to_csv(output_dir / "external_motif_position_probe_null_summary.csv", index=False, encoding="utf-8-sig")
    plot_summary(summary, output_dir / "external_motif_position_probe.png")
    write_summary(
        output_dir / "external_motif_position_probe_summary.md",
        reads,
        summary,
        null_summary,
        "https://doi.org/10.5061/dryad.8b203",
    )
    (output_dir / "external_motif_position_probe_run.json").write_text(
        json.dumps(
            {
                "elapsed_seconds": time.time() - started,
                "site_fasta": str(args.site_fasta),
                "crm_fasta": str(args.crm_fasta),
                "lengths": lengths,
                "windows_per_bin": args.windows_per_bin,
                "cv_folds": args.cv_folds,
                "null_repeats": args.null_repeats,
                "seed": args.seed,
                "representations": representations,
                "n_samples": int(len(reads)),
                "n_groups": int(reads["source_id"].nunique()),
                "source": "Clifford and Adami Dryad dataset 10.5061/dryad.8b203",
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    print(f"Wrote external motif-position probe to {output_dir}")


if __name__ == "__main__":
    main()
