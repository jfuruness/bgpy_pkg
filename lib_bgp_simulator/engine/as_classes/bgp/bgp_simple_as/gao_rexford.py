from typing import Optional

from .....announcements import Announcement as Ann
from .....enums import Relationships

opt_bool = Optional[bool]


def _new_ann_better(self,
                    current_ann: Optional[Ann],
                    current_processed: bool,
                    default_current_recv_rel: Relationships,
                    new_ann: Ann,
                    new_processed: Relationships,
                    default_new_recv_rel: Relationships,
                    **kwargs) -> opt_bool:
    """Assigns the priority to an announcement according to Gao Rexford

    NOTE: processed is processed for second ann"""

    # Can't assert this here due to passing new_ann as None
    # msg = "Should have been removed in the validation func"
    # assert self.asn not in new_ann.as_path, msg

    new_rel_better: opt_bool = self._new_rel_better(current_ann,
                                                    current_processed,
                                                    default_current_recv_rel,
                                                    new_ann,
                                                    new_processed,
                                                    default_new_recv_rel,
                                                    **kwargs)
    if new_rel_better is not None:
        return new_rel_better
    else:
        return self._new_as_path_ties_better(current_ann,
                                             current_processed,
                                             new_ann,
                                             new_processed,
                                             **kwargs)


def _new_as_path_ties_better(self,
                             current_ann: Optional[Ann],
                             current_processed: bool,
                             new_ann: Ann,
                             new_processed: bool,
                             **kwargs) -> opt_bool:

    new_as_path_shorter: opt_bool = self._new_as_path_shorter(
        current_ann,
        current_processed,
        new_ann,
        new_processed,
        **kwargs)

    if new_as_path_shorter is not None:
        return new_as_path_shorter
    else:
        return self._new_wins_ties(current_ann,
                                   current_processed,
                                   new_ann,
                                   new_processed,
                                   **kwargs)


def _new_rel_better(self,
                    current_ann: Optional[Ann],
                    current_processed: bool,
                    default_current_recv_rel: Relationships,
                    new_ann: Ann,
                    new_processed: bool,
                    default_new_recv_rel: Relationships,
                    **kwargs) -> opt_bool:
    if current_ann is None:
        return True
    elif new_ann is None:
        return False
    else:
        # Get relationship of current ann
        if current_processed:
            current_rel: Relationships = current_ann.recv_relationship
        else:
            current_rel: Relationships = default_current_recv_rel

        # Get relationship of new ann. Common case first
        if not new_processed:
            new_rel: Relationships = default_new_recv_rel
        else:
            new_rel: Relationships = new_ann.recv_relationship

    if current_rel.value > new_rel.value:
        return False
    elif current_rel.value < new_rel.value:
        return True
    else:
        return None


def _new_as_path_shorter(self,
                         current_ann: Optional[Ann],
                         current_processed: bool,
                         new_ann: Ann,
                         new_processed: bool,
                         **kwargs) -> opt_bool:
    current_as_path_len = len(current_ann.as_path) + int(not current_processed)
    new_as_path_len: int = len(new_ann.as_path) + int(not new_processed)
    if current_as_path_len < new_as_path_len:
        return False
    elif current_as_path_len > new_as_path_len:
        return True
    else:
        return None


def _new_wins_ties(self,
                   current_ann,
                   current_processed,
                   new_ann,
                   new_processed,
                   **kwargs) -> bool:
    # Gets the indexes of the neighbors
    current_index = min(int(current_processed), len(current_ann.as_path) - 1)
    new_index = min(int(new_processed), len(new_ann.as_path) - 1)

    return new_ann.as_path[new_index] < current_ann.as_path[current_index]
