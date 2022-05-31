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
        self.data = defaultdict(list)

    @abstractmethod
    def aggregate_data_from_engine_run(self,
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
        """

        raise NotImplementedError
