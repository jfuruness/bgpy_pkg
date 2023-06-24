import logging
from pathlib import Path
from typing import Any, Optional

from yamlable import yaml_info, YamlAble, yaml_info_decorate

from .base_as import AS

from bgp_simulator_pkg.caida_collector.links import CustomerProviderLink as CPLink
from bgp_simulator_pkg.caida_collector.links import PeerLink


# can't import into class due to mypy issue
# https://github.com/python/mypy/issues/7045
# Graph building functionality
from .graph_building_funcs import _gen_graph
from .graph_building_funcs import _add_relationships
from .graph_building_funcs import _make_relationships_tuples
from .graph_building_funcs import _add_extra_csv_info

# propagation rank building funcs
from .propagation_rank_funcs import _assign_propagation_ranks
from .propagation_rank_funcs import _assign_ranks_helper
from .propagation_rank_funcs import _get_propagation_ranks

# Customer cone funcs
from .customer_cone_funcs import _get_customer_cone_size
from .customer_cone_funcs import _get_cone_size_helper


@yaml_info(yaml_tag="BGPDAG")
class BGPDAG(YamlAble):
    """BGP Topology from caida which is a DAG"""

    # Graph building functionality
    _gen_graph = _gen_graph
    _add_relationships = _add_relationships
    _make_relationships_tuples = _make_relationships_tuples
    _add_extra_csv_info = _add_extra_csv_info

    # propagation rank building funcs
    _assign_propagation_ranks = _assign_propagation_ranks
    _assign_ranks_helper = _assign_ranks_helper
    _get_propagation_ranks = _get_propagation_ranks

    # Customer cone funcs
    _get_customer_cone_size = _get_customer_cone_size
    _get_cone_size_helper = _get_cone_size_helper

    def __init_subclass__(cls, *args, **kwargs):
        """This method essentially creates a list of all subclasses
        This is allows us to easily assign yaml tags
        """

        super().__init_subclass__(*args, **kwargs)
        # Fix this later once the system test framework is updated
        yaml_info_decorate(cls, yaml_tag=cls.__name__)

    def __init__(
        self,
        cp_links: set[CPLink],
        peer_links: set[PeerLink],
        ixps: Optional[set[int]] = None,
        input_clique: Optional[set[int]] = None,
        BaseASCls: type[AS] = AS,
        yaml_as_dict: Optional[dict[int, AS]] = None,
        csv_path: Path = (Path(__file__).parent.parent / "combined.csv"),
    ):
        """Reads in relationship data from a TSV and generate graph"""

        if yaml_as_dict is not None:
            self.as_dict: dict[int, AS] = yaml_as_dict
            # Convert ASNs to refs
            for as_obj in self.as_dict.values():
                as_obj.peers = tuple([self.as_dict[asn] for asn in as_obj.peers])
                as_obj.customers = tuple(
                    [self.as_dict[asn] for asn in as_obj.customers]
                )
                as_obj.providers = tuple(
                    [self.as_dict[asn] for asn in as_obj.providers]
                )

            # Used for iteration
            self.ases: tuple[AS, ...] = tuple(self.as_dict.values())
            self.propagation_ranks: tuple[
                tuple[AS, ...], ...
            ] = self._get_propagation_ranks()

        else:
            self.as_dict: dict[int, AS] = dict()  # type: ignore
            logging.debug("gen graph")
            # Just adds all ASes to the dict, and adds ixp/input_clique info
            self._gen_graph(
                cp_links,
                peer_links,
                ixps if ixps else set(),
                input_clique if input_clique else set(),
                BaseASCls,
            )
            logging.debug("gen graph done")
            # Adds references to all relationships
            self._add_relationships(cp_links, peer_links)
            # Used for iteration
            self.ases: tuple[AS, ...] = tuple(self.as_dict.values())  # type: ignore
            logging.debug("add rels done")
            # Remove duplicates from relationships and sort
            self._make_relationships_tuples()
            logging.debug("typles done")
            # Assign propagation rank to each AS
            self._assign_propagation_ranks()
            logging.debug("assigned prop ranks")
            # Get the ranks for the graph
            self.propagation_ranks = self._get_propagation_ranks()
            logging.debug("got prop ranks")
            # Determine customer cones of all ases
            self._get_customer_cone_size()
            logging.debug("Customer cones complete")
            self._add_extra_csv_info(csv_path)

        # Some helpful sets of asns
        self.stub_ases = set([x for x in self if x.stub])
        self.mh_ases = set([x for x in self if x.multihomed])
        self.stub_or_mh_ases = set(self.stub_ases | self.mh_ases)
        self.input_clique_ases = set([x for x in self if x.input_clique])
        self.etc_ases = set(
            [x for x in self if not (x.stub or x.multihomed or x.input_clique)]
        )
        # Backwards compatibility
        self.stub_asns = set([x.asn for x in self if x.stub])
        self.mh_asns = set([x.asn for x in self if x.multihomed])
        self.stub_or_mh_asns = set(self.stub_asns | self.mh_asns)
        self.input_clique_asns = set([x.asn for x in self if x.input_clique])
        self.etc_asns = set(
            [x.asn for x in self if not (x.stub or x.multihomed or x.input_clique)]
        )

    ##############
    # Yaml funcs #
    ##############

    def __to_yaml_dict__(self) -> dict[int, AS]:  # type: ignore
        """Optional method called when yaml.dump is called"""

        return {asn: as_obj for asn, as_obj in self.as_dict.items()}

    @classmethod
    def __from_yaml_dict__(cls, dct, yaml_tag) -> Any:
        """Optional method called when yaml.load is called"""

        return cls(set(), set(), yaml_as_dict=dct)

    ##################
    # Iterator funcs #
    ##################

    # https://stackoverflow.com/a/7542261/8903959
    def __getitem__(self, index) -> AS:
        return self.ases[index]  # type: ignore

    def __len__(self) -> int:
        return len(self.as_dict)
