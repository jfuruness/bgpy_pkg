from lib_caida_collector import CaidaCollector
from lib_utils import Base


class Simulator(Base):
    """Runs simulations for BGP attack/defend scenarios"""

    def run(self,
            num_trials=1,
            graphs=[],
            base_as=[]):
        """Downloads relationship data, runs simulation"""

        self._download_relationships()
        self._download_as_rank()

    def _download_relationships(self):
        pass

    def _download_as_rank(self):
        pass
