from pathlib import Path
import subprocess

import pytest

from bgpy.caida_collector import CaidaCollector

from .engine_tests import DiagramAggregator


DIAGRAM_PATH = Path(__file__).parent / "engine_tests" / "engine_test_outputs"


# https://github.com/pytest-dev/pytest-xdist/issues/783
def pytest_configure(config):
    """Caches the caida collector before parallelization"""

    # Prevent workers from running the same code
    if not hasattr(config, "workerinput"):
        # Caches CAIDA downloaded file only once before tests run
        CaidaCollector().run(tsv_path=None)


def pytest_sessionfinish(session, exitstatus):
    """Runs when all tests are done, once per session, even with xdist

    https://github.com/pytest-dev/pytest-xdist/issues/271#issuecomment-826396320  # noqa
    """

    # Only run in master thread after all other threads/tests have finished
    # Also runs when xdist isn't running
    if not hasattr(session.config, "workerinput"):
        DiagramAggregator(DIAGRAM_PATH).aggregate_diagrams()
        # Teardown stuff (open PDF for viewing)
        if session.config.getoption("view"):
            # https://stackoverflow.com/q/19453338/8903959
            agg_path = DiagramAggregator(DIAGRAM_PATH).aggregated_diagrams_path
            subprocess.call(["xdg-open", str(agg_path)])


@pytest.fixture(scope="session")
def overwrite(pytestconfig):
    return pytestconfig.getoption("overwrite")


# https://stackoverflow.com/a/66597438/8903959
def pytest_addoption(parser):
    # View test PDF when complete
    parser.addoption("--view", action="store_true", default=False)
    # Overwrite ground truth
    parser.addoption("--overwrite", action="store_true", default=False)
