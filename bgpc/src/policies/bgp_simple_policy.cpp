#include <iostream>
#include <algorithm>
#include <stdexcept>

#include "policy.hpp"
#include "bgp_simple_policy.hpp"
#include "as.hpp"

BGPSimplePolicy::BGPSimplePolicy() : Policy() {
    std::cout << "in bgpsimple" << std::endl;
    initialize_gao_rexford_functions();
    std::cout << "out bgpsimple" << std::endl;
}

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
void BGPSimplePolicy::propagate_to_providers() {
    std::set<Relationships> send_rels = {Relationships::ORIGIN, Relationships::CUSTOMERS};
    propagate(Relationships::PROVIDERS, send_rels);
}

void BGPSimplePolicy::propagate_to_customers() {
    std::set<Relationships> send_rels = {Relationships::ORIGIN, Relationships::CUSTOMERS, Relationships::PEERS, Relationships::PROVIDERS};
    propagate(Relationships::CUSTOMERS, send_rels);
}

void BGPSimplePolicy::propagate_to_peers() {
    std::set<Relationships> send_rels = {Relationships::ORIGIN, Relationships::CUSTOMERS};
    propagate(Relationships::PEERS, send_rels);
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


/////////////////////////////////////////// gao rexford

void BGPSimplePolicy::initialize_gao_rexford_functions() {

    std::cout<<"in init gao"<<std::endl;
    gao_rexford_functions = {
        std::bind(&BGPSimplePolicy::get_best_ann_by_local_pref, this, std::placeholders::_1, std::placeholders::_2),
        std::bind(&BGPSimplePolicy::get_best_ann_by_as_path, this, std::placeholders::_1, std::placeholders::_2),
        std::bind(&BGPSimplePolicy::get_best_ann_by_lowest_neighbor_asn_tiebreaker, this, std::placeholders::_1, std::placeholders::_2)
    };

    std::cout<<"end init gao"<<std::endl;
}
std::shared_ptr<Announcement> BGPSimplePolicy::get_best_ann_by_gao_rexford(const std::shared_ptr<Announcement>& current_ann, const std::shared_ptr<Announcement>& new_ann) {
    if (!new_ann) {
        throw std::runtime_error("New announcement can't be null.");
    }

    if (!current_ann) {
        return new_ann;
    } else {
        for (auto& func : gao_rexford_functions) {
            auto best_ann = func(current_ann, new_ann);
            if (best_ann) {
                return best_ann;
            }
        }
        throw std::runtime_error("No announcement was chosen.");
    }
}

std::shared_ptr<Announcement> BGPSimplePolicy::get_best_ann_by_local_pref(const std::shared_ptr<Announcement>& current_ann, const std::shared_ptr<Announcement>& new_ann) {
    if (!current_ann || !new_ann) {
        throw std::runtime_error("Announcement is null in get_best_ann_by_local_pref.");
    }

    if (current_ann->recv_relationship > new_ann->recv_relationship) {
        return current_ann;
    } else if (current_ann->recv_relationship < new_ann->recv_relationship) {
        return new_ann;
    } else {
        return nullptr;
    }
}

std::shared_ptr<Announcement> BGPSimplePolicy::get_best_ann_by_as_path(const std::shared_ptr<Announcement>& current_ann, const std::shared_ptr<Announcement>& new_ann) {
    if (!current_ann || !new_ann) {
        throw std::runtime_error("Announcement is null in get_best_ann_by_as_path.");
    }

    if (current_ann->as_path.size() < new_ann->as_path.size()) {
        return current_ann;
    } else if (current_ann->as_path.size() > new_ann->as_path.size()) {
        return new_ann;
    } else {
        return nullptr;
    }
}

std::shared_ptr<Announcement> BGPSimplePolicy::get_best_ann_by_lowest_neighbor_asn_tiebreaker(const std::shared_ptr<Announcement>& current_ann, const std::shared_ptr<Announcement>& new_ann) {
    // Determines if the new announcement is better than the current announcement by Gao-Rexford criteria for ties
    if (!current_ann || current_ann->as_path.empty() || !new_ann || new_ann->as_path.empty()) {
        throw std::runtime_error("Invalid announcement or empty AS path in get_best_ann_by_lowest_neighbor_asn_tiebreaker.");
    }

    int current_neighbor_asn = current_ann->as_path.size() > 1 ? current_ann->as_path[1] : current_ann->as_path[0];
    int new_neighbor_asn = new_ann->as_path.size() > 1 ? new_ann->as_path[1] : new_ann->as_path[0];

    if (current_neighbor_asn <= new_neighbor_asn) {
        return current_ann;
    } else {
        return new_ann;
    }
}

///////////////////////////////// propagate
void BGPSimplePolicy::propagate(Relationships propagate_to, const std::set<Relationships>& send_rels) {
    std::vector<std::weak_ptr<AS>> neighbors;

    auto as_shared = as.lock();
    if (!as_shared) {
        // Handle the case where the AS object is no longer valid
        throw std::runtime_error("Weak ref from policy to as no longer exists");
    }

    switch (propagate_to) {
        case Relationships::PROVIDERS:
            neighbors = as_shared->providers;
            break;
        case Relationships::PEERS:
            neighbors = as_shared->peers;
            break;
        case Relationships::CUSTOMERS:
            neighbors = as_shared->customers;
            break;
        default:
            throw std::runtime_error("Unsupported relationship type.");
    }

    for (const auto& neighbor_weak : neighbors) {
        for (const auto& [prefix, ann] : localRIB.prefix_anns()) {
            if (send_rels.find(ann->recv_relationship) != send_rels.end() && !prev_sent(neighbor_weak, ann)) {
                if (policy_propagate(neighbor_weak, ann, propagate_to, send_rels)) {
                    continue;
                } else {
                    process_outgoing_ann(neighbor_weak, ann, propagate_to, send_rels);
                }
            }
        }
    }
}

bool BGPSimplePolicy::policy_propagate(const std::weak_ptr<AS>& neighbor_weak, const std::shared_ptr<Announcement>& ann, Relationships propagate_to, const std::set<Relationships>& send_rels) {
    // This method simply returns false and does not use the neighbor_weak reference
    return false;
}

bool BGPSimplePolicy::prev_sent(const std::weak_ptr<AS>& neighbor_weak, const std::shared_ptr<Announcement>& ann) {
    // This method simply returns false and does not use the neighbor_weak reference
    return false;
}

void BGPSimplePolicy::process_outgoing_ann(const std::weak_ptr<AS>& neighbor_weak, const std::shared_ptr<Announcement>& ann, Relationships propagate_to, const std::set<Relationships>& send_rels) {
    auto neighbor = neighbor_weak.lock();
    if (!neighbor || !neighbor->policy) {
        throw std::runtime_error("weak ref no longer exists");
    }
    neighbor->policy->receive_ann(ann);
}


