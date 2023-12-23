#include <iostream>
#include <fstream>
#include <sstream>
#include <chrono>
#include <stdexcept>
#include <iomanip>
#include <algorithm>

#include "relationships.hpp"
#include "announcement.hpp"
#include "policy.hpp"
#include "bgp_simple_policy.hpp"
#include "as.hpp"
#include "as_graph.hpp"
#include "cpp_simulation_engine.hpp"

CPPSimulationEngine::CPPSimulationEngine(std::unique_ptr<ASGraph> as_graph, int ready_to_run_round)
    : as_graph(std::move(as_graph)), ready_to_run_round(ready_to_run_round) {
    register_policies();
}

void CPPSimulationEngine::setup(const std::vector<std::shared_ptr<Announcement>>& announcements,
           const std::string& base_policy_class_str,
           const std::map<int, std::string>& non_default_asn_cls_str_dict) {
    std::cout<<"in here"<<std::endl;
    set_as_classes(base_policy_class_str, non_default_asn_cls_str_dict);

    std::cout<<"here"<<std::endl;
    seed_announcements(announcements);

    std::cout<<"out here"<<std::endl;
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
    register_policy_factory("BGPSimplePolicy", []() -> std::unique_ptr<Policy>{
        std::cout <<"in register_policy"<<std::endl;
        return std::make_unique<BGPSimplePolicy>();
    });
    // Register other policies similarly
    // e.g., register_policy_factory("SpecificPolicy", ...);
}
void CPPSimulationEngine::set_as_classes(const std::string& base_policy_class_str, const std::map<int, std::string>& non_default_asn_cls_str_dict) {
    std::cout << "in set_as_classes" << std::endl;
    for (auto& [asn, as_obj] : as_graph->as_dict) {

            std::cout << "in set_as_classes loop" << std::endl;
        // Determine the policy class string to use
        auto cls_str_it = non_default_asn_cls_str_dict.find(as_obj->asn);

        std::cout << "a" << std::endl;
        std::string policy_class_str = (cls_str_it != non_default_asn_cls_str_dict.end()) ? cls_str_it->second : base_policy_class_str;
        std::cout << "b" << std::endl;

        // Find the factory function in the dictionary
        auto factory_it = name_to_policy_func_dict.find(policy_class_str);

        std::cout << "c" << std::endl;
        if (factory_it == name_to_policy_func_dict.end()) {
            throw std::runtime_error("Policy class not implemented: " + policy_class_str);
        }

        std::cout << "d" << std::endl;
        // Create and set the new policy object

        // Create the policy object using the factory function
        auto policy_object = factory_it->second();
        std::cout << "Policy object created" << std::endl; // Print statement
        // Assign the created policy object to as_obj->policy
        as_obj->policy = std::move(policy_object);

        std::cout << "g" << std::endl;
        //set the reference to the AS
        as_obj->policy->as = std::weak_ptr<AS>(as_obj->shared_from_this());

        std::cout << "f" << std::endl;
    }
}
void CPPSimulationEngine::seed_announcements(const std::vector<std::shared_ptr<Announcement>>& announcements) {
    auto start = std::chrono::high_resolution_clock::now();
    for (const auto& ann : announcements) {
        if (!ann || !ann->seed_asn.has_value()) {
            throw std::runtime_error("Announcement seed ASN is not set.");
        }

        auto as_it = as_graph->as_dict.find(ann->seed_asn.value());
        if (as_it == as_graph->as_dict.end()) {
            throw std::runtime_error("AS object not found in ASGraph.");
        }

        auto& obj_to_seed = as_it->second;
        if (obj_to_seed->policy->localRIB.get_ann(ann->prefix)) {
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
