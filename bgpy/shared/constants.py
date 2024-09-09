import logging
from datetime import date
from pathlib import Path

from platformdirs import PlatformDirs, PlatformDirsABC

# NOTE: Can't use getpass here due to windows bug (https://bugs.python.org/issue32731)
DIRS: PlatformDirsABC = PlatformDirs("bgpy", Path.home().name)

SINGLE_DAY_CACHE_DIR: Path = Path(DIRS.user_cache_dir) / str(date.today())
SINGLE_DAY_CACHE_DIR.mkdir(exist_ok=True, parents=True)

bgpy_logger = logging.getLogger("bgpy")
bgpy_logger.setLevel(logging.INFO)
