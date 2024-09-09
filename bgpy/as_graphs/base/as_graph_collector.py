import shutil
from abc import ABC, abstractmethod
from datetime import datetime
from functools import cached_property
from pathlib import Path

from bgpy.shared.constants import SINGLE_DAY_CACHE_DIR, bgpy_logger


class ASGraphCollector(ABC):
    def __init__(
        self,
        dl_time: datetime | None = None,
        cache_dir: Path = SINGLE_DAY_CACHE_DIR,
    ) -> None:
        """Stores download time and cache_dir instance vars and creates dir"""

        self.dl_time: datetime = dl_time if dl_time else self.default_dl_time

        self.cache_dir: Path = cache_dir
        # Make cache dir if cache is being used
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def run(self) -> Path:
        """Runs run func and deletes cache if anything is amiss"""

        try:
            return self._run()
        except Exception as e:
            bgpy_logger.exception(
                f"Error {e}, deleting cached as graph file at {self.cache_path}"
            )
            # Make sure no matter what don't create a messed up cache
            shutil.rmtree(self.cache_path)
            raise

    @cached_property
    def cache_path(self) -> Path:
        """Path to the cache file for that day"""

        fmt = f"{self.__class__.__name__}_%Y.%m.%d.txt"
        return self.cache_dir / self.dl_time.strftime(fmt)

    ####################
    # Abstract methods #
    ####################

    @abstractmethod
    def _run(self) -> Path:
        """Download file and caches it, returning path to the file"""
        raise NotImplementedError

    @cached_property
    @abstractmethod
    def default_dl_time(self) -> datetime:
        """Returns the default download time"""
        raise NotImplementedError
