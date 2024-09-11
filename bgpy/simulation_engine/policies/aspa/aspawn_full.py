from bgpy.simulation_engine.policies.rov.rov_full import ROVFull

from .aspawn import ASPAwN


class ASPAwNFull(ASPAwN, ROVFull):
    """An Policy that deploys ASPA and has withdrawals, ribs in and out"""

    name: str = "ASPAwN Full"
