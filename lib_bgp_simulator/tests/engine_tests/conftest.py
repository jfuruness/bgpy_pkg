import os
from pathlib import Path
import subprocess

import pytest


# https://stackoverflow.com/a/40673918/8903959
@pytest.fixture(scope="session", autouse=True)
def open_pdf(view):
    """Runs at the end of all tests"""

    # Setup stuff
    yield
    # Teardown stuff (open PDF for viewing)
    if view:
        # https://stackoverflow.com/q/19453338/8903959
        dir_ = Path(__file__).parent
        path = dir_ / "engine_test_outputs" / "aggregated_diagrams.pdf"
        subprocess.call(["xdg-open", str(path)])

@pytest.fixture(scope="session")
def view(pytestconfig):
    return pytestconfig.getoption("view")

# https://stackoverflow.com/a/66597438/8903959
def pytest_addoption(parser):
    parser.addoption("--view", action="store_true", default=False)
