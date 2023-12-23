#include <unordered_map>
#include <unordered_set>
#include <vector>
#include <string>
#include <optional>
#include <cassert>
#include <memory>

#include "enums.hpp"
#include "announcement.hpp"
#include "policy.hpp"
#include "as.hpp"
#include "as_graph.hpp"
#include "cpp_simulation_engine.hpp"



class ASGraphAnalyzer {
public:
    ASGraphAnalyzer(std::shared_ptr<CPPSimulationEngine> engine,
                  const std::vector<std::string>& ordered_prefixes,
                  const std::unordered_set<int>& victim_asns,
                  const std::unordered_set<int>& attacker_asns);

    std::unordered_map<int, std::unordered_map<int, Outcomes>> analyze();

private:
    std::shared_ptr<CPPSimulationEngine> engine;
    std::unordered_set<int> victim_asns;
    std::unordered_set<int> attacker_asns;
    std::unordered_map<int, std::optional<std::shared_ptr<Announcement>>> most_specific_ann_dict;
    std::unordered_map<int, Outcomes> data_plane_outcomes;
    std::unordered_map<int, Outcomes> control_plane_outcomes;
    std::unordered_map<int, std::unordered_map<int, Outcomes>> outcomes;

    std::optional<std::shared_ptr<Announcement>> get_most_specific_ann(std::shared_ptr<AS> as_obj, const std::vector<std::string>& ordered_prefixes);
    Outcomes get_as_outcome_data_plane(std::shared_ptr<AS> as_obj);
    Outcomes determine_as_outcome_data_plane(std::shared_ptr<AS> as_obj, std::optional<std::shared_ptr<Announcement>> most_specific_ann);
    Outcomes get_as_outcome_ctrl_plane(std::shared_ptr<AS> as_obj);
    Outcomes determine_as_outcome_ctrl_plane(std::shared_ptr<AS> as_obj, std::optional<std::shared_ptr<Announcement>> ann);
    Outcomes get_other_as_outcome_hook(std::shared_ptr<AS> as_obj);
};
