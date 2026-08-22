"""2020 高教社杯 A 题「炉温曲线」求解脚本

流程：附件数据拟合热参数 -> 问题1 -> 问题2 -> 问题3 -> 问题4

用法::

    python src/solve/solve.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import numpy as np
import pandas as pd

_project_root = Path(__file__).resolve().parent.parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from src.algorithms.pso import PSO
from src.models.model import model
from src.utils.plot import Plotter, setup_cjk_font

setup_cjk_font()
# 论文图表字体
matplotlib.rcParams["font.family"] = "serif"
matplotlib.rcParams["font.serif"] = ["Songti SC", "Times New Roman", "SimSun"]

L = 435.5  # 炉长
DX = 0.5  # 炉长方向步长
DZ = 0.025  # 厚度方向步长
DT = 0.05  # 时间步长
PENALTY = 5000  # 制程界限罚系数

# 各工况温区设定值
ZONES_FIT = [175] * 5 + [195, 235, 255, 255, 25, 25]
ZONES_Q1 = [173] * 5 + [198, 230, 257, 257, 25, 25]
ZONES_Q2 = [182] * 5 + [203, 237, 254, 254, 25, 25]


def simulate(v, zones, a, k, fp=1.0):
    """按给定工况跑一遍炉温仿真，返回模型对象"""
    m = model(dt=DT, dx=DX, dz=DZ, temperature_zone=list(zones),
              end_time=L / (v / 60), v=v, a=a, k=k, front_power=fp)
    m.run()
    return m


def violation(mt):
    """制程界限的归一化违约度"""
    v = 0.0
    v += max(0.0, mt["slope_up"] - 3) / 3
    v += max(0.0, -3 - mt["slope_down"]) / 3
    v += max(0.0, 60 - mt["t150_190"]) / 30 + max(0.0, mt["t150_190"] - 120) / 30
    v += max(0.0, 40 - mt["t217"]) / 20 + max(0.0, mt["t217"] - 90) / 20
    v += max(0.0, 240.1 - mt["peak"]) / 5 + max(0.0, mt["peak"] - 249.9) / 5
    return v


def fit_parameters():
    """用附件数据拟合热参数与炉前幂指数"""
    data = pd.read_excel(_project_root / "data/raw/A/附件.xlsx")
    t_obs = data.iloc[:, 0].to_numpy()
    T_obs = data.iloc[:, 1].to_numpy()

    def mse(p):
        m = simulate(70, ZONES_FIT, 10 ** p[0], 10 ** p[1:4], fp=p[4])
        T_sim = np.interp(t_obs, m.time_axis, m.center_temperature)
        return float(np.mean((T_sim - T_obs) ** 2))

    bounds = [(-2, 1), (-3, 0), (-3, 0), (-3, 0), (1, 16)]
    best, f = PSO(mse, bounds, n_particles=30, max_iter=100, seed=42).run()
    a, k, fp = 10 ** best[0], 10 ** best[1:4], float(best[4])
    print(f"  a={a:.4f}, k1/k2/k3={k[0]:.5f}/{k[1]:.5f}/{k[2]:.5f}, "
          f"炉前幂指数={fp:.2f}, MSE={f:.4f}")

    m = simulate(70, ZONES_FIT, a, k, fp)
    T_sim = np.interp(t_obs, m.time_axis, m.center_temperature)

    xgrid = np.arange(m.x_len) * DX
    fig, ax = Plotter.subplots(1, 1, figsize=(9, 5))
    Plotter.line(m.air_temperature, xgrid, ax=ax, color="black",
                 title="炉内空气温度分布", xlabel="位置/cm", ylabel="温度/°C")
    Plotter.save(str(_project_root / "outputs/q0_空气温度分布.png"), fig)

    fig, ax = Plotter.subplots(1, 1, figsize=(9, 5))
    Plotter.line(T_obs, t_obs, ax=ax, color="black", label="实测曲线")
    Plotter.line(T_sim, t_obs, ax=ax, color="red", linestyle="--", label="模拟曲线",
                 title="附件数据拟合效果", xlabel="时间/s", ylabel="温度/°C")
    ax.legend()
    Plotter.save(str(_project_root / "outputs/q0_参数拟合.png"), fig)
    return a, k, fp


def q1(a, k, fp):
    print("\n--------- 问题1：炉温曲线 --------")
    m = simulate(78, ZONES_Q1, a, k, fp)
    spots = {"小温区3中点": 111.25, "小温区6中点": 217.75,
             "小温区7中点": 253.25, "小温区8结束处": 304.0}
    for name, x in spots.items():
        print(f"  {name}：{m.temperature_at_position(x):.2f}")

    step = round(0.5 / m.dt)
    idx = np.arange(0, m.end_time_idx, step)
    out = _project_root / "data/raw/A/result.csv"
    with open(out, "w", encoding="gbk", newline="") as f:
        f.write("时间(s),温度(摄氏度)\r\n")
        for i in idx:
            f.write(f"{m.time_axis[i]:g},{m.center_temperature[i]:.2f}\r\n")

    fig, ax = Plotter.subplots(1, 1, figsize=(9, 5))
    Plotter.line(m.center_temperature, m.time_axis, ax=ax, color="black",
                 title="问题1炉温曲线（过炉速度78 cm/min）",
                 xlabel="时间/s", ylabel="温度/°C")
    for name, x in spots.items():
        ax.axvline(x / (78 / 60), color="gray", linestyle=":", linewidth=0.8)
        ax.annotate(name, (x / (78 / 60), m.temperature_at_position(x)),
                    textcoords="offset points", xytext=(5, 5), fontsize=9)
    Plotter.save(str(_project_root / "outputs/q1_炉温曲线.png"), fig)


def q2(a, k, fp):
    print("\n--------- 问题2：最大过炉速度 --------")

    def obj(v):
        m = simulate(v[0], ZONES_Q2, a, k, fp)
        return -v[0] + PENALTY * violation(m.metrics())

    best, _ = PSO(obj, [(65, 100)], n_particles=20, max_iter=60, seed=1).run()
    v_max = float(best[0])

    m = simulate(v_max, ZONES_Q2, a, k, fp)
    print(f"  最大过炉速度：{v_max:.2f}")

    fig, ax = Plotter.subplots(1, 1, figsize=(9, 5))
    Plotter.line(m.center_temperature, m.time_axis, ax=ax, color="black",
                 title=f"问题2最大过炉速度下的炉温曲线（{v_max:.2f} cm/min）",
                 xlabel="时间/s", ylabel="温度/°C")
    Plotter.save(str(_project_root / "outputs/q2_最大速度.png"), fig)
    return v_max


def q3(a, k, fp):
    print("\n------ 问题3：最小覆盖面积 ------")

    def obj(p):
        zones = [p[0]] * 5 + [p[1], p[2], p[3], p[3], 25, 25]
        m = simulate(p[4], zones, a, k, fp)
        return m.area_above(217) + PENALTY * violation(m.metrics())

    bounds = [(165, 185), (185, 205), (225, 245), (245, 265), (65, 100)]
    best, _ = PSO(obj, bounds, n_particles=30, max_iter=100, seed=2).run()# 粒子群

    zones = [best[0]] * 5 + [best[1], best[2], best[3], best[3], 25, 25]
    m = simulate(best[4], zones, a, k, fp)
    area = m.area_above(217)
    print(f"  最优设定：温区1至5={best[0]:.2f}, 温区6={best[1]:.2f}, "
          f"温区7={best[2]:.2f}, 温区8到9={best[3]:.2f}, v={best[4]:.2f}")
    print(f"  覆盖面积：{area:.2f}, 对称度：{m.symmetry_index():.4f}")

    fig, ax = Plotter.subplots(1, 1, figsize=(9, 5))
    Plotter.line(m.center_temperature, m.time_axis, ax=ax, color="black",
                 title="问题3最优炉温曲线", xlabel="时间/s", ylabel="温度/°C")
    ax.axhline(217, color="gray", linestyle="--", linewidth=0.8, label="217")
    ax.fill_between(m.time_axis, 217, m.center_temperature,
                    where=m.center_temperature > 217, color="0.85")
    ax.legend()
    Plotter.save(str(_project_root / "outputs/q3_最优曲线.png"), fig)
    return best, area


def q4(a, k, fp):
    print("\n------- 问题4：面积与对称性 --------")
    W_SYM = 500  # 对称度权重

    def obj(p):
        zones = [p[0]] * 5 + [p[1], p[2], p[3], p[3], 25, 25]
        m = simulate(p[4], zones, a, k, fp)
        return (m.area_above(217) + W_SYM * m.symmetry_index()
                + PENALTY * violation(m.metrics()))

    bounds = [(165, 185), (185, 205), (225, 245), (245, 265), (65, 100)]
    best, _ = PSO(obj, bounds, n_particles=30, max_iter=100, seed=3).run()

    zones = [best[0]] * 5 + [best[1], best[2], best[3], best[3], 25, 25]
    m = simulate(best[4], zones, a, k, fp)
    area, sym = m.area_above(217), m.symmetry_index()
    print(f"  最优设定：温区1至5={best[0]:.2f}, 温区6={best[1]:.2f}, "
          f"温区7={best[2]:.2f}, 温区8到9={best[3]:.2f}, v={best[4]:.2f}")
    print(f"  覆盖面积：{area:.2f}, 对称度：{sym:.4f}")

    fig, ax = Plotter.subplots(1, 1, figsize=(9, 5))
    Plotter.line(m.center_temperature, m.time_axis, ax=ax, color="black",
                 title="问题4最优炉温曲线", xlabel="时间/s", ylabel="温度/°C")
    ax.axhline(217, color="gray", linestyle="--", linewidth=0.8, label="217°C")
    ax.fill_between(m.time_axis, 217, m.center_temperature,
                    where=m.center_temperature > 217, color="0.85")
    t_peak = m.time_axis[int(np.argmax(m.center_temperature))]
    ax.axvline(t_peak, color="gray", linestyle=":", linewidth=0.8, label="峰值中心线")
    ax.legend()
    Plotter.save(str(_project_root / "outputs/q4_最优曲线.png"), fig)
    return best, area, sym


def main() -> None:
    print("------- 参数拟合 -------")
    a, k, fp = fit_parameters()
    q1(a, k, fp)
    q2(a, k, fp)
    q3(a, k, fp)
    q4(a, k, fp)
    print("\n求解全部完成")


if __name__ == "__main__":
    main()
