"""计时与性能工具。"""

from __future__ import annotations

import time
from collections.abc import Callable
from contextlib import contextmanager
from typing import Any


@contextmanager
def timer(label: str = "耗时"):
    """上下文管理器：打印代码块执行时间。

    用法::

        with timer("训练模型"):
            model.run(X, y)
    """
    t0 = time.perf_counter()
    yield
    elapsed = time.perf_counter() - t0
    print(f"{label}: {elapsed:.4f} s")


def timeit(func: Callable) -> Callable:
    """装饰器：每次调用自动打印执行时间。

    用法::

        @timeit
        def heavy_computation():
            ...
    """
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        t0 = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - t0
        print(f"{func.__name__}: {elapsed:.4f} s")
        return result

    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    return wrapper


class Stopwatch:
    """秒表：start / lap / stop，适合手动计时多个阶段。

    用法::

        sw = Stopwatch()
        sw.start()
        # ... 阶段 1 ...
        sw.lap("数据加载")
        # ... 阶段 2 ...
        sw.lap("模型计算")
        sw.stop()
    """

    def __init__(self) -> None:
        self._t0: float = 0.0
        self._laps: list[tuple[str, float]] = []

    def start(self) -> Stopwatch:
        self._t0 = time.perf_counter()
        self._laps.clear()
        return self

    def lap(self, label: str = "") -> float:
        t = time.perf_counter()
        elapsed = t - self._t0
        self._laps.append((label, elapsed))
        if label:
            print(f"  [{label}] {elapsed:.4f} s")
        self._t0 = t
        return elapsed

    def stop(self) -> None:
        """停止计时并打印汇总。"""
        if not self._laps:
            return
        total = sum(e for _, e in self._laps)
        print(f"  总计: {total:.4f} s")
        max_label = max(len(l) for l, _ in self._laps) if self._laps else 0
        for label, elapsed in self._laps:
            bar = "#" * int(elapsed / total * 30) if total > 0 else ""
            print(f"    {label:<{max_label}}  {elapsed:8.4f} s  {bar}")
