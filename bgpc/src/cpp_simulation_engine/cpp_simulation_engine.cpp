#include <iostream>
#include <fstream>
#include <sstream>
#include <chrono>
#include <stdexcept>
#include <iomanip>
#include <algorithm>

#include "enums.hpp"
#include "announcement.hpp"
#include "policy.hpp"
#include "bgp_simple_policy.hpp"
#include "rov_simple_policy.hpp"
#include "as.hpp"
#include "as_graph.hpp"
#include "cpp_simulation_engine.hpp"

CPPSimulationEngine::CPPSimulationEngine(std::unique_ptr<ASGraph> as_graph, int ready_to_run_round)
    : as_graph(std::move(as_graph)), ready_to_run_round(ready_to_run_round) {
    register_policies();
}

void CPPSimulationEngine::setup(
        const std::vector<std::shared_ptr<Announcement>>& announcements,
        const std::string& base_policy_class_str,
        const std::unordered_map<int, std::string>& non_default_asn_cls_str_dict,
        int max_prefix_block_id) {
    if(max_prefix_block_id == 0){
        max_prefix_block_id = announcements.size();
    }
    set_as_classes(base_policy_class_str, non_default_asn_cls_str_dict, max_prefix_block_id);

    seed_announcements(announcements);

    ready_to_run_round = 0;
}

void CPPSimulationEngine::run(int propagation_round) {

    auto start = std::chrono::high_resolution_clock::now();
    // Ensure that the simulator is ready to run this round
    if (ready_to_run_round != propagation_round) {
        throw std::runtime_error("Engine not set up to run for round " + std::to_string(propagation_round));
    }

    // Propagate announcements
    propagate(propagation_round);

    // Increment the ready to run round
    ready_to_run_round++;
    auto end = std::chrono::high_resolution_clock::now();
    std::chrono::duration<double> elapsed = end - start;
    std::cout << "Propagated in "
              << std::fixed << std::setprecision(2) << elapsed.count() << " seconds." << std::endl;

}

///////////////////////setup funcs
// Method to register policy factory functions
void CPPSimulationEngine::register_policy_factory(const std::string& name, const PolicyFactoryFunc& factory) {
    name_to_policy_func_dict[name] = factory;
}
// Method to register all policies
void CPPSimulationEngine::register_policies() {
    // Example of registering a base policy
    register_policy_factory("BGP Simple", [](int max_prefix_block_id) -> std::unique_ptr<Policy>{
        return std::make_unique<BGPSimplePolicy>(max_prefix_block_id);
    });
    register_policy_factory("BGPSimplePolicy", [](int max_prefix_block_id) -> std::unique_ptr<Policy>{
        return std::make_unique<BGPSimplePolicy>(max_prefix_block_id);
    });

    register_policy_factory("BGP", [](int max_prefix_block_id) -> std::unique_ptr<Policy>{
        return std::make_unique<BGPSimplePolicy>(max_prefix_block_id);
    });
    register_policy_factory("ROVSimple", [](int max_prefix_block_id) -> std::unique_ptr<Policy>{
        return std::make_unique<ROVSimplePolicy>(max_prefix_block_id);
    });
    register_policy_factory("ROV", [](int max_prefix_block_id) -> std::unique_ptr<Policy>{
        return std::make_unique<ROVSimplePolicy>(max_prefix_block_id);
    });
    register_policy_factory("RealPeerROVSimple", [](int max_prefix_block_id) -> std::unique_ptr<Policy>{
        return std::make_unique<ROVSimplePolicy>(max_prefix_block_id);
    });


    // Register other policies similarly
    // e.g., register_policy_factory("SpecificPolicy", ...);
}
void CPPSimulationEngine::set_as_classes(const std::string& base_policy_class_str, const std::unordered_map<int, std::string>& non_default_asn_cls_str_dict, const int max_prefix_block_id){
    for (auto& [asn, as_obj] : as_graph->as_dict) {

        // Determine the policy class string to use
        auto cls_str_it = non_default_asn_cls_str_dict.find(as_obj->asn);

        std::string policy_class_str = (cls_str_it != non_default_asn_cls_str_dict.end()) ? cls_str_it->second : base_policy_class_str;

        // Find the factory function in the dictionary
        auto factory_it = name_to_policy_func_dict.find(policy_class_str);

        if (factory_it == name_to_policy_func_dict.end()) {
            throw std::runtime_error("Policy class not implemented: " + policy_class_str);
        }

        // Create and set the new policy object

        // Create the policy object using the factory function
        auto policy_object = factory_it->second(max_prefix_block_id);
        // Assign the created policy object to as_obj->policy
        as_obj->policy = std::move(policy_object);

        //set the reference to the AS
        as_obj->policy->as = std::weak_ptr<AS>(as_obj->shared_from_this());
    }
}
void CPPSimulationEngine::seed_announcements(const std::vector<std::shared_ptr<Announcement>>& announcements) {
    auto start = std::chrono::high_resolution_clock::now();
    for (const auto& ann : announcements) {
        if (!ann || !ann->seed_asn().has_value()) {
            throw std::runtime_error("Announcement seed ASN is not set.");
        }

        auto as_it = as_graph->as_dict.find(ann->seed_asn().value());
        if (as_it == as_graph->as_dict.end()) {
            throw std::runtime_error("AS object not found in ASGraph.");
        }

        auto& obj_to_seed = as_it->second;
        if (obj_to_seed->policy->localRIB.get_ann(ann->prefix_block_id)) {
            throw std::runtime_error("Seeding conflict: Announcement already exists in the local RIB.");
        }

        obj_to_seed->policy->localRIB.add_ann(ann);
    }
    auto end = std::chrono::high_resolution_clock::now();
    std::chrono::duration<double> elapsed = end - start;
    std::cout << "Seeded " << announcements.size() << " announcements in "
              << std::fixed << std::setprecision(2) << elapsed.count() << " seconds." << std::endl;

}

///////////////////propagation funcs

void CPPSimulationEngine::propagate(int propagation_round) {
    propagate_to_providers(propagation_round);
    propagate_to_peers(propagation_round);
    propagate_to_customers(propagation_round);
}
void CPPSimulationEngine::propagate_to_providers(int propagation_round) {
    for (size_t i = 0; i < as_graph->propagation_ranks.size(); ++i) {
        auto& rank = as_graph->propagation_ranks[i];

        if (i > 0) {
            for (auto& as_obj : rank) {
                as_obj->policy->process_incoming_anns(Relationships::CUSTOMERS, propagation_round);
            }
        }

        for (auto& as_obj : rank) {
            as_obj->policy->propagate_to_providers();
        }
    }
}
void CPPSimulationEngine::propagate_to_peers(int propagation_round) {
    for (auto& [asn, as_obj] : as_graph->as_dict) {
        as_obj->policy->propagate_to_peers();
    }

    for (auto& [asn, as_obj] : as_graph->as_dict) {
        as_obj->policy->process_incoming_anns(Relationships::PEERS, propagation_round);
    }
}

void CPPSimulationEngine::propagate_to_customers(int propagation_round) {
    auto& ranks = as_graph->propagation_ranks;
    size_t i = 0; // Initialize i to 0

    for (auto it = ranks.rbegin(); it != ranks.rend(); ++it, ++i) {
        auto& rank = *it;
        // There are no incoming anns in the top row
        if (i > 0) {
            for (auto& as_obj : rank) {
                as_obj->policy->process_incoming_anns(Relationships::PROVIDERS, propagation_round);
            }
        }

        for (auto& as_obj : rank) {
            as_obj->policy->propagate_to_customers();
        }
    }
}


//// CSV funcs////////////////////////////
void CPPSimulationEngine::dump_local_ribs_to_tsv(const std::string& tsv_path) {
    std::ofstream file(tsv_path);

    // Check if file is open
    if (!file.is_open()) {
        std::cerr << "Failed to open file: " << tsv_path << std::endl;
        throw std::runtime_error("could not open file");
    }

    // Write TSV header
    file << "dumping_asn\tprefix\tas_path\ttimestamp\tseed_asn\troa_valid_length\troa_origin\trecv_relationship\twithdraw\ttraceback_end\tcommunities\n";

    // Iterate through AS graph and get announcements from their local RIBs
    for (const auto& asPair : as_graph->as_dict) {
        const auto& as = asPair.second;
        const auto& policy = as->policy;
        const auto& localRIB = policy->localRIB;


        // Get announcements from the local RIB
        for (const auto& annPair : localRIB.prefix_anns()) {
            const auto& ann = annPair.second;

            // Write each announcement's details to the TSV file
            file << std::to_string(asPair.first) << "\t" << ann->prefix() << "\t{" << join(ann->as_path, ",") << "}\t" << ann->timestamp() << "\t"
                 << optionalToString(ann->seed_asn()) << "\t" << booleanToString(ann->roa_valid_length()) << "\t"
                 << optionalToString(ann->roa_origin()) << "\t" << static_cast<int>(ann->recv_relationship) << "\t"
                 << booleanToString(ann->withdraw(), true) << "\t" << booleanToString(ann->traceback_end, true) << "\n";
                 //<< join(ann->communities, " ") << "\n";
        }
    }

    file.close();
}

// Helper function to join a vector into a string with a separator
template <typename T>
std::string CPPSimulationEngine::join(const std::vector<T>& vec, const std::string& sep) {
    std::string result;
    for (const auto& item : vec) {
        if (!result.empty()) {
            result += sep;
        }
        if constexpr (std::is_same<T, std::string>::value) {
            result += item; // Directly append if T is a string
        } else {
            result += std::to_string(item); // Use to_string for other types
        }
    }
    return result;
}

// Helper function to convert optional values to string
template <typename T>
std::string CPPSimulationEngine::optionalToString(const std::optional<T>& opt) {
    return opt.has_value() ? std::to_string(opt.value()) : "";
}

// Helper function to convert boolean values to string ("True" or "False")
std::string CPPSimulationEngine::booleanToString(const std::optional<bool>& opt, bool capitalize) {
    if (!opt.has_value()) return "";
    return opt.value() ? (capitalize ? "True" : "true") : (capitalize ? "False" : "false");
}

std::map<int, std::vector<std::shared_ptr<Announcement>>> CPPSimulationEngine::get_announcements() {
    std::map<int, std::vector<std::shared_ptr<Announcement>>> asn_to_announcements;

    for (const auto& asPair : as_graph->as_dict) {
        const auto& as = asPair.second;
        const auto& localRIB = as->policy->localRIB;

        std::vector<std::shared_ptr<Announcement>> announcements;
        for (const auto& annPair : localRIB.prefix_anns()) {
            announcements.push_back(annPair.second);
        }

        asn_to_announcements[as->asn] = announcements;
    }

    return asn_to_announcements;
}
