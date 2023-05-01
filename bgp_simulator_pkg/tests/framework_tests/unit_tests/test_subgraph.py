import pytest


@pytest.mark.framework
@pytest.mark.unit_tests
class TestSubgraphs:
    @pytest.mark.skip(reason="TODO")
    def test_write_graph(self):
        """Tests that the graph gets written properly"""

        raise NotImplementedError

    @pytest.mark.skip(
        reason=(
            "Low priority, checked a lot by hand and tests "
            "couldn't account for all cases"
        )
    )
    def test_add_trial_info(self):
        """Tests adding trial info to another subgraph"""

        raise NotImplementedError

    @pytest.mark.skip(
        reason=(
            "Low priority, checked a lot by hand and tests "
            "couldn't account for all cases"
        )
    )
    def test_aggregate_engine_run_data(self):
        """Tests aggregate_engine_run_data

        1. outcomes and shared data must only be set once
        2. data must be added to self.data properly (use examples)
        """

        raise NotImplementedError

    @pytest.mark.skip(
        reason=(
            "Low priority, checked a lot by hand and tests "
            "couldn't account for all cases"
        )
    )
    def test_add_traceback_to_shared_data(self):
        """Tests add_traceback_to_shared_data with examples"""

        raise NotImplementedError

    # The system tests test the outcomes
    # Which is way more extensive than anything we could write
    # def test_traceback_funcs(self):
    #     pass
