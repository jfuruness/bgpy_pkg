#include <iostream>
#include <algorithm>
#include <stdexcept>

#include "policy.hpp"
#include "bgp_simple_policy.hpp"
#include "as.hpp"

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


