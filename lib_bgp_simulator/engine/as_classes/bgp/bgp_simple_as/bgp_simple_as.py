from lib_caida_collector import AS

from ....ann_containers import LocalRIB
from ....ann_containers import RecvQueue
from .....enums import Relationships
from .....announcements import Announcement as Ann


class BGPSimpleAS(AS):
    # TODO: fix later? class error? Does this impact speed?
    __slots__ = ("_local_rib", "_recv_q", "_ribs_in", "_ribs_out", "_send_q")

    name = "BGP"
    as_class_names = []
    as_classes = []

    def __init_subclass__(cls, *args, **kwargs):
        """This method essentially creates a list of all subclasses
        This is allows us to know all attackers that have been created
        """

        super().__init_subclass__(*args, **kwargs)
        assert hasattr(cls, "name"), "Policy must have a name"
        cls.as_class_names.append(cls.name)
        msg = (f"Duplicate name {cls.name} with {cls.__name__}."
               "Please make a class attr name for the policy something else")
        assert len(set(cls.as_class_names)) == len(cls.as_class_names), msg
        cls.as_classes.append(cls)
        if BGPSimpleAS not in cls.as_classes:
            cls.as_classes.append(BGPSimpleAS)


    def __init__(self, *args, _local_rib=None, _recv_q=None, **kwargs):
        """Add local rib and data structures here

        This way they can be easily cleared later without having to redo
        the graph
        """

        if kwargs.get("reset_base", True):
            super(BGPSimpleAS, self).__init__(*args, **kwargs)
        self._local_rib = _local_rib if _local_rib else LocalRIB()
        self._recv_q = _recv_q if _recv_q else RecvQueue()

    def __eq__(self, other):
        if isinstance(other, BGPSimpleAS):
            for attr in self.__slots__:
                if not hasattr(self, attr) == hasattr(other, attr):
                    return False
                elif hasattr(self, attr):
                    if not getattr(self, attr) == getattr(other, attr):
                        return False
            return True
        else:
            raise NotImplementedError

    # https://stackoverflow.com/a/53519136/8903959
    __hash__ = AS.__hash__

    # Propagation functionality
    from .propagate_funcs import propagate_to_providers
    from .propagate_funcs import propagate_to_customers
    from .propagate_funcs import propagate_to_peers
    from .propagate_funcs import _propagate
    from .propagate_funcs import _policy_propagate
    from .propagate_funcs import _process_outgoing_ann

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

##############
# Yaml funcs #
##############

    def __to_yaml_dict__(self):
        """ This optional method is called when you call yaml.dump()"""

        as_dict = super(BGPSimpleAS, self).__to_yaml_dict__()
        as_dict.update({"_local_rib": self._local_rib,
                        "_recv_q": self._recv_q})
        return as_dict

    @classmethod
    def __from_yaml_dict__(cls, dct, yaml_tag):
        """ This optional method is called when you call yaml.load()"""

        return cls(**dct)
