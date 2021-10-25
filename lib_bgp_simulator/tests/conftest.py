import pytest

class PytestOptions:
    pass

def pytest_addoption(parser):
    parser.addoption("--write_no_verify", action="store_true", default=False)
    parser.addoption("--view", action="store_true", default=False)

# Only way to access this outside of test funcs that I could find
# https://stackoverflow.com/a/66597438/8903959
def pytest_configure(config):
    global PytestOptions
    for opt in ["write_no_verify", "view"]:
        setattr(PytestOptions, opt, config.getoption(f"--{opt}"))
