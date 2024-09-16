from bgpy.simulation_engine.policies.rov import ROVFull

from .rovpp_v2_improved_lite import ROVPPV2ImprovedLite


class ROVPPV2ImprovedLiteFull(ROVPPV2ImprovedLite, ROVFull):
    """Full version of ROVPPV2ImprovedLite"""

    name: str = "ROV++V2i Lite Full"
