#ifndef UTILS_HPP
#define UTILS_HPP

#include <vector>
#include <string>
#include <memory>
#include <string>
#include <vector>
#include <unordered_set>
#include <unordered_map>

#include "announcement.hpp"
#include "cpp_simulation_engine.hpp"

CPPSimulationEngine get_engine(std::string as_graph_tsv_path);

std::vector<std::shared_ptr<Announcement>> get_announcements_from_tsv_for_extrapolation(
    const std::string& path,
    const bool origin_only_seeding = true,
    const std::unordered_set<int>& valid_seed_asns = std::unordered_set<int>(),
    const std::unordered_set<int>& omitted_vantage_point_asns = std::unordered_set<int>(),
    const std::unordered_set<unsigned long>& valid_prefix_ids = std::unordered_set<unsigned long>()
);


void extrapolate(
    const std::vector<std::string>& tsv_paths,
    const bool origin_only_seeding,
    const std::unordered_set<int>& valid_seed_asns,
    const std::unordered_set<int>& omitted_vantage_point_asns,
    const std::unordered_set<unsigned long>& valid_prefix_ids,
    const long max_prefix_block_id,
    const std::vector<int>& output_asns,
    const std::string& out_path,
    const std::unordered_map<int, std::string>& non_default_asn_cls_str_dict,
    const std::string& caida_tsv_path
);


#endif // UTILS_HPP
