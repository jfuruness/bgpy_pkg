#include <iostream>
#include <algorithm>
#include <stdexcept>

#include "policy.hpp"
#include "bgp_simple_policy.hpp"
#include "as.hpp"
/*
///////////BGPSimple implementation. Done outside of the class to avoid circular ref with AS
void BGPSimplePolicy::process_incoming_anns(Relationships from_rel, int propagation_round, bool reset_q) {
    // Process all announcements that were incoming from a specific relationship

    // For each prefix, get all announcements received
    for (const auto& [prefix, ann_list] : recvQueue.prefix_anns()) {
        if (ann_list.size() == 0){
            continue;
        }
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
*/
///////////BGPSimple implementation. Done outside of the class to avoid circular ref with AS
void BGPSimplePolicy::process_incoming_anns(Relationships from_rel, int propagation_round, bool reset_q) {
    // Process all announcements that were incoming from a specific relationship

    // For each prefix, get all announcements received
    //for (const auto& [prefix_block_id, ann_list] : recvQueue.prefix_anns()) {
    for (unsigned short int prefix_block_id = 0; prefix_block_id < static_cast<unsigned short int>(recvQueue.prefix_anns().size()); ++prefix_block_id) {
        const auto& ann_list = recvQueue.prefix_anns()[prefix_block_id];
        if(ann_list.size() == 0){
            continue;
        }
        // Get announcement currently in local RIB
        auto current_ann = localRIB.get_ann(prefix_block_id);

        /*
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
        */
        bool current_ann_processed = true;
        // For each announcement that was incoming
        for (const auto& new_ann : ann_list) {
            // Make sure there are no loops
            if (valid_ann(new_ann, from_rel)) {
                if (!current_ann){
                    current_ann = new_ann;
                    current_ann_processed = false;
                    continue;
                }

                if (current_ann_processed){
                    if (current_ann->recv_relationship > from_rel) {
                        continue;
                    } else if (current_ann->recv_relationship < from_rel) {
                        current_ann = new_ann;
                        current_ann_processed = false;
                        continue;
                    }
                }

                if (current_ann_processed){
                     if (current_ann->as_path.size() < new_ann->as_path.size() + 1) {
                        continue;
                    } else if (current_ann->as_path.size() > new_ann->as_path.size() + 1) {
                        current_ann = new_ann;
                        current_ann_processed = false;
                        continue;
                    }
                }
                else{
                     if (current_ann->as_path.size() < new_ann->as_path.size()) {
                        continue;
                    } else if (current_ann->as_path.size() > new_ann->as_path.size()) {
                        current_ann = new_ann;
                        current_ann_processed = false;
                        continue;
                    }

                }

                if (current_ann_processed){
                    int current_neighbor_asn = current_ann->as_path.size() > 1 ? current_ann->as_path[1] : current_ann->as_path[0];
                    int new_neighbor_asn = new_ann->as_path.size() > 1 ? new_ann->as_path[1] : new_ann->as_path[0];

                    if (current_neighbor_asn <= new_neighbor_asn) {
                        continue;
                    } else {
                        current_ann = new_ann;
                        current_ann_processed = false;
                        continue;

                    }
                } else {
                    int current_neighbor_asn = current_ann->as_path[0];
                    int new_neighbor_asn = new_ann->as_path[0];

                    if (current_neighbor_asn <= new_neighbor_asn) {
                        continue;
                    } else {
                        current_ann = new_ann;
                        current_ann_processed = false;
                        continue;

                    }

                }

                throw std::runtime_error("you shouldnt reach this pt");


                //current_ann = get_best_ann_by_gao_rexford(current_ann, new_ann_processed);
            }
        }

        // This is a new best announcement. Process it and add it to the local RIB
        if (!current_ann_processed) {
            // Save to local RIB
            localRIB.add_ann(copy_and_process(current_ann, from_rel));
        }


    }

    reset_queue(reset_q);
}

void BGPSimplePolicy::receive_ann(const std::shared_ptr<Announcement>& ann) {
    recvQueue.add_ann(ann);
}

bool BGPSimplePolicy::valid_ann(const std::shared_ptr<Announcement>& ann, Relationships recv_relationship) const {

                    std::cout<<"valid_ann1"<<std::endl;
    // BGP Loop Prevention Check
    if (auto as_ptr = as.lock()) { // Safely obtain a shared_ptr from weak_ptr

                    std::cout<<"valid_ann2"<<std::endl;
        for (auto as_path_int : ann->as_path){
            std::cout<<as_path_int<<std::endl;
        }
            std::cout<<"valid ann 3"<<std::endl;
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
    std::vector<int> new_as_path(ann->as_path.size() + 1);
    new_as_path[0] = as_ptr->asn;
    //Complete - change the line below
    for (size_t i = 0; i < ann->as_path.size(); ++i) {
        new_as_path[i + 1] = ann->as_path[i];
    }

    // Return a new Announcement object with the modified AS path and recv_relationship
    return std::make_shared<Announcement>(
        ann->prefix_block_id,
        ann->staticData,
        new_as_path,
        recv_relationship,
        false
    );
}

void BGPSimplePolicy::reset_queue(bool reset_q) {
    if (reset_q) {
        // Reset the recvQueue by replacing it with a new instance
        recvQueue.reset(max_prefix_block_id);// = RecvQueue(max_prefix_block_id);
    }
}
