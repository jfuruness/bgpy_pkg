from abc import ABC, abstractmethod
from collections import defaultdict

import ipaddress

from ..attacker_success_subgraph import AttackerSuccessSubgraph
from .....enums import Outcomes
from .....engine import BGPAS


class AttackerSuccessAdoptingStubsAndMHSubgraph(AttackerSuccessSubgraph):
    """Graph for attacker success with adopting stubs or multihomed ASes"""

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
