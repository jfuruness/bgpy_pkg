from abc import ABC, abstractmethod

from ipaddress import ip_network

from ...announcement import Announcement
from ...engine import BGPSimpleAS


class Scenario(ABC):
    """Contains information regarding an attack"""

    __slots__ = ("non_default_as_cls_dict", "prefix_subprefix_dict")

    # This is the base type of announcement for this class
    # You can subclass this engine input and specify a different base ann
    AnnCls = Announcement

    def __init__(self, BaseASCls=BGPSimpleAS):
        """inits attrs

        non_default_as_cls_dict is a dict of asn: AdoptASCls
        where you do __not__ include any of the BaseASCls,
        since that is the default
        """

        self.BaseASCls = BaseASCls
        self.announcements = self._get_announcements()
        self._get_ordered_prefix_subprefix_dict()

#############################
# Engine Manipulation Funcs #
#############################

    def setup_engine(self,
                     engine,
                     percent_adoption,
                     prev_scenario=None):
        """Sets up engine input"""

        self._set_engine_as_classes(engine, percent_adoption, prev_scenario)
        self._seed_engine_announcements(engine,
                                        percent_adoption,
                                        prev_scenario)
        engine.ready_to_run_round = 0

    def _set_engine_as_classes(self,
                               engine,
                               percent_adoption,
                               prev_scenario):
        """Resets Engine ASes and changes their AS class

        We do this here because we already seed from the scenario
        to allow for easy overriding. If scenario controls seeding,
        it doesn't make sense for engine to control resetting either
        and have each do half and half
        """

        # non_default_as_cls_dict is a dict of asn: AdoptASCls
        # where you do __not__ include any of the BaseASCls,
        # since that is the default
        # Only regenerate this if it's not already set (like with YAML)
        self.non_default_as_cls_dict = self._get_non_default_as_cls_dict(
            engine,
            percent_adoption,
            prev_scenario=prev_scenario)
        # Validate that this is only non_default ASes
        # This matters, because later this entire dict may be used for the next
        # scenario
        for asn, ASCls in self.non_default_as_cls_dict.items():
            assert ASCls != self.BaseASCls, "No defaults! See comment above"

        for as_obj in engine:
            # Set the AS class to be the proper type of AS
            as_obj.__class__ = self.non_default_as_cls_dict.get(as_obj.asn,
                                                                self.BaseASCls)
            # Clears all RIBs, etc
            # Reset base is False to avoid overrides base AS info (peers, etc)
            as_obj.__init__(reset_base=False)

    def _seed_engine_announcements(self, engine, *args):
        """Seeds announcement at the proper AS

        Since this is the simulator engine, we should
        never have to worry about overlapping announcements
        """

        for ann in self.announcements:
            # Get the AS object to seed at
            obj_to_seed = engine.as_dict[ann.seed_asn]
            # Ensure we aren't replacing anything
            err = "Seeding conflict"
            assert obj_to_seed._local_rib.get_ann(ann.prefix) is None, err
            # Seed by placing in the local rib
            obj_to_seed._local_rib.add_ann(ann)

    def post_propagation_hook(self, *args, **kwargs):
        """Useful hook for post propagation"""

        pass

##################
# Abstract Funcs #
##################

    @abstractmethod
    def _get_announcements(self):
        """Returns announcements"""

        raise NotImplementedError

    @abstractmethod
    def _get_non_default_as_cls_dict(self,
                                     engine,
                                     percent_adoption,
                                     prev_scenario):
        """Returns AS class dict

        non_default_as_cls_dict is a dict of asn: AdoptASCls
        where you do __not__ include any of the BaseASCls,
        since that is the default
        """

        raise NotImplementedError

    @abstractmethod
    def determine_as_outcome(self, as_obj, most_specific_ann):
        """Determines the outcome at an AS

        most_specific_ann is the most specific prefix announcement
        that exists at that AS
        """

        raise NotImplementedError

    @abstractmethod
    def graph_label(self):
        """Label that will be on the graph"""

        raise NotImplementedError

################
# Helper Funcs #
################

    def _get_ordered_prefix_subprefix_dict(self):
        """Saves a dict of prefix to subprefixes"""

        prefixes = set([])
        for ann in self.announcements:
            prefixes.add(ann.prefix)
        # Do this here for speed
        prefixes = [ip_network(x) for x in prefixes]
        # Sort prefixes with most specific prefix first
        # Note that this must be sorted for the traceback to get the
        # most specific prefix first
        prefixes = list(sorted(prefixes, key=lambda x: x.num_addresses))

        prefix_subprefix_dict = {x: [] for x in prefixes}
        for outer_prefix, subprefix_list in prefix_subprefix_dict.items():
            for prefix in prefixes:
                if prefix.subnet_of(outer_prefix) and prefix != outer_prefix:
                    subprefix_list.append(str(prefix))
        # Get rid of ip_network
        self.ordered_prefix_subprefix_dict = {str(k): v for k, v
                                              in prefix_subprefix_dict.items()}
