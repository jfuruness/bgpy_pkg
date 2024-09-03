from getpass import getuser
from platformdirs import PlatformDirs


DIRS: PlatformDirs = PlatformDirs("bgpy", getuser())
