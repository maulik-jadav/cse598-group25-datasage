"""Tests for the statistics helpers used by the scale and ablation study. No model calls."""

import math

import pytest

from eval.stats import bootstrap_ci, discordant, holm, mcnemar_exact, paired_bootstrap


def test_mcnemar_exact_known_values():
    assert mcnemar_exact(0, 0) == 1.0
    assert mcnemar_exact(3, 3) == 1.0
    # 10 discordant pairs all one way: p = 2 * 0.5**10
    assert mcnemar_exact(10, 0) == pytest.approx(2 / 1024)
    assert mcnemar_exact(0, 10) == pytest.approx(2 / 1024)
    # b=1, c=6: p = 2 * (C(7,0)+C(7,1)) / 2**7 = 16/128
    assert mcnemar_exact(1, 6) == pytest.approx(0.125)
    assert mcnemar_exact(5, 6) == 1.0  # capped at 1


def test_discordant_counts_only_disagreements():
    first = [True, True, False, False, True]
    second = [True, False, True, False, False]
    assert discordant(first, second) == (2, 1)
    with pytest.raises(ValueError):
        discordant([True], [True, False])


def test_bootstrap_ci_brackets_the_mean_and_is_deterministic():
    values = [1] * 30 + [0] * 10
    lo, hi = bootstrap_ci(values, n_boot=2000, seed=1)
    assert lo < 0.75 < hi
    assert 0.55 < lo and hi < 0.9
    assert bootstrap_ci(values, n_boot=2000, seed=1) == (lo, hi)
    assert bootstrap_ci([1, 1, 1, 1]) == (1.0, 1.0)


def test_cluster_bootstrap_is_wider_when_groups_are_correlated():
    # Pairs of questions share an outcome, so resampling pairs gives a wider interval than resampling questions.
    values = [1, 1, 0, 0] * 10
    groups = [i // 2 for i in range(len(values))]
    lo_i, hi_i = bootstrap_ci(values, n_boot=4000, seed=2)
    lo_c, hi_c = bootstrap_ci(values, groups=groups, n_boot=4000, seed=2)
    assert hi_c - lo_c > hi_i - lo_i
    with pytest.raises(ValueError):
        bootstrap_ci([1, 0], groups=[0])


def test_paired_bootstrap_difference():
    first = [1] * 20 + [0] * 0
    second = [1] * 10 + [0] * 10
    out = paired_bootstrap(first, second, n_boot=2000, seed=3)
    assert out["diff"] == pytest.approx(0.5)
    assert out["ci"][0] > 0.2 and out["ci"][1] <= 0.75
    assert out["share_le_zero"] == 0.0
    same = paired_bootstrap([1, 0, 1], [1, 0, 1], n_boot=500)
    assert same["diff"] == 0 and same["ci"] == (0.0, 0.0) and same["share_le_zero"] == 1.0


def test_holm_adjustment():
    adjusted = holm([0.01, 0.04, 0.03, 0.5])
    assert adjusted == pytest.approx([0.04, 0.09, 0.09, 0.5])
    assert all(0 <= p <= 1 for p in holm([0.9, 0.8]))
    assert math.isclose(holm([0.2])[0], 0.2)
