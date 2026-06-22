from bgpy.simulation_engine import ROVFull

from .aspa_mpc import ASPA_MPC


class ASPA_MPC_Full(ASPA_MPC, ROVFull):
    """ASPA-MPC with withdrawals ribs in and ribs out"""

    name = "ASPA-MPC Full"
