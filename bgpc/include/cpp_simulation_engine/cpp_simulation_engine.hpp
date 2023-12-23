#ifndef CPP_SIMULATION_ENGINE_HPP
#define CPP_SIMULATION_ENGINE_HPP

#include <memory>
#include <vector>
#include <string>
#include <functional>

#include "enums.hpp"
#include "announcement.hpp"
#include "policy.hpp"
#include "bgp_simple_policy.hpp"
#include "as.hpp"
#include "as_graph.hpp"


// Factory function type for creating Policy objects
using PolicyFactoryFunc = std::function<std::unique_ptr<Policy>()>;

class CPPSimulationEngine {
public:
    std::unique_ptr<ASGraph> as_graph;
    int ready_to_run_round;

    CPPSimulationEngine(std::unique_ptr<ASGraph> as_graph, int ready_to_run_round = -1);

    // Disable copy semantics
    CPPSimulationEngine(const CPPSimulationEngine&) = delete;
    CPPSimulationEngine& operator=(const CPPSimulationEngine&) = delete;

    // Enable move semantics
    CPPSimulationEngine(CPPSimulationEngine&&) = default;
    CPPSimulationEngine& operator=(CPPSimulationEngine&&) = default;

    void setup(const std::vector<std::shared_ptr<Announcement>>& announcements,
               const std::string& base_policy_class_str = "BGPSimplePolicy",
               const std::map<int, std::string>& non_default_asn_cls_str_dict = {});

    void run(int propagation_round = 0);

protected:
    std::map<std::string, PolicyFactoryFunc> name_to_policy_func_dict;

    void register_policy_factory(const std::string& name, const PolicyFactoryFunc& factory);
    void register_policies();
    void set_as_classes(const std::string& base_policy_class_str, const std::map<int, std::string>& non_default_asn_cls_str_dict);
    void seed_announcements(const std::vector<std::shared_ptr<Announcement>>& announcements);

    void propagate(int propagation_round);
    void propagate_to_providers(int propagation_round);
    void propagate_to_peers(int propagation_round);
    void propagate_to_customers(int propagation_round);
};

#endif // CPP_SIMULATION_ENGINE_HPP
