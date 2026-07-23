from __future__ import annotations

from pathlib import Path

import pandas as pd


def _find_project_root(start: Path) -> Path:
    for candidate in [start.parent, *start.parents]:
        if (candidate / "methods").is_dir() and (candidate / "configs").is_dir():
            return candidate
    raise RuntimeError("Could not locate the release repository root.")


PROJECT_ROOT = _find_project_root(Path(__file__).resolve())
TABLE_DIR = PROJECT_ROOT / "paper" / "tables"


def write_md_csv(df: pd.DataFrame, name: str) -> None:
    TABLE_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(TABLE_DIR / f"{name}.csv", index=False, encoding="utf-8-sig")
    (TABLE_DIR / f"{name}.md").write_text(to_markdown_table(df) + "\n", encoding="utf-8")


def to_markdown_table(df: pd.DataFrame) -> str:
    cols = [str(col) for col in df.columns]
    rows = [[str(value) for value in row] for row in df.astype(str).itertuples(index=False, name=None)]
    widths = [len(col) for col in cols]
    for row in rows:
        widths = [max(width, len(cell)) for width, cell in zip(widths, row)]

    def fmt_row(values: list[str]) -> str:
        return "| " + " | ".join(value.ljust(width) for value, width in zip(values, widths)) + " |"

    header = fmt_row(cols)
    sep = "| " + " | ".join("-" * width for width in widths) + " |"
    body = [fmt_row(row) for row in rows]
    return "\n".join([header, sep, *body])


def fmt(value: float, digits: int = 3) -> str:
    return f"{value:.{digits}f}"


def table_representation_families() -> pd.DataFrame:
    rows = [
        {
            "family": "CK4 / CK5",
            "information channel": "exact local identity",
            "main role": "identity backbone and comparator",
            "main-text interpretation": "necessary for taxonomic, allele and SNP-level evidence",
        },
        {
            "family": "P",
            "information channel": "biochemical summaries",
            "main role": "perturbation-stable side channel",
            "main-text interpretation": "adds robustness information but does not replace identity",
        },
        {
            "family": "CK4+P",
            "information channel": "identity plus global biochemical signal",
            "main role": "global property baseline",
            "main-text interpretation": "tests whether biochemical summaries add to CK4",
        },
        {
            "family": "CK4+MSP",
            "information channel": "identity plus positionalized biochemical signal",
            "main role": "positional property ablation",
            "main-text interpretation": "tests whether MSP returns coarse layout information without global P",
        },
        {
            "family": "CK4P-MSP",
            "information channel": "identity plus multi-scale biochemical layout",
            "main role": "compact main representation",
            "main-text interpretation": "balances stability, readability and feature dimension",
        },
        {
            "family": "full-position matrix",
            "information channel": "per-position identity or property signal",
            "main role": "upper-bound diagnostic",
            "main-text interpretation": "tests fine positional information at higher dimensional cost",
        },
        {
            "family": "CSP",
            "information channel": "spaced-seed prior plus biochemical summary",
            "main role": "spaced-seed transfer comparator",
            "main-text interpretation": "delimits where matching-oriented spaced seeds transfer to dense features",
        },
    ]
    return pd.DataFrame(rows)


def table_data_layers() -> pd.DataFrame:
    rows = [
        {
            "data layer": "WGS perturbation pairs",
            "scale": "25,200 rows; 3,600 clean templates; 6 genera/21 species; lengths 69,75,100,125,150,300 bp",
            "diagnostic question": "Which representations keep clean and perturbed reads close?",
            "primary metrics": "paired cosine, L2 drift, retrieval",
            "claim boundary": "controlled representation stability, not clinical validation",
        },
        {
            "data layer": "Position-property ablation",
            "scale": "36,000 rows; 3,600 templates; 6 genera/21 species; lengths 69,75,100,125,150,300 bp",
            "diagnostic question": "What do P and MSP add to the CK4 identity backbone?",
            "primary metrics": "paired stability, block drift, delta-readout, MI proxies",
            "claim boundary": "decomposable representation audit, not a natural physical metric",
        },
        {
            "data layer": "ART Illumina-like simulation",
            "scale": "75,592 paired rows; 37,796 templates; 6 genera/21 species; lengths 69,75,100,125,150 bp",
            "diagnostic question": "Do stability trends persist under simulator-derived read errors?",
            "primary metrics": "paired cosine, L2 drift, retrieval",
            "claim boundary": "platform-like consistency check",
        },
        {
            "data layer": "CAMI_TOY_low probes",
            "scale": "104,166-row initial subset and 216,000-row expanded subset; 30 labels; lengths 69,75,100 bp",
            "diagnostic question": "Is information readable in an external metagenomic readout?",
            "primary metrics": "macro-F1, accuracy",
            "claim boundary": "lightweight readout, not clinical classification",
        },
        {
            "data layer": "CAMI II marine anonymous-read probe",
            "scale": "48,000 rows from 4,000 anonymous source reads; lengths 69,75,100 bp",
            "diagnostic question": "Do stability trends persist in a more complex external metagenomic read source?",
            "primary metrics": "paired cosine, L2 drift, retrieval",
            "claim boundary": "paired stability without reconstructed read-level taxonomic labels",
        },
        {
            "data layer": "controlled position tasks",
            "scale": "controlled synthetic tasks over the short-read length grid",
            "diagnostic question": "What does fine positional resolution add?",
            "primary metrics": "macro-F1, feature dimension",
            "claim boundary": "upper-bound diagnostic",
        },
        {
            "data layer": "local mutation sensitivity",
            "scale": "250 triplets per analysis cell; 12 representations; 4 local modes; lengths 69,100,150 bp",
            "diagnostic question": "Can local biochemical change be detected beyond equal-count noise?",
            "primary metrics": "sensitivity ratio, delta-readout macro-F1",
            "claim boundary": "selective sensitivity, not functional effect prediction",
        },
        {
            "data layer": "boundary probes",
            "scale": "spaced-seed, context-visibility and ARG/SNP boundary screens",
            "diagnostic question": "Where do spaced-seed, context and ARG/SNP claims stop?",
            "primary metrics": "seed stability, visibility threshold, macro-F1",
            "claim boundary": "mechanism boundary and failure modes",
        },
    ]
    return pd.DataFrame(rows)


def label_map() -> dict[str, str]:
    return {
        "ckmer4_count_l2": "CK4",
        "ckmer4_property_l2": "CK4+P",
        "ckmer4_property_multiscale_mean_l2": "CK4P-MSP",
        "ckmer5_count_l2": "CK5",
        "cspaced_property_l2": "CSP",
        "property_channels": "position property channels",
        "one_hot": "position one-hot",
        "kmer_property": "position k-mer property",
        "base_property": "one-hot + property",
    }


def compact_main_method_table() -> pd.DataFrame:
    stability = pd.read_csv(PROJECT_ROOT / "results/stage3/position_property_ablation/compact_baseline_stability.csv")
    readout = pd.read_csv(PROJECT_ROOT / "results/stage3/position_property_ablation/compact_baseline_readout.csv")
    reps = ["ckmer4_count_l2", "ckmer4_property_l2", "ckmer4_property_multiscale_mean_l2", "ckmer5_count_l2"]
    stab = (
        stability[stability["representation"].isin(reps)]
        .groupby("representation", as_index=False)
        .agg(
            paired_cosine=("paired_cosine_mean", "mean"),
            l2_drift=("l2_delta_mean", "mean"),
            features=("n_features", "median"),
        )
    )
    read = (
        readout[(readout["representation"].isin(reps)) & (readout["classifier"].eq("logistic"))]
        .groupby("representation", as_index=False)
        .agg(readout_macro_f1=("macro_f1", "mean"))
    )
    merged = stab.merge(read, on="representation", how="left")
    merged["representation"] = pd.Categorical(merged["representation"], categories=reps, ordered=True)
    merged = merged.sort_values("representation")
    labels = label_map()
    out = pd.DataFrame(
        {
            "representation": merged["representation"].map(labels),
            "paired cosine": merged["paired_cosine"].map(fmt),
            "L2 drift": merged["l2_drift"].map(fmt),
            "readout macro-F1": merged["readout_macro_f1"].map(fmt),
            "features": merged["features"].round(0).astype(int),
        }
    )
    return out


def local_mutation_table() -> pd.DataFrame:
    summary = pd.read_csv(PROJECT_ROOT / "results/stage3/local_mutation_sensitivity/local_mutation_sensitivity_summary.csv")
    readout = pd.read_csv(PROJECT_ROOT / "results/stage3/local_mutation_sensitivity/local_mutation_delta_readout.csv")
    reps = [
        "ckmer4_count_l2",
        "ckmer4_property_l2",
        "ckmer4_property_multiscale_mean_l2",
        "cspaced_property_l2",
        "one_hot",
        "property_channels",
        "base_property",
        "kmer_property",
    ]
    labels = {
        "ckmer4_count_l2": "CK4",
        "ckmer4_property_l2": "CK4+P",
        "ckmer4_property_multiscale_mean_l2": "CK4P-MSP",
        "cspaced_property_l2": "CSP",
        "one_hot": "one-hot",
        "property_channels": "P-channels",
        "base_property": "one-hot+P",
        "kmer_property": "position k-mer P",
    }
    s = (
        summary[summary["representation"].isin(reps)]
        .groupby("representation", as_index=False)
        .agg(
            noise_l2=("noise_l2_mean", "mean"),
            local_l2=("local_l2_mean", "mean"),
            local_minus_noise_l2=("local_minus_noise_l2_mean", "mean"),
            sensitivity_ratio=("selective_sensitivity_ratio_mean", "mean"),
            features=("n_features", "median"),
        )
    )
    r = (
        readout[
            readout["representation"].isin(reps)
            & readout["classifier"].eq("logistic")
            & readout["split"].astype(str).str.contains("fold_cv")
        ]
        .groupby("representation", as_index=False)
        .agg(delta_readout_macro_f1=("macro_f1", "mean"))
    )
    merged = s.merge(r, on="representation", how="left")
    merged["representation"] = pd.Categorical(merged["representation"], categories=reps, ordered=True)
    merged = merged.sort_values("representation")
    return pd.DataFrame(
        {
            "representation": merged["representation"].astype(str).map(labels),
            "noise L2": merged["noise_l2"].map(fmt),
            "local L2": merged["local_l2"].map(fmt),
            "local - noise L2": merged["local_minus_noise_l2"].map(fmt),
            "sensitivity ratio": merged["sensitivity_ratio"].map(fmt),
            "delta-readout macro-F1": merged["delta_readout_macro_f1"].map(fmt),
            "features": merged["features"].round(0).astype(int),
        }
    )


def boundary_summary_table() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "boundary": "spaced-seed transfer",
                "main observation": "The best tested 4-position dense stability pattern was contiguous 0-1-2-3 across the 69/75 bp sanity grid.",
                "interpretation": "spaced seeds remain useful matching priors, but transfer is regime-specific",
            },
            {
                "boundary": "context visibility",
                "main observation": "motif-pair visibility thresholds depended on placement, emerging at 130, 140, 148 or 155 bp.",
                "interpretation": "a representation cannot encode context absent from the read",
            },
            {
                "boundary": "ARG/SNP readout",
                "main observation": "stable compact features did not by themselves establish allele, resistance-SNP or functional equivalence.",
                "interpretation": "identity/database evidence remains necessary for final biological calls",
            },
        ]
    )


def main() -> None:
    write_md_csv(table_representation_families(), "nature_table1_representation_families")
    write_md_csv(table_data_layers(), "nature_table2_data_layers")
    write_md_csv(compact_main_method_table(), "nature_table3_compact_main_method")
    write_md_csv(local_mutation_table(), "nature_table4_local_mutation_sensitivity")
    write_md_csv(boundary_summary_table(), "nature_table5_boundary_summary")
    print("Wrote Nature-style main manuscript tables")


if __name__ == "__main__":
    main()

