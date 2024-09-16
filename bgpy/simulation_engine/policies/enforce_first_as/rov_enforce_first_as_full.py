from bgpy.simulation_engine.policies.rov.rov_full import ROVFull

from .rov_enforce_first_as import ROVEnforceFirstAS


class ROVEnforceFirstASFull(ROVEnforceFirstAS, ROVFull):
    """An Policy that deploys EnforceFirstAS+ROV and has withdrawals, ribs in and out"""

    name: str = "ROV + Enforce-First-AS Full"
