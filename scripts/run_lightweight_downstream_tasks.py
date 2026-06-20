from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier, NearestCentroid
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.representation_registry import build_representation, l2_normalize_dense, parse_kmer_representation
from src.sklearn_features import build_kmer_matrix, transform_feature_matrix
from src.spaced_features import spaced_count_dense


def parse_csv_list(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def parse_int_list(value: str) -> list[int]:
    return [int(item.strip()) for item in value.split(",") if item.strip()]


def write_json(path: Path, obj: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        json.dump(obj, fh, indent=2, ensure_ascii=False, sort_keys=True)


def cosine_sim_matrix(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    a = l2_normalize_dense(a)
    b = l2_normalize_dense(b)
    return a @ b.T


def build_representation_matrix(
    sequences: list[str],
    representation: str,
    length: int,
    train_indices: list[int] | None = None,
) -> np.ndarray:
    """Build a dense feature matrix, fitting k-mer vocab/IDF on train rows only."""
    parsed = parse_kmer_representation(representation)
    if not parsed:
        if representation in {"spaced_count_l2", "cspaced_count_l2", "cspaced_property_l2"}:
            canonical = representation.startswith("cs")
            add_property = representation == "cspaced_property_l2"
            return spaced_count_dense(sequences, canonical=canonical, train_indices=train_indices, add_property_summary=add_property)
        return build_representation(sequences, representation, length, train_indices=train_indices)

    k, feature_type, normalization, canonical = parsed
    if train_indices is None:
        train_indices = list(range(len(sequences)))
    train_sequences = [sequences[i] for i in train_indices]
    _, vocabulary = build_kmer_matrix(train_sequences, k=k, canonical=canonical, vocabulary_mode="observed")
    mat, _ = build_kmer_matrix(sequences, k=k, canonical=canonical, vocabulary=vocabulary)
    feat, _ = transform_feature_matrix(
        mat,
        feature_type=feature_type,
        normalization=normalization,
        train_indices=train_indices,
    )
    return feat.toarray()


def build_representation_pair(
    seq_a: list[str],
    seq_b: list[str],
    representation: str,
    length: int,
) -> tuple[np.ndarray, np.ndarray]:
    parsed = parse_kmer_representation(representation)
    if not parsed:
        if representation in {"spaced_count_l2", "cspaced_count_l2", "cspaced_property_l2"}:
            canonical = representation.startswith("cs")
            add_property = representation == "cspaced_property_l2"
            all_seq = seq_a + seq_b
            dense = spaced_count_dense(
                all_seq,
                canonical=canonical,
                train_indices=list(range(len(seq_a))),
                add_property_summary=add_property,
            )
            return dense[: len(seq_a)], dense[len(seq_a):]
        return build_representation(seq_a, representation, length), build_representation(seq_b, representation, length)
    k, feature_type, normalization, canonical = parsed
    all_seq = seq_a + seq_b
    _, vocabulary = build_kmer_matrix(seq_a, k=k, canonical=canonical, vocabulary_mode="observed")
    mat, _ = build_kmer_matrix(all_seq, k=k, canonical=canonical, vocabulary=vocabulary)
    feat, _ = transform_feature_matrix(
        mat,
        feature_type=feature_type,
        normalization=normalization,
        train_indices=list(range(len(seq_a))),
    )
    dense = feat.toarray()
    return dense[: len(seq_a)], dense[len(seq_a):]


def paired_similarity_summary(sim: np.ndarray) -> dict[str, float]:
    diag = np.diag(sim)
    masked = sim.copy()
    np.fill_diagonal(masked, -np.inf)
    nearest_nonpaired = np.max(masked, axis=1)
    ranks = []
    for i in range(sim.shape[0]):
        order = np.argsort(-sim[i])
        rank = int(np.where(order == i)[0][0]) + 1
        ranks.append(rank)
    ranks_arr = np.asarray(ranks)
    margins = diag - nearest_nonpaired
    return {
        "top1": float(np.mean(ranks_arr <= 1)),
        "top5": float(np.mean(ranks_arr <= 5)),
        "mrr": float(np.mean(1.0 / ranks_arr)),
        "mean_rank": float(np.mean(ranks_arr)),
        "mean_paired_cosine": float(np.mean(diag)),
        "median_paired_cosine": float(np.median(diag)),
        "mean_nearest_nonpaired_cosine": float(np.mean(nearest_nonpaired)),
        "mean_pair_margin": float(np.mean(margins)),
        "margin_positive_rate": float(np.mean(margins > 0)),
    }


def paired_retrieval(df: pd.DataFrame, representation: str, length: int, condition: str) -> dict[str, object]:
    clean = df[(df["source_length"] == length) & (df["condition"] == "clean")].copy()
    pert = df[(df["source_length"] == length) & (df["condition"] == condition)].copy()
    if clean.empty or pert.empty:
        return {"error": "missing clean or perturbed data"}
    clean = clean.sort_values("clean_read_id").reset_index(drop=True)
    pert = pert.sort_values("clean_read_id").reset_index(drop=True)
    common = sorted(set(clean["clean_read_id"]) & set(pert["clean_read_id"]))
    clean = clean[clean["clean_read_id"].isin(common)].sort_values("clean_read_id").reset_index(drop=True)
    pert = pert[pert["clean_read_id"].isin(common)].sort_values("clean_read_id").reset_index(drop=True)
    x_clean, x_pert = build_representation_pair(clean["sequence"].tolist(), pert["sequence"].tolist(), representation, length)
    sim = cosine_sim_matrix(x_pert, x_clean)
    summary = paired_similarity_summary(sim)
    return {
        "task": "paired_retrieval",
        "representation": representation,
        "length": length,
        "condition": condition,
        "n": int(len(common)),
        **summary,
    }


def rc_consistency(df: pd.DataFrame, representation: str, length: int) -> dict[str, object]:
    clean = df[(df["source_length"] == length) & (df["condition"] == "clean")].copy()
    rc = df[(df["source_length"] == length) & (df["condition"] == "reverse_complement")].copy()
    if clean.empty or rc.empty:
        return {"error": "missing clean or reverse_complement data"}
    common = sorted(set(clean["clean_read_id"]) & set(rc["clean_read_id"]))
    clean = clean[clean["clean_read_id"].isin(common)].sort_values("clean_read_id").reset_index(drop=True)
    rc = rc[rc["clean_read_id"].isin(common)].sort_values("clean_read_id").reset_index(drop=True)
    x_clean, x_rc = build_representation_pair(clean["sequence"].tolist(), rc["sequence"].tolist(), representation, length)
    sim = cosine_sim_matrix(x_rc, x_clean)
    summary = paired_similarity_summary(sim)
    return {
        "task": "rc_consistency",
        "representation": representation,
        "length": length,
        "n": int(len(clean)),
        "nearest_rc_hit_rate": summary["top1"],
        **summary,
    }


def contamination_detection(df: pd.DataFrame, representation: str, length: int, seed: int) -> dict[str, object]:
    # positive: low_complexity/adapter/N_3pct if available; negative: clean
    subset = df[(df["source_length"] == length) & (df["condition"].isin(["clean", "N_3pct", "low_complexity", "adapter_like"]))].copy()
    if subset["condition"].nunique() < 2:
        return {"error": "need clean plus contamination-like condition"}
    subset["target"] = (subset["condition"] != "clean").astype(int)
    y = subset["target"].to_numpy()
    if len(np.unique(y)) < 2:
        return {"error": "single target class"}
    idx = np.arange(len(y))
    train_idx, test_idx = train_test_split(idx, test_size=0.3, random_state=seed, stratify=y)
    x = build_representation_matrix(subset["sequence"].tolist(), representation, length, train_indices=train_idx.tolist())
    clf = make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000, random_state=seed))
    clf.fit(x[train_idx], y[train_idx])
    pred = clf.predict(x[test_idx])
    score = clf.predict_proba(x[test_idx])[:, 1]
    return {
        "task": "contamination_detection",
        "representation": representation,
        "length": length,
        "n": int(len(subset)),
        "accuracy": float(accuracy_score(y[test_idx], pred)),
        "macro_f1": float(f1_score(y[test_idx], pred, average="macro", zero_division=0)),
        "auroc": float(roc_auc_score(y[test_idx], score)),
    }


def lightweight_classification(
    df: pd.DataFrame,
    representation: str,
    length: int,
    labels: list[str],
    condition: str,
    seed: int,
    task: str,
    classifier_names: list[str],
) -> list[dict[str, object]]:
    subset = df[(df["source_length"] == length) & (df["condition"] == condition) & (df["label"].isin(labels))].copy()
    if subset.empty or subset["label"].nunique() < 2:
        return [{"task": task, "representation": representation, "length": length, "condition": condition, "error": "missing labels"}]
    y = subset["label"].to_numpy()
    unique, counts = np.unique(y, return_counts=True)
    if np.min(counts) < 2:
        return [{"task": task, "representation": representation, "length": length, "condition": condition, "error": "not enough rows per label"}]
    idx = np.arange(len(y))
    train_idx, test_idx = train_test_split(idx, test_size=0.3, random_state=seed, stratify=y)
    x = build_representation_matrix(subset["sequence"].tolist(), representation, length, train_indices=train_idx.tolist())
    classifiers = {
        "nearest_centroid": NearestCentroid(),
        "knn_3": KNeighborsClassifier(n_neighbors=min(3, len(train_idx))),
        "logistic_regression": make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000, random_state=seed)),
    }
    classifiers = {name: clf for name, clf in classifiers.items() if name in set(classifier_names)}
    rows: list[dict[str, object]] = []
    for clf_name, clf in classifiers.items():
        try:
            clf.fit(x[train_idx], y[train_idx])
            pred = clf.predict(x[test_idx])
            rows.append(
                {
                    "task": task,
                    "representation": representation,
                    "length": length,
                    "condition": condition,
                    "classifier": clf_name,
                    "n": int(len(subset)),
                    "accuracy": float(accuracy_score(y[test_idx], pred)),
                    "macro_f1": float(f1_score(y[test_idx], pred, average="macro", zero_division=0)),
                }
            )
        except Exception as exc:
            rows.append(
                {
                    "task": task,
                    "representation": representation,
                    "length": length,
                    "condition": condition,
                    "classifier": clf_name,
                    "error": f"{type(exc).__name__}: {exc}",
                }
            )
    return rows


def length_transfer(df: pd.DataFrame, representation: str, train_length: int, test_length: int, seed: int) -> dict[str, object]:
    train = df[(df["source_length"] == train_length) & (df["condition"] == "clean")].copy()
    test = df[(df["source_length"] == test_length) & (df["condition"] == "clean")].copy()
    if train.empty or test.empty:
        return {"error": "missing train/test length"}
    # Encode both to train_length-compatible size by using each read's target length for its matrix is tricky.
    # Here we use max length and let shorter sequences pad.
    encode_length = max(train_length, test_length)
    x_train, x_test = build_representation_pair(train["sequence"].tolist(), test["sequence"].tolist(), representation, encode_length)
    y_train = train["label"].to_numpy()
    y_test = test["label"].to_numpy()
    clf = KNeighborsClassifier(n_neighbors=3)
    clf.fit(x_train, y_train)
    pred = clf.predict(x_test)
    return {
        "task": "length_transfer",
        "representation": representation,
        "train_length": train_length,
        "test_length": test_length,
        "accuracy": float(accuracy_score(y_test, pred)),
        "macro_f1": float(f1_score(y_test, pred, average="macro", zero_division=0)),
    }


def ood_rejection(
    df: pd.DataFrame,
    representation: str,
    length: int,
    known_labels: list[str],
    condition: str,
    seed: int,
) -> dict[str, object]:
    subset = df[(df["source_length"] == length) & (df["condition"] == condition)].copy()
    known = subset[subset["label"].isin(known_labels)].copy()
    unknown = subset[~subset["label"].isin(known_labels)].copy()
    if known["label"].nunique() < 2 or unknown.empty:
        return {"task": "ood_rejection", "representation": representation, "length": length, "condition": condition, "error": "need at least two known labels and one unknown label"}
    y_known = known["label"].to_numpy()
    train_known_idx, test_known_idx = train_test_split(
        np.arange(len(known)),
        test_size=0.3,
        random_state=seed,
        stratify=y_known,
    )
    train_df = known.iloc[train_known_idx].copy()
    test_df = pd.concat([known.iloc[test_known_idx], unknown], ignore_index=True)
    all_df = pd.concat([train_df, test_df], ignore_index=True)
    train_indices = list(range(len(train_df)))
    x = build_representation_matrix(all_df["sequence"].tolist(), representation, length, train_indices=train_indices)
    x_norm = l2_normalize_dense(x)
    centroids = []
    for label in known_labels:
        label_idx = [i for i, lab in enumerate(train_df["label"].tolist()) if lab == label]
        if label_idx:
            centroids.append(x_norm[label_idx].mean(axis=0))
    if len(centroids) < 2:
        return {"task": "ood_rejection", "representation": representation, "length": length, "condition": condition, "error": "missing class centroid"}
    centroid_mat = l2_normalize_dense(np.vstack(centroids))
    test_x = x_norm[len(train_df):]
    max_sim = np.max(test_x @ centroid_mat.T, axis=1)
    is_known = test_df["label"].isin(known_labels).astype(int).to_numpy()
    if len(np.unique(is_known)) < 2:
        return {"task": "ood_rejection", "representation": representation, "length": length, "condition": condition, "error": "single known/OOD target"}
    train_self_sim = np.max(x_norm[: len(train_df)] @ centroid_mat.T, axis=1)
    threshold = float(np.quantile(train_self_sim, 0.05))
    accepted = max_sim >= threshold
    return {
        "task": "ood_rejection",
        "representation": representation,
        "length": length,
        "condition": condition,
        "known_labels": ",".join(known_labels),
        "n_known_test": int(is_known.sum()),
        "n_ood": int((1 - is_known).sum()),
        "known_detection_auroc": float(roc_auc_score(is_known, max_sim)),
        "ood_detection_auroc": float(roc_auc_score(1 - is_known, -max_sim)),
        "known_accept_rate_at_train_p05": float(np.mean(accepted[is_known == 1])),
        "ood_reject_rate_at_train_p05": float(np.mean(~accepted[is_known == 0])),
        "mean_known_max_similarity": float(np.mean(max_sim[is_known == 1])),
        "mean_ood_max_similarity": float(np.mean(max_sim[is_known == 0])),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run lightweight downstream representation tasks.")
    parser.add_argument("--input", default="data/toy_reads/toy_first_wave.csv")
    parser.add_argument("--output-dir", default="results/runs/lightweight_downstream_first_wave")
    parser.add_argument("--representations", default="kmer5_count_l2,ckmer5_count_l2,kmer7_tfidf_l2,ckmer7_tfidf_l2,one_hot,property_channels,three_phase,spaced_kmer_phase,codon_frame_channels,rope_property,rc_rope_pool")
    parser.add_argument("--lengths", default="69,75,100")
    parser.add_argument("--paired-conditions", default="substitution_1pct,substitution_2pct,substitution_5pct,N_3pct,N_5pct,N_cluster_5pct,trim_to_69,random_crop_69,indel_stress")
    parser.add_argument("--classification-conditions", default="clean,substitution_1pct,N_3pct")
    parser.add_argument("--classification-classifiers", default="nearest_centroid,knn_3")
    parser.add_argument("--tasks", default="paired_retrieval,rc_consistency,contamination_detection,same_composition_order,motif_position,near_snp_discrimination,ood_rejection,length_transfer")
    parser.add_argument("--known-labels", default="GC_rich,AT_rich")
    parser.add_argument("--seed", type=int, default=13)
    args = parser.parse_args()

    df = pd.read_csv(args.input)
    reps = parse_csv_list(args.representations)
    lengths = parse_int_list(args.lengths)
    paired_conditions = parse_csv_list(args.paired_conditions)
    classification_conditions = parse_csv_list(args.classification_conditions)
    classification_classifiers = parse_csv_list(args.classification_classifiers)
    tasks = set(parse_csv_list(args.tasks))
    known_labels = parse_csv_list(args.known_labels)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    started = time.time()

    for rep in reps:
        for length in lengths:
            if "paired_retrieval" in tasks:
                for condition in paired_conditions:
                    if condition == "trim_to_69" and length < 69:
                        continue
                    try:
                        rows.append(paired_retrieval(df, rep, length, condition))
                    except Exception as exc:
                        rows.append({"task": "paired_retrieval", "representation": rep, "length": length, "condition": condition, "error": f"{type(exc).__name__}: {exc}"})
            if "rc_consistency" in tasks:
                try:
                    rows.append(rc_consistency(df, rep, length))
                except Exception as exc:
                    rows.append({"task": "rc_consistency", "representation": rep, "length": length, "error": f"{type(exc).__name__}: {exc}"})
            if "contamination_detection" in tasks:
                try:
                    rows.append(contamination_detection(df, rep, length, args.seed))
                except Exception as exc:
                    rows.append({"task": "contamination_detection", "representation": rep, "length": length, "error": f"{type(exc).__name__}: {exc}"})
            for condition in classification_conditions:
                if "same_composition_order" in tasks:
                    try:
                        rows.extend(lightweight_classification(df, rep, length, ["same_comp_A", "same_comp_B"], condition, args.seed, "same_composition_order", classification_classifiers))
                    except Exception as exc:
                        rows.append({"task": "same_composition_order", "representation": rep, "length": length, "condition": condition, "error": f"{type(exc).__name__}: {exc}"})
                if "motif_position" in tasks:
                    try:
                        rows.extend(lightweight_classification(df, rep, length, ["motif_front", "motif_middle", "motif_back"], condition, args.seed, "motif_position", classification_classifiers))
                    except Exception as exc:
                        rows.append({"task": "motif_position", "representation": rep, "length": length, "condition": condition, "error": f"{type(exc).__name__}: {exc}"})
                if "near_snp_discrimination" in tasks:
                    try:
                        rows.extend(lightweight_classification(df, rep, length, ["GC_rich", "near_SNP"], condition, args.seed, "near_snp_discrimination", classification_classifiers))
                    except Exception as exc:
                        rows.append({"task": "near_snp_discrimination", "representation": rep, "length": length, "condition": condition, "error": f"{type(exc).__name__}: {exc}"})
            if "ood_rejection" in tasks:
                try:
                    rows.append(ood_rejection(df, rep, length, known_labels, "clean", args.seed))
                except Exception as exc:
                    rows.append({"task": "ood_rejection", "representation": rep, "length": length, "condition": "clean", "error": f"{type(exc).__name__}: {exc}"})
        if "length_transfer" in tasks:
            for test_length in [69, 100, 150]:
                if test_length == 75:
                    continue
                try:
                    rows.append(length_transfer(df, rep, 75, test_length, args.seed))
                except Exception as exc:
                    rows.append({"task": "length_transfer", "representation": rep, "train_length": 75, "test_length": test_length, "error": f"{type(exc).__name__}: {exc}"})

    write_json(output_dir / "lightweight_downstream_results.json", {"elapsed_seconds": time.time() - started, "results": rows})
    pd.DataFrame(rows).to_csv(output_dir / "lightweight_downstream_results.csv", index=False, encoding="utf-8-sig")
    print(f"Wrote {len(rows)} downstream task rows to {output_dir}")


if __name__ == "__main__":
    main()
