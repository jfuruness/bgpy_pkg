from .examples import example_configs
from .internals import internal_configs

engine_test_configs = example_configs + internal_configs


__all__ = [
    "engine_test_configs",
]
