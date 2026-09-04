from dataclasses import dataclass


@dataclass(frozen=True)
class ASPARecord:
    """An AS's published ASPA: the providers it authorizes"""

    asn: int
    provider_asns: frozenset[int] = frozenset()


@dataclass(frozen=True)
class ASPAPPRecord:
    """
    An AS's published ASPA++ records

    max_provider_path is the longest customer -> provider chain above the AS,
    max_customer_path the longest provider -> customer chain below it the AS
    """

    asn: int
    max_provider_path: int | None = None
    max_customer_path: int | None = None


@dataclass(frozen=True)
class ASRARecord:
    """Base class for a published ASRA record."""

    asn: int


@dataclass(frozen=True)
class ASRACRecord(ASRARecord):
    """ASRA-C: the AS's customers"""

    customer_asns: frozenset[int] = frozenset()


@dataclass(frozen=True)
class ASRALPRecord(ASRARecord):
    """ASRA-LP: the AS's lateral peers"""

    peer_asns: frozenset[int] = frozenset()


@dataclass(frozen=True)
class ASRACLPRecord(ASRARecord):
    """ASRA-CLP: customers and lateral peers"""

    customer_and_peer_asns: frozenset[int] = frozenset()
