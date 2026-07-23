from __future__ import annotations

import argparse
import json
import random
import sys
import time
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

def _find_project_root(start: Path) -> Path:
    for candidate in [start.parent, *start.parents]:
        if (candidate / "methods").is_dir() and (candidate / "configs").is_dir():
            return candidate
    raise RuntimeError("Could not locate the release repository root.")


PROJECT_ROOT = _find_project_root(Path(__file__).resolve())
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.run_attention_context_diagnostic import (
    ANCHOR_MOTIF,
    ANCHOR_POS,
    CLASS_MOTIFS,
    DISTRACTORS,
    evaluate_classifier,
    insert,
    observe_read,
    parse_csv_list,
    parse_int_list,
    partial_class_prefix_rate,
    summarize_attention_capacity,
    visibility_metrics,
)
from src.sequence_utils import random_dna


def set_global_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)


def make_template(label: str, latent_length: int, class_motif_pos: int, rng: random.Random) -> str:
    seq = random_dna(latent_length, {"A": 0.25, "C": 0.25, "G": 0.25, "T": 0.25}, rng)
    seq = insert(seq, ANCHOR_MOTIF, ANCHOR_POS)
    seq = insert(seq, CLASS_MOTIFS[label], class_motif_pos)
    for pos in [52, 88, 178, 222]:
        if pos + 8 < latent_length and abs(pos - class_motif_pos) > 16:
            seq = insert(seq, rng.choice(DISTRACTORS), pos)
    return seq


def generate_breakpoint_dataset(
    lengths: list[int],
    motif_positions: list[int],
    reads_per_class: int,
    seed: int,
) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    rng = random.Random(seed)
    for motif_position in motif_positions:
        for label in CLASS_MOTIFS:
            for idx in range(reads_per_class):
                local_rng = random.Random(f"{seed}:{motif_position}:{label}:{idx}:{rng.random()}")
                template = make_template(label, latent_length=340, class_motif_pos=motif_position, rng=local_rng)
                for length in lengths:
                    layout = "PE150" if length == 300 else f"SE{length}"
                    read = observe_read(template, length, layout=layout)
                    class_motif = CLASS_MOTIFS[label]
                    anchor_visible = ANCHOR_MOTIF in read
                    class_visible = class_motif in read
                    rows.append(
                        {
                            "read_id": f"{label}_P{motif_position}_{layout}_{idx:04d}",
                            "sequence": read,
                            "label": label,
                            "source_length": length,
                            "observed_layout": layout,
                            "motif_position": motif_position,
                            "anchor_visible": int(anchor_visible),
                            "class_motif_visible": int(class_visible),
                            "any_class_motif_visible": int(any(motif in read for motif in CLASS_MOTIFS.values())),
                            "pair_visible": int(anchor_visible and class_visible),
                            "anchor_pos": read.find(ANCHOR_MOTIF),
                            "class_pos": read.find(class_motif),
                            "context_distance": read.find(class_motif) - read.find(ANCHOR_MOTIF)
                            if anchor_visible and class_visible
                            else -1,
                        }
                    )
    return pd.DataFrame(rows)


def run_breakpoint(
    df: pd.DataFrame,
    lengths: list[int],
    motif_positions: list[int],
    representations: list[str],
    seed: int,
) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for motif_position in motif_positions:
        for length in lengths:
            subset = df[(df["motif_position"] == motif_position) & (df["source_length"] == length)].reset_index(drop=True)
            if subset.empty:
                continue
            base_metrics = visibility_metrics(subset)
            base_metrics["partial_class_prefix_visible_rate"] = float(partial_class_prefix_rate(subset))
            base_metrics.update(summarize_attention_capacity(length))
            for rep in representations:
                try:
                    for eval_row in evaluate_classifier(subset, rep, seed=seed):
                        rows.append(
                            {
                                "motif_position": motif_position,
                                "length": length,
                                "observed_layout": "PE150" if length == 300 else f"SE{length}",
                                "representation": rep,
                                **base_metrics,
                                **eval_row,
                            }
                        )
                except Exception as exc:
                    rows.append(
                        {
                            "motif_position": motif_position,
                            "length": length,
                            "observed_layout": "PE150" if length == 300 else f"SE{length}",
                            "representation": rep,
                            **base_metrics,
                            "error": f"{type(exc).__name__}: {exc}",
                        }
                    )
    return pd.DataFrame(rows)


def summarize_change_points(summary: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    visibility = summary.drop_duplicates(["motif_position", "length"])[
        ["motif_position", "length", "pair_visible_rate", "class_motif_visible_rate", "partial_class_prefix_visible_rate"]
    ].copy()
    for motif_position, group in visibility.groupby("motif_position"):
        group = group.sort_values("length")
        visible = group[group["pair_visible_rate"] >= 0.5]
        rows.append(
            {
                "motif_position": int(motif_position),
                "first_length_pair_visible_ge_0_5": int(visible["length"].iloc[0]) if not visible.empty else -1,
                "max_pair_visible_rate": float(group["pair_visible_rate"].max()),
                "lengths_tested": ",".join(str(int(x)) for x in group["length"].tolist()),
            }
        )
    return pd.DataFrame(rows)


def plot_breakpoints(summary: pd.DataFrame, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    visibility = summary.drop_duplicates(["motif_position", "length"])[
        ["motif_position", "length", "pair_visible_rate", "class_motif_visible_rate"]
    ].sort_values(["motif_position", "length"])
    plt.figure(figsize=(10, 5))
    for motif_position, group in visibility.groupby("motif_position"):
        plt.plot(group["length"].astype(str), group["pair_visible_rate"], marker="o", label=f"motif {motif_position}")
    plt.ylim(-0.02, 1.05)
    plt.xlabel("Read length")
    plt.ylabel("Anchor + class motif visible")
    plt.title("Attention Context Breakpoints Across Motif Positions")
    plt.legend(ncol=2, fontsize=8)
    plt.tight_layout()
    plt.savefig(output_dir / "fig_stage2_attention_breakpoint_visibility.png", dpi=220)
    plt.close()

    clf = summary.dropna(subset=["macro_f1"]).copy()
    if clf.empty:
        return
    keep = clf[clf["representation"].isin(["kmer5_count_l2", "property_channels", "rope_property", "oracle_motif_pair"])]
    if keep.empty:
        keep = clf
    for motif_position, group_pos in keep.groupby("motif_position"):
        plt.figure(figsize=(10, 5))
        for rep, group in group_pos.groupby("representation"):
            group = group.sort_values("length")
            plt.plot(group["length"].astype(str), group["macro_f1"], marker="o", label=rep)
        plt.ylim(-0.02, 1.05)
        plt.xlabel("Read length")
        plt.ylabel("Macro-F1")
        plt.title(f"Readout Breakpoint at Motif Position {motif_position}")
        plt.legend(fontsize=8, ncol=2)
        plt.tight_layout()
        plt.savefig(output_dir / f"fig_stage2_attention_breakpoint_f1_pos{int(motif_position)}.png", dpi=220)
        plt.close()


def write_summary(summary: pd.DataFrame, change_points: pd.DataFrame, output_dir: Path) -> None:
    lines: list[str] = []
    lines.append("# Stage-2 Attention Breakpoint Diagnostic\n")
    lines.append("This diagnostic densifies the 125-150 bp interval and varies motif position to avoid relying on a single hand-picked context boundary.\n")
    lines.append("## Change points\n")
    lines.append(change_points.to_markdown(index=False))
    lines.append("")
    visibility = summary.drop_duplicates(["motif_position", "length"])[
        ["motif_position", "length", "pair_visible_rate", "class_motif_visible_rate", "partial_class_prefix_visible_rate"]
    ].sort_values(["motif_position", "length"])
    lines.append("## Visibility curve\n")
    lines.append(visibility.to_markdown(index=False, floatfmt=".3f"))
    lines.append("")
    clf = summary.dropna(subset=["macro_f1"])
    if not clf.empty:
        best = (
            clf.sort_values(["motif_position", "length", "macro_f1"], ascending=[True, True, False])
            .groupby(["motif_position", "length"], as_index=False)
            .first()
        )
        lines.append("## Best readout by motif position and length\n")
        lines.append(best[["motif_position", "length", "representation", "macro_f1", "accuracy"]].to_markdown(index=False, floatfmt=".3f"))
        lines.append("")
    (output_dir / "attention_breakpoint_summary.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run stage-2 dense attention breakpoint diagnostic.")
    parser.add_argument("--output-dir", default=str(PROJECT_ROOT / "results" / "stage2" / "attention_breakpoint"))
    parser.add_argument("--lengths", default="110,115,120,125,130,135,138,140,142,145,148,150,155,160")
    parser.add_argument("--motif-positions", default="120,130,138,145")
    parser.add_argument("--reads-per-class", type=int, default=120)
    parser.add_argument("--representations", default="kmer5_count_l2,ckmer5_count_l2,property_channels,rope_property,spaced_kmer_phase,cspaced_property_l2,oracle_motif_pair")
    parser.add_argument("--seed", type=int, default=404)
    args = parser.parse_args()

    started = time.time()
    set_global_seed(args.seed)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    lengths = parse_int_list(args.lengths)
    motif_positions = parse_int_list(args.motif_positions)
    reps = parse_csv_list(args.representations)
    df = generate_breakpoint_dataset(lengths, motif_positions, reads_per_class=args.reads_per_class, seed=args.seed)
    df.to_csv(output_dir / "attention_breakpoint_reads.csv", index=False, encoding="utf-8-sig")
    summary = run_breakpoint(df, lengths, motif_positions, reps, seed=args.seed)
    change_points = summarize_change_points(summary)
    summary.to_csv(output_dir / "attention_breakpoint_results.csv", index=False, encoding="utf-8-sig")
    change_points.to_csv(output_dir / "attention_breakpoint_change_points.csv", index=False, encoding="utf-8-sig")
    plot_breakpoints(summary, output_dir)
    write_summary(summary, change_points, output_dir)
    (output_dir / "attention_breakpoint_run.json").write_text(
        json.dumps(
            {
                "elapsed_seconds": time.time() - started,
                "lengths": lengths,
                "motif_positions": motif_positions,
                "reads_per_class": args.reads_per_class,
                "representations": reps,
                "seed": args.seed,
                "n_rows": int(len(summary)),
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    print(f"Wrote stage-2 attention breakpoint diagnostic to {output_dir}")


if __name__ == "__main__":
    main()

