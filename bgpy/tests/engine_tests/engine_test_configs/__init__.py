from .examples import example_configs
from .internals import internal_configs
from .aspapp import aspapp_configs

engine_test_configs = aspapp_configs
# example_configs + internal_configs


__all__ = [
    "engine_test_configs",
]
