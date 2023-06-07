import random

import pytest

from caida_collector_pkg import CaidaCollector

from ....enums import Prefixes
from ....simulation_framework import ScenarioConfig
from ....simulation_framework import SubprefixHijack
from ....simulation_framework import NonRoutedPrefixHijack
from ....simulation_engine import Announcement
from ....simulation_engine import BGPSimpleAS
from ....simulation_engine import BGPAS
from ....simulation_engine import ROVSimpleAS
from ....simulation_engine import ROVAS
from ....simulation_engine import SimulationEngine


@pytest.mark.framework
@pytest.mark.unit_tests
class TestScenario:
    @pytest.mark.parametrize(
        "num_attackers, num_victims", ((1, 1), (1, 2), (2, 1), (2, 2))
    )
    def test_init_valid(self, num_attackers, num_victims):
        """Tests the initialization works when valid"""

        scenario_config = ScenarioConfig(
            ScenarioCls=SubprefixHijack,
            AnnCls=Announcement,
            BaseASCls=BGPSimpleAS,
            AdoptASCls=None,
            num_attackers=num_attackers,
            num_victims=num_victims,
            override_attacker_asns=set(range(num_attackers)),
            override_victim_asns=set(range(num_victims)),
        )
        SubprefixHijack(scenario_config=scenario_config)

    def test_init_invalid_attackers(self):
        """Tests the len(attacker_asns) == num_attackers"""

        with pytest.raises(AssertionError):
            scenario_config = ScenarioConfig(
                num_attackers=1,
                override_attacker_asns={1, 2},
            )
            SubprefixHijack(scenario_config=scenario_config)

    def test_init_invalid_victims(self):
        """Tests the len(victim_asns) == num_victims"""

        with pytest.raises(AssertionError):
            scenario_config = ScenarioConfig(
                num_victims=1,
                override_victim_asns={1, 2},
            )
            SubprefixHijack(scenario_config=scenario_config)

    def test_init_adopt_as_cls(self):
        """Tests the AdoptASCls is never None, and is the pseudo BaseAS"""

        conf = ScenarioConfig(ScenarioCls=SubprefixHijack)

        assert issubclass(conf.AdoptASCls, conf.BaseASCls)

    ##############################################
    # Set Attacker/Victim and Announcement Funcs #
    ##############################################

    def test_set_attackers_victims_anns_w_prev_scenario(self, engine):
        """Tests the set_attackers_victims_anns with prev_scenario

        Ensures that attackers and victims are the same as the last
        scenario that was run
        """

        prev_scenario_config = ScenarioConfig(
            override_attacker_asns={1},
            override_victim_asns={2}
        )
        prev_scenario = SubprefixHijack(scenario_config=prev_scenario_config)
        scenario = SubprefixHijack(engine=engine, prev_scenario=prev_scenario)
        assert prev_scenario.attacker_asns == scenario.attacker_asns
        assert prev_scenario.victim_asns == scenario.victim_asns

    def test_set_attackers_victims_anns_wout_prev_scenario(self, engine):
        """Tests the set_attackers_victims_anns without prev_scenario

        Ensures that attackers and victims are randomly chosen
        """

        random.seed(0)
        scenario = SubprefixHijack(engine=engine)
        scenario_2 = SubprefixHijack(engine=engine)

        assert scenario.attacker_asns != scenario_2.attacker_asns
        assert scenario.victim_asns != scenario_2.victim_asns

    def test_set_attackers_victims_preset(self, engine):
        """Tests that the attackers/victims don't change if they were preset

        and tests that they do change if they weren't preset
        """

        attacker_asns = {1}
        victim_asns = {2}
        scenario = SubprefixHijack(
            scenario_config=ScenarioConfig(
                override_attacker_asns=attacker_asns,
                override_victim_asns=victim_asns
            )
        )
        assert scenario.attacker_asns == attacker_asns
        assert scenario.victim_asns == victim_asns

    def test_set_attackers_victims_not_preset(self, engine):
        """Tests that the attackers/victims change when not preset"""

        # No preset attacker and victim asns
        scenario = SubprefixHijack()
        # Ensure that these are filled
        assert scenario.attacker_asns
        assert scenario.victim_asns

    def test_get_attacker_asns(self, engine):
        """Tests that get_attacker_asns

        1. chooses attacker(s)
        2. That the number of attackers are equal to number of num_attackers
        3. That the selection is random
        4. That the selection is without replacement
           * Note: Part 4 is checked by default because it's a set
           * So if this failed, number 2 would fail
        """

        num_attackers = 2
        scenario_config = ScenarioConfig(num_attackers=num_attackers)
        scenario = SubprefixHijack(scenario_config=scenario_config)
        attacker_asns = scenario._get_attacker_asns(
            override_attacker_asns=None,
            engine=engine,
            prev_scenario=None
        )
        # Check for #1
        assert attacker_asns
        # Check for #2 (and therefore #4 as well)
        assert len(attacker_asns) == num_attackers
        # Check for number 3
        attacker_asns_2 = scenario._get_attacker_asns(
            override_attacker_asns=None,
            engine=engine,
            prev_scenario=None
        )
        assert attacker_asns != attacker_asns_2

    def test_get_victim_asns(self, engine):
        """Tests that get_victim_asns

        1. chooses victim(s)
        2. That the number of victims are equal to number of num_victims
        3. That the selection is random
        4. That the selection is without replacement
             * Note: This check is done by default
             * Since these are sets, and the sets must match
               the number of victims (#2)
        5. That no victims are attackers!!
        """

        num_victims = 2
        scenario_config = ScenarioConfig(num_victims=2)
        scenario = NonRoutedPrefixHijack(scenario_config=scenario_config)
        victim_asns = scenario._get_victim_asns(
            override_victim_asns=None,
            engine=engine,
            prev_scenario=None
        )
        # Check for #1
        assert victim_asns
        # Check for #2 (and therefore #4 as well)
        assert len(victim_asns) == num_victims
        # Check for number 3
        victim_asns_2 = scenario._get_victim_asns(
            override_victim_asns=None,
            engine=engine,
            prev_scenario=None
        )

        assert victim_asns != victim_asns_2
        # Check for #5 TODO: make this better by checking for __all__
        for attacker_asn in scenario.attacker_asns:
            assert attacker_asn not in victim_asns
            assert attacker_asn not in victim_asns_2

    def test_get_possible_attacker_asns(self):
        """Tests the possible attacker asns

        Ensures that a set is returned filled with at least a few ases
        """

        engine = CaidaCollector(
            BaseASCls=BGPSimpleAS,
            GraphCls=SimulationEngine,
        ).run(tsv_path=None)

        assert SubprefixHijack()._get_possible_attacker_asns(
            override_attacker_asns=None,
            engine=engine,
            prev_scenario=None
        )

    def test_get_possible_victim_asns(self, engine):
        """Tests that a set is returned with at least a few ases"""

        engine = CaidaCollector(
            BaseASCls=BGPSimpleAS,
            GraphCls=SimulationEngine,
        ).run(tsv_path=None)

        assert SubprefixHijack()._get_possible_victim_asns(
            override_victim_asns=None,
            engine=engine,
            prev_scenario=None
        )

    def test_get_announcements(self, engine):
        """Tests the get_announcements of a subclass of scenario

        Ensures that announcements are returned and returned properly
        """

        scenario = SubprefixHijack()
        # Victim prefix, subprefix attacker
        assert len(scenario.announcements) == 2
        for victim_asn in scenario.victim_asns:
            assert any(victim_asn == x.seed_asn for x in scenario.announcements)
        for attacker_asn in scenario.attacker_asns:
            assert any(attacker_asn == x.seed_asn for x in scenario.announcements)

    #######################
    # Adopting ASNs funcs #
    #######################

    def test_get_non_default_asn_cls_dict_prev_scenario_adopt(self, engine):
        """Tests that the non default as cls dict is set properly

        Old scenario must have mixed deployment to test that feature as well
        So old scenario must have three types of ASes:
        BaseASCls
        DefaultASCls
        AdoptASCls
        """

        BaseASCls = BGPSimpleAS

        prev_scenario_config = ScenarioConfig(
            AdoptASCls=ROVSimpleAS,
            BaseASCls=BaseASCls,
            override_non_default_asn_cls_dict={
                1: BaseASCls,
                2: ROVAS,
                3: ROVSimpleAS,
            }
        )
        prev_scenario = SubprefixHijack(scenario_config=prev_scenario_config)
        scenario_config = ScenarioConfig(
            AdoptASCls=BGPAS,
            BaseASCls=BaseASCls
        )
        scenario = SubprefixHijack(scenario_config=scenario_config)
        non_default_asn_cls_dict = scenario._get_non_default_asn_cls_dict(
            override_non_default_asn_cls_dict=None,
            engine=engine,
            prev_scenario=prev_scenario
        )

        gt = {1: BaseASCls, 2: ROVAS, 3: BGPAS}
        assert non_default_asn_cls_dict == gt

    def test_get_non_default_asn_cls_dict_prev_scenario_no_adopt(self, engine):
        """Tests that the non default as cls dict is set properly

        Old scenario must have mixed deployment but no adopting ASes!
        So old scenario must have two types of ASes:
        BaseASCls
        DefaultASCls
        """

        BaseASCls = BGPSimpleAS

        prev_scenario_config = ScenarioConfig(
            AdoptASCls=None,
            BaseASCls=BGPSimpleAS,
            override_non_default_asn_cls_dict={
                1: BaseASCls,
                2: ROVAS,
                3: BaseASCls,
            }
        )
        prev_scenario = SubprefixHijack(scenario_config=prev_scenario_config)
        scenario_config = ScenarioConfig(
            AdoptASCls=BGPAS,
            BaseASCls=BaseASCls
        )
        scenario = SubprefixHijack(scenario_config=scenario_config)
        non_default_asn_cls_dict = scenario._get_non_default_asn_cls_dict(
            override_non_default_asn_cls_dict=None,
            engine=engine,
            prev_scenario=prev_scenario
        )

        gt = {
            1: BaseASCls,
            2: ROVAS,
            3: BaseASCls
        }
        assert non_default_asn_cls_dict == gt

    def test_get_non_default_asn_cls_dict_no_prev_scenario_no_adopt(self, engine):
        """Tests that the non default as cls dict is set properly

        No prev_scenario and no adopt AS Cls - should be the result of the
        get_adopting_asns_dict
        """

        scenario_config = ScenarioConfig(
            AdoptASCls=ROVSimpleAS,
            BaseASCls=BGPSimpleAS
        )
        scenario = SubprefixHijack(scenario_config=scenario_config, percent_adoption=.5)
        non_default_asn_cls_dict = scenario._get_non_default_asn_cls_dict(
            override_non_default_asn_cls_dict=None,
            engine=engine,
            prev_scenario=None
        )

        assert ROVSimpleAS in list(non_default_asn_cls_dict.values())
        assert BGPSimpleAS not in list(non_default_asn_cls_dict.values())

    @pytest.mark.skip(reason="Covered by other unit tests")
    def test_get_non_default_asn_cls_dict_no_adoption_sequence(self):
        """Tests the Pseudo AdoptASCls

        # This is done to fix the following:
        # Scenario 1 has 3 BGP ASes and 1 AdoptCls
        # Scenario 2 has no adopt classes, so 4 BGP
        # Scenario 3 we want to run ROV++, but what were the adopting ASes from
        # scenario 1? We don't know anymore.
        # Instead for scenario 2, we have 3 BGP ASes and 1 Psuedo BGP AS
        # Then scenario 3 will still work as expected
        """

        raise NotImplementedError

    @pytest.mark.skip(reason="Low priority, clearly working through graphs")
    def test_get_adopting_asns_dict(self):
        """Tests the get adopting asns function

        Tests that for each subcategory they adopt at the proper percentages
        Tests that the adoption is random
        Tests for zero adoption that adoption is 1
        Tests for 100% adoption adoption is 100% - 1
        Tests that adopters can't be preset ASNs
        Tests that the default adopters always adopt
        Tests that the default_non_adopters don't always adopt
        """

        raise NotImplementedError

    def test_default_adopters(self):
        """Ensures that the default adopters returns the victims"""

        assert SubprefixHijack(
            scenario_config=ScenarioConfig(override_victim_asns={1})
        )._default_adopters == {1}

    def test_default_non_adopters(self):
        """Tests that the attacker does not adopt"""

        assert SubprefixHijack(
            scenario_config=ScenarioConfig(override_attacker_asns={1})
        )._default_non_adopters == {1}

    def test_preset_asns(self):
        """Tests that the preset ASNs is the union of default ASNs"""

        hijack = SubprefixHijack(
            scenario_config=ScenarioConfig(
                override_attacker_asns={1},
                override_victim_asns={2}
            )
        )
        assert hijack._preset_asns == {1, 2}

    @pytest.mark.skip(reason="Covered by vast amount of system tests")
    def test_determine_as_outcome(self):
        """Tests every possible condition for AS outcomes

        Probably split this into multiple tests
        """

        raise NotImplementedError

    #############################
    # Engine Manipulation Funcs #
    #############################

    @pytest.mark.skip(reason="Covered by vast amount of system tests")
    def test_setup_engine(self):
        """Tests setup_engine func

        1. Ensures attackers and victims are set properly
        2. Ensures the engines AS classes are correcct
        3. Ensures the announcements are seeded
        """

        raise NotImplementedError

    @pytest.mark.skip(reason="Covered by vast amount of system tests")
    def test_set_engine_as_classes(self):
        """Tests that the engine as classes are set properly

        1. Ensures that non default AS class dict doesn't contain BaseASCls
        2. Ensures that AS classes get reset
        3. Ensures that AS init gets called, but relationships remain
        """

        raise NotImplementedError

    @pytest.mark.skip(reason="Covered by vast amount of system tests")
    def test_seed_engine_announcements(self):
        """Tests the seeding of engine announcements

        1. Ensure you can't replace seeded announcements
        2. Ensure an AS has recieved the announcement
        """

        raise NotImplementedError

    def test_post_propagation_hook(self):
        """Test that the post_propagation_hook doesn't error"""

        SubprefixHijack().post_propagation_hook()

    ################
    # Helper Funcs #
    ################

    def test_get_ordered_prefix_subprefix_dict(self, engine):
        """Tests that the get_ordered_prefix_subprefix_dict works"""

        scenario = SubprefixHijack(engine=engine)
        gt = {
            Prefixes.PREFIX.value: [Prefixes.SUBPREFIX.value],
            Prefixes.SUBPREFIX.value: [],
        }
        assert scenario.ordered_prefix_subprefix_dict == gt
