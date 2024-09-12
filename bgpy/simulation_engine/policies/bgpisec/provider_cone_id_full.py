from bgpy.simulation_engine.policies.rov.rov_full import ROVFull

from .provider_cone_id import ProviderConeID


class ProviderConeIDFull(ProviderConeID, ROVFull):
    """ProviderConeID with withdrawals, ribs in and out"""

    name = "ProviderConeID Full"
