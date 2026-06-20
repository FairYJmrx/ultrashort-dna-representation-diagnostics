from __future__ import annotations

from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def load(path: Path) -> pd.DataFrame:
    return pd.read_csv(path) if path.exists() else pd.DataFrame()


def best_by(df: pd.DataFrame, group_col: str) -> pd.DataFrame:
    if df.empty:
        return df
    return (
        df.sort_values(["macro_f1", "accuracy"], ascending=False)
        .groupby(group_col, as_index=False)
        .first()
        .sort_values("macro_f1", ascending=False)
    )


def table(df: pd.DataFrame, cols: list[str], n: int = 20) -> str:
    if df.empty:
        return "_No data._"
    return df[cols].head(n).to_markdown(index=False)


def main() -> None:
    runs = PROJECT_ROOT / "results" / "runs"
    comp = load(runs / "composition_first_wave_k357_fast" / "composition_results_flat.csv")
    diag = load(runs / "kmer_diagnostics_first_wave" / "kmer_diagnostics.csv")
    base = load(runs / "base_signal_order_position" / "base_signal_results_flat.csv")
    token = load(runs / "token_audit_order_position" / "token_audit_results_flat.csv")
    pos = load(runs / "position_encoding_advanced_order_position" / "position_encoding_results_flat.csv")
    emb = load(runs / "embedding_proxy_order_position" / "embedding_proxy_results_flat.csv")

    out = []
    out.append("# Final Lightweight Comparison Report\n")
    out.append("This report summarizes the lightweight subproject. All accuracy/F1 values are controlled toy-task separability indicators, not clinical mNGS performance claims.\n")

    out.append("## 1. Datasets\n")
    out.append("- `toy_first_wave.csv`: GC-rich, AT-rich, near-SNP species; lengths 69/75/100/150/200; clean, substitution, N, trim, reverse-complement.\n")
    out.append("- `toy_order_position.csv`: same-composition/different-order and motif-position classes; designed to stress order and position information.\n")

    out.append("## 2. k-mer Diagnostics\n")
    if not diag.empty:
        d75 = diag[(diag["length"].astype(str) == "75") & (diag["condition"] == "clean")].sort_values("k")
        out.append(table(d75, ["k", "theoretical_vocab_size", "observed_vocab_size", "avg_nnz_per_read", "density", "profile_duplicate_rate"], 20))
    else:
        out.append("_No diagnostic data._")
    out.append("\nInterpretation: high k has enormous theoretical vocabulary, while each 75bp read only contributes roughly `L-k+1` observed k-mers. This supports using high k cautiously and measuring observed sparsity rather than assuming larger k is automatically stronger.\n")

    out.append("## 3. Composition Baseline\n")
    comp_best = best_by(comp, "k")
    out.append(table(comp_best, ["k", "length", "condition", "feature_type", "classifier", "accuracy", "macro_f1"], 20))
    out.append("\nInterpretation: k=3/5/7 all provide useful signal. This is a baseline family, not a final biological prior model.\n")

    out.append("## 4. Raw-Base and Signal Encodings\n")
    base_best = best_by(base, "encoding")
    out.append(table(base_best, ["encoding", "length", "condition", "classifier", "accuracy", "macro_f1", "n_features"], 20))
    out.append("\nInterpretation: one-hot/tetrahedron/property encodings are strong because they preserve base identity. Three-phase signal is promising but should be used as an additional channel rather than replacing identity-preserving encodings.\n")

    out.append("## 5. Token Audit and Ordinary Embedding Proxy\n")
    token_best = best_by(token, "feature")
    out.append("### Token Audit Best By Feature\n")
    out.append(table(token_best, ["feature", "length", "condition", "k", "ablation", "classifier", "accuracy", "macro_f1"], 20))
    emb_best = best_by(emb, "method")
    out.append("\n### Ordinary k-mer Embedding Proxy\n")
    out.append(table(emb_best, ["method", "length", "condition", "k", "dim", "classifier", "accuracy", "macro_f1", "n_features"], 20))
    out.append("\nInterpretation: ordinary k-mer embedding/pooling proxies are materially weaker on the order/position toy task than the best prior-aware encodings. This does not prove a full Transformer would fail, but it suggests pure tokenization without DNA priors is not the strongest lightweight representation here.\n")

    out.append("## 6. New Position/Biology-Aware Encodings\n")
    pos_best = best_by(pos, "scheme")
    out.append(table(pos_best, ["scheme", "length", "condition", "pooling", "classifier", "accuracy", "macro_f1", "n_features"], 30))
    out.append("\nKey observation: `spaced_kmer_phase`, `codon_frame_channels`, `rope_property`, `rope_onehot`, and `kmer_property` are among the strongest lightweight encodings. The strict hard-prior `joint_phase_prior` is weaker, while prior+residual improves it. This argues for flexible biological priors rather than rigid scalar phase alone.\n")

    out.append("## 7. Which Representation Fits Which Model?\n")
    out.append("| Representation | Information form | Best-fitting lightweight model | Deep model direction | Notes |\n")
    out.append("|---|---|---|---|---|\n")
    out.append("| k-mer count/TF-IDF | sparse global composition | kNN, linear SVM, logistic, tree models | MLP on sparse/dense SVD | Strong baseline; loses order and position. |\n")
    out.append("| ordinary k-mer token embedding | ordered discrete tokens | embedding pooling, CNN, GRU/Transformer | Transformer/BiLSTM with mask and canonical k-mer | Needs enough data; pure tokenization lacks biological priors. |\n")
    out.append("| one-hot/Voss | base identity per position | kNN/CNN on flattened or channels | CNN, lightweight Transformer possible but needs positional handling | Single-base Transformer is possible, but sequence length is short; CNN/Hyena-like conv may be more natural. |\n")
    out.append("| tetrahedron/property channels | base identity plus geometry/properties | kNN, linear, shallow CNN | CNN or attention over property channels | Good compromise between identity and biological prior. |\n")
    out.append("| three-phase scalar | codon/phase-inspired scalar signal | signal features, small CNN | auxiliary channel, not standalone Transformer input | Promising as channel; loses A/T and C/G identity if alone. |\n")
    out.append("| joint_phase_prior | rigid position-property phase | kNN/linear after flatten | small CNN/attention with residual | Too rigid alone in current results. |\n")
    out.append("| joint_phase_prior_residual | phase prior plus flexible property residual | kNN/linear/CNN | CNN/Transformer input initialization | More plausible than hard prior. |\n")
    out.append("| gated PE | property-modulated position signal | kNN/linear when flattened | Transformer/CNN position modulation | Useful when position matters; gate collision must be checked. |\n")
    out.append("| RoPE-like property/onehot | semantic vector rotated by position | kNN/linear flattened; attention-compatible | Transformer attention with relative position | Best theoretical fit for attention models. |\n")
    out.append("| codon_frame_channels | explicit 3-frame property exposure | kNN/CNN | CNN or grouped attention | Good mathematical/biological prior without forcing coding assumption. |\n")
    out.append("| spaced_kmer_phase | spaced seed + phase/location | nearest centroid, linear SVM | CNN/attention over spaced-token channels | Strong candidate for noisy short reads. |\n")
    out.append("| RC pooled encodings | strand-invariant plus strand-difference | kNN/linear | Siamese/contrastive RC consistency | Useful for clinical reads where strand should not change label. |\n")

    out.append("\n## 8. Current Best Candidate Methods\n")
    out.append("1. **Spaced k-mer phase encoding**: combines mismatch-tolerant spaced seed, local position phase, and property projection. It is compact and strong in the toy order/position task.\n")
    out.append("2. **RoPE-property / RoPE-onehot encoding**: best suited to future attention models because position is expressed through rotation rather than concatenated absolute coordinates.\n")
    out.append("3. **Codon-frame property channels**: exposes three-frame structure without claiming all reads are coding; mathematically clean and biologically interpretable.\n")
    out.append("4. **Property/tetrahedron + three-phase fusion**: safest near-term model input because it preserves base identity while adding prior channels.\n")
    out.append("5. **RC-consistent pooled encodings**: not the current top scorer, but important for a robust clinical method because prediction should be strand-stable.\n")

    out.append("## 9. What Should Be Improved Next?\n")
    out.append("- Add a true small CNN over channel-shaped encodings. Flattened kNN/linear evaluation is only a first pass.\n")
    out.append("- Implement a tiny attention model to test whether RoPE-property actually helps attention, not just flattened features.\n")
    out.append("- Add harder order-only datasets where composition is exactly matched at k=3/4/5.\n")
    out.append("- Add substitution gradients and indel stress to test whether spaced_kmer_phase is truly more robust.\n")
    out.append("- Add RC consistency metrics directly, not only classification F1.\n")

    out.append("## 10. Publication-Oriented Claim Boundary\n")
    out.append("Supported now: in controlled lightweight 69-100bp DNA tasks, prior-aware base/position encodings can outperform ordinary k-mer embedding proxies and provide clearer information structure.\n")
    out.append("\nNot supported yet: real clinical species-level superiority, full Transformer superiority, or final model accuracy claims. Those require harder generated benchmarks and eventually real/semireal reads.\n")

    output = runs / "final_lightweight_comparison_report.md"
    output.write_text("\n".join(out), encoding="utf-8")
    print(f"Wrote {output}")


if __name__ == "__main__":
    main()
