import bz2
import shutil
from datetime import datetime, timedelta
from functools import cached_property
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import cast

import requests
from bs4 import BeautifulSoup as Soup

from bgpy.as_graphs.base import ASGraphCollector
from bgpy.shared.constants import bgpy_logger
from bgpy.shared.exceptions import NoCAIDAURLError


class CAIDAASGraphCollector(ASGraphCollector):
    """Downloads relationships from CAIDA and caches file"""

    def _run(self) -> Path:
        """Downloads relationships into a file

        https://publicdata.caida.org/datasets/as-relationships/serial-2/

        Can specify a download time if you want to download an older dataset
        if cache is True it uses the downloaded file that was cached
        """

        if not self.cache_path.exists():
            bgpy_logger.info("No caida graph cached. Caching...")
            # Create a temporary dir to write to
            with TemporaryDirectory() as tmp_dir:
                # Path to bz2 download
                bz2_path: Path = Path(tmp_dir) / "download.bz2"
                # Download Bz2
                self._download_bz2_file(self._get_url(self.dl_time), bz2_path)
                self._unzip_and_write_to_cache(bz2_path)
        return self.cache_path

    @cached_property
    def default_dl_time(self) -> datetime:
        """Returns default DL time.

        For most things, we download from 4 days ago
        And for collectors, time must be divisible by 4/8
        """

        # 10 days because sometimes caida takes a while to upload
        # 7 days ago was actually not enough
        dl_time: datetime = datetime.now() - timedelta(days=10)
        return dl_time.replace(hour=0, minute=0, second=0, microsecond=0)

    #################
    # Request funcs #
    #################

    def _get_url(self, dl_time: datetime) -> str:
        """Gets urls to download relationship files"""

        # Api url
        prepend: str = "http://data.caida.org/datasets/as-relationships/serial-2/"
        # Gets all URLs. Keeps only the link for the proper download time
        urls = [
            prepend + x
            for x in self._get_hrefs(prepend)
            if dl_time.strftime("%Y%m01") in x
        ]
        if len(urls) > 0:
            return str(urls[0])
        else:  # pragma: no cover
            raise NoCAIDAURLError("No Urls")

    def _get_hrefs(self, url: str) -> list[str]:
        """Returns hrefs from a tags at a given url"""

        try:
            # Query URL
            with requests.get(url, stream=True, timeout=30) as r:
                # Check for errors
                r.raise_for_status()
                # Get soup
                soup = Soup(r.text, "html.parser")
                # Extract hrefs from a tags
                rv = [
                    x.get("href") for x in soup.select("a") if x.get("href") is not None
                ]
                return cast(list[str], rv)
        except requests.exceptions.ReadTimeout as e:
            bgpy_logger.exception(f"Failed to get {url} due to {e}")
            raise

    #########################
    # File formatting funcs #
    #########################

    def _download_bz2_file(self, url: str, bz2_path: Path) -> None:
        """Downloads bz2 file from caida"""

        # https://stackoverflow.com/a/39217788/8903959
        # Download the file
        with requests.get(url, stream=True, timeout=5) as r:
            r.raise_for_status()
            with bz2_path.open("wb") as f:
                shutil.copyfileobj(r.raw, f)

    def _unzip_and_write_to_cache(self, bz2_path: Path) -> None:
        """Unzips bz2 file and writes to cache"""

        # Unzip and read
        with bz2.open(bz2_path, mode="rb") as bz2_f, self.cache_path.open("w") as txt_f:
            for line in bz2_f:
                # Must decode the bytes into strings and strip
                txt_f.write(line.decode().strip() + "\n")
