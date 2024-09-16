import abc
from abc import ABC, abstractmethod
from functools import cached_property as cached_property
from ipaddress import IPv4Network, IPv6Network
from typing import Any

from _typeshed import Incomplete
from roa_checker import ROA as ROA
from roa_checker import ROAChecker as ROAChecker

from bgpy.as_graphs import AS as AS
from bgpy.shared.enums import SpecialPercentAdoptions as SpecialPercentAdoptions
from bgpy.simulation_engine import (
    Announcement as Ann,
)
from bgpy.simulation_engine import (
    BaseSimulationEngine as BaseSimulationEngine,
)
from bgpy.simulation_engine import (
    Policy as Policy,
)
from bgpy.simulation_framework.scenarios.scenario_config import (
    ScenarioConfig as ScenarioConfig,
)

class Scenario(ABC, metaclass=abc.ABCMeta):
    min_propagation_rounds: int
    scenario_config: Incomplete
    percent_adoption: Incomplete
    attacker_asns: Incomplete
    victim_asns: Incomplete
    adopting_asns: Incomplete
    announcements: Incomplete
    roas: Incomplete
    ordered_prefix_subprefix_dict: Incomplete
    def __init__(
        self,
        *,
        scenario_config: ScenarioConfig,
        percent_adoption: float | SpecialPercentAdoptions = 0,
        engine: BaseSimulationEngine | None = None,
        attacker_asns: frozenset[int] | None = None,
        victim_asns: frozenset[int] | None = None,
        adopting_asns: frozenset[int] | None = None,
    ) -> None: ...
    def _get_attacker_asns(
        self,
        override_attacker_asns: frozenset[int] | None,
        prev_attacker_asns: frozenset[int] | None,
        engine: BaseSimulationEngine | None,
    ) -> frozenset[int]: ...
    def _get_possible_attacker_asns(
        self,
        engine: BaseSimulationEngine,
        percent_adoption: float | SpecialPercentAdoptions,
    ) -> frozenset[int]: ...
    def _get_victim_asns(
        self,
        override_victim_asns: frozenset[int] | None,
        prev_victim_asns: frozenset[int] | None,
        engine: BaseSimulationEngine | None,
    ) -> frozenset[int]: ...
    def _get_possible_victim_asns(
        self,
        engine: BaseSimulationEngine,
        percent_adoption: float | SpecialPercentAdoptions,
    ) -> frozenset[int]: ...
    def _get_adopting_asns(
        self,
        override_adopting_asns: frozenset[int] | None,
        adopting_asns: frozenset[int] | None,
        engine: BaseSimulationEngine | None,
    ) -> frozenset[int]: ...
    def _get_randomized_adopting_asns(
        self, engine: BaseSimulationEngine
    ) -> frozenset[int]: ...
    @cached_property
    def _default_adopters(self) -> frozenset[int]: ...
    @cached_property
    def _default_non_adopters(self) -> frozenset[int]: ...
    @cached_property
    def _preset_asns(self) -> frozenset[int]: ...
    @property
    def untracked_asns(self) -> frozenset[int]: ...
    @property
    def _untracked_asns(self) -> frozenset[int]: ...
    def setup_engine(self, engine: BaseSimulationEngine) -> None: ...
    def get_policy_cls(self, as_obj: AS) -> type[Policy]: ...
    @abstractmethod
    def _get_announcements(
        self, *, engine: BaseSimulationEngine | None = None
    ) -> tuple[Ann, ...]: ...
    def _get_roas(
        self,
        *,
        announcements: tuple[Ann, ...] = (),
        engine: BaseSimulationEngine | None = None,
    ) -> tuple[ROA, ...]: ...
    def pre_aggregation_hook(
        self,
        engine: BaseSimulationEngine,
        percent_adopt: float | SpecialPercentAdoptions,
        trial: int,
        propagation_round: int,
    ) -> None: ...
    def post_propagation_hook(
        self,
        engine: BaseSimulationEngine,
        percent_adopt: float | SpecialPercentAdoptions,
        trial: int,
        propagation_round: int,
    ) -> None: ...
    def _add_roa_info_to_anns(
        self,
        *,
        announcements: tuple[Ann, ...] = (),
        engine: BaseSimulationEngine | None = None,
    ) -> tuple[Ann, ...]: ...
    def _get_roa_checker(self) -> ROAChecker: ...
    def _get_roa_origin(
        self, roa_checker: ROAChecker, prefix: IPv4Network | IPv6Network, origin: int
    ) -> int | None: ...
    def _get_roa_valid_length(
        self, roa_checker: ROAChecker, prefix: IPv4Network | IPv6Network, origin: int
    ) -> bool | None: ...
    def _get_ordered_prefix_subprefix_dict(self): ...
    def __to_yaml_dict__(self) -> dict[Any, Any]: ...
    @classmethod
    def __from_yaml_dict__(cls, dct, yaml_tag): ...
