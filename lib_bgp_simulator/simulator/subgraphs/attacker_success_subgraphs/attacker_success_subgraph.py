from abc import ABC, abstractmethod
from collections import defaultdict

import ipaddress

from ..subgraph import Subgraph
from ....enums import Outcomes
from ....engine import BGPAS


class AttackerSuccessSubgraph(Subgraph):
    """A subgraph for data display"""

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
