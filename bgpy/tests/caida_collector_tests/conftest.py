from datetime import datetime
import os
from pathlib import Path
from shutil import copyfile
from typing import Any, Generator
from unittest.mock import patch

import pytest

from bgpy.caida_collector import CaidaCollector

# https://stackoverflow.com/a/12233889/8903959
_file_path: str = os.path.abspath(__file__)
_example_dir: Path = Path(_file_path.replace("conftest.py", "examples"))
_dl_time: datetime = datetime(2021, 9, 20)
_html_path: Path = _example_dir / "serial_2.html"
_bz2_path: Path = _example_dir / "20210901.as-rel2.txt.bz2"
_decoded_path: Path = _example_dir / "20210901.as-rel2.decoded"


@pytest.fixture(scope="function")
def html_path() -> Path:
    return _html_path


@pytest.fixture(scope="function")
def bz2_path() -> Path:
    return _bz2_path


@pytest.fixture(scope="function")
def decoded_path() -> Path:
    return _decoded_path


@pytest.fixture()
def tsv_path(tmp_path) -> Path:
    return tmp_path / "test.tsv"  # type: ignore


# https://stackoverflow.com/a/28507806/8903959
# This method will be used by the mock to replace requests.get
def mocked_requests_get(*args, **kwargs):
    class MockResponse:
        def __init__(self):
            with open(_html_path, mode="r") as f:
                self.text: str = f.read()
            self.status_code: int = 200

        def __enter__(self, *args):
            return self

        def __exit__(self, *args):
            return True

        def raise_for_status(*args, **kwargs):
            pass

        def close(*args, **kwargs):
            pass

    return MockResponse()


def mocked_download_file(self, url: str, path: str):
    copyfile(str(_bz2_path), path)


@pytest.fixture(scope="function")
def run_kwargs(tmp_path: Path) -> Generator[dict[str, Any], dict[str, Any], None]:
    """Returns run kwargs for caida collector"""

    yield {
        "dl_time": _dl_time,
        "cache_dir": tmp_path,
        "tsv_path": tmp_path / "test.txt",
    }


@pytest.fixture(scope="function")
def mock_caida_collector():
    """Returns a CaidaCollector obj that has custom input files

    Clears cache and tsv before yielding"""

    with patch(
        ("bgpy.caida_collector.caida_collector." "html_funcs.requests.get"),
        mocked_requests_get,
    ):
        with patch(
            (
                "bgpy.caida_collector.caida_collector."
                "CaidaCollector._download_bz2_file"
            ),
            mocked_download_file,
        ):
            yield CaidaCollector()


@pytest.fixture(scope="function")
def caida_collector():
    """Returns a CaidaCollector obj that has custom input files

    Clears cache and tsv before yielding"""

    return CaidaCollector()
