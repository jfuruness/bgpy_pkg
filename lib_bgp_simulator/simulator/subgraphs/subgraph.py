from abc import ABC, abstractmethod
from collections import defaultdict


class Subgraph(ABC):
    """A subgraph for data display"""

    __slots__ = ("data",)

    def __init__(self):
        """Inits data"""

        # This is a list of all the trial info
        # You must save info trial by trial, so that you can join
        # After a return from multiprocessing
        # {scenario_label: {percent_adopt: [percentages]}}
        self.data = defaultdict(lambda: defaultdict(list))

    @abstractmethod
    def aggregate_engine_run_data(self,
                                  shared_data,
                                  engine,
                                  *,
                                  percent_adopt,
                                  trial,
                                  scenario,
                                  propagation_round):
        """Aggregates data after a single engine run

        Shared data is passed between subgraph classes and is
        mutable. This is done to speed up data aggregation, even
        though it is at the cost of immutability

        shared_data ex:
        {stubs_hijacked: int,
         stubs_hijacked_total: int,
         stubs_hijacked_percentage: float,
         stubs_hijacked_adopting: int
         stubs_hijacked_adopting_total: int,
         stubs_hijacked_adopting_percentage: float,
         stubs_hijacked_non_adopting: int,
         stubs_hijacked_non_adopting_total: int
         stubs_hijacked_non_adopting_percentage: float,
         ...
         }

        self.data ex:
        {scenario_label: {percent_adopt: [percents]}}
        """

        raise NotImplementedError

    def _add_traceback_to_shared_data(self, shared_data):
        """Adds traceback info to shared data"""

        outcomes = self._get_engine_outcomes()

    def _get_engine_outcomes(self):
        """Gets the outcomes of all ASes"""

        # {ASN: outcome}
        outcomes = dict()
        for as_obj in self.engine.as_dict.values():
            outcome[as_obj] = self._get_as_outcome(as_obj, outcomes

    # NOTE for next time:
    # Copy most of the existing functionality to the subgraph
    # Esp because subgraph decides how to aggregate data
    # Not a specific scenario
    # That is the sole purpose of the subgraph
    # After you get the traceback function coded, add logic so that
    # It doesn't repeat itself between each subgraph
    # Then add logic to add the info the self.data
    # Then go back into the graph func and aggregate self.data
    # Then add logic to graph
    # Then run it
    # Then start working on refactoring the tests to ensure they work,
    # considering things like how to add the exr to this
