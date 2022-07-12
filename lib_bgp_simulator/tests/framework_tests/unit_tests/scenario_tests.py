import pytest


@pytest.mark.skip(reason="Templating out for later")
class TestScenario:
    def test_init(self):
        """Tests the validation checks in the init

        1. Ensures that the number of attackers are == attacker_asns if set
        2. Same as 1, but for victim asns
        3. Ensures the attacker_victim_asns_preset is correct
        """

        raise NotImplementedError

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

    def finish_tests(self):
        raise NotImplementedError("SEE COMMENTS BELOW")

# Must complete - adopting ASN funcs
# Engine manipulation funcs
# Helper funcs
