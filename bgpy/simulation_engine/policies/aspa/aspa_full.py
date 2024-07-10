from .aspa import ASPA

from bgpy.simulation_engine.policies.rov.rov_full import ROVFull


class ASPAFull(ASPA, ROVFull):
    """An Policy that deploys ASPA and has withdrawals, ribs in and out"""

    name: str = "ASPA Full"
