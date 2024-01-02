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
using PolicyFactoryFunc = std::function<std::unique_ptr<Policy>(int max_prefix_block_id, LocalRIB&& local_rib, RecvQueue&& recv_queue)>;

class CPPSimulationEngine {
public:
    std::unique_ptr<ASGraph> as_graph;
    int ready_to_run_round;

    CPPSimulationEngine(std::unique_ptr<ASGraph> as_graph, int ready_to_run_round = -1);

    void dump_local_ribs_to_tsv(const std::string& tsv_path);

    // Disable copy semantics
    CPPSimulationEngine(const CPPSimulationEngine&) = delete;
    CPPSimulationEngine& operator=(const CPPSimulationEngine&) = delete;

    // Enable move semantics
    CPPSimulationEngine(CPPSimulationEngine&&) = default;
    CPPSimulationEngine& operator=(CPPSimulationEngine&&) = default;

    void setup(const std::vector<std::shared_ptr<Announcement>>& announcements,
               const std::string& base_policy_class_str = "BGPSimplePolicy",
               const std::unordered_map<int, std::string>& non_default_asn_cls_str_dict = {},
               int max_prefix_block_id = 0);

    void run(const int propagation_round = 0);
    std::map<int, std::vector<std::shared_ptr<Announcement>>> get_announcements();

protected:
    std::map<std::string, PolicyFactoryFunc> name_to_policy_func_dict;

    void register_policy_factory(const std::string& name, const PolicyFactoryFunc& factory);
    void register_policies();
    void set_as_classes(const std::string& base_policy_class_str, const std::unordered_map<int, std::string>& non_default_asn_cls_str_dict, const int max_prefix_block_id);
    void seed_announcements(const std::vector<std::shared_ptr<Announcement>>& announcements);

    void propagate(const int propagation_round);
    void propagate_to_providers(const int propagation_round);
    void propagate_to_peers(const int propagation_round);
    void propagate_to_customers(const int propagation_round);

    // CSV Helper functions
    template <typename T>
    std::string join(const std::vector<T>& vec, const std::string& sep);

    template <typename T>
    std::string optionalToString(const std::optional<T>& opt);

    std::string booleanToString(const std::optional<bool>& opt, bool capitalize = false);
};

#endif // CPP_SIMULATION_ENGINE_HPP
