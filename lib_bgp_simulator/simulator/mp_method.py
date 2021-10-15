from enum import Enum


class MPMethod(Enum):
    SINGLE_PROCESS = 0
    MP = 1
    RAY = 2
