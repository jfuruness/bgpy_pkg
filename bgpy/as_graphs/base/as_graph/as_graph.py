from typing import Any, Callable
from weakref import proxy

from frozendict import frozendict
from yamlable import YamlAble, yaml_info, yaml_info_decorate

import bgpy
from bgpy.as_graphs.base.as_graph_info import ASGraphInfo
from bgpy.shared.enums import ASGroups, Relationships

from .base_as import AS
from .cone_funcs import (
    _get_and_store_customer_cone_and_set_size,
    _get_and_store_provider_cone_and_set_size,
    _get_as_rank,
    _get_cone_helper,
    _get_size_of_and_store_cone,
)

# can't import into class due to mypy issue
# https://github.com/python/mypy/issues/7045
# Graph building functionality
from .graph_building_funcs import (
    _add_relationships,
    _gen_graph,
    _make_relationships_tuples,
)

# propagation rank building funcs
from .propagation_rank_funcs import (
    _assign_propagation_ranks,
    _assign_ranks_helper,
    _get_propagation_ranks,
)


@yaml_info(yaml_tag="ASGraph")
class ASGraph(YamlAble):
    """BGP Topology"""

    # Graph building functionality
    _gen_graph = _gen_graph
    _add_relationships = _add_relationships
    _make_relationships_tuples = _make_relationships_tuples

    # propagation rank building funcs
    _assign_propagation_ranks = _assign_propagation_ranks
    _assign_ranks_helper = _assign_ranks_helper
    _get_propagation_ranks = _get_propagation_ranks

    # Cone funcs
    _get_size_of_and_store_cone = _get_size_of_and_store_cone
    _get_and_store_customer_cone_and_set_size = (
        _get_and_store_customer_cone_and_set_size
    )
    _get_and_store_provider_cone_and_set_size = (
        _get_and_store_provider_cone_and_set_size
    )
    _get_and_store_provider_cone_and_set_size = (
        _get_and_store_provider_cone_and_set_size
    )
    _get_cone_helper = _get_cone_helper
    _get_as_rank = _get_as_rank

    def __init_subclass__(cls, *args, **kwargs):
        """This method essentially creates a list of all subclasses
        This is allows us to easily assign yaml tags
        """

        super().__init_subclass__(*args, **kwargs)
        # Fix this later once the system test framework is updated
        yaml_info_decorate(cls, yaml_tag=cls.__name__)

    def __init__(
        self,
        as_graph_info: "ASGraphInfo",
        BaseASCls: type[AS] = AS,
        BasePolicyCls: type[bgpy.simulation_engine.Policy] = bgpy.simulation_engine.BGP,
        store_customer_cone_size: bool = True,
        store_customer_cone_asns: bool = False,
        store_provider_cone_size: bool = False,
        store_provider_cone_asns: bool = False,
        yaml_as_dict: frozendict[int, AS] | None = None,
        yaml_ixp_asns: frozenset[int] = frozenset(),
        # Users can pass in any additional AS groups they want to keep track of
        additional_as_group_filters: frozendict[
            str, Callable[["ASGraph"], frozenset[AS]]
        ] = frozendict(),
    ):
        """Reads in relationship data from a TSV and generate graph"""

        if yaml_as_dict is not None:
            # We are coming from YAML, so init from YAML (for testing)
            self._set_yaml_attrs(yaml_as_dict, yaml_ixp_asns)
        else:
            # init as normal, through the as_graph_info
            self._set_non_yaml_attrs(
                as_graph_info,
                BaseASCls,
                BasePolicyCls,
                store_customer_cone_size,
                store_customer_cone_asns,
                store_provider_cone_size,
                store_provider_cone_asns,
            )
        # Set the AS and ASN group groups
        self._set_as_groups(additional_as_group_filters)

    def __eq__(self, other) -> bool:
        if isinstance(other, ASGraph):
            return self.__to_yaml_dict__() == other.__to_yaml_dict__()
        else:
            return NotImplemented

    ##############
    # Init funcs #
    ##############

    def _set_yaml_attrs(
        self,
        yaml_as_dict: frozendict[int, AS],
        yaml_ixp_asns: frozenset[int],
    ) -> None:
        """Generates the AS Graph from YAML"""

        self.ixp_asns: frozenset[int] = yaml_ixp_asns
        self.as_dict: frozendict[int, AS] = yaml_as_dict
        # Convert ASNs to refs
        for as_obj in self.as_dict.values():
            as_obj.as_graph = proxy(self)
            as_obj.peers = tuple([self.as_dict[asn] for asn in as_obj.peers])
            as_obj.customers = tuple([self.as_dict[asn] for asn in as_obj.customers])
            as_obj.providers = tuple([self.as_dict[asn] for asn in as_obj.providers])

        # Used for iteration
        self.ases: tuple[AS, ...] = tuple(self.as_dict.values())
        self.propagation_ranks: tuple[tuple[AS, ...], ...] = (
            self._get_propagation_ranks()
        )

    def _set_non_yaml_attrs(
        self,
        as_graph_info: ASGraphInfo,
        BaseASCls: type["AS"],
        BasePolicyCls: type["bgpy.simulation_engine.Policy"],
        store_customer_cone_size: bool,
        store_customer_cone_asns: bool,
        store_provider_cone_size: bool,
        store_provider_cone_asns: bool,
    ) -> None:
        """Generates the AS graph normally (not from YAML)"""

        assert as_graph_info.ixp_asns is not None
        self.ixp_asns = as_graph_info.ixp_asns
        # Probably there is a better way to do this, but for now we
        # store this as a dict then later make frozendict, thus the type ignore
        self.as_dict: frozendict[int, AS] = dict()  # type: ignore
        # Just adds all ASes to the dict, and adds ixp/input_clique info
        self._gen_graph(
            as_graph_info,
            BaseASCls,
            BasePolicyCls,
        )
        # Can't allow modification of the AS dict since other things like
        # as group filters will be broken then
        self.as_dict = frozendict(self.as_dict)
        # Adds references to all relationships
        self._add_relationships(as_graph_info)
        # Used for iteration
        self.ases = tuple(self.as_dict.values())
        # Remove duplicates from relationships and sort
        self._make_relationships_tuples()
        # Assign propagation rank to each AS
        self._assign_propagation_ranks()
        # Get the ranks for the graph
        self.propagation_ranks = self._get_propagation_ranks()
        # We don't run this every time since it has the runtime greater than the
        # entire graph generation
        if any([store_customer_cone_size, store_customer_cone_asns]):
            # Determine customer cones of all ases
            self._get_size_of_and_store_cone(
                rel_attr=Relationships.CUSTOMERS.name.lower(),
                store_cone_asns=store_customer_cone_asns,
            )
            self._get_as_rank()

        if any([store_provider_cone_size, store_provider_cone_asns]):
            self._get_size_of_and_store_cone(
                rel_attr=Relationships.PROVIDERS.name.lower(),
                store_cone_asns=store_provider_cone_asns,
            )

    def _set_as_groups(
        self,
        additional_as_group_filters: (
            frozendict[str, Callable[["ASGraph"], frozenset[AS]]] | None
        ),
    ) -> None:
        """Sets the AS Groups"""

        as_group_filters: dict[str, Callable[[ASGraph], frozenset[AS]]] = dict(
            self._default_as_group_filters
        )

        if additional_as_group_filters:
            as_group_filters.update(additional_as_group_filters)

        self.as_group_filters: frozendict[str, Callable[[ASGraph], frozenset[AS]]] = (
            frozendict(as_group_filters)
        )

        # Some helpful sets of ases for faster loops
        as_groups: dict[str, frozenset[AS]] = dict()
        asn_groups: dict[str, frozenset[int]] = dict()

        for as_group_key, filter_func in self.as_group_filters.items():
            as_groups[as_group_key] = filter_func(self)
            asn_groups[as_group_key] = frozenset(x.asn for x in filter_func(self))

        # Turn these into frozen dicts. They shouldn't be modified
        self.as_groups: frozendict[str, frozenset[AS]] = frozendict(as_groups)
        self.asn_groups: frozendict[str, frozenset[int]] = frozendict(asn_groups)

    @property
    def _default_as_group_filters(
        self,
    ) -> frozendict[str, Callable[["ASGraph"], frozenset[AS]]]:
        """Returns the default filter functions for AS groups"""

        def ixp_filter(as_graph: "ASGraph") -> frozenset[AS]:
            return frozenset(x for x in as_graph if x.ixp)

        def stub_no_ixp_filter(as_graph: "ASGraph") -> frozenset[AS]:
            return frozenset(x for x in as_graph if x.stub and not x.ixp)

        def multihomed_no_ixp_filter(as_graph: "ASGraph") -> frozenset[AS]:
            return frozenset(x for x in as_graph if x.multihomed and not x.ixp)

        def stubs_or_multihomed_no_ixp_filter(as_graph: "ASGraph") -> frozenset[AS]:
            return frozenset(
                x for x in as_graph if (x.stub or x.multihomed) and not x.ixp
            )

        def input_clique_no_ixp_filter(as_graph: "ASGraph") -> frozenset[AS]:
            return frozenset(x for x in as_graph if x.input_clique and not x.ixp)

        def etc_no_ixp_filter(as_graph: "ASGraph") -> frozenset[AS]:
            return frozenset(
                x
                for x in as_graph
                if not (x.stub or x.multihomed or x.input_clique or x.ixp)
            )

        def transit_no_ixp_filter(as_graph: "ASGraph") -> frozenset[AS]:
            return frozenset(x for x in as_graph if x.transit and not x.ixp)

        def all_no_ixp_filter(as_graph: "ASGraph") -> frozenset[AS]:
            return frozenset(list(as_graph))

        return frozendict(
            {
                ASGroups.IXPS.value: ixp_filter,
                ASGroups.STUBS.value: stub_no_ixp_filter,
                ASGroups.MULTIHOMED.value: multihomed_no_ixp_filter,
                ASGroups.STUBS_OR_MH.value: stubs_or_multihomed_no_ixp_filter,
                ASGroups.INPUT_CLIQUE.value: input_clique_no_ixp_filter,
                ASGroups.ETC.value: etc_no_ixp_filter,
                ASGroups.TRANSIT.value: transit_no_ixp_filter,
                ASGroups.ALL_WOUT_IXPS.value: all_no_ixp_filter,
            }
        )

    ##############
    # Yaml funcs #
    ##############

    def __to_yaml_dict__(self) -> dict[str, Any]:
        """Optional method called when yaml.dump is called"""

        return {
            "as_dict": dict(self.as_dict.items()),
            "ixp_asns": list(self.ixp_asns),
        }

    @classmethod
    def __from_yaml_dict__(cls, dct, yaml_tag) -> Any:
        """Optional method called when yaml.load is called"""

        return cls(
            ASGraphInfo(),
            yaml_as_dict=frozendict(dct["as_dict"]),
            yaml_ixp_asns=frozenset(dct["ixp_asns"]),
        )

    ##################
    # Iterator funcs #
    ##################

    # https://stackoverflow.com/a/7542261/8903959
    def __getitem__(self, index: int) -> AS:
        return self.ases[index]

    def __len__(self) -> int:
        return len(self.as_dict)
