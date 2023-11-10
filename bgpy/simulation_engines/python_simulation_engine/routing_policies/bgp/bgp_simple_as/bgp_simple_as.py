from bgpy.caida_collector import AS
from typing import Optional

# Propagation functionality
from .propagate_funcs import propagate_to_providers
from .propagate_funcs import propagate_to_customers
from .propagate_funcs import propagate_to_peers
from .propagate_funcs import _propagate
from .propagate_funcs import _policy_propagate
from .propagate_funcs import _process_outgoing_ann
from .propagate_funcs import _prev_sent

# Process incoming announcements
from .process_incoming_funcs import receive_ann
from .process_incoming_funcs import process_incoming_anns
from .process_incoming_funcs import _valid_ann
from .process_incoming_funcs import _copy_and_process
from .process_incoming_funcs import _reset_q

# Gao rexford functions
from .gao_rexford import _new_ann_better
from .gao_rexford import _new_as_path_ties_better
from .gao_rexford import _new_rel_better
from .gao_rexford import _new_as_path_shorter
from .gao_rexford import _new_wins_ties


from bgpy.simulation_engine.ann_containers import LocalRIB
from bgpy.simulation_engine.ann_containers import RecvQueue


class BGPSimpleAS(AS):
    name: str = "BGP Simple"
    as_class_names: list[str] = []
    as_classes: list[type[AS]] = []

    def __init_subclass__(cls, *args, **kwargs):
        """This method essentially creates a list of all subclasses

        This is allows us to know all AS types that have been created
        """

        super().__init_subclass__(*args, **kwargs)
        assert hasattr(cls, "name"), "Policy must have a name"
        cls.as_class_names.append(cls.name)
        msg: str = (
            f"Duplicate name {cls.name} with {cls.__name__}."
            "Please make a class attr "
            "name for the policy something else"
        )
        assert len(set(cls.as_class_names)) == len(cls.as_class_names), msg
        cls.as_classes.append(cls)
        if BGPSimpleAS not in cls.as_classes:
            cls.as_classes.append(BGPSimpleAS)

    def __init__(
        self,
        *args,
        _local_rib: Optional[LocalRIB] = None,
        _recv_q: Optional[RecvQueue] = None,
        **kwargs,
    ):
        """Add local rib and data structures here

        This way they can be easily cleared later without having to redo
        the graph

        This is also useful for regenerating an AS from YAML
        """

        if kwargs.get("reset_base", True):
            super(BGPSimpleAS, self).__init__(*args, **kwargs)
        self._local_rib = _local_rib if _local_rib else LocalRIB()
        self._recv_q = _recv_q if _recv_q else RecvQueue()

    def __eq__(self, other) -> bool:
        if isinstance(other, BGPSimpleAS):
            # Ugh this is bad
            for attr in [x for x in self.__dict__ if x not in self.base_slots]:
                if not hasattr(self, attr) == hasattr(other, attr):
                    return False
                elif hasattr(self, attr):
                    if not getattr(self, attr) == getattr(other, attr):
                        return False
            return True
        else:
            return NotImplemented

    # https://stackoverflow.com/a/53519136/8903959
    __hash__ = AS.__hash__

    # Propagation functionality
    propagate_to_providers = propagate_to_providers
    propagate_to_customers = propagate_to_customers
    propagate_to_peers = propagate_to_peers
    _propagate = _propagate
    _policy_propagate = _policy_propagate
    _process_outgoing_ann = _process_outgoing_ann
    _prev_sent = _prev_sent

    # Process incoming announcements
    receive_ann = receive_ann
    process_incoming_anns = process_incoming_anns
    _valid_ann = _valid_ann
    _copy_and_process = _copy_and_process
    _reset_q = _reset_q

    # Gao rexford functions
    _new_ann_better = _new_ann_better
    _new_as_path_ties_better = _new_as_path_ties_better
    _new_rel_better = _new_rel_better
    _new_as_path_shorter = _new_as_path_shorter
    _new_wins_ties = _new_wins_ties

    ##############
    # Yaml funcs #
    ##############

    def __to_yaml_dict__(self):
        """This optional method is called when you call yaml.dump()"""

        as_dict = super(BGPSimpleAS, self).__to_yaml_dict__()
        as_dict.update({"_local_rib": self._local_rib, "_recv_q": self._recv_q})
        return as_dict

    @classmethod
    def __from_yaml_dict__(cls, dct, yaml_tag):
        """This optional method is called when you call yaml.load()"""

        return cls(**dct)
