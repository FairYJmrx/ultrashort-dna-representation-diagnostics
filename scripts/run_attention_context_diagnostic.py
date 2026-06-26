from __future__ import annotations

import argparse
import json
import math
import random
import sys
from collections import Counter
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import sparse
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, mutual_info_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.representation_registry import build_representation, parse_kmer_representation
from src.sequence_utils import random_dna, reverse_complement
from src.sklearn_features import build_kmer_matrix, transform_feature_matrix
from src.spaced_features import spaced_count_dense


ANCHOR_MOTIF = "ACGTTGCA"
ANCHOR_POS = 18
CLASS_MOTIF_POS = 138
CLASS_MOTIFS = {
    "context_A": "GATTACAGCG",
    "context_B": "CTAGGCTTAA",
    "context_C": "TGCACCATGA",
}
DISTRACTORS = ["AACCGGTA", "TTGACCAA", "CGTATGGC", "GGCATACC"]


def parse_int_list(value: str) -> list[int]:
    return [int(item.strip()) for item in value.split(",") if item.strip()]


def parse_csv_list(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def insert(seq: str, motif: str, pos: int) -> str:
    chars = list(seq)
    chars[pos : pos + len(motif)] = list(motif)
    return "".join(chars)


def make_latent_template(label: str, latent_length: int, rng: random.Random) -> str:
    seq = random_dna(latent_length, {"A": 0.25, "C": 0.25, "G": 0.25, "T": 0.25}, rng)
    seq = insert(seq, ANCHOR_MOTIF, ANCHOR_POS)
    seq = insert(seq, CLASS_MOTIFS[label], CLASS_MOTIF_POS)
    for pos in [52, 88, 178, 222]:
        seq = insert(seq, rng.choice(DISTRACTORS), pos)
    return seq


def observe_read(template: str, length: int, layout: str, pe_length: int = 150, insert_size: int = 240) -> str:
    if layout.startswith("PE"):
        r1 = template[:pe_length]
        r2_start = max(pe_length, insert_size - pe_length)
        r2 = reverse_complement(template[r2_start : r2_start + pe_length])
        return r1 + r2
    return template[:length]


def generate_dataset(lengths: list[int], reads_per_class: int, seed: int) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    rng = random.Random(seed)
    for label in CLASS_MOTIFS:
        for idx in range(reads_per_class):
            local_rng = random.Random(f"{seed}:{label}:{idx}:{rng.random()}")
            template = make_latent_template(label, latent_length=320, rng=local_rng)
            for length in lengths:
                if length == 300:
                    layout = "PE150"
                    read = observe_read(template, length, layout="PE150")
                else:
                    layout = f"SE{length}"
                    read = observe_read(template, length, layout=layout)
                class_motif = CLASS_MOTIFS[label]
                anchor_visible = ANCHOR_MOTIF in read
                class_visible = class_motif in read
                any_class_visible = any(motif in read for motif in CLASS_MOTIFS.values())
                rows.append(
                    {
                        "read_id": f"{label}_{layout}_{idx:04d}",
                        "sequence": read,
                        "label": label,
                        "source_length": length,
                        "observed_layout": layout,
                        "anchor_visible": int(anchor_visible),
                        "class_motif_visible": int(class_visible),
                        "any_class_motif_visible": int(any_class_visible),
                        "pair_visible": int(anchor_visible and class_visible),
                        "anchor_pos": read.find(ANCHOR_MOTIF),
                        "class_pos": read.find(class_motif),
                        "context_distance": read.find(class_motif) - read.find(ANCHOR_MOTIF)
                        if anchor_visible and class_visible
                        else -1,
                    }
                )
    return pd.DataFrame(rows)


def kmer_presence_features(sequences: list[str], k: int, vocabulary: list[str] | None = None) -> tuple[np.ndarray, list[str]]:
    if vocabulary is None:
        observed = set()
        for seq in sequences:
            for i in range(max(0, len(seq) - k + 1)):
                token = seq[i : i + k]
                if "N" not in token:
                    observed.add(token)
        vocabulary = sorted(observed)
    vocab_index = {token: idx for idx, token in enumerate(vocabulary)}
    x = np.zeros((len(sequences), len(vocabulary)), dtype=np.float64)
    for row, seq in enumerate(sequences):
        seen = set()
        for i in range(max(0, len(seq) - k + 1)):
            token = seq[i : i + k]
            if token in vocab_index:
                seen.add(vocab_index[token])
        for col in seen:
            x[row, col] = 1.0
    return x, vocabulary


def motif_pair_features(df: pd.DataFrame) -> np.ndarray:
    rows = []
    for _, row in df.iterrows():
        seq = str(row["sequence"])
        anchor = 1.0 if ANCHOR_MOTIF in seq else 0.0
        class_hits = [1.0 if motif in seq else 0.0 for motif in CLASS_MOTIFS.values()]
        pair_hits = [anchor * hit for hit in class_hits]
        distances = []
        anchor_pos = seq.find(ANCHOR_MOTIF)
        for motif in CLASS_MOTIFS.values():
            pos = seq.find(motif)
            distances.append((pos - anchor_pos) / 300.0 if anchor_pos >= 0 and pos >= 0 else -1.0)
        rows.append([anchor, *class_hits, *pair_hits, *distances, len(seq) / 300.0])
    return np.asarray(rows, dtype=np.float64)


def partial_class_prefix_rate(df: pd.DataFrame, min_prefix: int = 5) -> float:
    hits = 0
    for _, row in df.iterrows():
        seq = str(row["sequence"])
        motif = CLASS_MOTIFS[str(row["label"])]
        if any(motif[:prefix] in seq for prefix in range(len(motif) - 1, min_prefix - 1, -1)):
            hits += 1
    return hits / max(1, len(df))


def build_representation_matrix(
    sequences: list[str],
    representation: str,
    length: int,
    train_indices: list[int],
) -> np.ndarray:
    if representation == "kmer5_presence":
        train_sequences = [sequences[i] for i in train_indices]
        _, vocabulary = kmer_presence_features(train_sequences, 5)
        x, _ = kmer_presence_features(sequences, 5, vocabulary)
        return x
    parsed = parse_kmer_representation(representation)
    if parsed:
        k, feature_type, normalization, canonical = parsed
        train_sequences = [sequences[i] for i in train_indices]
        _, vocabulary = build_kmer_matrix(train_sequences, k=k, canonical=canonical, vocabulary_mode="observed")
        mat, _ = build_kmer_matrix(sequences, k=k, canonical=canonical, vocabulary=vocabulary)
        feat, _ = transform_feature_matrix(mat, feature_type=feature_type, normalization=normalization, train_indices=train_indices)
        return feat.toarray() if sparse.issparse(feat) else np.asarray(feat)
    if representation in {"spaced_count_l2", "cspaced_count_l2", "cspaced_property_l2"}:
        canonical = representation.startswith("cs")
        add_property = representation == "cspaced_property_l2"
        return spaced_count_dense(sequences, canonical=canonical, train_indices=train_indices, add_property_summary=add_property)
    return build_representation(sequences, representation, length=length, train_indices=train_indices)


def evaluate_classifier(df: pd.DataFrame, representation: str, seed: int) -> list[dict[str, object]]:
    y = df["label"].astype(str).to_numpy()
    idx = np.arange(len(df))
    train_idx, test_idx = train_test_split(idx, test_size=0.3, random_state=seed, stratify=y)
    if representation == "oracle_motif_pair":
        x = motif_pair_features(df)
    else:
        x = build_representation_matrix(df["sequence"].tolist(), representation, int(df["source_length"].iloc[0]), train_idx.tolist())
    rows = []
    for clf_name, clf in {
        "nearest_linear_probe": make_pipeline(StandardScaler(), LogisticRegression(max_iter=3000, random_state=seed)),
    }.items():
        clf.fit(x[train_idx], y[train_idx])
        pred = clf.predict(x[test_idx])
        rows.append(
            {
                "classifier": clf_name,
                "accuracy": float(accuracy_score(y[test_idx], pred)),
                "macro_f1": float(f1_score(y[test_idx], pred, average="macro", zero_division=0)),
                "n_features": int(x.shape[1]),
            }
        )
    return rows


def visibility_metrics(df: pd.DataFrame) -> dict[str, float]:
    y = pd.Categorical(df["label"]).codes
    pair = df["pair_visible"].to_numpy()
    any_class = df["any_class_motif_visible"].to_numpy()
    class_visible = df["class_motif_visible"].to_numpy()
    context_distance = df.loc[df["context_distance"] >= 0, "context_distance"]
    return {
        "anchor_visible_rate": float(df["anchor_visible"].mean()),
        "class_motif_visible_rate": float(class_visible.mean()),
        "any_class_motif_visible_rate": float(any_class.mean()),
        "pair_visible_rate": float(pair.mean()),
        "partial_class_prefix_visible_rate": float(partial_class_prefix_rate(df)),
        "mi_label_pair_visible": float(mutual_info_score(y, pair)),
        "mi_label_any_class_visible": float(mutual_info_score(y, any_class)),
        "mean_context_distance": float(context_distance.mean()) if not context_distance.empty else float("nan"),
    }


def summarize_attention_capacity(length: int) -> dict[str, float]:
    # Full self-attention can only connect observed tokens. The loss here is not
    # quadratic complexity but absence of the second motif in the observed read.
    token_count_base = max(0, length)
    token_count_k5 = max(0, length - 5 + 1)
    possible_pairs_base = token_count_base * token_count_base
    possible_pairs_k5 = token_count_k5 * token_count_k5
    return {
        "base_tokens": int(token_count_base),
        "k5_tokens": int(token_count_k5),
        "full_attention_base_pairs": int(possible_pairs_base),
        "full_attention_k5_pairs": int(possible_pairs_k5),
    }


def plot_results(summary: pd.DataFrame, outdir: Path) -> None:
    outdir.mkdir(parents=True, exist_ok=True)
    plt.figure(figsize=(8, 5))
    metric_df = summary.drop_duplicates(["length"])[["length", "pair_visible_rate", "class_motif_visible_rate"]].sort_values("length")
    x_labels = ["PE150" if v == 300 else str(int(v)) for v in metric_df["length"]]
    plt.plot(x_labels, metric_df["pair_visible_rate"], marker="o", label="Anchor + class motif visible")
    plt.plot(x_labels, metric_df["class_motif_visible_rate"], marker="s", label="Class motif visible")
    plt.ylim(-0.02, 1.05)
    plt.xlabel("Observed read length / layout")
    plt.ylabel("Visibility rate")
    plt.title("Context Visibility Under Read-Length Truncation")
    plt.legend()
    plt.tight_layout()
    plt.savefig(outdir / "fig_attention_context_visibility.png", dpi=200)
    plt.close()

    clf = summary.dropna(subset=["macro_f1"]).copy()
    if not clf.empty:
        plt.figure(figsize=(9, 5))
        for rep, group in clf.groupby("representation"):
            group = group.sort_values("length")
            labels = ["PE150" if v == 300 else str(int(v)) for v in group["length"]]
            plt.plot(labels, group["macro_f1"], marker="o", label=rep)
        plt.ylim(-0.02, 1.05)
        plt.xlabel("Observed read length / layout")
        plt.ylabel("Macro-F1")
        plt.title("Context-Dependent Classification Under Truncation")
        plt.legend(fontsize=8, ncol=2)
        plt.tight_layout()
        plt.savefig(outdir / "fig_attention_context_classification.png", dpi=200)
        plt.close()


def write_markdown(summary: pd.DataFrame, output: Path) -> None:
    lines = [
        "# Attention Context-Loss Diagnostic",
        "",
        "This experiment tests the user hypothesis that ultra-short reads lose more than a linear number of bases: when a class depends on a motif pair, a truncated read may contain the shared anchor motif but not the class-defining second motif. Full self-attention cannot recover a token that is absent from the observed read.",
        "",
        f"Synthetic latent templates contain a shared anchor motif near position {ANCHOR_POS} and a class-specific motif near position {CLASS_MOTIF_POS}. Reads are cropped to 69, 75, 100, 125, and 150 bp, with PE150 represented by concatenating R1 and reverse-complemented R2.",
        "",
        "## Visibility Metrics",
        "",
        "| Length/layout | Pair visible | Class motif visible | Partial motif prefix visible | MI(label; pair visible) | Mean context distance |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    metrics = summary.drop_duplicates(["length"])[
        [
            "length",
            "pair_visible_rate",
            "class_motif_visible_rate",
            "partial_class_prefix_visible_rate",
            "mi_label_pair_visible",
            "mean_context_distance",
        ]
    ].sort_values("length")
    for _, row in metrics.iterrows():
        label = "PE150" if int(row["length"]) == 300 else f"{int(row['length'])} bp"
        dist = "" if pd.isna(row["mean_context_distance"]) else f"{row['mean_context_distance']:.1f}"
        lines.append(
            f"| {label} | {row['pair_visible_rate']:.3f} | {row['class_motif_visible_rate']:.3f} | {row['partial_class_prefix_visible_rate']:.3f} | {row['mi_label_pair_visible']:.3f} | {dist} |"
        )
    lines.extend(["", "## Lightweight Classifier Results", "", "| Representation | Length/layout | Macro-F1 | Accuracy |", "|---|---|---:|---:|"])
    clf = summary.dropna(subset=["macro_f1"]).sort_values(["representation", "length"])
    for _, row in clf.iterrows():
        label = "PE150" if int(row["length"]) == 300 else f"{int(row['length'])} bp"
        lines.append(f"| {row['representation']} | {label} | {row['macro_f1']:.3f} | {row['accuracy']:.3f} |")
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "The diagnostic separates two effects. Short reads have fewer possible attention pairs, but the more important failure mode here is semantic absence: the class-defining motif is not observed below the designed boundary. In that regime, attention can only attend over the shared prefix and distractors, so label information is structurally unavailable. Once the second motif enters the observed read, simple pair-aware features and ordinary sequence representations recover the label more easily.",
            "",
            "This supports a restrained manuscript claim: read-length effects can be nonlinear for context-dependent tasks because the observed sequence may lose an entire motif co-occurrence relation. It does not prove that a full Transformer is superior; it shows why attention-compatible encodings require enough observed context to be meaningful.",
        ]
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run lightweight attention context-loss diagnostic.")
    parser.add_argument("--output-dir", default="results/runs/attention_context_loss")
    parser.add_argument("--figures-dir", default="results/figures")
    parser.add_argument("--lengths", default="69,75,100,125,150,300")
    parser.add_argument("--reads-per-class", type=int, default=180)
    parser.add_argument(
        "--representations",
        default="kmer5_presence,kmer5_count_l2,ckmer5_count_l2,property_channels,rope_property,spaced_kmer_phase,cspaced_property_l2,oracle_motif_pair",
    )
    parser.add_argument("--seed", type=int, default=101)
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    lengths = parse_int_list(args.lengths)
    reps = parse_csv_list(args.representations)
    df = generate_dataset(lengths, reads_per_class=args.reads_per_class, seed=args.seed)
    df.to_csv(output_dir / "attention_context_reads.csv", index=False, encoding="utf-8-sig")

    rows: list[dict[str, object]] = []
    for length in lengths:
        subset = df[df["source_length"] == length].reset_index(drop=True)
        base_metrics = visibility_metrics(subset)
        base_metrics.update(summarize_attention_capacity(length))
        for rep in reps:
            try:
                for eval_row in evaluate_classifier(subset, rep, seed=args.seed):
                    row = {
                        "length": length,
                        "observed_layout": "PE150" if length == 300 else f"SE{length}",
                        "representation": rep,
                        **base_metrics,
                        **eval_row,
                    }
                    rows.append(row)
            except Exception as exc:
                rows.append(
                    {
                        "length": length,
                        "observed_layout": "PE150" if length == 300 else f"SE{length}",
                        "representation": rep,
                        **base_metrics,
                        "error": f"{type(exc).__name__}: {exc}",
                    }
                )
    summary = pd.DataFrame(rows)
    summary.to_csv(output_dir / "attention_context_results.csv", index=False, encoding="utf-8-sig")
    (output_dir / "attention_context_results.json").write_text(
        json.dumps({"results": rows}, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    plot_results(summary, Path(args.figures_dir))
    write_markdown(summary, Path("manuscript") / "attention_context_loss_results.md")
    print(f"Wrote attention context diagnostic to {output_dir}")


if __name__ == "__main__":
    main()
