from typing import TYPE_CHECKING, Any, Optional
from warnings import warn

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
    from weakref import CallableProxyType

    from bgpy.as_graphs import AS


class BGP(Policy):
    name: str = "BGP"

    def __init__(
        self,
        local_rib: LocalRIB | None = None,
        recv_q: RecvQueue | None = None,
        as_: Optional["AS"] = None,
    ) -> None:
        """Add local rib and data structures here

        This way they can be easily cleared later without having to redo
        the graph

        This is also useful for regenerating an AS from YAML
        """

        self.local_rib = local_rib if local_rib else LocalRIB()
        self.recv_q = recv_q if recv_q else RecvQueue()
        # This gets set within the AS class so it's fine
        self.as_: CallableProxyType[AS] = as_  # type: ignore

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

    @property
    def _local_rib(self) -> LocalRIB:
        warn(
            "Please use .local_rib instead of ._local_rib. "
            "This will be removed in a later version",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.local_rib

    @property
    def _recv_q(self) -> RecvQueue:
        warn(
            "Please use .recv_q instead of ._recv_q. "
            "This will be removed in a later version",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.recv_q

    ##############
    # Yaml funcs #
    ##############

    def __to_yaml_dict__(self) -> dict[Any, Any]:
        """This optional method is called when you call yaml.dump()"""

        return {"local_rib": self.local_rib, "recv_q": self.recv_q}

    @classmethod
    def __from_yaml_dict__(cls, dct, yaml_tag) -> Policy:
        """This optional method is called when you call yaml.load()"""

        return cls(**dct)
