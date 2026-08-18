"""Math Framework -- 数学建模与综合评价算法框架。

一键使用::

    import src as mf

    # ---- 算法（一行调用）----
    mf.entropy_weight(matrix)                 # 熵权法 -> weights
    mf.topsis(matrix, kinds=[1, 2, 1])        # TOPSIS -> closeness
    mf.ahp(judgment_matrix)                   # AHP -> (lambda_max, weights)
    mf.grey_relational(matrix)                # 灰色关联 -> scores
    mf.fuzzy_eval(R, weights, scores)         # 模糊综合评价 -> result

    # ---- 矩阵变换 ----
    mf.positive(matrix, kinds)                 # 正向化
    mf.normalize(matrix)                       # 向量归一化
    mf.sum_normalize(matrix)                   # 列和归一化

    # ---- 数据 I/O ----
    mf.read_matrix()                           # 控制台输入矩阵
    mf.write_matrix(m, "out.xlsx", labels=...)  # 矩阵 -> Excel
    mf.load("data.csv")                        # 加载数据

    # ---- 画图 ----
    mf.plot.line([1, 2, 3])
    mf.plot.bar(["A", "B"], [10, 20])

    # ---- 数值 & 计时 ----
    mf.newton(f, df, x0=1.0)
    with mf.timer("训练"): ...

    # ---- 帮助 ----
    mf.help()
"""

# ===================================================================
# 算法 -- 快捷包装（完整流程一行完成）
# ===================================================================

import numpy as np

from src.algorithms.ahp import (
    WeightVectorType,
    calculate_weight_vector,
    is_valid_judgment_matrix,
)
from src.algorithms.entropy_weight import calculate_entropy_weights
from src.algorithms.fuzzy_comprehensive_evaluation import (
    FuzzyOperator,
    fuzzy_comprehensive_evaluate,
    validate_weights,
    validate_membership_matrix,
    build_membership_matrix,
)
from src.algorithms.grey_relational_analysis import (
    grey_relational_analysis,
    normalize_data as _grey_normalize,
)
from src.algorithms.topsis import (
    calculate_closeness,
    convert_indicators,
    ideal_solutions,
    normalize_matrix,
    weighted_normalized_matrix,
)

from src.utils.matrix import (
    positive_transform,
    sum_normalize,
    vector_normalize,
    extract_x,
    extract_y,
)


def entropy_weight(matrix, kinds=None, *, best_values=None, intervals=None):
    """熵权法：一步计算指标客观权重。"""
    return calculate_entropy_weights(matrix, kinds=kinds, best_values=best_values, intervals=intervals)


def topsis(matrix, kinds, *, weights=None, best_values=None, intervals=None):
    """TOPSIS：一步得到贴近度。"""
    converted = convert_indicators(matrix, kinds, best_values, intervals)
    normalized = normalize_matrix(converted)
    m = matrix.shape[1]
    w = np.ones(m) / m if weights is None else np.asarray(weights, dtype=float)
    w = w / np.sum(w)
    weighted = normalized * w
    v_pos, v_neg = ideal_solutions(weighted)
    return calculate_closeness(weighted, v_pos, v_neg)


def ahp(matrix):
    """AHP：计算最大特征值与权重。"""
    n = matrix.shape[0]
    return calculate_weight_vector(matrix, n, WeightVectorType.EIGVEC)


def grey_relational(matrix, kinds=None, *, rho=0.5):
    """灰色关联分析：一步得到关联度。"""
    data = matrix.copy()
    if kinds is not None:
        data = positive_transform(data, kinds)
    normalized = _grey_normalize(data)
    return grey_relational_analysis(normalized, rho=rho)


def fuzzy_eval(R, weights, scores, grades=None, *, operator=None):
    """模糊综合评价：一步得到得分与等级。"""
    if operator is None:
        operator = FuzzyOperator.WEIGHTED_AVERAGE
    return fuzzy_comprehensive_evaluate(
        validate_weights(weights), R, scores, grades or [], operator,
    )


# ===================================================================
# 便捷别名
# ===================================================================

positive = positive_transform
normalize = vector_normalize


# ===================================================================
# 工具
# ===================================================================

from src.utils.numeric import newton_raphson as newton, rk4_step, rk4_integrate
from src.utils.plot import Plotter as _Plotter, setup_cjk_font
from src.utils.timing import timer, timeit, Stopwatch

# 画图子模块
plot = _Plotter

# 模型基类
from src.models.base import Model

# I/O -- 常用函数直接暴露
from src.io.data import load_raw as load, write_matrix_excel as write_matrix, write_sheets, read_matrix_excel
from src.io.matrix_io import read_matrix, print_matrix


# ===================================================================
# 帮助
# ===================================================================

def help() -> None:  # noqa: A001
    """Print full API reference."""
    print("""
+------------------------------------------------------------+
|            Math Framework API  (import src as mf)           |
+------------------------------------------------------------+
| [Algorithms]                                               |
| mf.entropy_weight(matrix, kinds=None) -> weights           |
| mf.topsis(matrix, kinds, weights=None) -> closeness        |
| mf.ahp(matrix) -> lambda_max, weights                      |
| mf.grey_relational(matrix, kinds=None) -> scores           |
| mf.fuzzy_eval(R, weights, scores, grades) -> result        |
+------------------------------------------------------------+
| [Matrix]                                                   |
| mf.positive(m, kinds)      mf.normalize(m)                 |
| mf.sum_normalize(m)        mf.extract_x / extract_y        |
+------------------------------------------------------------+
| [Data I/O]                                                 |
| mf.load("file.csv")               -> DataFrame             |
| mf.read_matrix()                  -> ndarray (console)     |
| mf.write_matrix(m, path, labels)  -> .xlsx                 |
| mf.write_sheets(dict, path)       -> multi-sheet .xlsx     |
| mf.print_matrix(m)                                         |
+------------------------------------------------------------+
| [Plot]  mf.plot.line(y) / .bar(x,h) / .scatter(y) / ...   |
| mf.setup_cjk_font()              CJK font config            |
+------------------------------------------------------------+
| [Numeric]                                                  |
| mf.newton(f, df, x0)             Newton-Raphson root       |
| mf.rk4_step(f, t, y, dt)         Single RK4 step           |
| mf.rk4_integrate(f, y0, span, dt) Full interval integrate  |
+------------------------------------------------------------+
| [Timing]                                                   |
| with mf.timer("label"): ...      Context manager           |
| @mf.timeit                       Decorator                 |
| sw = mf.Stopwatch()              Multi-stage stopwatch     |
+------------------------------------------------------------+
| mf.Model                         Base class (ABC)          |
| mf.help()                        Print this help           |
+------------------------------------------------------------+
""")
