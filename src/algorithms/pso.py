"""粒子群优化算法(PSO) -- 求解有界连续最小化问题。"""

from __future__ import annotations

from collections.abc import Callable

import numpy as np


class PSO:
    """标准粒子群算法，求解有界连续最小化问题"""

    def __init__(self, func: Callable, bounds, n_particles: int = 30,
                 max_iter: int = 100, c1: float = 1.5, c2: float = 1.5,
                 seed: int | None = None):
        self.func = func
        self.bounds = np.asarray(bounds, dtype=float)
        self.n = n_particles
        self.max_iter = max_iter
        self.c1, self.c2 = c1, c2
        self.rng = np.random.default_rng(seed)
        self.best_x = None
        self.best_f = np.inf

    def run(self, verbose: bool = False):
        lo, hi = self.bounds[:, 0], self.bounds[:, 1]
        dim = len(lo)
        pos = self.rng.uniform(lo, hi, (self.n, dim))
        vel = self.rng.uniform(-1, 1, (self.n, dim)) * (hi - lo) * 0.1
        pbest = pos.copy()
        pfit = np.array([self.func(p) for p in pos])
        g = int(np.argmin(pfit))
        self.best_x, self.best_f = pbest[g].copy(), float(pfit[g])

        for it in range(self.max_iter):
            w = 0.9 - 0.5 * it / self.max_iter  # 惯性权重线性递减
            r1 = self.rng.random((self.n, dim))
            r2 = self.rng.random((self.n, dim))
            vel = w * vel + self.c1 * r1 * (pbest - pos) + self.c2 * r2 * (self.best_x - pos)
            pos = np.clip(pos + vel, lo, hi)
            fit = np.array([self.func(p) for p in pos])
            better = fit < pfit
            pbest[better] = pos[better]
            pfit[better] = fit[better]
            g = int(np.argmin(pfit))
            if pfit[g] < self.best_f:
                self.best_x, self.best_f = pbest[g].copy(), float(pfit[g])
            if verbose and (it % 10 == 0 or it == self.max_iter - 1):
                print(f"  iter {it:3d}  best = {self.best_f:.6g}")
        return self.best_x, self.best_f
