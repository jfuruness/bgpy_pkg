#include <iostream>
#include <algorithm>
#include <stdexcept>

#include "policy.hpp"
#include "bgp_simple_policy.hpp"
#include "as.hpp"

///////////BGPSimple implementation. Done outside of the class to avoid circular ref with AS
void BGPSimplePolicy::process_incoming_anns(Relationships from_rel, int propagation_round, bool reset_q) {
    // Process all announcements that were incoming from a specific relationship

    // For each prefix, get all announcements received
    for (const auto& [prefix, ann_list] : recvQueue.prefix_anns()) {
        // Get announcement currently in local RIB
        auto current_ann = localRIB.get_ann(prefix);

        // Check if current announcement is seeded; if so, continue
        if (current_ann && current_ann->seed_asn.has_value()) {
            continue;
        }

        std::shared_ptr<Announcement> og_ann = current_ann;

        // For each announcement that was incoming
        for (const auto& new_ann : ann_list) {
            // Make sure there are no loops
            if (valid_ann(new_ann, from_rel)) {
                auto new_ann_processed = copy_and_process(new_ann, from_rel);

                current_ann = get_best_ann_by_gao_rexford(current_ann, new_ann_processed);
            }
        }

        // This is a new best announcement. Process it and add it to the local RIB
        if (og_ann != current_ann) {
            // Save to local RIB
            localRIB.add_ann(current_ann);
        }
    }

    reset_queue(reset_q);
}

void BGPSimplePolicy::receive_ann(const std::shared_ptr<Announcement>& ann) {
    recvQueue.add_ann(ann);
}

bool BGPSimplePolicy::valid_ann(const std::shared_ptr<Announcement>& ann, Relationships recv_relationship) const {
    // BGP Loop Prevention Check
    if (auto as_ptr = as.lock()) { // Safely obtain a shared_ptr from weak_ptr
        return std::find(ann->as_path.begin(), ann->as_path.end(), as_ptr->asn) == ann->as_path.end();
    }else{
        throw std::runtime_error("AS pointer is not valid.");
    }
}
std::shared_ptr<Announcement> BGPSimplePolicy::copy_and_process(const std::shared_ptr<Announcement>& ann, Relationships recv_relationship) {
    // Check for a valid 'AS' pointer
    auto as_ptr = as.lock();
    if (!as_ptr) {
        throw std::runtime_error("AS pointer is not valid.");
    }

    // Creating a new announcement with modified attributes
    std::vector<int> new_as_path = {as_ptr->asn};
    new_as_path.insert(new_as_path.end(), ann->as_path.begin(), ann->as_path.end());

    // Return a new Announcement object with the modified AS path and recv_relationship
    return std::make_shared<Announcement>(
        ann->prefix,
        new_as_path,
        ann->timestamp,
        ann->seed_asn,
        ann->roa_valid_length,
        ann->roa_origin,
        recv_relationship,
        ann->withdraw,
        ann->traceback_end,
        ann->communities
    );
}

void BGPSimplePolicy::reset_queue(bool reset_q) {
    if (reset_q) {
        // Reset the recvQueue by replacing it with a new instance
        recvQueue = RecvQueue();
    }
}
