from frozendict import frozendict
from bgpy.tests.engine_tests.graphs import graph_040

from bgpy.tests.engine_tests.utils import EngineTestConfig


from bgpy.simulation_engine import BGPSimpleAS
from bgpy.simulation_framework import ValidPrefix, ScenarioConfig


class Custom30MultiValidPrefix(ValidPrefix):
    """A valid prefix engine input with multiple victims"""

    def _get_announcements(self, *args, **kwargs):
        """Returns several valid prefix announcements"""

        vic_anns = super()._get_announcements()

        for i in range(len(vic_anns)):
            if vic_anns[i].origin == 1:
                # longer path for AS 1
                # vic_anns[i].as_path = (
                #     vic_anns[i].origin,
                #     vic_anns[i].origin,
                #     vic_anns[i].origin,
                # )

                object.__setattr__(
                    vic_anns[i],
                    "as_path",
                    (vic_anns[i].origin, vic_anns[i].origin, vic_anns[i].origin),
                )
        return vic_anns


config_030 = EngineTestConfig(
    name="030",
    desc="Test seeded announcement should never be replaced",
    scenario_config=ScenarioConfig(
        ScenarioCls=Custom30MultiValidPrefix,
        BaseASCls=BGPSimpleAS,
        override_victim_asns=frozenset({1, 4, 3, 5}),
        num_victims=4,
        override_non_default_asn_cls_dict=frozendict(),
    ),
    graph=graph_040,
)
