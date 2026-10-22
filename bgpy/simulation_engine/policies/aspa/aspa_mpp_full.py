from bgpy.simulation_engine import ROVFull

from .aspa_mpc import ASPA_MPP


class ASPA_MPP_Full(ASPA_MPP, ROVFull):
    """ASPA-MPP with withdrawals ribs in and ribs out"""

    name = "ASPA-MPP Full"
