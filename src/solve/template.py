"""求解脚本模板 -- 复制此文件到 solve/ 目录下改名即可开始。

使用方式::

    cp src/solve/template.py src/solve/my_solution.py
    # 编辑 my_solution.py, 填入你的模型与数据
    python src/solve/my_solution.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

_project_root = Path(__file__).resolve().parent.parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from src.utils.plot import Plotter, setup_cjk_font

setup_cjk_font()


def main() -> None:
    # 1. 构造/加载数据
    X = np.array([[1, 2], [3, 4], [5, 6]])
    y = np.array([0, 1, 0])
    print(f"数据: {X.shape[0]} 样本, {X.shape[1]} 特征")

    # 2. 实例化模型并运行
    from src.algorithms.topsis import (
        calculate_closeness, convert_indicators,
        ideal_solutions, normalize_matrix,
    )

    kinds = [1, 1]  # 两个指标都是极大型
    converted = convert_indicators(X, kinds)
    normalized = normalize_matrix(converted)
    weighted = normalized  # 等权重

    v_pos, v_neg = ideal_solutions(weighted)
    closeness = calculate_closeness(weighted, v_pos, v_neg)

    # 3. 输出结果
    ranks = np.argsort(-closeness) + 1
    for i, (c, r) in enumerate(zip(closeness, ranks)):
        print(f"方案 {i + 1}: 贴近度 = {c:.4f}, 排名 = {r}")

    # 4. 可视化
    Plotter.bar([f"方案{i + 1}" for i in range(len(closeness))],
                 closeness, title="TOPSIS 贴近度")
    Plotter.save("outputs/template_demo.png")
    print("完成 -- 图片已保存至 outputs/template_demo.png")


if __name__ == "__main__":
    main()
