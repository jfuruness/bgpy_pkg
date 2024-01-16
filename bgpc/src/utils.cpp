#include <fstream>
#include <iostream>
#include <sstream>
#include <stdexcept>
#include <optional>
#include <memory>
#include <string>
#include <climits>
#include <vector>
#include <map>
#include <unordered_set>

#include "announcement.hpp"
#include "utils.hpp"


CPPSimulationEngine get_engine(std::string as_graph_tsv_path) {
    auto asGraph = std::make_unique<ASGraph>(readASGraph(as_graph_tsv_path));
    return CPPSimulationEngine(std::move(asGraph));
}


void extrapolate(
    const std::vector<std::string>& tsv_paths,
    const bool origin_only_seeding,
    const std::unordered_set<int>& valid_seed_asns,
    const std::unordered_set<int>& omitted_vantage_point_asns,
    const std::unordered_set<unsigned long>& valid_prefix_ids,
    const long max_prefix_block_id,
    const std::unordered_set<int>& output_asns,
    const std::string& out_path,
    const std::unordered_map<int, std::string>& non_default_asn_cls_str_dict,
    const std::string& caida_tsv_path
) {
    auto engine = get_engine(caida_tsv_path);
    engine.set_as_classes("BGPSimplePolicy", non_default_asn_cls_str_dict, max_prefix_block_id);
    for (const std::string& tsv_path : tsv_paths){
        engine.seed_announcements(
            get_announcements_from_tsv_for_extrapolation(
                tsv_path,
                origin_only_seeding,
                valid_seed_asns,
                omitted_vantage_point_asns,
                valid_prefix_ids
            )
        );
    }
    engine.ready_to_run_round = 0;
    engine.run(0, {}, {}, {});
    engine.dump_local_ribs_to_tsv(out_path, output_asns);
}


// TODO: Definitely needs a big refactor. Wayyy too large of a function
std::vector<std::shared_ptr<Announcement>> get_announcements_from_tsv_for_extrapolation(
    const std::string& path,
    const bool origin_only_seeding,
    const std::unordered_set<int>& valid_seed_asns,
    const std::unordered_set<int>& omitted_vantage_point_asns,
    const std::unordered_set<unsigned long>& valid_prefix_ids
) {
    std::vector<std::shared_ptr<Announcement>> announcements;
    std::ifstream file(path);
    std::string line;
    std::map<std::string, size_t> headerIndices;

    // Read the header line
    if (!std::getline(file, line)) {
        throw std::runtime_error("TSV file is empty or header is missing.");
    }

    std::istringstream headerStream(line);
    std::string header;
    size_t index = 0;
    while (std::getline(headerStream, header, '\t')) {
        headerIndices[header] = index++;
    }

    // Verify required headers
    std::vector<std::string> requiredHeaders = {
        "block_prefix_id", "prefix", "as_path", "timestamp", "prefix_id", "roa_validity",
        "roa_routed",
    };

    for (const auto& requiredHeader : requiredHeaders) {
        if (headerIndices.find(requiredHeader) == headerIndices.end()) {
            throw std::runtime_error("Missing required header: " + requiredHeader);
        }
    }

    while (std::getline(file, line)) {
        std::istringstream iss(line);
        std::string token;
        std::vector<std::string> fields(index);

        size_t currentIdx = 0;
        while (std::getline(iss, token, '\t')) {
            if (currentIdx < fields.size()) {
                fields[currentIdx++] = token;
            }
        }

        // Validate line format
        if (currentIdx != index) {
            throw std::runtime_error("Incorrect number of fields in a line.");
        }

        // Parse each field using the headerIndices
        unsigned short int prefix_block_id = std::stoul(fields[headerIndices["block_prefix_id"]]);
        std::string prefix = fields[headerIndices["prefix"]];
        std::string asPathStr = fields[headerIndices["as_path"]];

        // Skip line if AS path contains "{", indicating an AS-SET
        if (asPathStr.find('{') != std::string::npos) {
            continue;
        }
        // Parse as_path (assuming it's a comma-separated list within a single field)

        std::vector<int> as_path;
        std::istringstream asPathStream(asPathStr);
        int asNum;
        while (asPathStream >> asNum) {
            as_path.push_back(asNum);
        }
        if (as_path.size() == 0){
            throw std::runtime_error("as path is empty");
        }
        int roa_validity = std::stoi(fields[headerIndices["roa_validity"]]);
        int roa_routed = std::stoi(fields[headerIndices["roa_routed"]]);
        int timestamp = std::stoi(fields[headerIndices["timestamp"]]);
        unsigned long prefix_id = std::stoul(fields[headerIndices["prefix_id"]]);

        // TODO: this needs to be fixed if we ever want to propagate this info
        // but for now, this will work correctly with ROV
        // this info is simply missing from the mrt analysis
        // both for roa_valid_length and roa_origin
        std::optional<bool> roa_valid_length = (roa_validity == 0 || roa_validity == 1 || roa_validity == 3);
        std::optional<int> roa_origin = 0;
        // TODO: make this proper if we want to check this later
        // but for now this will accurately work with ROV
        if (roa_validity == 3 || roa_validity == 4 || roa_routed == 2){
            roa_origin = 0;
        } else {
            roa_origin = as_path[as_path.size() - 1];
        }
        //std::cout<<"a"<<std::endl;

        for (int i = as_path.size() - 1; i >= 0; --i){

            // std::cout<<"b"<<std::endl;
            // If the seed_asns is not in the list of valid_seed_asns, don't create ann
            // (valid_seed_asns is typically all non stub ASNs)
            // Additionally, ensure we aren't seeding anything at the omitted vantage points
            // Additionally, ensure we have a valid prefix_id
            if (
                valid_seed_asns.find(as_path[i]) != valid_seed_asns.end()
                && omitted_vantage_point_asns.find(as_path[0]) == omitted_vantage_point_asns.end()
                && valid_prefix_ids.find(prefix_id) != valid_prefix_ids.end()
            ){

                //std::cout<<"c"<<std::endl;
                std::optional<int> seed_asn = as_path[i];

                std::vector<int> temp_as_path;
                // Go from i to the end of the as path
                for (int j = i; j < as_path.size() ; ++j){

                    //std::cout<<"d"<<std::endl;
                    temp_as_path.push_back(as_path[j]);
                    //std::cout<<"e"<<std::endl;
                }

                //std::cout<<"f"<<std::endl;

                std::shared_ptr<Announcement> ann = std::make_shared<Announcement>(
                    prefix_block_id,
                    prefix,
                    temp_as_path,
                    timestamp,
                    // seed_asn
                    seed_asn,
                    // roa_valid_length
                    roa_valid_length,
                    // roa_origin
                    roa_origin,
                    // always default to the origin
                    // doesn't matter, we just never want to override
                    // seeding announcements
                    Relationships::ORIGIN,
                    // withdraw
                    false,
                    // traceback_end
                    // TODO: this may be off if the origin isn't in the graph
                    // however, we don't use this anyways for extrapolation
                    i == 0
                    // communities, we don't track these rn
                    //{}
                );


                announcements.push_back(ann);
                // If origin_only_seeding and seed_asn in the as graph, break
                // Must check if it's in the graph since we may remove stubs, and
                // the caida graph might not have every AS. Doesn't mean we should
                // discard the announcements. We check if the seed_asn is in the graph
                // in the if statement above, so we only need to check this here
                if (origin_only_seeding){
                    break;
                }
            }
        }
    }
    //std::cout<<"done with anns"<<std::endl;
    return announcements;
}
