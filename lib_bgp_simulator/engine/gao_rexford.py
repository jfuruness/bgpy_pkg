def _new_ann_better(policy_self,
                    self,
                    current_ann,
                    current_processed,
                    default_current_recv_rel,
                    new_ann,
                    new_processed,
                    default_new_recv_rel):
    """Assigns the priority to an announcement according to Gao Rexford

    NOTE: processed is processed for second ann"""

    # Can't assert this here due to passing new_ann as None
    # msg = "Should have been removed in the validation func"
    #assert self.asn not in new_ann.as_path, msg

    new_rel_better = policy_self._new_rel_better(current_ann,
                                                 current_processed,
                                                 default_current_recv_rel,
                                                 new_ann,
                                                 new_processed,
                                                 default_new_recv_rel)
    if new_rel_better is not None:
        return new_rel_better
    else:
        return policy_self._new_as_path_ties_better(current_ann,
                                                    current_processed,
                                                    new_ann,
                                                    new_processed)

def _new_as_path_ties_better(policy_self,
                             current_ann,
                             current_processed,
                             new_ann,
                             new_processed):
    new_as_path_shorter = policy_self._new_as_path_shorter(current_ann,
                                                           current_processed,
                                                           new_ann,
                                                           new_processed)
    if new_as_path_shorter is not None:
        return new_as_path_shorter
    else:
        return policy_self._new_wins_ties(current_ann,
                                          current_processed,
                                          new_ann,
                                          new_processed)

def _new_rel_better(policy_self,
                    current_ann,
                    current_processed,
                    default_current_recv_rel,
                    new_ann,
                    new_processed,
                    default_new_recv_rel):
    if current_ann is None:
        return True
    elif new_ann is None:
        return False
    else:
        # Get relationship of current ann
        if current_processed:
            current_rel = current_ann.recv_relationship
        else:
            current_rel = default_current_recv_rel

        # Get relationship of new ann. Common case first
        if not new_processed:
            new_rel = default_new_recv_rel
        else:
            new_rel = new_ann.recv_relatinship

    if current_rel.value > new_rel.value:
        return False
    elif current_rel.value < new_rel.value:
        return True
    else:
        return None


def _new_as_path_shorter(policy_self,
                         current_ann,
                         current_processed,
                         new_ann,
                         new_processed):
    current_as_path_len = len(current_ann.as_path) + int(not current_processed)
    new_as_path_len = len(new_ann.as_path) + int(not new_processed)
    if current_as_path_len < new_as_path_len:
        return False
    elif current_as_path_len > new_as_path_len:
        return True
    else:
        return None

def _new_wins_ties(policy_self,
                   current_ann,
                   current_processed,
                   new_ann,
                   new_processed) -> bool:
    # Gets the indexes of the neighbors
    current_index = min(int(current_processed), len(current_ann.as_path) - 1)
    new_index = min(int(new_processed), len(new_ann.as_path) - 1)
    # No ties!
    assert current_ann.as_path[current_index] != new_ann.as_path[new_index]

    return new_ann.as_path[new_index] < current_ann.as_path[current_index]
