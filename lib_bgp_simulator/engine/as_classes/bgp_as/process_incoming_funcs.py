from lib_caida_collector import AS

from ...ann_containers import LocalRib
from ...ann_containers import RecvQueue
from ....enums import Relationships
from ....announcements import Announcement as Ann


def receive_ann(self, ann: Ann):
    self._recv_q.add_ann(ann)

def process_incoming_anns(self,
                          from_rel: Relationships,
                          *args,
                          propagation_round=None,
                          attack=None,  # Usually None
                          reset_q=True,
                          **kwargs):
    """Process all announcements that were incoming from a specific rel"""

    for prefix, ann_list in self._recv_q.prefix_anns():
        # Get announcement currently in local rib
        current_ann = self._local_rib.get_ann(prefix)
        current_processed = True

        # Seeded Ann will never be overriden, so continue
        if getattr(current_ann, "seed_asn", None) is not None:
            continue

        # For each announcement that was incoming
        for ann in ann_list:
            # Make sure there are no loops
            # In ROV subclass also check roa validity
            if self._valid_ann(ann, from_rel):
                new_ann_better = self._new_ann_better(current_ann,
                                                      current_processed,
                                                      from_rel,
                                                      ann,
                                                      False,
                                                      from_rel)
                if new_ann_better:
                    current_ann = ann
                    current_processed = False

        # This is a new best ann. Process it and add it to the local rib
        if current_processed is False:
            current_ann = self._copy_and_process(current_ann, from_rel)
            # Save to local rib
            self._local_rib.add_ann(current_ann)

    self._reset_q(reset_q)

def _valid_ann(self, ann, recv_relationship):
    """Determine if an announcement is valid or should be dropped"""

    # BGP Loop Prevention Check
    return not (self.asn in ann.as_path)

def _copy_and_process(self, ann, recv_relationship, **extra_kwargs):
    """Deep copies ann and modifies attrs"""

    kwargs = {"as_path": (self.asn,) + ann.as_path,
              "recv_relationship": recv_relationship}
    kwargs.update(extra_kwargs)

    return ann.copy(**kwargs)

def _reset_q(self, reset_q):
    if reset_q:
        self._recv_q = RecvQueue()
