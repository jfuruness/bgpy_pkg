from datetime import datetime
import logging
import os
from pathlib import Path
import shutil
from tempfile import TemporaryDirectory
from typing import Optional

import bz2
import requests


# type for lines that are read from caida/cached files
LINES_TYPE = tuple[str, ...]


def read_file(self, cache_path: Optional[Path], dl_time: datetime) -> LINES_TYPE:
    """Reads the file from the URL and unzips it and returns the lines

    Also caches the file for later calls
    """

    # If cache exists
    if cache_path and cache_path.exists():
        lines: LINES_TYPE = self._read_from_cache(cache_path)
    else:
        # Write the raw file
        lines: LINES_TYPE = self._read_from_caida(dl_time)  # type: ignore
        # Copies to cache if cache_path is set
        self._copy_to_cache(cache_path, lines)

    return lines


def _read_from_cache(self, cache_path: Path) -> LINES_TYPE:
    """Reads from the cache"""

    # Open cache
    with cache_path.open(mode="r") as f:
        # Read cached file
        return tuple([x.strip() for x in f])


def _read_from_caida(self, dl_time: datetime) -> LINES_TYPE:
    """Reads Caida file"""

    logging.info("No file cached from Caida. Downloading Caida file now")

    # Create a temporary dir to write to
    with TemporaryDirectory() as tmp_dir:
        # Path to bz2 download
        bz2_path: str = os.path.join(tmp_dir, "download.bz2")
        # Download Bz2
        self._download_bz2_file(self._get_url(dl_time), bz2_path)

        # Unzip and read
        with bz2.open(bz2_path, mode="rb") as f:
            # Must decode the bytes into strings and strip
            return tuple([x.decode().strip() for x in f])


def _download_bz2_file(self, url: str, bz2_path: str):
    """Downloads Caida BZ2 file"""

    # https://stackoverflow.com/a/39217788/8903959
    # Download the file
    with requests.get(url, stream=True, timeout=5) as r:
        r.raise_for_status()  # type: ignore
        with open(bz2_path, mode="wb") as f:
            shutil.copyfileobj(r.raw, f)  # type: ignore


def _copy_to_cache(self, cache_path: Optional[Path], lines: LINES_TYPE):
    """Copies file to the cache"""

    if cache_path:
        # Copy raw file to cache
        with cache_path.open(mode="w") as f:
            f.write("\n".join(lines))
