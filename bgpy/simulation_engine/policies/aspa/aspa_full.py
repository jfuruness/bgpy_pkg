from bgpy.simulation_engine.policies.rov.rov_full import ROVFull

from .aspa import ASPA


class ASPAFull(ASPA, ROVFull):
    """An Policy that deploys ASPA and has withdrawals, ribs in and out"""

    name: str = "ASPA Full"
