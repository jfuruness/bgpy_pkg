from typing import Any

import pytest

from bgpy.caida_collector import CaidaCollector

COLLECTOR_AND_KWARGS = tuple[CaidaCollector, dict[str, Any]]


@pytest.mark.read_file_funcs
class TestReadFileFuncs:
    @pytest.mark.skip(reason="Will come back to it later")
    def test_read_file(self, cache_path, dl_time):
        """Tests reading a file with all possible parameters"""

        raise NotImplementedError

    @pytest.mark.skip(reason="Will come back to it later")
    def test_read_from_cache(self, cache_path):
        """Tests that reading from the cache

        Should result in the same format as reading from raw
        """

        raise NotImplementedError

    @pytest.mark.skip(reason="Will come back to it later")
    def test_read_from_caida(self):
        """Tests reading file from caida

        Both mock and not mocked
        """

        raise NotImplementedError

    @pytest.mark.skip(reason="Will come back to it later")
    def test_download_bz2_file(self):
        """Tests that you can download the bz2 file from Caida"""

        raise NotImplementedError

    @pytest.mark.skip(reason="Will come back to it later")
    def test_copy_to_cache(self):
        """Tests that you can copy to cache correctly"""

        raise NotImplementedError
