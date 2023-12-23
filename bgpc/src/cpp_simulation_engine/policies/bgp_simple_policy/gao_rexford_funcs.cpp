#include <iostream>
#include <algorithm>
#include <stdexcept>

#include "policy.hpp"
#include "bgp_simple_policy.hpp"
#include "as.hpp"

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
