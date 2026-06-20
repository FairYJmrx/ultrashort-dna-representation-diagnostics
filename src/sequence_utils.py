"""Basic DNA sequence helpers used by the lightweight experiments."""

from __future__ import annotations

import random
from collections import Counter
from itertools import product

BASES = "ACGT"
COMPLEMENT = str.maketrans("ACGTNacgtn", "TGCANtgcan")


def reverse_complement(seq: str) -> str:
    return seq.translate(COMPLEMENT)[::-1].upper()


def random_base(weights: dict[str, float] | None = None, rng: random.Random | None = None) -> str:
    rng = rng or random
    if not weights:
        return rng.choice(BASES)
    total = sum(weights.get(base, 0.0) for base in BASES)
    pick = rng.random() * total
    current = 0.0
    for base in BASES:
        current += weights.get(base, 0.0)
        if pick <= current:
            return base
    return BASES[-1]


def random_dna(length: int, weights: dict[str, float] | None = None, rng: random.Random | None = None) -> str:
    rng = rng or random
    return "".join(random_base(weights, rng) for _ in range(length))


def mutate_substitutions(seq: str, rate: float, rng: random.Random) -> tuple[str, list[int]]:
    chars = list(seq.upper())
    positions: list[int] = []
    for i, base in enumerate(chars):
        if base in BASES and rng.random() < rate:
            choices = [b for b in BASES if b != base]
            chars[i] = rng.choice(choices)
            positions.append(i)
    return "".join(chars), positions


def mask_n(seq: str, rate: float, rng: random.Random, mode: str = "random") -> tuple[str, list[int]]:
    chars = list(seq.upper())
    positions: list[int] = []
    n = max(1, round(len(chars) * rate)) if rate > 0 else 0
    if n == 0:
        return seq.upper(), positions
    if mode == "terminal":
        start = max(0, len(chars) - n)
        positions = list(range(start, len(chars)))
    elif mode == "cluster":
        start = rng.randrange(0, max(1, len(chars) - n + 1))
        positions = list(range(start, start + n))
    else:
        positions = sorted(rng.sample(range(len(chars)), min(n, len(chars))))
    for pos in positions:
        chars[pos] = "N"
    return "".join(chars), positions


def trim_sequence(seq: str, target_length: int, mode: str = "right", rng: random.Random | None = None) -> str:
    rng = rng or random
    seq = seq.upper()
    if target_length >= len(seq):
        return seq
    if mode == "left":
        return seq[-target_length:]
    if mode == "both":
        remove = len(seq) - target_length
        left = remove // 2
        return seq[left:left + target_length]
    if mode == "random":
        start = rng.randrange(0, len(seq) - target_length + 1)
        return seq[start:start + target_length]
    return seq[:target_length]


def inject_indel(seq: str, rate: float, rng: random.Random) -> tuple[str, list[str]]:
    events: list[str] = []
    out: list[str] = []
    for i, base in enumerate(seq.upper()):
        if rng.random() < rate / 2:
            events.append(f"del:{i}:{base}")
            continue
        out.append(base)
        if rng.random() < rate / 2:
            inserted = rng.choice(BASES)
            out.append(inserted)
            events.append(f"ins:{i}:{inserted}")
    return "".join(out), events


def kmer_counts(seq: str, k: int, canonical: bool = False, ignore_n: bool = True) -> Counter[str]:
    seq = seq.upper()
    counts: Counter[str] = Counter()
    if k <= 0 or len(seq) < k:
        return counts
    for i in range(len(seq) - k + 1):
        kmer = seq[i:i + k]
        if ignore_n and "N" in kmer:
            continue
        if canonical:
            rc = reverse_complement(kmer)
            kmer = min(kmer, rc)
        counts[kmer] += 1
    return counts


def kmer_tokens(seq: str, k: int, canonical: bool = False, ignore_n: bool = False) -> list[str]:
    seq = seq.upper()
    tokens: list[str] = []
    if k <= 0 or len(seq) < k:
        return tokens
    for i in range(len(seq) - k + 1):
        kmer = seq[i:i + k]
        if ignore_n and "N" in kmer:
            continue
        if canonical:
            kmer = min(kmer, reverse_complement(kmer))
        tokens.append(kmer)
    return tokens


def all_kmers(k: int) -> list[str]:
    return ["".join(p) for p in product(BASES, repeat=k)]


def gc_fraction(seq: str) -> float:
    seq = seq.upper()
    bases = [b for b in seq if b in BASES]
    if not bases:
        return 0.0
    return sum(1 for b in bases if b in "GC") / len(bases)


def shannon_entropy(seq: str) -> float:
    import math

    seq = seq.upper()
    counts = Counter(b for b in seq if b in "ACGTN")
    total = sum(counts.values())
    if total == 0:
        return 0.0
    entropy = 0.0
    for count in counts.values():
        p = count / total
        entropy -= p * math.log2(p)
    return entropy

