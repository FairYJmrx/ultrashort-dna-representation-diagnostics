from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def load_if_exists(path: Path) -> pd.DataFrame:
    if path.exists():
        return pd.read_csv(path)
    return pd.DataFrame()


def md_table(df: pd.DataFrame, columns: list[str], n: int = 10) -> str:
    if df.empty:
        return "_No data._\n"
    small = df[columns].head(n).copy()
    return small.to_markdown(index=False)


def main() -> None:
    parser = argparse.ArgumentParser(description="Summarize first smoke runs.")
    parser.add_argument("--runs-dir", default=str(PROJECT_ROOT / "results" / "runs"))
    parser.add_argument("--output", default=str(PROJECT_ROOT / "results" / "runs" / "smoke_summary.md"))
    args = parser.parse_args()

    runs_dir = Path(args.runs_dir)
    comp = load_if_exists(runs_dir / "composition_smoke" / "composition_results_flat.csv")
    base = load_if_exists(runs_dir / "base_signal_smoke" / "base_signal_results_flat.csv")
    token = load_if_exists(runs_dir / "token_audit_smoke" / "token_audit_results_flat.csv")

    lines: list[str] = []
    lines.append("# Smoke Run Summary\n")
    lines.append("This report summarizes the first lightweight runs. Accuracy is only a separability smoke-test signal, not a clinical-performance claim.\n")

    if not comp.empty:
        comp_top = comp.sort_values(["macro_f1", "accuracy"], ascending=False)
        lines.append("## Composition Top Results\n")
        lines.append(md_table(comp_top, ["length", "condition", "k", "feature_type", "normalization", "svd_components", "classifier", "accuracy", "macro_f1", "density"], 12))
        lines.append("\n")
        best_by_k = (
            comp.sort_values(["macro_f1", "accuracy"], ascending=False)
            .groupby("k", as_index=False)
            .first()
            .sort_values("k")
        )
        lines.append("## Composition Best By k\n")
        lines.append(md_table(best_by_k, ["k", "length", "condition", "feature_type", "normalization", "svd_components", "classifier", "macro_f1", "density"], 20))
        lines.append("\n")

    if base.empty:
        lines.append("## Base/Signal Results\n_No data._\n")
    else:
        base_top = base.sort_values(["macro_f1", "accuracy"], ascending=False)
        lines.append("## Base/Signal Top Results\n")
        lines.append(md_table(base_top, ["length", "condition", "encoding", "classifier", "accuracy", "macro_f1", "n_features"], 12))
        lines.append("\n")

    if token.empty:
        lines.append("## Token Audit Results\n_No data._\n")
    else:
        token_top = token.sort_values(["macro_f1", "accuracy"], ascending=False)
        lines.append("## Token Audit Top Results\n")
        lines.append(md_table(token_top, ["length", "condition", "k", "ablation", "feature", "classifier", "accuracy", "macro_f1", "vocab_size"], 12))
        lines.append("\n")
        pivot = (
            token[token["feature"].eq("transition")]
            .groupby(["k", "ablation"], as_index=False)["macro_f1"]
            .max()
            .sort_values(["k", "ablation"])
        )
        lines.append("## Token Transition Ablation Max Macro-F1\n")
        lines.append(md_table(pivot, ["k", "ablation", "macro_f1"], 30))
        lines.append("\n")

    lines.append("## Initial Interpretation\n")
    lines.append("- The scripts and environment are working: toy generation, k-mer composition, token audit, and raw-base/signal encodings all produced results.\n")
    lines.append("- Several toy conditions are intentionally easy; high accuracy here only means the feature can separate the constructed classes.\n")
    lines.append("- Token shuffle can still score highly in this first dataset, which means the current classes contain strong composition signal. The next dataset must add same-composition different-order and motif-position classes before judging order/position encodings.\n")
    lines.append("- The next experimental step is not larger training. It is a sharper toy dataset that isolates order and position information.\n")

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {output}")


if __name__ == "__main__":
    main()
