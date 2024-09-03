from datetime import date
from getpass import getuser
from pathlib import Path

from platformdirs import PlatformDirs

DIRS: PlatformDirs = PlatformDirs("bgpy", getuser())

SINGLE_DAY_CACHE_DIR: Path = Path(DIRS.user_cache_dir) / str(date.today())
SINGLE_DAY_CACHE_DIR.mkdir(exist_ok=True, parents=True)
