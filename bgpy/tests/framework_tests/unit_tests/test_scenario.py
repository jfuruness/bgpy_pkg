import random
from ipaddress import ip_network

import pytest
from roa_checker import ROA

from bgpy.shared.enums import ASNs, Prefixes
from bgpy.simulation_engine import BGP, Announcement, BGPFull
from bgpy.simulation_framework import (
    NonRoutedPrefixHijack,
    ScenarioConfig,
    SubprefixHijack,
    ValidPrefix,
)


@pytest.mark.framework
@pytest.mark.unit_tests
class TestScenario:
    @pytest.mark.parametrize("num_attackers", [1, 2])
    def test_init_valid(self, num_attackers):
        """Tests the initialization works when valid"""

        num_victims = 1
        scenario_config = ScenarioConfig(
            ScenarioCls=SubprefixHijack,
            AnnCls=Announcement,
            BasePolicyCls=BGP,
            AdoptPolicyCls=BGPFull,
            num_attackers=num_attackers,
            num_victims=num_victims,
            override_attacker_asns=frozenset(range(num_attackers)),
            override_victim_asns=frozenset(range(num_victims)),
            override_adopting_asns=frozenset({1}),
        )
        SubprefixHijack(scenario_config=scenario_config)

    def test_init_invalid_attackers(self):
        """Tests the len(attacker_asns) == num_attackers"""

        scenario_config = ScenarioConfig(
            ScenarioCls=SubprefixHijack,
            num_attackers=1,
            override_attacker_asns=frozenset({1, 2}),
        )
        with pytest.raises(AssertionError):
            SubprefixHijack(scenario_config=scenario_config)

    def test_init_invalid_victims(self):
        """Tests the len(victim_asns) == num_victims"""

        scenario_config = ScenarioConfig(
            ScenarioCls=SubprefixHijack,
            num_victims=1,
            override_victim_asns=frozenset({1, 2}),
        )
        with pytest.raises(AssertionError):
            SubprefixHijack(scenario_config=scenario_config)

    def test_init_adopt_as_cls(self):
        """Tests the AdoptPolicyCls is never None, and is the pseudo BaseAS"""

        conf = ScenarioConfig(ScenarioCls=SubprefixHijack)

        assert issubclass(conf.AdoptPolicyCls, conf.BasePolicyCls)

    ##############################################
    # set Attacker/Victim and Announcement Funcs #
    ##############################################

    def test_set_attackers_victims_anns_w_prev_scenario(self, engine):
        """Tests the set_attackers_victims_anns with prev_scenario

        Ensures that attackers and victims are the same as the last
        scenario that was run
        """

        prev_scenario_config = ScenarioConfig(
            ScenarioCls=SubprefixHijack,
            override_attacker_asns=frozenset({1}),
            override_victim_asns=frozenset({2}),
        )
        prev_scenario = SubprefixHijack(
            scenario_config=prev_scenario_config, engine=engine
        )
        scenario = SubprefixHijack(
            scenario_config=ScenarioConfig(ScenarioCls=SubprefixHijack),
            engine=engine,
            attacker_asns=prev_scenario.attacker_asns,
            victim_asns=prev_scenario.victim_asns,
        )
        assert prev_scenario.attacker_asns == scenario.attacker_asns
        assert prev_scenario.victim_asns == scenario.victim_asns

    def test_set_attackers_victims_anns_wout_prev_scenario(self, engine):
        """Tests the set_attackers_victims_anns without prev_scenario

        Ensures that attackers and victims are randomly chosen
        """

        random.seed(0)
        scenario = SubprefixHijack(
            scenario_config=ScenarioConfig(ScenarioCls=SubprefixHijack), engine=engine
        )
        scenario_2 = SubprefixHijack(
            scenario_config=ScenarioConfig(ScenarioCls=SubprefixHijack), engine=engine
        )

        assert scenario.attacker_asns != scenario_2.attacker_asns
        assert scenario.victim_asns != scenario_2.victim_asns

    def test_set_attackers_victims_preset(self, engine):
        """Tests that the attackers/victims don't change if they were preset

        and tests that they do change if they weren't preset
        """

        attacker_asns = frozenset({1})
        victim_asns = frozenset({2})
        scenario = SubprefixHijack(
            scenario_config=ScenarioConfig(
                ScenarioCls=SubprefixHijack,
                override_attacker_asns=attacker_asns,
                override_victim_asns=victim_asns,
            ),
            engine=engine,
        )
        assert scenario.attacker_asns == attacker_asns, scenario.attacker_asns
        assert scenario.victim_asns == victim_asns, scenario.victim_asns

    def test_set_attackers_victims_not_preset(self, engine):
        """Tests that the attackers/victims change when not preset"""

        # No preset attacker and victim asns
        scenario = SubprefixHijack(
            scenario_config=ScenarioConfig(ScenarioCls=SubprefixHijack), engine=engine
        )
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
        scenario_config = ScenarioConfig(
            ScenarioCls=SubprefixHijack, num_attackers=num_attackers
        )
        scenario = SubprefixHijack(scenario_config=scenario_config, engine=engine)
        attacker_asns = scenario._get_attacker_asns(
            override_attacker_asns=None, prev_attacker_asns=None, engine=engine
        )
        # Check for #1
        assert attacker_asns
        # Check for #2 (and therefore #4 as well)
        assert len(attacker_asns) == num_attackers
        # Check for number 3
        attacker_asns_2 = scenario._get_attacker_asns(
            override_attacker_asns=None, prev_attacker_asns=None, engine=engine
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
        scenario_config = ScenarioConfig(
            ScenarioCls=NonRoutedPrefixHijack, num_victims=2
        )
        scenario = NonRoutedPrefixHijack(scenario_config=scenario_config, engine=engine)
        victim_asns = scenario._get_victim_asns(
            override_victim_asns=None, prev_victim_asns=None, engine=engine
        )
        # Check for #1
        assert victim_asns
        # Check for #2 (and therefore #4 as well)
        assert len(victim_asns) == num_victims
        # Check for number 3
        victim_asns_2 = scenario._get_victim_asns(
            override_victim_asns=None, prev_victim_asns=None, engine=engine
        )

        assert victim_asns != victim_asns_2
        # Check for #5 TODO: make this better by checking for __all__
        for attacker_asn in scenario.attacker_asns:
            assert attacker_asn not in victim_asns
            assert attacker_asn not in victim_asns_2

    def test_get_possible_attacker_asns(self, engine):
        """Tests the possible attacker asns

        Ensures that a set is returned filled with at least a few ases
        """
        scenario = SubprefixHijack(
            scenario_config=ScenarioConfig(ScenarioCls=SubprefixHijack), engine=engine
        )
        assert scenario._get_possible_attacker_asns(engine=engine, percent_adoption=0.5)

    def test_get_possible_victim_asns(self, engine):
        """Tests that a set is returned with at least a few ases"""

        scenario = SubprefixHijack(
            scenario_config=ScenarioConfig(ScenarioCls=SubprefixHijack), engine=engine
        )
        assert scenario._get_possible_victim_asns(engine=engine, percent_adoption=0.5)

    def test_get_announcements(self, engine):
        """Tests the get_announcements of a subclass of scenario

        Ensures that announcements are returned and returned properly
        """

        scenario = SubprefixHijack(
            scenario_config=ScenarioConfig(ScenarioCls=SubprefixHijack), engine=engine
        )
        # Victim prefix, subprefix attacker
        assert len(scenario.announcements) == 2
        for victim_asn in scenario.victim_asns:
            assert any(victim_asn == x.seed_asn for x in scenario.announcements)
        for attacker_asn in scenario.attacker_asns:
            assert any(attacker_asn == x.seed_asn for x in scenario.announcements)

    def test_no_attackers(self, engine):
        """
        Ensures that get_attacker_asns is empty if override_attacker_asns is an empty
        set.

        This trivial test ensures that the method does not regress to previous
        behavior, where a random attacker was selected.
        """
        override_attackers = frozenset[int]()
        config = ScenarioConfig(
            ScenarioCls=SubprefixHijack,
            num_attackers=0,
            override_attacker_asns=override_attackers,
        )
        scenario = SubprefixHijack(scenario_config=config, engine=engine)
        attackers = scenario._get_attacker_asns(override_attackers, None, engine)

        assert attackers == frozenset()

    def test_no_victims(self, engine):
        """
        Ensures that get_victim_asns is empty if override_victim_asns is an empty
        set.

        This trivial test ensures that the method does not regress to previous
        behavior, where a random victim was selected.
        """
        override_victims = frozenset[int]()
        config = ScenarioConfig(
            ScenarioCls=ValidPrefix,  # SubprefixHijack wont't work bc it needs 1 victim
            num_victims=0,
            override_victim_asns=override_victims,
        )
        scenario = ValidPrefix(scenario_config=config, engine=engine)
        victims = scenario._get_victim_asns(override_victims, None, engine)

        assert victims == frozenset()

    def test_add_roa_info_to_anns(self, engine):
        """
        Tests that add_roa_info_to_anns maintains the correct number of announcements
        and defines the appropriate ROA information for valid and malicious
        announcements.
        """
        # Subprefix hijack where attacker 666 sends a more specific prefix
        victim = ASNs.VICTIM.value
        attacker = ASNs.ATTACKER.value
        anns = (
            Announcement(prefix="1.2.0.0/16", as_path=(victim,), seed_asn=victim),
            Announcement(prefix="1.2.0.0/24", as_path=(attacker,), seed_asn=attacker),
        )
        roas = (ROA(prefix=ip_network("1.2.0.0/16"), origin=victim),)

        config = ScenarioConfig(
            ScenarioCls=ValidPrefix,
            override_victim_asns=frozenset({victim}),
            override_attacker_asns=frozenset({attacker}),
            override_announcements=anns,
            override_roas=roas,
        )
        scenario = ValidPrefix(scenario_config=config, engine=engine)
        bgp = BGP()
        # Check we still have the right anns
        assert len(scenario.announcements) == len(anns)
        valid, malicious = scenario.announcements

        # First announcement should be validated by ROA
        assert (
            next(
                iter(bgp.roa_checker.get_relevant_roas(ip_network(valid.prefix)))
            ).origin
            == victim
        )
        assert bgp.ann_is_valid_by_roa(valid)

        # Second announcement, from a different origin and more specific prefix, should
        # be invalidated
        assert (
            next(
                iter(bgp.roa_checker.get_relevant_roas(ip_network(malicious.prefix)))
            ).origin
            == victim
        )
        assert bgp.ann_is_invalid_by_roa(malicious)

    #######################
    # Adopting ASNs funcs #
    #######################

    def test_default_adopters(self, engine):
        """Ensures that the default adopters returns the victims"""

        assert SubprefixHijack(
            scenario_config=ScenarioConfig(
                ScenarioCls=SubprefixHijack, override_victim_asns=frozenset({1})
            ),
            engine=engine,
        )._default_adopters == {1}

    def test_default_non_adopters(self, engine):
        """Tests that the attacker does not adopt"""

        assert SubprefixHijack(
            scenario_config=ScenarioConfig(
                ScenarioCls=SubprefixHijack, override_attacker_asns=frozenset({1})
            ),
            engine=engine,
        )._default_non_adopters == {1}

    def test_preset_asns(self, engine):
        """Tests that the preset ASNs is the union of default ASNs"""

        hijack = SubprefixHijack(
            scenario_config=ScenarioConfig(
                ScenarioCls=SubprefixHijack,
                override_attacker_asns=frozenset({1}),
                override_victim_asns=frozenset({2}),
            ),
            engine=engine,
        )
        assert hijack._preset_asns == {1, 2}

    def test_post_propagation_hook(self, engine):
        """Test that the post_propagation_hook doesn't error"""

        SubprefixHijack(
            scenario_config=ScenarioConfig(ScenarioCls=SubprefixHijack), engine=engine
        ).post_propagation_hook(engine, percent_adopt=0.5, trial=0, propagation_round=0)

    ################
    # Helper Funcs #
    ################

    def test_get_ordered_prefix_subprefix_dict(self, engine):
        """Tests that the get_ordered_prefix_subprefix_dict works"""

        scenario = SubprefixHijack(
            scenario_config=ScenarioConfig(ScenarioCls=SubprefixHijack), engine=engine
        )
        gt = {
            Prefixes.PREFIX.value: [Prefixes.SUBPREFIX.value],
            Prefixes.SUBPREFIX.value: [],
        }
        assert scenario.ordered_prefix_subprefix_dict == gt
