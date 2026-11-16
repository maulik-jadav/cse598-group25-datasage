"""Small statistics helpers for the evaluation (standard library only).

- bootstrap_ci: percentile bootstrap CI of a mean. With `groups`, whole groups are resampled
  (a cluster bootstrap), which we use because the two questions about one table are not independent.
- mcnemar_exact: exact two-sided McNemar test on the discordant pairs of a paired comparison.
- paired_bootstrap: CI of the mean difference between two systems scored on the same questions.
- holm: Holm-Bonferroni adjustment for a family of p-values.
"""

from __future__ import annotations

import math
import random
from collections import defaultdict
from typing import Hashable, Sequence


def _clusters(values: Sequence[float], groups: Sequence[Hashable] | None) -> list[list[float]]:
    if groups is None:
        return [[v] for v in values]
    if len(groups) != len(values):
        raise ValueError("values and groups must have the same length")
    by: dict = defaultdict(list)
    for v, g in zip(values, groups):
        by[g].append(v)
    return list(by.values())


def _percentile(sorted_values: list[float], q: float) -> float:
    """Linear-interpolated percentile, q in [0, 1]."""
    if not sorted_values:
        raise ValueError("no values")
    pos = q * (len(sorted_values) - 1)
    lo, hi = math.floor(pos), math.ceil(pos)
    return sorted_values[lo] + (sorted_values[hi] - sorted_values[lo]) * (pos - lo)


def _boot_means(clusters: list[list[float]], n_boot: int, seed: int) -> list[float]:
    """Sorted means of `n_boot` resamples (with replacement) of whole clusters."""
    rng = random.Random(seed)
    k = len(clusters)
    sums = [(sum(c), len(c)) for c in clusters]
    means = []
    for _ in range(n_boot):
        total = count = 0.0
        for _ in range(k):
            s, n = sums[rng.randrange(k)]
            total += s
            count += n
        means.append(total / count)
    means.sort()
    return means


def bootstrap_ci(values: Sequence[float], groups: Sequence[Hashable] | None = None, n_boot: int = 10000,
                 alpha: float = 0.05, seed: int = 0) -> tuple[float, float]:
    """Percentile bootstrap CI of the mean of `values` (resampling groups when given)."""
    clusters = _clusters([float(v) for v in values], groups)
    if not clusters:
        raise ValueError("no values")
    means = _boot_means(clusters, n_boot, seed)
    return _percentile(means, alpha / 2), _percentile(means, 1 - alpha / 2)


def mcnemar_exact(b: int, c: int) -> float:
    """Exact two-sided McNemar p-value. b = pairs only the first system got right, c = only the second."""
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    tail = sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n
    return min(1.0, 2 * tail)


def discordant(first: Sequence[bool], second: Sequence[bool]) -> tuple[int, int]:
    """(b, c): questions only `first` got right, and questions only `second` got right."""
    if len(first) != len(second):
        raise ValueError("paired lists must have the same length")
    b = sum(1 for x, y in zip(first, second) if x and not y)
    c = sum(1 for x, y in zip(first, second) if y and not x)
    return b, c


def paired_bootstrap(first: Sequence[float], second: Sequence[float], groups: Sequence[Hashable] | None = None,
                     n_boot: int = 10000, alpha: float = 0.05, seed: int = 0) -> dict:
    """Mean of first - second on the same questions, with a (cluster) bootstrap CI and the share of
    resamples in which the difference is <= 0 (a one-sided bootstrap p-value for first > second)."""
    if len(first) != len(second):
        raise ValueError("paired lists must have the same length")
    diffs = [float(a) - float(b) for a, b in zip(first, second)]
    clusters = _clusters(diffs, groups)
    means = _boot_means(clusters, n_boot, seed)
    return {"diff": sum(diffs) / len(diffs), "ci": (_percentile(means, alpha / 2), _percentile(means, 1 - alpha / 2)),
            "share_le_zero": sum(m <= 0 for m in means) / n_boot}


def holm(pvalues: Sequence[float]) -> list[float]:
    """Holm-Bonferroni adjusted p-values, in the input order."""
    m = len(pvalues)
    order = sorted(range(m), key=lambda i: pvalues[i])
    adjusted = [0.0] * m
    running = 0.0
    for rank, i in enumerate(order):
        running = max(running, min(1.0, (m - rank) * pvalues[i]))
        adjusted[i] = running
    return adjusted
