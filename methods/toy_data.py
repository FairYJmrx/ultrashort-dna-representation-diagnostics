"""Controlled lightweight DNA data generation."""

from __future__ import annotations

import csv
import json
import random
from pathlib import Path

from .sequence_utils import (
    inject_indel,
    mask_n,
    mutate_substitutions,
    random_dna,
    reverse_complement,
    trim_sequence,
)


def build_templates(template_length: int = 6000, seed: int = 13) -> dict[str, str]:
    rng = random.Random(seed)
    gc_weights = {"A": 0.15, "C": 0.35, "G": 0.35, "T": 0.15}
    at_weights = {"A": 0.35, "C": 0.15, "G": 0.15, "T": 0.35}
    balanced = {"A": 0.25, "C": 0.25, "G": 0.25, "T": 0.25}

    gc = list(random_dna(template_length, gc_weights, rng))
    motifs = ["GCGTACG", "CCGGAAG", "GGCATGC"]
    for pos in range(100, template_length - 20, 700):
        motif = motifs[(pos // 700) % len(motifs)]
        gc[pos:pos + len(motif)] = motif
    gc_seq = "".join(gc)

    at = list(random_dna(template_length, at_weights, rng))
    for pos in range(180, template_length - 20, 650):
        motif = "ATTAATA"
        at[pos:pos + len(motif)] = motif
    at_seq = "".join(at)

    near = list(gc_seq)
    snp_positions: list[int] = []
    for pos in range(75, template_length, 150):
        current = near[pos]
        choices = [b for b in "ACGT" if b != current]
        near[pos] = rng.choice(choices)
        snp_positions.append(pos)

    host_like = list(random_dna(template_length, balanced, rng))
    for pos in range(250, template_length - 30, 900):
        repeat = "ATATATATATAT"
        host_like[pos:pos + len(repeat)] = repeat

    return {
        "GC_rich": gc_seq,
        "AT_rich": at_seq,
        "near_SNP": "".join(near),
        "host_like": "".join(host_like),
    }


def same_composition_read(length: int, variant: str, rng: random.Random) -> str:
    """Generate reads with nearly identical base composition but different order."""
    motif_a = "AACCGGTT"
    motif_b = "AGTCAGTC"
    motif_c = "ATCGATCG"
    motif = {"same_comp_A": motif_a, "same_comp_B": motif_b}.get(variant, motif_c)
    shift = rng.randrange(0, len(motif))
    repeated = (motif[shift:] + motif[:shift]) * ((length // len(motif)) + 2)
    seq = repeated[:length]
    # Keep counts similar while adding small local variability.
    chars = list(seq)
    swap_count = max(1, length // 30)
    for _ in range(swap_count):
        i = rng.randrange(0, length)
        j = rng.randrange(0, length)
        chars[i], chars[j] = chars[j], chars[i]
    return "".join(chars)


def motif_position_read(length: int, species_id: str, rng: random.Random) -> str:
    """Generate reads with the same motif at controlled positions."""
    background = list(random_dna(length, {"A": 0.25, "C": 0.25, "G": 0.25, "T": 0.25}, rng))
    motif = "GATTACAGCG"
    if species_id == "motif_front":
        pos = 5
    elif species_id == "motif_middle":
        pos = max(0, (length - len(motif)) // 2)
    elif species_id == "motif_back":
        pos = max(0, length - len(motif) - 5)
    else:
        pos = rng.randrange(0, max(1, length - len(motif) + 1))
    background[pos:pos + len(motif)] = motif
    return "".join(background)


def make_clean_sequence(
    templates: dict[str, str],
    species_id: str,
    length: int,
    rng: random.Random,
) -> tuple[str, str]:
    if species_id in {"same_comp_A", "same_comp_B"}:
        return same_composition_read(length, species_id, rng), "-1"
    if species_id in {"motif_front", "motif_middle", "motif_back"}:
        return motif_position_read(length, species_id, rng), "-1"
    if species_id not in templates:
        raise ValueError(f"Unknown species/template: {species_id}")
    template = templates[species_id]
    max_start = len(template) - length
    start = rng.randrange(0, max_start + 1)
    return template[start:start + length], str(start)


def sample_clean_reads(
    templates: dict[str, str],
    species: list[str],
    lengths: list[int],
    reads_per_species: int,
    seed: int,
) -> list[dict[str, str]]:
    rng = random.Random(seed)
    rows: list[dict[str, str]] = []
    for length in lengths:
        for species_id in species:
            for idx in range(reads_per_species):
                seq, start = make_clean_sequence(templates, species_id, length, rng)
                clean_id = f"{species_id}_L{length}_R{idx:04d}"
                rows.append(
                    {
                        "read_id": f"{clean_id}_clean",
                        "clean_read_id": clean_id,
                        "sequence": seq,
                        "label": species_id,
                        "species_id": species_id,
                        "condition": "clean",
                        "source_rule": "template_slice",
                        "source_length": str(length),
                        "length": str(len(seq)),
                        "template_start": start,
                        "mutation_profile": "{}",
                        "notes": "",
                    }
                )
    return rows


def apply_condition(row: dict[str, str], condition: str, seed: int) -> dict[str, str]:
    rng = random.Random(f"{seed}:{row['clean_read_id']}:{condition}")
    seq = row["sequence"]
    profile: dict[str, object] = {"condition": condition}
    source_rule = condition

    if condition == "clean":
        new_seq = seq
    elif condition == "substitution_0_5pct":
        new_seq, positions = mutate_substitutions(seq, 0.005, rng)
        profile["substitution_positions"] = positions
    elif condition == "substitution_1pct":
        new_seq, positions = mutate_substitutions(seq, 0.01, rng)
        profile["substitution_positions"] = positions
    elif condition == "substitution_2pct":
        new_seq, positions = mutate_substitutions(seq, 0.02, rng)
        profile["substitution_positions"] = positions
    elif condition == "substitution_5pct":
        new_seq, positions = mutate_substitutions(seq, 0.05, rng)
        profile["substitution_positions"] = positions
    elif condition == "terminal_substitution_gradient":
        chars = list(seq)
        positions: list[int] = []
        for i, base in enumerate(chars):
            rate = 0.005 if i < max(0, len(chars) - 20) else 0.03
            if base in "ACGT" and rng.random() < rate:
                choices = [b for b in "ACGT" if b != base]
                chars[i] = rng.choice(choices)
                positions.append(i)
        new_seq = "".join(chars)
        profile["substitution_positions"] = positions
    elif condition == "N_1pct":
        new_seq, positions = mask_n(seq, 0.01, rng)
        profile["N_positions"] = positions
    elif condition == "N_3pct":
        new_seq, positions = mask_n(seq, 0.03, rng)
        profile["N_positions"] = positions
    elif condition == "N_5pct":
        new_seq, positions = mask_n(seq, 0.05, rng)
        profile["N_positions"] = positions
    elif condition == "N_cluster_5pct":
        new_seq, positions = mask_n(seq, 0.05, rng, mode="cluster")
        profile["N_positions"] = positions
    elif condition == "trim_to_69":
        new_seq = trim_sequence(seq, 69, mode="right", rng=rng)
    elif condition == "trim_to_60":
        new_seq = trim_sequence(seq, 60, mode="right", rng=rng)
    elif condition == "trim_to_50":
        new_seq = trim_sequence(seq, 50, mode="right", rng=rng)
    elif condition == "random_crop_69":
        new_seq = trim_sequence(seq, 69, mode="random", rng=rng)
    elif condition == "reverse_complement":
        new_seq = reverse_complement(seq)
    elif condition == "indel_stress":
        new_seq, events = inject_indel(seq, 0.005, rng)
        profile["indel_events"] = events
    elif condition == "low_complexity":
        motif = rng.choice(["AAAAAAAAAA", "TTTTTTTTTT", "ATATATATAT", "CACACACACA"])
        pos = rng.randrange(0, max(1, len(seq) - len(motif) + 1))
        new_seq = seq[:pos] + motif + seq[pos + len(motif):]
        profile["inserted_low_complexity"] = {"position": pos, "motif": motif}
    elif condition == "adapter_like":
        adapter = "AGATCGGAAGAGC"
        n = min(len(adapter), len(seq))
        new_seq = seq[:-n] + adapter[:n]
        profile["adapter"] = adapter[:n]
    else:
        raise ValueError(f"Unsupported condition: {condition}")

    out = dict(row)
    out["condition"] = condition
    out["sequence"] = new_seq
    out["length"] = str(len(new_seq))
    out["read_id"] = f"{row['clean_read_id']}_{condition}"
    out["source_rule"] = source_rule
    out["mutation_profile"] = json.dumps(profile, sort_keys=True)
    return out


def generate_dataset(
    output_csv: Path,
    species: list[str],
    lengths: list[int],
    conditions: list[str],
    reads_per_species: int = 20,
    seed: int = 13,
    template_length: int = 6000,
) -> list[dict[str, str]]:
    templates = build_templates(template_length=template_length, seed=seed)
    clean_rows = sample_clean_reads(templates, species, lengths, reads_per_species, seed)
    rows: list[dict[str, str]] = []
    for row in clean_rows:
        for condition in conditions:
            rows.append(apply_condition(row, condition, seed))

    output_csv.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "read_id",
        "clean_read_id",
        "sequence",
        "label",
        "species_id",
        "condition",
        "source_rule",
        "source_length",
        "length",
        "template_start",
        "mutation_profile",
        "notes",
    ]
    with output_csv.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    return rows
