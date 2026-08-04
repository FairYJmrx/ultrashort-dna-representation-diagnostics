"""Run E1 length interaction and E4 audit-to-retention association analyses."""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr


def find_project_root(start: Path) -> Path:
    for candidate in [start.parent, *start.parents]:
        if (candidate / "methods").is_dir() and (candidate / "configs").is_dir():
            return candidate
    raise RuntimeError("Could not locate the release repository root.")


PROJECT_ROOT = find_project_root(Path(__file__).resolve())


def parse_int_list(value: str) -> list[int]:
    return [int(item.strip()) for item in value.split(",") if item.strip()]


def canonical_representation(value: str) -> str:
    return str(value)


def run_e1(
    stability_path: Path,
    readout_path: Path,
    anchor_stability_path: Path,
    output_dir: Path,
    short_max: int,
) -> dict[str, object]:
    stability = pd.read_csv(stability_path)
    readout = pd.read_csv(readout_path)
    anchor_stability = pd.read_csv(anchor_stability_path)
    stability["length"] = stability["length"].astype(int)
    readout["length"] = readout["length"].astype(int)
    anchor_stability["length"] = anchor_stability["length"].astype(int)
    stability["representation"] = stability["representation"].map(canonical_representation)
    readout["representation"] = readout["representation"].map(canonical_representation)
    anchor_stability["representation"] = anchor_stability["representation"].map(canonical_representation)

    anchor_stability = anchor_stability[
        anchor_stability["length"].gt(short_max)
        & anchor_stability["length"].le(150)
        & anchor_stability["representation"].isin(["ck4", "ck4p_msp"])
    ].copy()
    if "retrieval_top1_mean" not in anchor_stability.columns and "retrieval_top1" in anchor_stability.columns:
        anchor_stability["retrieval_top1_mean"] = anchor_stability["retrieval_top1"]
    stability = pd.concat(
        [
            stability[stability["length"].le(short_max)],
            anchor_stability,
        ],
        ignore_index=True,
    )

    main_representation = next(
        (
            candidate
            for candidate in ["ck4p_msp"]
            if candidate in set(stability["representation"].astype(str))
            and candidate in set(readout["representation"].astype(str))
        ),
        None,
    )
    if main_representation is None:
        raise ValueError("Could not find CK4P-MSP under the canonical key ck4p_msp.")

    stable_pivot = stability.pivot_table(
        index="length",
        columns="representation",
        values=["l2_delta_mean", "paired_cosine_mean", "retrieval_top1_mean"],
        aggfunc="mean",
    )
    rows: list[dict[str, object]] = []
    for length in sorted(stability["length"].unique()):
        row = {"length": int(length)}
        for metric, direction in [
            ("l2_delta_mean", "ck4_minus_method"),
            ("paired_cosine_mean", "method_minus_ck4"),
            ("retrieval_top1_mean", "method_minus_ck4"),
        ]:
            try:
                ck4 = float(stable_pivot.loc[length, (metric, "ck4")])
                method = float(stable_pivot.loc[length, (metric, main_representation)])
            except KeyError:
                continue
            row[f"{direction}_{metric}"] = (ck4 - method) if direction == "ck4_minus_method" else (method - ck4)
            row[f"ck4_{metric}"] = ck4
            row[f"ck4p_msp_{metric}"] = method
        rows.append(row)
    interaction = pd.DataFrame(rows)
    interaction["length_regime"] = np.where(
        interaction["length"].astype(int) <= short_max,
        f"short_<=_{short_max}bp",
        f"long_>_{short_max}bp",
    )

    readout_pivot = readout.pivot_table(
        index="length",
        columns="representation",
        values="macro_f1_mean",
        aggfunc="mean",
    )
    readout_rows = []
    for length in sorted(readout["length"].unique()):
        if "ck4" not in readout_pivot.columns or main_representation not in readout_pivot.columns:
            continue
        readout_rows.append(
            {
                "length": int(length),
                "ck4_macro_f1": float(readout_pivot.loc[length, "ck4"]),
                "ck4p_msp_macro_f1": float(readout_pivot.loc[length, main_representation]),
                "ck4p_msp_minus_ck4_macro_f1": float(
                    readout_pivot.loc[length, main_representation] - readout_pivot.loc[length, "ck4"]
                ),
            }
        )
    readout_delta = pd.DataFrame(readout_rows)
    interaction = interaction.merge(readout_delta, on="length", how="left")

    regime_summary = (
        interaction.groupby("length_regime", as_index=False)
        .agg(
            n_lengths=("length", "nunique"),
            drift_gain_mean=("ck4_minus_method_l2_delta_mean", "mean"),
            cosine_gain_mean=("method_minus_ck4_paired_cosine_mean", "mean"),
            retrieval_gain_mean=("method_minus_ck4_retrieval_top1_mean", "mean"),
            readout_gain_mean=("ck4p_msp_minus_ck4_macro_f1", "mean"),
        )
    )
    interaction.to_csv(output_dir / "e1_length_interaction_by_length.csv", index=False, encoding="utf-8-sig")
    regime_summary.to_csv(output_dir / "e1_length_interaction_regime_summary.csv", index=False, encoding="utf-8-sig")
    return {
        "n_lengths": int(interaction["length"].nunique()),
        "lengths": sorted(interaction["length"].astype(int).unique().tolist()),
        "short_max": short_max,
        "main_representation_key": main_representation,
        "readout_length_scope": sorted(readout_delta["length"].astype(int).unique().tolist()) if not readout_delta.empty else [],
        "stability_length_scope": sorted(interaction["length"].astype(int).unique().tolist()),
        "regime_summary": regime_summary.to_dict(orient="records"),
    }


def run_e4(
    stability_path: Path,
    cami_path: Path,
    output_dir: Path,
) -> dict[str, object]:
    stability = pd.read_csv(stability_path)
    cami = pd.read_csv(cami_path)
    stability["length"] = stability["length"].astype(int)
    cami["length"] = cami["length"].astype(int)
    if "probe_scaling" in cami.columns:
        cami = cami[cami["probe_scaling"].astype(str).eq("contract")].copy()

    audit_columns = [
        "l2_delta_mean",
        "paired_cosine_mean",
        "retrieval_top1",
        "margin_positive_rate",
    ]
    available_audit = [column for column in audit_columns if column in stability.columns]
    stability = stability[
        ["representation", "length", "condition", *available_audit]
    ].drop_duplicates(["representation", "length", "condition"])
    cami_columns = [
        "representation",
        "length",
        "condition",
        "label_retention_ratio",
        "macro_f1",
        "delta_macro_f1",
    ]
    available_cami = [column for column in cami_columns if column in cami.columns]
    cami = cami[available_cami].drop_duplicates(["representation", "length", "condition"])
    merged = stability.merge(
        cami,
        on=["representation", "length", "condition"],
        how="inner",
        suffixes=("_audit", "_cami"),
    )
    merged.to_csv(output_dir / "e4_audit_retention_pairs.csv", index=False, encoding="utf-8-sig")

    rows: list[dict[str, object]] = []
    for representation, group in merged.groupby("representation", sort=True):
        for metric in available_audit:
            if metric not in group.columns:
                continue
            valid = group[[metric, "label_retention_ratio"]].dropna()
            if len(valid) < 4 or valid[metric].nunique() < 2 or valid["label_retention_ratio"].nunique() < 2:
                rho, p_value = np.nan, np.nan
            else:
                result = spearmanr(valid[metric], valid["label_retention_ratio"])
                rho, p_value = float(result.statistic), float(result.pvalue)
            rows.append(
                {
                    "scope": "representation",
                    "representation": representation,
                    "metric": metric,
                    "n_pairs": int(len(valid)),
                    "spearman_rho": rho,
                    "p_value": p_value,
                }
            )
    for metric in available_audit:
        if metric not in merged.columns:
            continue
        valid = merged[[metric, "label_retention_ratio"]].dropna()
        if len(valid) < 4 or valid[metric].nunique() < 2 or valid["label_retention_ratio"].nunique() < 2:
            rho, p_value = np.nan, np.nan
        else:
            result = spearmanr(valid[metric], valid["label_retention_ratio"])
            rho, p_value = float(result.statistic), float(result.pvalue)
        rows.append(
            {
                "scope": "pooled",
                "representation": "all_common_methods",
                "metric": metric,
                "n_pairs": int(len(valid)),
                "spearman_rho": rho,
                "p_value": p_value,
            }
        )
    correlations = pd.DataFrame(rows)
    correlations.to_csv(output_dir / "e4_spearman_audit_retention.csv", index=False, encoding="utf-8-sig")
    return {
        "n_pairs": int(len(merged)),
        "representations": sorted(merged["representation"].astype(str).unique().tolist()),
        "conditions": sorted(merged["condition"].astype(str).unique().tolist()),
        "correlations": correlations.to_dict(orient="records"),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--continuity-stability",
        default=str(
            PROJECT_ROOT
            / "results"
            / "stage3"
            / "contract_v2"
            / "short_read_length_continuity"
            / "length_continuity_stability_summary.csv"
        ),
    )
    parser.add_argument(
        "--continuity-readout",
        default=str(
            PROJECT_ROOT
            / "results"
            / "stage3"
            / "contract_v2"
            / "short_read_length_continuity"
            / "length_continuity_delta_readout_summary.csv"
        ),
    )
    parser.add_argument(
        "--compact-stability",
        default=str(
            PROJECT_ROOT
            / "results"
            / "stage3"
            / "contract_v2"
            / "compact_baselines"
            / "compact_baseline_stability.csv"
        ),
    )
    parser.add_argument(
        "--anchor-stability",
        default=str(
            PROJECT_ROOT
            / "results"
            / "stage3"
            / "contract_v2"
            / "compact_baselines"
            / "compact_baseline_stability.csv"
        ),
    )
    parser.add_argument(
        "--cami-metrics",
        default=str(
            PROJECT_ROOT
            / "results"
            / "stage3"
            / "contract_v2"
            / "cami_fixed_head_transfer"
            / "cami_fixed_head_metrics.csv"
        ),
    )
    parser.add_argument(
        "--output-dir",
        default=str(PROJECT_ROOT / "results" / "decision_stage" / "e1_e4"),
    )
    parser.add_argument("--short-max", type=int, default=75)
    args = parser.parse_args()

    started = time.time()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    e1 = run_e1(
        Path(args.continuity_stability),
        Path(args.continuity_readout),
        Path(args.anchor_stability),
        output_dir,
        short_max=args.short_max,
    )
    e4 = run_e4(
        Path(args.compact_stability),
        Path(args.cami_metrics),
        output_dir,
    )
    metadata = {
        "elapsed_seconds": round(time.time() - started, 3),
        "e1": e1,
        "e4": e4,
        "interpretation": {
            "e1": "short-read framing is strengthened only if CK4P-MSP gains show a reproducible short-versus-long interaction",
            "e4": "strong association supports criterion-related audit validity; weak association keeps the protocol descriptive",
        },
    }
    (output_dir / "e1_e4_run.json").write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    (output_dir / "e1_e4_summary.md").write_text(
        "# E1/E4: read-length interaction and audit-retention association\n\n"
        "E1 re-summarizes the existing shared-template length-continuity results; "
        "it does not generate a new sequence dataset. E4 pairs existing compact-baseline "
        "stability values with CAMI fixed-head retention by representation, length and "
        "condition. It is an association audit, not an external task predictor.\n\n"
        "The larger mean stability gain in the lower read-length regime is descriptive "
        "because no corresponding long-read readout grid or independent interaction test "
        "was run. Weak representation-specific E4 associations keep the profile "
        "descriptive rather than criterion validated.\n\n"
        f"E1 summary: {json.dumps(e1, ensure_ascii=False)}\n\n"
        f"E4 matched pairs: {e4['n_pairs']}\n",
        encoding="utf-8",
    )
    print(f"Wrote E1/E4 decision-stage audits to {output_dir}")


if __name__ == "__main__":
    main()
