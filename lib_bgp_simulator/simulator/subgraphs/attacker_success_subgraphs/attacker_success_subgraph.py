from abc import ABC, abstractmethod
from collections import defaultdict

import ipaddress

from ..subgraph import Subgraph
from ....enums import Outcomes
from ....engine import BGPAS


class AttackerSuccessSubgraph(Subgraph):
    """A subgraph for data display"""

    @abstractmethod
    def _get_subgraph_key(self, *args):
        """Returns the key to be used in shared_data on the subgraph"""

        raise NotImplementedError
