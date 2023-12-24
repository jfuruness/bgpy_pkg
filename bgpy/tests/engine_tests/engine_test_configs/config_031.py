from frozendict import frozendict
from bgpy.tests.engine_tests.as_graph_infos import as_graph_info_040
from bgpy.tests.engine_tests.utils import EngineTestConfig


from bgpy.simulation_engines.py_simulation_engine import BGPSimplePolicy
from bgpy.simulation_frameworks.py_simulation_framework import (
    ValidPrefix,
    ScenarioConfig,
)


class Custom31ValidPrefix(ValidPrefix):
    """A valid prefix engine input"""

    def _get_announcements(self, *args, **kwargs):
        vic_ann = super()._get_announcements()[0]
        # Add 1 to the path so AS 1 rejects this
        # vic_ann.as_path = (vic_ann.origin, 1, vic_ann.origin)

        object.__setattr__(vic_ann, "as_path", [vic_ann.origin, 1, vic_ann.origin])
        return (vic_ann,)


config_031 = EngineTestConfig(
    name="031",
    desc="Test loop prevention mechanism",
    scenario_config=ScenarioConfig(
        ScenarioCls=Custom31ValidPrefix,
        override_victim_asns=frozenset({4}),
        BasePolicyCls=BGPSimplePolicy,
        override_non_default_asn_cls_dict=frozendict(),
    ),
    as_graph_info=as_graph_info_040,
)
