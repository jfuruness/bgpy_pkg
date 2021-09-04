from lib_caida_collector import BGPDAG


from .bgp_as import BGPAS
from ..relationships import Relationships
from ..announcement import Announcement


class SimulatorEngine(BGPDAG):
    __slots__ = []

    def __init__(self,
                 *args,
                 BaseASCls=BGPAS,
                 as_policies=dict(),
                 **kwargs):
        super(SimulatorEngine, self).__init__(*args,
                                              BaseASCls=BaseASCls,
                                              **kwargs)

        from datetime import datetime
        start = datetime.now()
        print(start)
        for asn, Policy in as_policies.items():
            self.as_dict[asn].policy = Policy()
        print((datetime.now()-start).total_seconds())

    def run(self, announcements, save_path=None, clear=False):
        """Propogates announcements"""

        self._seed(announcements)

        #print("\nRanks. Later change to logging only for tests")
        #for rank in reversed(self.ranks):
        #    print([x.asn for x in rank])

        #print("\nlocal ribs post seed. Change to logging only for tests")
        #for as_obj in self.as_dict.values():
        #    print(f"{as_obj.asn} {as_obj.local_rib}")

        self._propagate()
        if save_path:
            self._save(save_path)
        if clear:
            self._clear()

    def _seed(self, announcements: list):
        """Seeds/inserts announcements into the BGP DAG"""

        for ann in announcements:
            assert isinstance(ann, Announcement)

        prefix_origins = list()
        for ann in announcements:
            # Let the announcement do the seeding
            # That way it's easy for anns to seed with path manipulation
            # Simply inherit the announcement class
            ann.seed(self.as_dict)
            prefix_origins.append((ann.prefix, ann.origin))

        msg = "You should never have overlapping prefix origin pairs"
        assert len(prefix_origins) == len(set(prefix_origins)), msg

    def _propagate(self):
        """Propogates announcements"""

        for i, rank in enumerate(self.propagation_ranks):

            print(f"propogating up with rank {i}/{len(self.propagation_ranks)} of len {len(rank)}")
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

            for as_obj in rank:
                as_obj.propagate_to_peers()
            for as_obj in rank:
                as_obj.process_incoming_anns(Relationships.PEERS)
            #print("\npropagated to peers for this rank")
            #print(self)


        for i, rank in enumerate(reversed(self.propagation_ranks)):
            print(f"propogating down with rank {len(self.propagation_ranks) -i}/{len(self.propagation_ranks)}")
            # There are no incomming Anns at the top
            if i > 0:
                for as_obj in rank:
                    as_obj.process_incoming_anns(Relationships.PROVIDERS)
            for as_obj in rank:
                as_obj.propagate_to_customers()

    def _save(self):
        """Saves DAG"""

        print("fill in save func")

    def _clear(self):
        """Clears DAG"""

        print("fill in clear func")

    def __str__(self):
        string = ""
        for as_obj in self:
            string += f"{as_obj.asn}:\n"
            for ann in as_obj.local_rib.values():
                string += f"\t{str(ann)}\n"
        return string
