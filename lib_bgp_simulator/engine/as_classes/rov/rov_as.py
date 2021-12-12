from .rov_simple_as import ROVSimpleAS

from ..bgp import BGPAS


class ROVAS(ROVSimpleAS, BGPAS):
    __slots__ = tuple()

    name = "ROV"
