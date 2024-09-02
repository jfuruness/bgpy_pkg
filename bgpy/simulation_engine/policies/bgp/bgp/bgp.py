from typing import TYPE_CHECKING, Any, Optional
from weakref import CallableProxyType

from bgpy.simulation_engine.ann_containers import LocalRIB, RecvQueue
from bgpy.simulation_engine.policies.policy import Policy

# Gao rexford functions
from .gao_rexford import (
    _get_best_ann_by_as_path,
    _get_best_ann_by_gao_rexford,
    _get_best_ann_by_local_pref,
    _get_best_ann_by_lowest_neighbor_asn_tiebreaker,
)

# Process incoming announcements
from .process_incoming_funcs import (
    _copy_and_process,
    _reset_q,
    _valid_ann,
    process_incoming_anns,
    receive_ann,
    seed_ann,
)

# Propagation functionality
from .propagate_funcs import (
    _policy_propagate,
    _prev_sent,
    _process_outgoing_ann,
    _propagate,
    propagate_to_customers,
    propagate_to_peers,
    propagate_to_providers,
)

if TYPE_CHECKING:
    from bgpy.as_graphs import AS


class BGP(Policy):
    name: str = "BGP"

    def __init__(
        self,
        _local_rib: LocalRIB | None = None,
        _recv_q: RecvQueue | None = None,
        as_: Optional["AS"] = None,
    ) -> None:
        """Add local rib and data structures here

        This way they can be easily cleared later without having to redo
        the graph

        This is also useful for regenerating an AS from YAML
        """

        self._local_rib = _local_rib if _local_rib else LocalRIB()
        self._recv_q = _recv_q if _recv_q else RecvQueue()
        # This gets set within the AS class so it's fine
        self.as_: CallableProxyType["AS"] = as_  # type: ignore

    # Propagation functionality
    propagate_to_providers = propagate_to_providers
    propagate_to_customers = propagate_to_customers
    propagate_to_peers = propagate_to_peers
    _propagate = _propagate
    _policy_propagate = _policy_propagate
    _process_outgoing_ann = _process_outgoing_ann
    _prev_sent = _prev_sent

    # Process incoming announcements
    seed_ann = seed_ann
    receive_ann = receive_ann
    process_incoming_anns = process_incoming_anns
    _valid_ann = _valid_ann
    _copy_and_process = _copy_and_process
    _reset_q = _reset_q

    # Gao rexford functions
    _get_best_ann_by_gao_rexford = _get_best_ann_by_gao_rexford
    _get_best_ann_by_local_pref = _get_best_ann_by_local_pref
    _get_best_ann_by_as_path = _get_best_ann_by_as_path
    _get_best_ann_by_lowest_neighbor_asn_tiebreaker = (
        _get_best_ann_by_lowest_neighbor_asn_tiebreaker
    )

    ##############
    # Yaml funcs #
    ##############

    def __to_yaml_dict__(self) -> dict[Any, Any]:
        """This optional method is called when you call yaml.dump()"""

        return {"_local_rib": self._local_rib, "_recv_q": self._recv_q}

    @classmethod
    def __from_yaml_dict__(cls, dct, yaml_tag) -> Policy:
        """This optional method is called when you call yaml.load()"""

        # We can type ignore here because we add this in the AS class
        # Only way to do it, otherwise it's a circular reference
        return cls(**dct)  # type: ignore
