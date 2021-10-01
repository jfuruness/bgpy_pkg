from lib_caida_collector import BGPDAG


from .bgp_as import BGPAS
from ..enums import Relationships
from ..announcement import Announcement


class SimulatorEngine(BGPDAG):
    __slots__ = []

    def __init__(self,
                 *args,
                 BaseASCls=BGPAS,
                 **kwargs):
        super(SimulatorEngine, self).__init__(*args,
                                              BaseASCls=BaseASCls,
                                              **kwargs)

    def run(self, announcements, propagation_round=0, attack=None):
        """Propogates announcements"""

        self._seed(announcements, propagation_round)
        self._propagate(propagation_round, attack)

    def _seed(self, announcements: list, propagation_round: int):
        """Seeds/inserts announcements into the BGP DAG"""

        for ann in announcements:
            assert isinstance(ann, Announcement)

        for ann in announcements:
            # Let the announcement do the seeding
            # That way it's easy for anns to seed with path manipulation
            # Simply inherit the announcement class
            ann.seed(self.as_dict, propagation_round)

    def _propagate(self, propagation_round, attack):
        """Propogates announcements"""

        for i, rank in enumerate(self.propagation_ranks):
            # Nothing to process at the start
            if i > 0:
                # Process first because maybe it recv from lower ranks
                for as_obj in rank:
                    as_obj.process_incoming_anns(Relationships.CUSTOMERS, propagation_round=propagation_round, attack=attack)
            # Send to the higher ranks
            for as_obj in rank:
                as_obj.propagate_to_providers()

        # The reason you must separate this for loop here is because propagation ranks do not take into account peering
        # It'd be impossible to take into account peering since different customers peer to different ranks
        # So first do customer to provider propagation, then peer propagation
        for as_obj in self:
            as_obj.propagate_to_peers()
        for as_obj in self:
            as_obj.process_incoming_anns(Relationships.PEERS, propagation_round=propagation_round, attack=attack)


        for i, rank in enumerate(reversed(self.propagation_ranks)):
            # There are no incomming Anns at the top
            if i > 0:
                for as_obj in rank:
                    as_obj.process_incoming_anns(Relationships.PROVIDERS, propagation_round=propagation_round, attack=attack)
            for as_obj in rank:
                as_obj.propagate_to_customers()

    def __str__(self):
        string = ""
        for as_obj in self:
            string += f"{as_obj.asn}:\n"
            for ann in as_obj.local_rib.values():
                string += f"\t{str(ann)}\n"
        return string
