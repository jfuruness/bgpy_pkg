from typing import Optional

from .....announcement import Announcement as Ann
from .....enums import Relationships

opt_bool = Optional[bool]


def _new_ann_better(self,
                    # Current announcement to check against
                    current_ann: Optional[Ann],
                    # Whether or not current ann has been processed local rib
                    # or if it resides in the ribs in
                    current_processed: bool,
                    # Default recv relationship if current ann is unprocessed
                    default_current_recv_rel: Relationships,
                    # New announcement
                    new_ann: Ann,
                    # If new announcement is in local rib, this is True
                    new_processed: Relationships,
                    # Default recv rel if new ann is unprocessed
                    default_new_recv_rel: Relationships,
                    ) -> opt_bool:
    """Determines if the new ann > current ann by Gao Rexford

    current_ann: Announcement we are checking against
    current_processed: True if announcement was processed (in local rib)
        This means that the announcement has the current as preprended
            to the AS path, and the proper recv_relationship set
    default_current_recv_rel:: Relationship for if the ann is unprocessed
    new_ann: New announcement
    new_processed: True if announcement was processed (in local rib)
        This means that the announcement has the current AS prepended
            to the AS path, and the proper recv_relationship set
    default_new_recv_rel: Relationship for if the ann is unprocessed
    """

    # Can't assert this here due to passing new_ann as None
    # msg = "Should have been removed in the validation func"
    # assert self.asn not in new_ann.as_path, msg

    # First check if new relationship is better
    new_rel_better: opt_bool = self._new_rel_better(current_ann,
                                                    current_processed,
                                                    default_current_recv_rel,
                                                    new_ann,
                                                    new_processed,
                                                    default_new_recv_rel)
    # If new rel better is True or False, return it
    if new_rel_better is not None:
        return new_rel_better
    else:
        # Return the outcome of as path and tiebreaks
        return self._new_as_path_ties_better(current_ann,
                                             current_processed,
                                             new_ann,
                                             new_processed)


def _new_as_path_ties_better(self,
                             current_ann: Optional[Ann],
                             current_processed: bool,
                             new_ann: Ann,
                             new_processed: bool
                             ) -> opt_bool:
    """Returns bool if new_ann > current_ann by gao rexford

    Specifically relating to as path and tie breaks

    current_ann: Announcement we are checking against
    current_processed: True if announcement was processed (in local rib)
        This means that the announcement has the current as preprended
            to the AS path, and the proper recv_relationship set
    new_ann: New announcement
    new_processed: True if announcement was processed (in local rib)
        This means that the announcement has the current AS prepended
            to the AS path, and the proper recv_relationship set
    """

    # Determine if the new as path is shorter
    new_as_path_shorter: opt_bool = self._new_as_path_shorter(
        current_ann,
        current_processed,
        new_ann,
        new_processed)

    # If new_as_path_shorter is True or False, return it
    if new_as_path_shorter is not None:
        return new_as_path_shorter
    # Otherwise it's a tie and we must tiebreak
    else:
        return self._new_wins_ties(current_ann,
                                   current_processed,
                                   new_ann,
                                   new_processed)


def _new_rel_better(self,
                    current_ann: Optional[Ann],
                    current_processed: bool,
                    default_current_recv_rel: Relationships,
                    new_ann: Ann,
                    new_processed: bool,
                    default_new_recv_rel: Relationships,
                    ) -> opt_bool:
    """Determines if the new ann > current ann by Gao Rexford/relationship

    current_ann: Announcement we are checking against
    current_processed: True if announcement was processed (in local rib)
        This means that the announcement has the current as preprended
            to the AS path, and the proper recv_relationship set
    default_current_recv_rel:: Relationship for if the ann is unprocessed
    new_ann: New announcement
    new_processed: True if announcement was processed (in local rib)
        This means that the announcement has the current AS prepended
            to the AS path, and the proper recv_relationship set
    default_new_recv_rel: Relationship for if the ann is unprocessed
    """

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
                         ) -> opt_bool:
    """Determines if the new ann > current ann by Gao Rexford for AS Path

    current_ann: Announcement we are checking against
    current_processed: True if announcement was processed (in local rib)
        This means that the announcement has the current as preprended
            to the AS path, and the proper recv_relationship set
    new_ann: New announcement
    new_processed: True if announcement was processed (in local rib)
        This means that the announcement has the current AS prepended
            to the AS path, and the proper recv_relationship set
    """

    # Remember, unprocessed anns do not have the current AS prepended to
    # the AS Path, so we have to account for this
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
                   ) -> bool:
    """Determines if the new ann > current ann by Gao Rexford for ties

    This breaks ties by lowest asn

    current_ann: Announcement we are checking against
    current_processed: True if announcement was processed (in local rib)
        This means that the announcement has the current as preprended
            to the AS path, and the proper recv_relationship set
    new_ann: New announcement
    new_processed: True if announcement was processed (in local rib)
        This means that the announcement has the current AS prepended
            to the AS path, and the proper recv_relationship set
    """

    # Remember, unprocessed Anns do not have the current AS prepended to the
    # AS Path, so we need to account for that

    # Gets the indexes of the neighbors
    current_index = min(int(current_processed), len(current_ann.as_path) - 1)
    new_index = min(int(new_processed), len(new_ann.as_path) - 1)

    return new_ann.as_path[new_index] < current_ann.as_path[current_index]
