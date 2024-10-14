from bgpy.simulation_engine.policies.rov.rov_full import ROVFull

from .asra import ASRA


class ASRAFull(ASRA, ROVFull):
    """An Policy that deploys ASRA and has withdrawals, ribs in and out"""

    name: str = "ASRA Full"
