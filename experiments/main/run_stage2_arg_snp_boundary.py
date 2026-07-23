from __future__ import annotations

import argparse
import json
import random
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import train_test_split
from sklearn.neighbors import NearestCentroid
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import LabelEncoder, StandardScaler

def _find_project_root(start: Path) -> Path:
    for candidate in [start.parent, *start.parents]:
        if (candidate / "methods").is_dir() and (candidate / "configs").is_dir():
            return candidate
    raise RuntimeError("Could not locate the release repository root.")


PROJECT_ROOT = _find_project_root(Path(__file__).resolve())
sys.path.insert(0, str(PROJECT_ROOT))

from experiments.main.run_stage2_representation_grid import apply_stage2_condition
from src.sequence_utils import random_dna
from src.stage2_features import build_feature_matrix, paired_retrieval_metrics


ARG_MOTIFS = {
    "bla_family_A": "ATGAAACGCTTTGCCGATGACGGTACCGTTAACGCCGAACTG",
    "bla_family_B": "ATGAAACGCTTCGCCGATGATGGTACCGTCAACGCCGAACTG",
}
NON_ARG_MOTIF = "TTACTGACCATCGTTAACGTAGGCTACCATGGATCAACTGAC"
SNP_LEFT = "GCTGATCGTACCGGATACGTTGACCTGACCGTACGATCGTAC"
SNP_RIGHT = "CCGATGACTTACCGGATCAAGCTTAGGCCATCGTAACCGTTA"


def parse_csv_list(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def parse_int_list(value: str) -> list[int]:
    return [int(item.strip()) for item in value.split(",") if item.strip()]


def set_global_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)


def mutate_template(seq: str, positions: list[int], seed: int) -> str:
    rng = random.Random(seed)
    chars = list(seq)
    for pos in positions:
        base = chars[pos]
        choices = [b for b in "ACGT" if b != base]
        chars[pos] = rng.choice(choices)
    return "".join(chars)


def template_with_marker(marker: str, rng: random.Random, total_len: int = 420, marker_pos: int = 170) -> str:
    bg = list(random_dna(total_len, {"A": 0.25, "C": 0.25, "G": 0.25, "T": 0.25}, rng))
    bg[marker_pos : marker_pos + len(marker)] = list(marker)
    return "".join(bg)


def resistance_templates() -> dict[str, str]:
    susceptible = SNP_LEFT + "A" + SNP_RIGHT
    resistant_transition = SNP_LEFT + "G" + SNP_RIGHT
    resistant_transversion = SNP_LEFT + "T" + SNP_RIGHT
    return {
        "snp_susceptible_A": susceptible,
        "snp_resistant_G": resistant_transition,
        "snp_resistant_T": resistant_transversion,
    }


def sample_window(seq: str, center: int, length: int, rng: random.Random, jitter: int) -> tuple[str, int]:
    start = center - length // 2 + rng.randint(-jitter, jitter)
    start = max(0, min(start, len(seq) - length))
    return seq[start : start + length], start


def generate_clean_rows(lengths: list[int], reads_per_label: int, seed: int) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    rng = random.Random(seed)
    templates: dict[str, tuple[str, str, str, int]] = {}
    for label, motif in ARG_MOTIFS.items():
        template = template_with_marker(motif, rng=random.Random(f"{seed}:{label}"), marker_pos=170)
        templates[label] = ("arg_family", label, template, 170 + len(motif) // 2)
    non_arg = template_with_marker(NON_ARG_MOTIF, rng=random.Random(f"{seed}:non_arg"), marker_pos=170)
    templates["non_arg_background"] = ("arg_family", "non_arg_background", non_arg, 170 + len(NON_ARG_MOTIF) // 2)

    base_allele = template_with_marker(ARG_MOTIFS["bla_family_A"], rng=random.Random(f"{seed}:allele_base"), marker_pos=170)
    templates["arg_allele_A"] = ("arg_allele", "arg_allele_A", base_allele, 190)
    templates["arg_allele_B"] = ("arg_allele", "arg_allele_B", mutate_template(base_allele, [184, 195, 207], seed + 1), 190)
    templates["arg_allele_C"] = ("arg_allele", "arg_allele_C", mutate_template(base_allele, [181, 199, 214], seed + 2), 190)

    snp_templates = resistance_templates()
    snp_center = len(SNP_LEFT)
    for label, template in snp_templates.items():
        templates[label] = ("resistance_snp", "resistant" if "resistant" in label else "susceptible", template, snp_center)

    for label, (task, task_label, template, center) in templates.items():
        for length in lengths:
            if length > len(template):
                continue
            for idx in range(reads_per_label):
                local_rng = random.Random(f"{seed}:{task}:{label}:{length}:{idx}:{rng.random()}")
                jitter = 8 if task != "resistance_snp" else 2
                read, start = sample_window(template, center, length, local_rng, jitter=jitter)
                clean_id = f"{task}_{label}_L{length}_R{idx:04d}"
                rows.append(
                    {
                        "read_id": f"{clean_id}_clean",
                        "clean_read_id": clean_id,
                        "sequence": read,
                        "label": task_label,
                        "raw_label": label,
                        "task": task,
                        "condition": "clean",
                        "source_length": length,
                        "length": len(read),
                        "template_start": start,
                        "mutation_profile": "{}",
                    }
                )
    return pd.DataFrame(rows)


def derive_conditions(clean: pd.DataFrame, conditions: list[str], seed: int) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for _, row in clean.iterrows():
        for condition in conditions:
            out = apply_stage2_condition(row, condition, seed)
            out["task"] = row["task"]
            out["raw_label"] = row["raw_label"]
            rows.append(out)
    df = pd.DataFrame(rows)
    df["source_length"] = df["source_length"].astype(int)
    df["length"] = df["length"].astype(int)
    return df


def paired_subsets(df: pd.DataFrame, task: str, length: int, condition: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    clean = df[(df["task"] == task) & (df["source_length"] == length) & (df["condition"] == "clean")].copy()
    pert = df[(df["task"] == task) & (df["source_length"] == length) & (df["condition"] == condition)].copy()
    common = sorted(set(clean["clean_read_id"]) & set(pert["clean_read_id"]))
    clean = clean[clean["clean_read_id"].isin(common)].sort_values("clean_read_id").reset_index(drop=True)
    pert = pert[pert["clean_read_id"].isin(common)].sort_values("clean_read_id").reset_index(drop=True)
    return clean, pert


def run_stability(df: pd.DataFrame, reps: list[str], lengths: list[int], conditions: list[str]) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for task in sorted(df["task"].unique()):
        for length in lengths:
            for condition in conditions:
                if condition == "clean":
                    continue
                clean, pert = paired_subsets(df, task, length, condition)
                if clean.empty:
                    continue
                all_seq = clean["sequence"].tolist() + pert["sequence"].tolist()
                train_idx = list(range(len(clean)))
                for rep in reps:
                    try:
                        x, info = build_feature_matrix(all_seq, rep, length=length, train_indices=train_idx)
                        metric = paired_retrieval_metrics(x[: len(clean)], x[len(clean) :])
                        metric.update(
                            {
                                "task": task,
                                "length": length,
                                "condition": condition,
                                "representation": rep,
                                "n_pairs": int(len(clean)),
                                "n_features": info.n_features,
                                "density": info.density,
                            }
                        )
                        rows.append(metric)
                    except Exception as exc:
                        rows.append(
                            {
                                "task": task,
                                "length": length,
                                "condition": condition,
                                "representation": rep,
                                "error": f"{type(exc).__name__}: {exc}",
                            }
                        )
    return pd.DataFrame(rows)


def run_readouts(df: pd.DataFrame, reps: list[str], lengths: list[int], conditions: list[str], seed: int) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    models = {
        "nearest_centroid": NearestCentroid(),
        "logistic": make_pipeline(StandardScaler(), LogisticRegression(max_iter=3000, random_state=seed)),
    }
    for task in sorted(df["task"].unique()):
        for length in lengths:
            for condition in conditions:
                subset = df[(df["task"] == task) & (df["source_length"] == length) & (df["condition"] == condition)].copy()
                if subset.empty or subset["label"].nunique() < 2:
                    continue
                y = LabelEncoder().fit_transform(subset["label"].astype(str).to_numpy())
                unique, counts = np.unique(y, return_counts=True)
                if np.min(counts) < 4:
                    continue
                idx = np.arange(len(y))
                train_idx, test_idx = train_test_split(idx, test_size=0.3, random_state=seed, stratify=y)
                for rep in reps:
                    try:
                        x, info = build_feature_matrix(subset["sequence"].tolist(), rep, length=length, train_indices=train_idx.tolist())
                        for model_name, model in models.items():
                            model.fit(x[train_idx], y[train_idx])
                            pred = model.predict(x[test_idx])
                            rows.append(
                                {
                                    "task": task,
                                    "length": length,
                                    "condition": condition,
                                    "representation": rep,
                                    "classifier": model_name,
                                    "n_samples": int(len(subset)),
                                    "n_classes": int(len(unique)),
                                    "n_features": info.n_features,
                                    "accuracy": float(accuracy_score(y[test_idx], pred)),
                                    "macro_f1": float(f1_score(y[test_idx], pred, average="macro", zero_division=0)),
                                }
                            )
                    except Exception as exc:
                        rows.append(
                            {
                                "task": task,
                                "length": length,
                                "condition": condition,
                                "representation": rep,
                                "classifier": "all",
                                "error": f"{type(exc).__name__}: {exc}",
                            }
                        )
    return pd.DataFrame(rows)


def write_summary(stability: pd.DataFrame, readout: pd.DataFrame, output_dir: Path) -> None:
    lines: list[str] = []
    lines.append("# Stage-2 ARG/SNP Boundary Task\n")
    lines.append("This synthetic boundary task tests whether CSP can act alone in ARG-family, ARG-allele and resistance-SNP style probes.\n")
    if not stability.empty:
        valid = stability[~stability.get("error", pd.Series(index=stability.index, dtype=object)).notna()]
        best = (
            valid.sort_values(["task", "condition", "length", "paired_cosine_mean"], ascending=[True, True, True, False])
            .groupby(["task", "condition", "length"], as_index=False)
            .first()
        )
        lines.append("## Best perturbation stability\n")
        lines.append(best[["task", "condition", "length", "representation", "paired_cosine_mean", "l2_delta_mean", "retrieval_top1", "n_features"]].to_markdown(index=False, floatfmt=".3f"))
        lines.append("")
    if not readout.empty and "macro_f1" in readout:
        valid_r = readout.dropna(subset=["macro_f1"])
        best_r = (
            valid_r.sort_values(["task", "condition", "length", "macro_f1"], ascending=[True, True, True, False])
            .groupby(["task", "condition", "length"], as_index=False)
            .first()
        )
        lines.append("## Best readout performance\n")
        lines.append(best_r[["task", "condition", "length", "representation", "classifier", "macro_f1", "accuracy"]].to_markdown(index=False, floatfmt=".3f"))
        lines.append("")
        snp = valid_r[valid_r["task"] == "resistance_snp"]
        if not snp.empty:
            lines.append("## Resistance-SNP task by representation\n")
            pivot = snp.groupby(["condition", "length", "representation"], as_index=False).agg(mean_macro_f1=("macro_f1", "mean"))
            lines.append(pivot.to_markdown(index=False, floatfmt=".3f"))
            lines.append("")
    (output_dir / "arg_snp_boundary_summary.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run synthetic ARG/SNP boundary probes.")
    parser.add_argument("--output-dir", default=str(PROJECT_ROOT / "results" / "stage2" / "arg_snp_boundary"))
    parser.add_argument("--lengths", default="69,75,100,150")
    parser.add_argument("--conditions", default="clean,substitution_1pct,N_3pct,trim_5bp,substitution_1pct_N_3pct,local_mismatch_6bp")
    parser.add_argument("--representations", default="ckmer5_count_l2,ckmer7_count_l2,cspaced_count_l2,cspaced_property_l2,hybrid_ckmer5_csp,hybrid_ckmer7_csp")
    parser.add_argument("--reads-per-label", type=int, default=120)
    parser.add_argument("--seed", type=int, default=505)
    args = parser.parse_args()

    started = time.time()
    set_global_seed(args.seed)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    lengths = parse_int_list(args.lengths)
    conditions = parse_csv_list(args.conditions)
    reps = parse_csv_list(args.representations)
    clean = generate_clean_rows(lengths, reads_per_label=args.reads_per_label, seed=args.seed)
    df = derive_conditions(clean, conditions, seed=args.seed)
    df.to_csv(output_dir / "arg_snp_reads.csv", index=False, encoding="utf-8-sig")
    stability = run_stability(df, reps, lengths, conditions)
    readout = run_readouts(df, reps, lengths, conditions, seed=args.seed)
    stability.to_csv(output_dir / "arg_snp_stability.csv", index=False, encoding="utf-8-sig")
    readout.to_csv(output_dir / "arg_snp_readout.csv", index=False, encoding="utf-8-sig")
    write_summary(stability, readout, output_dir)
    (output_dir / "arg_snp_boundary_run.json").write_text(
        json.dumps(
            {
                "elapsed_seconds": time.time() - started,
                "lengths": lengths,
                "conditions": conditions,
                "representations": reps,
                "reads_per_label": args.reads_per_label,
                "seed": args.seed,
                "n_reads": int(len(df)),
                "n_stability_rows": int(len(stability)),
                "n_readout_rows": int(len(readout)),
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    print(f"Wrote ARG/SNP boundary task to {output_dir}")


if __name__ == "__main__":
    main()

