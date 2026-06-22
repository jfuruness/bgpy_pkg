from bgpy.simulation_engine import ROVFull

from .aspapp import ASPAPP


class ASPAPPFull(ASPAPP, ROVFull):
    """ASPA++ with withdrawals ribs in and ribs out"""

    name = "ASPA++ Full"
