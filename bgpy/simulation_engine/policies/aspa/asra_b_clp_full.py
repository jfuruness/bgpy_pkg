from bgpy.simulation_engine.policies.rov.rov_full import ROVFull

from .asra_b_clp import ASRA_B_CLP


class ASRA_B_CLP_Full(ASRA_B_CLP, ROVFull):
    """An Policy that deploys ASRA and has withdrawals, ribs in and out"""

    name: str = "ASRA-B-CLP Full"
