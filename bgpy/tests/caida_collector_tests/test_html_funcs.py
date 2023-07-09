from datetime import date
from typing import Any

import pytest

from bgpy.caida_collector import CaidaCollector


@pytest.mark.html_funcs
class TestHTMLFuncs:
    """Tests funcs related to html"""

    def test_get_url(
        self,
        caida_collector: CaidaCollector,
        mock_caida_collector: CaidaCollector,
        run_kwargs: dict[str, Any],
    ):
        """Tests that the URL collected from Caida is accurate

        Get an example html and ensure that the URL is what we expect
        """

        test_url: str = (
            "http://data.caida.org/datasets/as-relationships/"
            "serial-2/20210901.as-rel2.txt.bz2"
        )

        dl_time = run_kwargs["dl_time"]

        # This is from the test html file
        assert mock_caida_collector._get_url(dl_time) == test_url
        # This is from their website. Just to make sure their website
        # format hasn't changed
        dl_time = date.today().replace(day=1)
        dl_time.replace(month=dl_time.month - 1)
        caida_collector._get_url(dl_time)
