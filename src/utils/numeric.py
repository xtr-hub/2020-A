"""通用数值方法 -- 从 2024-A 真实建模项目中提炼。

提供 Newton-Raphson 求根、RK4 常微分方程积分等基础数值工具。
"""

from __future__ import annotations

from collections.abc import Callable
from typing import TypeVar

T = TypeVar("T", float, list[float])


# ---------------------------------------------------------------------------
# Newton-Raphson
# ---------------------------------------------------------------------------

def newton_raphson(
    f: Callable[[float], float],
    df: Callable[[float], float],
    x0: float,
    *,
    max_iter: int = 100,
    tol: float = 1e-8,
) -> float:
    """Newton-Raphson 法求 ``f(x) = 0`` 的根。

    迭代公式：``x_{n+1} = x_n - f(x_n) / f'(x_n)``，直至 ``|Δx| < tol`` 或达到最大迭代次数。

    Args:
        f: 目标函数。
        df: 目标函数的导数。
        x0: 初始猜测值。
        max_iter: 最大迭代次数，默认 100。
        tol: 收敛容差，默认 1e-8。

    Returns:
        近似根。

    Raises:
        RuntimeError: 在 ``max_iter`` 次迭代后未收敛。
    """
    x = x0
    for _ in range(max_iter):
        fx = f(x)
        dfx = df(x)
        if dfx == 0.0:
            raise RuntimeError(f"导数为零，无法继续迭代（x={x}）")
        x_new = x - fx / dfx
        if abs(x_new - x) < tol:
            return x_new
        x = x_new
    raise RuntimeError(f"Newton-Raphson 在 {max_iter} 次迭代后未收敛（tol={tol}）")


# ---------------------------------------------------------------------------
# RK4
# ---------------------------------------------------------------------------

def rk4_step(
    f: Callable[[float, float], float],
    t: float,
    y: float,
    dt: float,
) -> float:
    """单步 4 阶 Runge-Kutta 积分。

    Args:
        f: 导数函数 ``f(t, y) -> dy/dt``。
        t: 当前时间。
        y: 当前状态值。
        dt: 时间步长。

    Returns:
        下一时刻的状态值 ``y(t + dt)``。
    """
    k1 = f(t, y)
    k2 = f(t + dt / 2, y + k1 * dt / 2)
    k3 = f(t + dt / 2, y + k2 * dt / 2)
    k4 = f(t + dt, y + k3 * dt)
    return y + dt / 6 * (k1 + 2 * k2 + 2 * k3 + k4)


def rk4_integrate(
    f: Callable[[float, float], float],
    y0: float,
    t_span: tuple[float, float],
    dt: float,
) -> tuple[list[float], list[float]]:
    """用 RK4 在区间上积分一阶 ODE ``dy/dt = f(t, y)``。

    Args:
        f: 导数函数 ``f(t, y) -> dy/dt``。
        y0: 初始值 ``y(t0)``。
        t_span: 积分区间 ``(t0, t_end)``。
        dt: 时间步长。

    Returns:
        ``(t_values, y_values)`` 两个列表。
    """
    t0, t_end = t_span
    n_steps = int((t_end - t0) / dt)
    t = t0
    y = y0
    t_vals = [t]
    y_vals = [y]
    for _ in range(n_steps):
        y = rk4_step(f, t, y, dt)
        t += dt
        t_vals.append(t)
        y_vals.append(y)
    return t_vals, y_vals
