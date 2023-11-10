from .rov_simple_policy import ROVSimplePolicy


class RealROVSimplePolicy(ROVSimplePolicy):
    """An Policy that deploys ROV in real life"""

    name: str = "RealROVSimple"
