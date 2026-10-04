"""Exploratory statistics: bootstrap CIs, permutation p-values, Holm, random-entry foil."""

from __future__ import annotations

import random
from statistics import mean

SEED = 20261004
N_BOOT = 10_000


def metric(xs: list[float], kind: str) -> float:
    if kind == "win_rate":
        return sum(1 for x in xs if x > 0) / len(xs)
    return mean(xs)


def boot_ci(xs: list[float], kind: str = "mean_R", n: int = N_BOOT, seed: int = SEED, alpha: float = 0.05):
    rng = random.Random(seed)
    k = len(xs)
    vals = sorted(metric([xs[rng.randrange(k)] for _ in range(k)], kind) for _ in range(n))
    return vals[int(alpha / 2 * n)], vals[int((1 - alpha / 2) * n) - 1]


def diff_test(a: list[float], b: list[float], kind: str, direction: str, n: int = N_BOOT, seed: int = SEED) -> dict:
    """Difference metric(a) - metric(b): bootstrap 95% CI + one-sided permutation p."""
    rng = random.Random(seed)
    obs = metric(a, kind) - metric(b, kind)
    boots = []
    for _ in range(n):
        ra = [a[rng.randrange(len(a))] for _ in a]
        rb = [b[rng.randrange(len(b))] for _ in b]
        boots.append(metric(ra, kind) - metric(rb, kind))
    boots.sort()
    pooled = a + b
    sign = 1 if direction == "higher_when_true" else -1
    ge = 0
    for _ in range(n):
        rng.shuffle(pooled)
        dd = metric(pooled[:len(a)], kind) - metric(pooled[len(a):], kind)
        if sign * dd >= sign * obs - 1e-12:
            ge += 1
    return {"diff": obs, "ci95": (boots[int(0.025 * n)], boots[int(0.975 * n) - 1]),
            "p_one_sided": (ge + 1) / (n + 1)}


def holm(pvals: dict[str, float]) -> dict[str, float]:
    items = sorted(pvals.items(), key=lambda kv: kv[1])
    m = len(items)
    out, running = {}, 0.0
    for i, (k, p) in enumerate(items):
        running = max(running, min(1.0, (m - i) * p))
        out[k] = running
    return out


def max_drawdown(rs: list[float]) -> float:
    """Peak-to-trough of cumulative R in the given (time) order."""
    peak = cur = dd = 0.0
    for r in rs:
        cur += r
        peak = max(peak, cur)
        dd = max(dd, peak - cur)
    return dd
