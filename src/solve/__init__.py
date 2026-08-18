"""问题求解脚本目录。

每个求解脚本是一个可独立运行的 ``.py`` 文件（或 notebook），遵循统一模板：

1. 加载/构造数据
2. 实例化模型（来自 ``src.models`` 或 ``src.algorithms``）
3. ``model.run(X, y)`` 或调用算法函数
4. 输出结果 + 可视化

模板见 ``src/solve/template.py``。
"""
