import pytest


@pytest.mark.skip(reason="Templating out for later")
class TestScenario:
    def test_init(self):
        """Tests the validation checks in the init

        1. Ensures that the number of attackers are == attacker_asns if set
        2. Same as 1, but for victim asns
        3. Ensures the attacker_victim_asns_preset is correct
        4. Checks for the AdoptASCls to be correct (even if None)
        """

        raise NotImplementedError

##############################################
# Set Attacker/Victim and Announcement Funcs #
##############################################

    def test_set_attackers_victims_anns_w_prev_scenario(self):
        """Tests the set_attackers_victims_anns with prev_scenario

        Ensures that attackers and victims are the same as the last
        scenario that was run
        """

        raise NotImplementedError

    def test_set_attackers_victims_anns_wout_prev_scenario(self):
        """Tests the set_attackers_victims_anns without prev_scenario

        Ensures that attackers and victims are randomly chosen
        """

        raise NotImplementedError

    def test_set_attackers_victims(self):
        """Tests that the attackers/victims don't change if they were preset

        and tests that they do change if they weren't preset

        Note for dev: parameterize this!
        """

        raise NotImplementedError

    def test_get_attacker_asns(self):
        """Tests that get_attacker_asns

        1. chooses attacker(s)
        2. That the number of attackers are equal to number of num_attackers
        3. That the selection is random
        4. That the selection is without replacement
        """

        raise NotImplementedError

    def test_get_victim_asns(self):
        """Tests that get_victim_asns

        1. chooses victim(s)
        2. That the number of victims are equal to number of num_victims
        3. That the selection is random
        4. That the selection is without replacement
        5. That no victims are attackers!!
        """

        raise NotImplementedError

    def test_get_possible_attacker_asns(self):
        """Tests the possible attacker asns

        Ensures that a set is returned filled with at least a few ases
        """

        raise NotImplementedError

    def test_get_possible_victim_asns(self):
        """Tests that a set is returned with at least a few ases"""

        raise NotImplementedError

    def test_get_announcements(self):
        """Tests the get_announcements of a subclass of scenario

        Ensures that announcements are returned and returned properly
        """

        raise NotImplementedError

#######################
# Adopting ASNs funcs #
#######################

    def test_get_non_default_as_cls_dict_prev_scenario_adopt(self):
        """Tests that the non default as cls dict is set properly

        Old scenario must have mixed deployment to test that feature as well
        So old scenario must have three types of ASes:
        BaseASCls
        DefaultASCls
        AdoptASCls
        """

        raise NotImplementedError

    def test_get_non_default_as_cls_dict_prev_scenario_no_adopt(self):
        """Tests that the non default as cls dict is set properly

        Old scenario must have mixed deployment but no adopting ASes!
        So old scenario must have two types of ASes:
        BaseASCls
        DefaultASCls
        """

        raise NotImplementedError

    def test_get_non_default_as_cls_dict_no_prev_scenario_no_adopt(self):
        """Tests that the non default as cls dict is set properly

        No prev_scenario and no adopt AS Cls - should be the result of the
        get_adopting_asns_dict
        """

        raise NotImplementedError

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

        raise NotImplementedError

    def test_default_non_adopters(self):
        """Tests that the attacker does not adopt"""

        raise NotImplementedError

    def test_preset_asns(self):
        """Tests that the preset ASNs is the union of default ASNs"""

        raise NotImplementedError

    def test_determine_as_outcome(self):
        """Tests every possible condition for AS outcomes

        Probably split this into multiple tests
        """

        raise NotImplementedError

#############################
# Engine Manipulation Funcs #
#############################

    def test_setup_engine(self):
        """Tests setup_engine func

        1. Ensures attackers and victims are set properly
        2. Ensures the engines AS classes are correcct
        3. Ensures the announcements are seeded
        """

        raise NotImplementedError

    def test_set_engine_as_classes(self):
        """Tests that the engine as classes are set properly

        1. Ensures that non default AS class dict doesn't contain BaseASCls
        2. Ensures that AS classes get reset
        3. Ensures that AS init gets called, but relationships remain
        """

        raise NotImplementedError

    def test_seed_engine_announcements(self):
        """Tests the seeding of engine announcements

        1. Ensure you can't replace seeded announcements
        2. Ensure an AS has recieved the announcement
        """

        raise NotImplementedError

    def test_post_propagation_hook(self):
        """Test that the post_propagation_hook doesn't error"""

        raise NotImplementedError

################
# Helper Funcs #
################

    def test_get_ordered_prefix_subprefix_dict(self):
        """Tests that the get_ordered_prefix_subprefix_dict works"""

        raise NotImplementedError
