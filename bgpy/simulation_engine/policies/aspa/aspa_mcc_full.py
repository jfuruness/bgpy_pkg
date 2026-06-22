from bgpy.simulation_engine import ROVFull

from .aspa_mcc import ASPA_MCC


class ASPA_MCC_Full(ASPA_MCC, ROVFull):
    """ASPA-MCC with withdrawals ribs in and ribs out"""

    name = "ASPA-MCC Full"
