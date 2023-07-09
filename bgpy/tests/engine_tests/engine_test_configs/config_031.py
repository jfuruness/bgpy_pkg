from frozendict import frozendict
from bgpy.tests.engine_tests.graphs import graph_040
from bgpy.tests.engine_tests.utils import EngineTestConfig


from bgpy.simulation_engine import BGPSimpleAS
from bgpy.simulation_framework import ValidPrefix, ScenarioConfig


class Custom31ValidPrefix(ValidPrefix):
    """A valid prefix engine input"""

    def _get_announcements(self, *args, **kwargs):
        vic_ann = super()._get_announcements()[0]
        # Add 1 to the path so AS 1 rejects this
        # vic_ann.as_path = (vic_ann.origin, 1, vic_ann.origin)

        object.__setattr__(vic_ann, "as_path", (vic_ann.origin, 1, vic_ann.origin))
        return (vic_ann,)


config_031 = EngineTestConfig(
    name="031",
    desc="Test loop prevention mechanism",
    scenario_config=ScenarioConfig(
        ScenarioCls=Custom31ValidPrefix,
        override_victim_asns=frozenset({4}),
        BaseASCls=BGPSimpleAS,
        override_non_default_asn_cls_dict=frozendict(),
    ),
    graph=graph_040,
)
