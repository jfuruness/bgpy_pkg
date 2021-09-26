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

    def run(self, announcements, propagation_round=0):
        """Propogates announcements"""

        self._seed(announcements, propagation_round)
        self._propagate()

    def _seed(self, announcements: list, propagation_round: int):
        """Seeds/inserts announcements into the BGP DAG"""

        for ann in announcements:
            assert isinstance(ann, Announcement)

        for ann in announcements:
            # Let the announcement do the seeding
            # That way it's easy for anns to seed with path manipulation
            # Simply inherit the announcement class
            ann.seed(self.as_dict, propagation_round)

    def _propagate(self):
        """Propogates announcements"""

        for i, rank in enumerate(self.propagation_ranks):

            # print(f"propogating up with rank {i}/{len(self.propagation_ranks)} of len {len(rank)}")
            # Nothing to process at the start
            if i > 0:
                # Process first because maybe it recv from lower ranks
                for as_obj in rank:
                    as_obj.process_incoming_anns(Relationships.CUSTOMERS)
            # Send to the higher ranks
            for as_obj in rank:
                as_obj.propagate_to_providers()
            #print("\npropagated to providers for this rank")
            #print(self)

            # MUST propagate peers then process
            # Or else peers will not have ann to process yet
            for as_obj in rank:
                as_obj.propagate_to_peers()
            for as_obj in rank:
                as_obj.process_incoming_anns(Relationships.PEERS)
            #print("\npropagated to peers for this rank")
            #print(self)


        for i, rank in enumerate(reversed(self.propagation_ranks)):
            # print(f"propogating down with rank {len(self.propagation_ranks) -i}/{len(self.propagation_ranks)}")
            # There are no incomming Anns at the top
            if i > 0:
                for as_obj in rank:
                    as_obj.process_incoming_anns(Relationships.PROVIDERS)
            for as_obj in rank:
                as_obj.propagate_to_customers()

    def __str__(self):
        string = ""
        for as_obj in self:
            string += f"{as_obj.asn}:\n"
            for ann in as_obj.local_rib.values():
                string += f"\t{str(ann)}\n"
        return string
