from bgpy.simulation_engine.policies.rov.rov_full import ROVFull

from .enforce_first_as import EnforceFirstAS


class EnforceFirstASFull(EnforceFirstAS, ROVFull):
    """An Policy that deploys EnforceFirstAS and has withdrawals, ribs in and out"""

    name: str = "Enforce-First-AS Full"
