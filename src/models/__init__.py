"""数学建模模块。"""

try:
    from src.models.base import Model, evaluate_model
except ImportError:
    pass

from src.models.model import model

