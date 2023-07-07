import copyreg
from typing import Any, Callable
from mypy_extensions import NamedArg

from bgp_simulator_pkg.caida_collector.graph.base_as import AS
from bgp_simulator_pkg.enums import ASGroups, Plane, Outcomes
from bgp_simulator_pkg.simulation_engine import SimulationEngine
from bgp_simulator_pkg.simulation_framework.scenarios import Scenario

from .metric import Metric

# TODO: Clean up these unpicklable dynamic subclasses
# https://stackoverflow.com/a/75943813/8903959
class Metaclass(type):
    pass

def _reduce_metaclass(cls):
    metaclass = cls.__class__
    cls_vars = dict(vars(cls))
    cls_vars.pop("__dict__", None)
    cls_vars.pop("__weakref__", None)
    for unpicklable_func in ("label_prefix", "_add_numerator", "_add_denominator"):
        cls_vars.pop(unpicklable_func)
    # print("reduce metaclass", cls, metaclass, cls.__name__, cls.__bases__, vars(cls))
    return metaclass, (cls.__name__, cls.__bases__, cls_vars)

copyreg.pickle(Metaclass, _reduce_metaclass)


class MetricFactory:
    def __init__(self) -> None:
        """Generates a list of all metric subclasses to use"""

        self.metric_subclasses: list[type[Metric]] = list()

        for i, args in enumerate(self._all_metric_combos()):
            class_dict = {
                "label_prefix": self._get_label_prefix_func(*args),
                "_add_numerator": self._get_add_numerator_func(*args),
                "_add_denominator": self._get_add_denominator_func(*args),
            }
            subclass = Metaclass(f"Metric{i}", (Metric,), class_dict)
            self.metric_subclasses.append(subclass)

    def get_metric_subclasses(self) -> list[Metric]:
        """Returns a list of all combinations of metric objects"""

        return [Cls() for Cls in self.metric_subclasses]

    def _all_metric_combos(self):
        """Returns all possible metric combos"""

        for plane in Plane:
            for as_group in ASGroups:
                for outcome in [x for x in Outcomes if x != Outcomes.UNDETERMINED]:
                    yield plane, as_group, outcome

#######################
# Function Generators #
#######################

    def _get_label_prefix_func(
        self,
        plane: Plane,
        as_group: ASGroups,
        outcome: Outcomes
    ) -> property:  # Callable[[], str]:

        return property(lambda self: f"{plane.value}_{as_group.value}_{outcome.value}")

    def _get_add_numerator_func(
        self,
        plane: Plane,
        as_group: ASGroups,
        outcome: Outcomes
    ) -> Callable[[
        Any,
        NamedArg(AS, "as_obj"),
        NamedArg(SimulationEngine, "engine"),
        NamedArg(Scenario, "scenario"),
        NamedArg(Outcomes, "ctrl_plane_outcome"),
        NamedArg(Outcomes, "data_plane_outcome")
    ], None]:
        """Returns the _add_numerator func"""

        def _add_numerator(
            self,
            *,
            as_obj: AS,
            engine: SimulationEngine,
            scenario: Scenario,
            ctrl_plane_outcome: Outcomes,
            data_plane_outcome: Outcomes,
        ) -> None:
            """Adds result to numerator"""

            result = data_plane_outcome if Plane.DATA else ctrl_plane_outcome
            if as_obj.asn in engine.asn_groups[as_group.value] and outcome == result:
                self._numerators[as_obj.__class__] += 1

        return _add_numerator

    def _get_add_denominator_func(
        self,
        plane: Plane,
        as_group: ASGroups,
        outcome: Outcomes
    ) -> Callable[[
        Any,
        NamedArg(AS, "as_obj"),
        NamedArg(SimulationEngine, "engine"),
        NamedArg(Scenario, "scenario"),
        NamedArg(Outcomes, "ctrl_plane_outcome"),
        NamedArg(Outcomes, "data_plane_outcome")
    ], None]:
        """Returns the _add_denominator_func"""

        def _add_denominator(
            self,
            *,
            as_obj: AS,
            engine: SimulationEngine,
            scenario: Scenario,
            ctrl_plane_outcome: Outcomes,
            data_plane_outcome: Outcomes,
        ) -> bool:
            """Adds result to the denominator"""

            if as_obj.asn in engine.asn_groups[as_group.value]:
                self._denominators[as_obj.__class__] += 1
                return True
            else:
                return False

        return _add_denominator
