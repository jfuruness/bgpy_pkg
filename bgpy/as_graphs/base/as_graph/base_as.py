from functools import cached_property
from typing import TYPE_CHECKING, Any, Optional
from weakref import CallableProxyType, proxy

from yamlable import YamlAble, yaml_info

if TYPE_CHECKING:
    from bgpy.simulation_engine import Policy

    from .as_graph import ASGraph


@yaml_info(yaml_tag="AS")
class AS(YamlAble):
    """Autonomous System class. Contains attributes of an AS"""

    def __init__(
        self,
        *,
        asn: int,
        input_clique: bool = False,
        ixp: bool = False,
        peer_asns: frozenset[int] = frozenset(),
        provider_asns: frozenset[int] = frozenset(),
        customer_asns: frozenset[int] = frozenset(),
        peers: tuple["AS", ...] = tuple(),
        providers: tuple["AS", ...] = tuple(),
        customers: tuple["AS", ...] = tuple(),
        customer_cone_asns: frozenset[int] | None = None,
        customer_cone_size: int | None = None,
        provider_cone_asns: frozenset[int] | None = None,
        provider_cone_size: int | None = None,
        as_rank: int | None = None,
        propagation_rank: int | None = None,
        policy: Optional["Policy"] = None,
        as_graph: Optional["ASGraph"] = None,
    ) -> None:
        # Make sure you're not accidentally passing in a string here
        self.asn: int = int(asn)

        self.peer_asns: frozenset[int] = peer_asns
        self.provider_asns: frozenset[int] = provider_asns
        self.customer_asns: frozenset[int] = customer_asns

        self.peers: tuple[AS, ...] = peers
        self.providers: tuple[AS, ...] = providers
        self.customers: tuple[AS, ...] = customers

        # Read Caida's paper to understand these
        self.input_clique: bool = input_clique
        self.ixp: bool = ixp
        self.customer_cone_asns: frozenset[int] | None = customer_cone_asns
        self.customer_cone_size: int | None = customer_cone_size
        self.provider_cone_asns: frozenset[int] | None = provider_cone_asns
        self.provider_cone_size: int | None = provider_cone_size
        self.as_rank: int | None = as_rank
        # Propagation rank. Rank leaves to clique
        self.propagation_rank: int | None = propagation_rank

        # Hash in advance and only once since this gets called a lot
        self.hashed_asn = hash(self.asn)

        assert policy, "This should never be None"
        self.policy: Policy = policy
        self.policy.as_ = proxy(self)

        # # This is useful for some policies to have knowledge of the graph
        if as_graph is not None:
            self.as_graph: CallableProxyType[ASGraph] = proxy(as_graph)
        else:
            # Ignoring this because it gets set properly immediatly
            self.as_graph = None  # type: ignore

    def __lt__(self, as_obj: Any) -> bool:
        if isinstance(as_obj, AS):
            return self.asn < as_obj.asn
        else:
            return NotImplemented

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, AS):
            return self.__to_yaml_dict__() == other.__to_yaml_dict__()
        else:
            return NotImplemented

    def __hash__(self) -> int:
        return self.hashed_asn

    @property
    def db_row(self) -> dict[str, str]:
        def asns(as_objs: tuple["AS", ...]) -> str:
            return "{" + ",".join(str(x.asn) for x in sorted(as_objs)) + "}"

        def frozenset_asns(asns: frozenset[int]) -> str:
            return "{" + ",".join(str(asn) for asn in sorted(asns)) + "}"

        def _format(x: Any) -> str:
            if (isinstance(x, (list, tuple))) and all(isinstance(y, AS) for y in x):
                assert not isinstance(x, list), "these should all be tuples"
                return asns(x)
            elif x is None:
                return ""
            elif any(isinstance(x, my_type) for my_type in (str, int, float)):
                return str(x)
            elif isinstance(x, frozenset):
                return frozenset_asns(x)
            else:
                raise ValueError(f"improper format type: {type(x)} {x}")

        return {attr: _format(getattr(self, attr)) for attr in self.db_row_keys}

    @cached_property
    def db_row_keys(self) -> tuple[str, ...]:
        return (
            "asn",
            "peers",
            "customers",
            "providers",
            "input_clique",
            "ixp",
            "customer_cone_asns",
            "customer_cone_size",
            "provider_cone_asns",
            "provider_cone_size",
            "as_rank",
            "propagation_rank",
            # Don't forget the properties
            *("stubs", "stub", "multihomed", "transit"),
        )

    def __str__(self):
        return "\n".join(str(x) for x in self.db_row.items())

    @cached_property
    def stub(self) -> bool:
        """Returns True if AS is a stub by RFC1772"""

        return len(self.neighbors) == 1

    @cached_property
    def multihomed(self) -> bool:
        """Returns True if AS is multihomed by RFC1772"""

        return len(self.customers) == 0 and len(self.peers) + len(self.providers) > 1

    @cached_property
    def transit(self) -> bool:
        """Returns True if AS is a transit AS by RFC1772"""

        return (
            len(self.customers) > 0
            and len(self.customers) + len(self.peers) + len(self.providers) > 1
        )

    @cached_property
    def stubs(self) -> tuple["AS", ...]:
        """Returns a list of any stubs connected to that AS"""

        return tuple([x for x in self.customers if x.stub])

    @cached_property
    def neighbors(self) -> tuple["AS", ...]:
        """Returns customers + peers + providers"""

        return self.customers + self.peers + self.providers

    @cached_property
    def neighbor_asns(self) -> frozenset[int]:
        """Returns neighboring ASNs (useful for ASRA)"""

        return frozenset([x.asn for x in self.neighbors])

    ##############
    # Yaml funcs #
    ##############

    def __to_yaml_dict__(self) -> dict[str, Any]:
        """This optional method is called when you call yaml.dump()"""

        return {
            "asn": self.asn,
            "customers": tuple([x.asn for x in self.customers]),
            "peers": tuple([x.asn for x in self.peers]),
            "providers": tuple([x.asn for x in self.providers]),
            "input_clique": self.input_clique,
            "ixp": self.ixp,
            "customer_cone_asns": self.customer_cone_asns,
            "customer_cone_size": self.customer_cone_size,
            "provider_cone_asns": self.provider_cone_asns,
            "provider_cone_size": self.provider_cone_size,
            "as_rank": self.as_rank,
            "propagation_rank": self.propagation_rank,
            "policy": self.policy,
        }

    @classmethod
    def __from_yaml_dict__(cls, dct: dict[Any, Any], yaml_tag: str = ""):
        """This optional method is called when you call yaml.load()"""

        dct["customer_asns"] = frozenset(dct["customers"])
        dct["peer_asns"] = frozenset(dct["peers"])
        dct["provider_asns"] = frozenset(dct["providers"])
        if dct["customer_cone_asns"] is not None:
            dct["customer_cone_asns"] = frozenset(dct["customer_cone_asns"])
        if dct["provider_cone_asns"] is not None:
            dct["provider_cone_asns"] = frozenset(dct["provider_cone_asns"])
        return cls(**dct)


# Needed for mypy type hinting
__all__ = ["AS"]
