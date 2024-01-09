#ifndef UTILS_HPP
#define UTILS_HPP

#include <vector>
#include <string>
#include <memory>
#include <string>

#include "announcement.hpp"
#include "cpp_simulation_engine.hpp"

CPPSimulationEngine get_engine(std::string as_graph_tsv_path = "/home/anon/Desktop/caida.tsv");

std::vector<std::shared_ptr<Announcement>> get_announcements_from_tsv(const std::string& path = "/home/anon/Desktop/anns_1000_mod.tsv", bool origin_only_seeding = false);

#endif // UTILS_HPP
