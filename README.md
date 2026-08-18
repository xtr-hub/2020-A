# Math Framework

数学建模与综合评价算法的 Python 框架。一行 `import src as mf` 即可使用全部功能。

## Quick Start

```bash
pip install -e ".[dev]"
```

```python
import numpy as np
import src as mf

# ----- 算法：一行调用 -----
matrix = np.array([[80, 90, 78], [76, 88, 85], [90, 82, 92]])

w = mf.entropy_weight(matrix)                       # 熵权法 -> weights
c = mf.topsis(matrix, kinds=[1, 2, 1])              # TOPSIS  -> closeness
lam, w = mf.ahp(np.array([[1,2,5],[1/2,1,3],[1/5,1/3,1]]))  # AHP

# ----- 画图 -----
mf.plot.line([1, 3, 2, 5, 4])                      # 只传 y, 自动 x
mf.plot.bar(["A","B","C"], [10, 20, 15])            # 柱状图
mf.plot.heatmap(matrix)                             # 热力图

# ----- 数据 -----
mf.write_matrix(matrix, "output.xlsx",
                row_labels=["S1","S2","S3"],
                col_labels=["C1","C2","C3"])

# ----- 数值 -----
root = mf.newton(lambda x: x**2 - 2, lambda x: 2*x, x0=1.0)

# ----- 帮助 -----
mf.help()
```

---

## API Reference

### Algorithms

| Function | Description | Returns |
|---|---|---|
| `mf.entropy_weight(m, kinds=None)` | Entropy weight method | `weights: (m,) ndarray` |
| `mf.topsis(m, kinds, weights=None)` | TOPSIS full pipeline | `closeness: (n,) ndarray` |
| `mf.ahp(A)` | AHP eigenvector weight | `(lambda_max, weights)` |
| `mf.grey_relational(m, kinds=None, rho=0.5)` | Grey relational analysis | `scores: (n,) ndarray` |
| `mf.fuzzy_eval(R, w, scores, grades)` | Fuzzy comprehensive evaluation | `dict{score, grade, vector}` |

All algorithm functions accept a `kinds` list to specify indicator types:

| kind | Meaning |
|---|---|
| `1` | Benefit (larger is better) |
| `2` | Cost (smaller is better) |
| `3` | Target (closer to best is better) |
| `4` | Interval (within range is best) |

For intermediate (kind=3) and interval (kind=4) indicators, pass `best_values` and `intervals` to `mf.topsis()` and `mf.entropy_weight()`.

#### Detailed Algorithm Examples

**Entropy Weight**

```python
# All indicators are benefit-type
m = np.array([[85, 90, 78], [76, 88, 85], [90, 82, 92]])
w = mf.entropy_weight(m)
# w = [0.44, 0.14, 0.41]

# Mixed indicator types: C2 is cost-type
w2 = mf.entropy_weight(m, kinds=[1, 2, 1])
```

**TOPSIS**

```python
# Supplier selection: Price(cost), Quality(benefit), Lead-time(cost), Service(benefit)
m = np.array([[80, 90, 3, 85], [85, 85, 5, 90], [90, 80, 2, 80]])
closeness = mf.topsis(m, kinds=[2, 1, 2, 1])
best = np.argmax(closeness) + 1  # -> 3
```

**AHP**

```python
# Pairwise comparison matrix (reciprocal)
A = np.array([
    [1,   2,   5  ],
    [1/2, 1,   3  ],
    [1/5, 1/3, 1  ],
])
lam, w = mf.ahp(A)  # lam=3.004, w=[0.58, 0.31, 0.11]
```

**Fuzzy Comprehensive Evaluation**

```python
# R: membership matrix (factors x grades)
R = np.array([[0.3, 0.4, 0.2, 0.1],
              [0.2, 0.3, 0.4, 0.1],
              [0.4, 0.3, 0.2, 0.1],
              [0.1, 0.3, 0.4, 0.2]])
w = [0.25, 0.25, 0.30, 0.20]
scores = [95, 82, 67, 50]
grades = ["Excellent", "Good", "Average", "Poor"]

result = mf.fuzzy_eval(R, w, scores, grades)
# {'score': 78.95, 'grade': 'Good', 'vector': [...]}
```

**Grey Relational Analysis**

```python
m = np.array([[80, 90], [85, 85], [90, 80]])
scores = mf.grey_relational(m, kinds=[1, 2])
best = np.argmax(scores) + 1
```

---

### Matrix Utilities

| Function | Description |
|---|---|
| `mf.positive(m, kinds)` | Convert all indicators to benefit-type |
| `mf.normalize(m)` | Vector normalize (divide by L2 norm) |
| `mf.sum_normalize(m)` | Column-sum normalize (each col sums to 1) |
| `mf.extract_x(coords)` | Extract x from `(..., 2)` array |
| `mf.extract_y(coords)` | Extract y from `(..., 2)` array |

**Indicator transformation with `positive`:**

```python
m = np.array([[80, 90, 3], [85, 85, 5], [90, 80, 2]])
# C1: benefit, C2: cost, C3: cost
converted = mf.positive(m, kinds=[1, 2, 2])

# With intermediate target:
converted = mf.positive(m, kinds=[3], best_values=[3.0])

# With interval:
converted = mf.positive(m, kinds=[4], intervals=[(3.0, 5.0)])
```

---

### Plotting (`mf.plot`)

17 chart types, all static methods on the `mf.plot` object. Call `mf.setup_cjk_font()` once before plotting with Chinese text.

| Chart | Signature | Notes |
|---|---|---|
| `line(y, x=None)` | Line plot | `x` auto-generates if omitted |
| `bar(x, h)` | Bar chart | `horizontal=True` for horizontal |
| `scatter(y, x=None)` | Scatter plot | `s` for point size |
| `pie(labels, values)` | Pie chart | `autopct="%1.1f%%"` |
| `hist(data, bins="auto")` | Histogram | `density=True` for PDF |
| `box(data, labels=None)` | Box plot | List of arrays or 2D array |
| `heatmap(m)` | Heatmap | Auto-annotates values |
| `radar(cats, values)` | Radar chart | Supports multiple series |
| `area(y, x=None)` | Area fill | With boundary line |
| `stem(y, x=None)` | Stem plot | Discrete sequence |
| `errorbar(x, y, yerr=None)` | Error bar | With `xerr` and `capsize` |
| `smooth_line(y, x=None)` | B-spline smooth | `num` controls resolution |
| `plot3d(x, y, z)` | 3D line | Spiral, parametric curves |
| `surface(X, Y, Z)` | 3D surface | Meshgrid inputs |
| `contour(X, Y, Z)` | Contour | `filled=True`/`False` |
| `animate(update, frames)` | Animation | Save to MP4/GIF |
| `subplots(r, c)` | Multi-panel | Returns `(fig, axes)` |

**Common keyword arguments (all chart methods):**

| kwarg | Type | Default | Description |
|---|---|---|---|
| `title` | `str` | None | Chart title |
| `xlabel` | `str` | None | X-axis label |
| `ylabel` | `str` | None | Y-axis label |
| `figsize` | `(w, h)` | varies | Figure size in inches |
| `color` | `str` | palette | Line/fill color |
| `ax` | `Axes` | None | Target axes (for subplots) |
| `block` | `bool` | `False` | Block until window closed |

**Figure management:**

```python
mf.plot.save("output.png")       # Save last figure
mf.plot.show()                   # Display all pending figures
mf.plot.close_all()              # Close all figure windows
```

**3D plotting:**

```python
# 3D spiral
t = np.linspace(0, 10, 200)
mf.plot.plot3d(np.sin(t), np.cos(t), t)

# 3D surface
x = np.linspace(-3, 3, 50)
y = np.linspace(-3, 3, 50)
X, Y = np.meshgrid(x, y)
Z = np.sin(np.sqrt(X**2 + Y**2))
mf.plot.surface(X, Y, Z)

# Contour
mf.plot.contour(X, Y, Z, levels=15)
```

**Animation:**

```python
import matplotlib.pyplot as plt

fig, ax = plt.subplots()
(line,) = ax.plot([], [], "o-")
ax.set_xlim(0, 10); ax.set_ylim(-1, 1)

def update(i):
    x = np.linspace(0, 10, 100)
    line.set_data(x, np.sin(x + i * 0.1))
    return [line]

mf.plot.animate(update, frames=100, interval=50,
                save_path="outputs/wave.mp4")
```

---

### Data I/O

| Function | Description |
|---|---|
| `mf.load("file.csv")` | Load CSV/Excel/Parquet from `data/raw/` |
| `mf.read_matrix()` | Interactive console matrix input |
| `mf.write_matrix(m, path, **opts)` | Write ndarray to Excel with labels |
| `mf.write_sheets(dict, path)` | Write dict of {name: ndarray/DataFrame} to multi-sheet Excel |
| `mf.print_matrix(m)` | Pretty-print matrix to console |

**Excel write with labels:**

```python
m = np.array([[1.0, 2.0], [3.0, 4.0]])

mf.write_matrix(m, "outputs/result.xlsx",
                title="TOPSIS Result",
                row_labels=["Plan A", "Plan B"],
                col_labels=["C1", "C2"])
```

**Multi-sheet Excel:**

```python
mf.write_sheets({
    "Raw Data": raw_matrix,
    "Normalized": normalized,
    "Weights": pd.DataFrame({"w": weights}),
}, "outputs/analysis.xlsx")
```

**Reading Excel matrices:**

```python
m = mf.read_matrix_excel("input.xlsx", sheet_name="Data")
```

---

### Numeric Methods

| Function | Description |
|---|---|
| `mf.newton(f, df, x0, max_iter=100, tol=1e-8)` | Newton-Raphson root finding |
| `mf.rk4_step(f, t, y, dt)` | Single RK4 integration step |
| `mf.rk4_integrate(f, y0, t_span, dt)` | Full RK4 integration over interval |

```python
# Solve dy/dt = sin(t) * y, y(0) = 1
f = lambda t, y: np.sin(t) * y
t, y = mf.rk4_integrate(f, y0=1.0, t_span=(0, 5), dt=0.01)
mf.plot.line(y, t, title="RK4 Solution")
```

---

### Timing Utilities

```python
# Context manager
with mf.timer("Model training"):
    model.run(X, y)

# Decorator
@mf.timeit
def expensive_function():
    return sum(range(10**6))

# Stopwatch for multi-stage profiling
sw = mf.Stopwatch()
sw.start()
# ... stage 1 ...
sw.lap("Data loading")
# ... stage 2 ...
sw.lap("Computation")
sw.stop()
```

---

### Base Model Class

```python
from src import Model

class MyModel(Model):
    def fit(self, X, y=None, **kwargs):
        self.coef_ = np.linalg.lstsq(X, y)[0]
        return self

    def predict(self, X):
        return X @ self.coef_

model = MyModel().run(X, y)
model.summary()
# Model: MyModel (fitted)
#   拟合耗时: 0.0012 s
```

---

## Project Structure

```
math/
|-- src/
|   |-- __init__.py              # Unified entry: import src as mf
|   |-- algorithms/              # Algorithm implementations
|   |   |-- ahp.py                   AHP
|   |   |-- entropy_weight.py        Entropy Weight
|   |   |-- topsis.py                TOPSIS
|   |   |-- fuzzy_comprehensive_evaluation.py  Fuzzy Eval
|   |   +-- grey_relational_analysis.py        Grey Relational
|   |-- models/                  # Model base class
|   |   +-- base.py
|   |-- solve/                   # Solution script templates
|   |   +-- template.py
|   |-- utils/                   # Utilities
|   |   |-- matrix.py                Matrix transforms
|   |   |-- numeric.py               Newton-Raphson, RK4
|   |   |-- plot.py                  Plotting (17 chart types)
|   |   +-- timing.py                Timer, Stopwatch, timeit
|   +-- io/                      # Data I/O
|       |-- matrix_io.py             Console matrix I/O
|       +-- data.py                  Excel/CSV/Parquet I/O
|-- scripts/
|   +-- make_appendix.py         # Code-to-docx appendix generator
|-- notebooks/                   # Jupyter demos
|-- tests/                       # Pytest suite (138 tests)
|-- data/                        # Raw and processed data
|-- outputs/                     # Generated figures and reports
+-- pyproject.toml
```

---

## Interactive Console Mode

Each algorithm module supports standalone interactive execution:

```bash
python src/algorithms/ahp.py
python src/algorithms/entropy_weight.py
python src/algorithms/topsis.py
python src/algorithms/fuzzy_comprehensive_evaluation.py
python src/algorithms/grey_relational_analysis.py
```

---

## Dependencies

```
numpy>=2.0, pandas>=2.2, matplotlib>=3.9, seaborn>=0.13,
scikit-learn>=1.5, scipy>=1.10, openpyxl>=3.0, jupyter>=1.0
```

Dev: `pytest>=8.0`, `ruff>=0.6`, `ipykernel>=6.29`

Optional (for `scripts/make_appendix.py`): `python-docx`, `pygments`

---

## Development

```bash
pip install -e ".[dev]"
pytest                          # Run all tests
pytest tests/ -q                # Quiet mode
ruff check src/ tests/          # Lint
```
