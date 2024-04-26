from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Optional, TYPE_CHECKING

from frozendict import frozendict
from yamlable import YamlAble, yaml_info, yaml_info_decorate

from ..policies import Policy

# https://stackoverflow.com/a/57005931/8903959
if TYPE_CHECKING:
    from bgpy.as_graphs import ASGraph
    from bgpy.simulation_engine.announcement import Announcement as Ann
    from bgpy.simulation_framework import Scenario


@yaml_info(yaml_tag="BaseSimulationEngine")
class BaseSimulationEngine(YamlAble, ABC):
    """AS Graph wrapper that supports announcement propogation

    This class must be first setup with the _setup function
    This resets all the ASes to their base state, and changes
    the classes to be adopting specific defensive policies
    Then the run function can be called, and propagation occurs
    """

    def __init_subclass__(cls, *args, **kwargs):
        """This method essentially creates a list of all subclasses
        This is allows us to easily assign yaml tags
        """

        super().__init_subclass__(*args, **kwargs)
        # Fix this later once the system test framework is updated
        yaml_info_decorate(cls, yaml_tag=cls.__name__)

    def __init__(
        self,
        as_graph: "ASGraph",
        # Useful for C++ Engine
        cached_as_graph_tsv_path: Optional[Path] = None,
        ready_to_run_round: int = -1,
    ) -> None:
        """Saves read_to_run_rund attr and inits superclass"""

        self.as_graph = as_graph
        # Useful for C++ version
        self.cached_as_graph_tsv_path: Optional[Path] = cached_as_graph_tsv_path
        # This indicates whether or not the simulator has been set up for a run
        # We use a number instead of a bool so that we can indicate for
        # each round whether it is ready to run or not
        self.ready_to_run_round: int = ready_to_run_round

    def __eq__(self, other) -> bool:
        """Returns if two simulators contain the same BGPDAG's"""

        if isinstance(other, BaseSimulationEngine):
            rv = self.as_graph.as_dict == other.as_graph.as_dict
            assert isinstance(rv, bool), "Make mypy happy"
            return rv
        else:
            return NotImplemented

    ###############
    # Setup funcs #
    ###############

    @abstractmethod
    def setup(
        self,
        announcements: tuple["Ann", ...] = (),
        BasePolicyCls: type[Policy] = Policy,
        non_default_asn_cls_dict: frozendict[int, type[Policy]] = (
            frozendict()  # type: ignore
        ),
        prev_scenario: Optional["Scenario"] = None,
        attacker_asns: frozenset[int] = frozenset(),
        AttackerBasePolicyCls: Optional[type[Policy]] = None,
    ) -> frozenset[type[Policy]]:
        """Sets AS classes and seeds announcements"""

        raise NotImplementedError

    #####################
    # Propagation funcs #
    #####################

    @abstractmethod
    def run(
        self, propagation_round: int = 0, scenario: Optional["Scenario"] = None
    ) -> None:
        """Propogates announcements and ensures proper setup"""

        raise NotImplementedError

    ##############
    # Yaml funcs #
    ##############

    @abstractmethod
    def __to_yaml_dict__(self) -> dict[str, Any]:
        """This optional method is called when you call yaml.dump()"""

        raise NotImplementedError

    @classmethod
    @abstractmethod
    def __from_yaml_dict__(
        cls: type["BaseSimulationEngine"], dct: dict[str, Any], yaml_tag: Any
    ) -> "BaseSimulationEngine":
        """This optional method is called when you call yaml.load()"""

        raise NotImplementedError
