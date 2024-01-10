#ifndef UTILS_HPP
#define UTILS_HPP

#include <vector>
#include <string>
#include <memory>
#include <string>
#include <unordered_set>

#include "announcement.hpp"
#include "cpp_simulation_engine.hpp"

CPPSimulationEngine get_engine(std::string as_graph_tsv_path = "/home/anon/Desktop/caida.tsv");

std::vector<std::shared_ptr<Announcement>> get_announcements_from_tsv_for_extrapolation(
    const std::string& path,
    const bool origin_only_seeding = true,
    const std::unordered_set<int>& valid_seed_asns = std::unordered_set<int>(),
    const std::unordered_set<int>& omitted_vantage_point_asns = std::unordered_set<int>(),
    const std::unordered_set<unsigned long>& valid_prefix_ids = std::unordered_set<unsigned long>()
);

#endif // UTILS_HPP
