import random

from lib_caida_collector import AS

from yamlable import YamlAble, yaml_info, yaml_info_decorate

from ipaddress import ip_network

from ..announcements import Announcement
from ..enums import Outcomes, Relationships


@yaml_info(yaml_tag="Scenario")
class Scenario(YamlAble):
    """Contains information regarding an attack"""

    __slots__ = ("non_default_as_cls_dict", "prefix_subprefix_dict")

    # This is the base type of announcement for this class
    # You can subclass this engine input and specify a different base ann
    AnnCls = Announcement
    BaseASCls = BGPSimple

    subclasses = []

    def __init_subclass__(cls, *args, **kwargs):
        """This method essentially creates a list of all subclasses
        This is allows us to know all attackers that have been created
        """

        super().__init_subclass__(*args, **kwargs)
        # Add yaml tag to subclass
        yaml_info_decorate(cls, yaml_tag=cls.__name__)

    def __init__(self, non_default_as_cls_dict=None):
        """inits attrs

        non_default_as_cls_dict is a dict of asn: AdoptASCls
        where you do __not__ include any of the BaseASCls,
        since that is the default
        """

        self._get_prefix_subprefix_dict()
        if non_default_as_cls_dict:
            self.non_default_as_cls_dict = non_default_as_cls_dict
        else:
            self.non_default_as_cls_dict = dict()

#############################
# Engine Manipulation Funcs #
#############################

    def setup_engine(self,
                     engine,
                     percent_adoption,
                     prev_scenario=None):
        """Sets up engine input"""

        self._set_engine_ases(engine, percent_adoption, prev_scenario)
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
        self.non_default_as_cls_dict = self._get_as_cls_dict(engine,
                                                             percent_adoption,
                                                             prev_scenario=prev_scenario)
        # Validate that this is only non_default ASes
        # This matters, because later this entire dict may be used for the next
        # scenario
        for asn, ASCls in self.non_default_as_cls_dict.items():
            assert ASCls != self.BaseASCls, "No defaults! See comment above"

        for as_obj in engine:
            # Set the AS class to be the proper type of AS
            as_obj.__class__ = self.as_cls_dict.get(as_obj.asn, self.BaseASCls)
            # Clears all RIBs, etc
            # Reset base is False to avoid overrides base AS info (peers, etc)
            as_obj.__init__(reset_base=False)
        

    def seed(self, engine, *args):
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

##################
# Abstract Funcs #
##################

    @abstractmethod
    def _get_announcements(self):
        """Returns announcements"""

        raise NotImplementedError

    @abstractmethod
    def _get_non_default_as_cls_dict(self, engine, percent_adoption, prev_scenario):
        """Returns AS class dict

        non_default_as_cls_dict is a dict of asn: AdoptASCls
        where you do __not__ include any of the BaseASCls,
        since that is the default
        """

        raise NotImplementedError

    @abstractmethod
    def graph_label(self):
        """Label that will be on the graph"""

        raise NotImplementedError

    @abstractmethod
    def __to_yaml_dict__(self):
        """This optional method is called when you call yaml.dump()"""

        raise NotImplementedError

    @classmethod
    @abstractmethod
    def __from_yaml_dict__(cls, dct, yaml_tag):
        """This optional method is called when you call yaml.load()"""

        raise NotImplementedError

################
# Helper Funcs #
################

    def _get_prefix_subprefix_dict(self):
        """Saves a dict of prefix to subprefixes"""

        prefixes = set([])
        for ann in self.announcements:
            prefixes.add(ann.prefix)
        # Do this here for speed
        prefixes = [ip_network(x) for x in prefixes]

        prefix_subprefix_dict = {x: [] for x in prefixes}
        for outer_prefix, subprefix_list in prefix_subprefix_dict.items():
            for prefix in prefixes:
                if prefix.subnet_of(outer_prefix) and prefix != outer_prefix:
                    subprefix_list.append(str(prefix))
        # Get rid of ip_network
        self.prefix_subprefix_dict = {str(k): v for k, v
                                      in prefix_subprefix_dict.items()}
