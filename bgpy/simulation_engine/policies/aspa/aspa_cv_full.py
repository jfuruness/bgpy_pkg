from bgpy.simulation_engine import ROVFull

from .aspa_cv import ASPACV


class ASPACVFull(ASPACV, ROVFull):
    """ASPA-CV with withdrawals ribs in and ribs out"""

    name = "ASPA-CV Full"
