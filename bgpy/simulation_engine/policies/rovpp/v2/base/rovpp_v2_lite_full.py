from bgpy.simulation_engine.policies.rov import ROVFull

from .rovpp_v2_lite import ROVPPV2Lite


class ROVPPV2LiteFull(ROVPPV2Lite, ROVFull):
    """An Policy that deploys ROV++V2 Lite as defined in the ROV++ paper, and
    has withdrawals, ribs in and out

    ROV++ Improved Deployable Defense against BGP Hijacking
    """

    name: str = "ROV++V2 Lite Full"
