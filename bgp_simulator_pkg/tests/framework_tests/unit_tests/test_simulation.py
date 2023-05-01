import pytest


@pytest.mark.framework
@pytest.mark.unit_tests
class TestSimulation:
    @pytest.mark.skip(reason="TODO")
    def test_init(self):
        """Tests init func

        1. Ensures scenarios are unique
        2. Ensures that the caida collector is cached
        """

        raise NotImplementedError

    # Omitted due to system tests (far more comprehensive)
    # def test_run(self):

    @pytest.mark.skip(reason="TODO")
    def test_write_data(self):
        """Tests that data is written and zipped

        Ensures that all subgraphs and JSON results are written
        """

        raise NotImplementedError

    @pytest.mark.skip(
        reason=("Low priority, doesn't affect data, " "high effort due to randomness")
    )
    def test_get_data_multiprocess_vs_single(self):
        """Tests that the multiprocess and single process are the same"""

        raise NotImplementedError

    @pytest.mark.skip(reason="Low priority, doesn't affect data")
    def test_get_data_single_process(self):
        """Tests that ONLY single_process_results get run properly

        (when self.parse_cpus == 1)
        """

        raise NotImplementedError

    @pytest.mark.skip(reason="Low priority, doesn't affect data")
    def test_get_data_multiprocess(self):
        """Ensure that mp is called when self.parse_cpus > 1"""

        raise NotImplementedError

    @pytest.mark.skip(
        reason=(
            "Low priority, checked a lot by hand, "
            "tests could never acct for all cases"
        )
    )
    def test_get_data(self):
        """Tests that the subgraphs aggregate properly"""

        raise NotImplementedError

    @pytest.mark.skip(reason="TODO")
    def test_get_chunks(self):
        """Tests that everything is chunked properly with an example"""

        raise NotImplementedError

    @pytest.mark.skip(
        reason=(
            "Low priority, checked a lot by hand, "
            "tests could never acct for all cases"
        )
    )
    def test_get_single_process_results(self):
        """Tests a sample set of results"""

        raise NotImplementedError

    @pytest.mark.skip(
        reason=(
            "Low priority, checked a lot by hand, "
            "tests could never acct for all cases"
        )
    )
    def test_get_multi_process_results(self):
        """Tests a sample set of results"""

        raise NotImplementedError

    @pytest.mark.skip(
        reason=(
            "Low priority, checked a lot by hand, "
            "tests could never acct for all cases"
        )
    )
    def test_run_chunk(self):
        """Tests the running of a chunk

        1. Test that each percent adopt and trial gets run
        2. Ensure that each scenario gets run over each percent adopt and trial
        3. Ensure that at the start of each new percent adopt/trial,
        scenario resets
        4. Ensure that round to round, engine gets reset
        5. Ensure that data is aggegated properly - potentially with examples
        """

        raise NotImplementedError

    @pytest.mark.skip(
        reason=(
            "Low priority, checked a lot by hand, "
            "tests could never acct for all cases"
        )
    )
    def test_aggregate_engine_run_data(self):
        """Tests that the data is aggregated properly with examples"""

        raise NotImplementedError
