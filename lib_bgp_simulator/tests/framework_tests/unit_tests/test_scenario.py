import random

import pytest

from lib_caida_collector import CaidaCollector

from ....enums import Prefixes
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
    @pytest.mark.parametrize("num_attackers, num_victims", ((1, 1),
                                                            (1, 2),
                                                            (2, 1),
                                                            (2, 2)))
    def test_init_valid(self, num_attackers, num_victims):
        """Tests the initialization works when valid"""

        SubprefixHijack(AnnCls=Announcement,
                        BaseASCls=BGPSimpleAS,
                        AdoptASCls=None,
                        num_attackers=num_attackers,
                        num_victims=num_victims,
                        attacker_asns=list(range(num_attackers)),
                        victim_asns=list(range(num_victims)))

    def test_init_invalid_attackers(self):
        """Tests the len(attacker_asns) == num_attackers"""

        with pytest.raises(AssertionError):
            SubprefixHijack(num_attackers=1,
                            attacker_asns={1, 2})

    def test_init_invalid_victims(self):
        """Tests the len(victim_asns) == num_victims"""

        with pytest.raises(AssertionError):
            SubprefixHijack(num_victims=1,
                            victim_asns={1, 2})

    @pytest.mark.parametrize("attacker, victim", ((True, True),
                                                  (True, False),
                                                  (False, False),
                                                  (False, True)))
    def test_init_attacker_victim_asns_preset(self, attacker, victim):
        """Tests the attacker_victim_asns_preset is correct"""

        kwargs = dict()
        if attacker:
            kwargs["attacker_asns"] = {1}
        elif victim:
            kwargs["victim_asns"] = {2}

        hijack = SubprefixHijack(**kwargs)
        if attacker or victim:
            assert hijack.attacker_victim_asns_preset
        else:
            assert hijack.attacker_victim_asns_preset is False

    def test_init_adopt_as_cls(self):
        """Tests the AdoptASCls is never None, and is the pseudo BaseAS"""

        hijack = SubprefixHijack()
        assert issubclass(hijack.AdoptASCls, hijack.BaseASCls)

##############################################
# Set Attacker/Victim and Announcement Funcs #
##############################################

    def test_set_attackers_victims_anns_w_prev_scenario(self, engine):
        """Tests the set_attackers_victims_anns with prev_scenario

        Ensures that attackers and victims are the same as the last
        scenario that was run
        """

        prev_scenario = SubprefixHijack(attacker_asns={1},
                                        victim_asns={2})
        scenario = SubprefixHijack()
        scenario._set_attackers_victims_anns(engine,
                                             0,
                                             prev_scenario)
        for attr in ("attacker_asns", "victim_asns"):
            assert getattr(scenario, attr) == getattr(prev_scenario, attr)

    def test_set_attackers_victims_anns_wout_prev_scenario(self, engine):
        """Tests the set_attackers_victims_anns without prev_scenario

        Ensures that attackers and victims are randomly chosen
        """

        # Seed randomness to ensure deterministic
        random.seed(0)
        scenario = SubprefixHijack()
        scenario._set_attackers_victims_anns(
            engine,
            percent_adoption=0,
            prev_scenario=None)  # type: ignore
        random.seed(1)
        scenario_2 = SubprefixHijack()
        scenario_2._set_attackers_victims_anns(
            engine,
            percent_adoption=0,
            prev_scenario=None)  # type: ignore

        for attr in ("attacker_asns", "victim_asns"):
            assert getattr(scenario, attr) != getattr(scenario_2, attr)

    def test_set_attackers_victims_preset(self, engine):
        """Tests that the attackers/victims don't change if they were preset

        and tests that they do change if they weren't preset
        """

        kwargs = {"attacker_asns": {1}, "victim_asns": {2}}
        # First check if they were preset that they don't change
        scenario = SubprefixHijack(**kwargs)
        scenario._set_attackers_victims(engine,
                                        percent_adoption=0,
                                        prev_scenario=None)
        for attr, val in kwargs.items():
            assert getattr(scenario, attr) == val

    def test_set_attackers_victims_not_preset(self, engine):
        """Tests that the attackers/victims change when not preset"""

        # No preset attacker and victim asns
        scenario = SubprefixHijack()
        # This should randomly select attackers and victims
        scenario._set_attackers_victims(engine,
                                        percent_adoption=0,
                                        prev_scenario=None)
        for attr in ("attacker_asns", "victim_asns"):
            # Ensure that these are filled
            assert getattr(scenario, attr)

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
        scenario = SubprefixHijack(num_attackers=num_attackers)
        attacker_asns = scenario._get_attacker_asns(engine, 0, None)
        # Check for #1
        assert attacker_asns
        # Check for #2 (and therefore #4 as well)
        assert len(attacker_asns) == num_attackers
        # Check for number 3
        attacker_asns_2 = scenario._get_attacker_asns(engine, 0, None)
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
        scenario = NonRoutedPrefixHijack(num_victims=num_victims)
        # Set attacker and victim asns
        scenario._set_attackers_victims_anns(engine, 0, None)
        victim_asns = scenario._get_victim_asns(engine, 0, None)
        # Check for #1
        assert victim_asns
        # Check for #2 (and therefore #4 as well)
        assert len(victim_asns) == num_victims
        # Check for number 3
        victim_asns_2 = scenario._get_victim_asns(engine, 0, None)
        assert victim_asns != victim_asns_2
        # Check for #5 TODO: make this better by checking for __all__
        for attacker_asn in scenario.attacker_asns:
            assert attacker_asn not in victim_asns
            assert attacker_asn not in victim_asns_2

    def test_get_possible_attacker_asns(self):
        """Tests the possible attacker asns

        Ensures that a set is returned filled with at least a few ases
        """

        engine = CaidaCollector(BaseASCls=BGPSimpleAS,
                                GraphCls=SimulationEngine,
                                ).run(tsv_path=None)

        assert SubprefixHijack()._get_possible_attacker_asns(
            engine, 0, prev_scenario=None)

    def test_get_possible_victim_asns(self, engine):
        """Tests that a set is returned with at least a few ases"""

        engine = CaidaCollector(BaseASCls=BGPSimpleAS,
                                GraphCls=SimulationEngine,
                                ).run(tsv_path=None)

        assert SubprefixHijack()._get_possible_victim_asns(engine,
                                                           0,
                                                           prev_scenario=None)

    def test_get_announcements(self, engine):
        """Tests the get_announcements of a subclass of scenario

        Ensures that announcements are returned and returned properly
        """

        scenario = SubprefixHijack()
        scenario._set_attackers_victims_anns(engine, 0, None)
        # Victim prefix, subprefix attacker
        assert len(scenario.announcements) == 2
        for victim_asn in scenario.victim_asns:
            assert any(victim_asn == x.seed_asn
                       for x in scenario.announcements)
        for attacker_asn in scenario.attacker_asns:
            assert any(attacker_asn == x.seed_asn
                       for x in scenario.announcements)

#######################
# Adopting ASNs funcs #
#######################

    def test_get_non_default_as_cls_dict_prev_scenario_adopt(self, engine):
        """Tests that the non default as cls dict is set properly

        Old scenario must have mixed deployment to test that feature as well
        So old scenario must have three types of ASes:
        BaseASCls
        DefaultASCls
        AdoptASCls
        """

        prev_scenario = SubprefixHijack(AdoptASCls=ROVSimpleAS,
                                        BaseASCls=BGPSimpleAS)
        prev_scenario.non_default_as_cls_dict = {1: prev_scenario.BaseASCls,
                                                 2: ROVAS,
                                                 3: ROVSimpleAS}
        scenario = SubprefixHijack(AdoptASCls=BGPAS,
                                   BaseASCls=BGPSimpleAS)
        non_default_as_cls_dict = scenario._get_non_default_as_cls_dict(
            engine, 0, prev_scenario)

        gt = {1: prev_scenario.BaseASCls,
              2: ROVAS,
              3: BGPAS}
        assert non_default_as_cls_dict == gt

    def test_get_non_default_as_cls_dict_prev_scenario_no_adopt(self, engine):
        """Tests that the non default as cls dict is set properly

        Old scenario must have mixed deployment but no adopting ASes!
        So old scenario must have two types of ASes:
        BaseASCls
        DefaultASCls
        """

        prev_scenario = SubprefixHijack(AdoptASCls=None,
                                        BaseASCls=BGPSimpleAS)
        prev_scenario.non_default_as_cls_dict = {1: prev_scenario.BaseASCls,
                                                 2: ROVAS,
                                                 3: prev_scenario.BaseASCls}
        scenario = SubprefixHijack(AdoptASCls=BGPAS,
                                   BaseASCls=BGPSimpleAS)
        non_default_as_cls_dict = scenario._get_non_default_as_cls_dict(
            engine, 0, prev_scenario)

        gt = {1: prev_scenario.BaseASCls,
              2: ROVAS,
              3: prev_scenario.BaseASCls}
        assert non_default_as_cls_dict == gt

    def test_get_non_default_as_cls_dict_no_prev_scenario_no_adopt(self,
                                                                   engine):
        """Tests that the non default as cls dict is set properly

        No prev_scenario and no adopt AS Cls - should be the result of the
        get_adopting_asns_dict
        """

        scenario = SubprefixHijack(AdoptASCls=ROVSimpleAS,
                                   BaseASCls=BGPSimpleAS)
        non_default_as_cls_dict = scenario._get_non_default_as_cls_dict(
            engine, 50, None)

        assert ROVSimpleAS in list(non_default_as_cls_dict.values())
        assert BGPSimpleAS not in list(non_default_as_cls_dict.values())

    @pytest.mark.skip(reason="Covered by other unit tests")
    def test_get_non_default_as_cls_dict_no_adoption_sequence(self):
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

        assert SubprefixHijack(victim_asns={1})._default_adopters == {1}

    def test_default_non_adopters(self):
        """Tests that the attacker does not adopt"""

        assert SubprefixHijack(attacker_asns={1})._default_non_adopters == {1}

    def test_preset_asns(self):
        """Tests that the preset ASNs is the union of default ASNs"""

        assert SubprefixHijack(attacker_asns={1},
                               victim_asns={2})._preset_asns == {1, 2}

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

        scenario = SubprefixHijack()
        scenario._set_attackers_victims_anns(engine, 50, None)
        gt = {Prefixes.PREFIX.value: [Prefixes.SUBPREFIX.value],
              Prefixes.SUBPREFIX.value: []}
        assert scenario.ordered_prefix_subprefix_dict == gt
