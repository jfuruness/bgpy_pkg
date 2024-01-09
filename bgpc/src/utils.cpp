#include <fstream>
#include <sstream>
#include <stdexcept>
#include <optional>
#include <memory>
#include <string>
#include <climits>
#include <vector>
#include <map>



#include "announcement.hpp"
#include "utils.hpp"

CPPSimulationEngine get_engine(std::string as_graph_tsv_path) {
    auto asGraph = std::make_unique<ASGraph>(readASGraph(as_graph_tsv_path));
    return CPPSimulationEngine(std::move(asGraph));
}


std::vector<std::shared_ptr<Announcement>> get_announcements_from_tsv_for_extrapolation(const std::string& path, const bool origin_only_seeding) {
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
        "prefix_block_id", "prefix", "as_path", "timestamp", "prefix_id", "roa_validity",
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
        unsigned short int prefix_block_id = std::stoul(fields[headerIndices["prefix_block_id"]]);
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

        // TODO: if prefix_id not in valid_prefix_ids, continue
        //
        //


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
            roa_origin = as_path[0];
        }

        for (size_t i = 0; i < as_path.size(); ++i){
            std::optional<int> seed_asn = as_path[i];

            std::vector<int> temp_as_path;
            for (size_t j = i; j < as_path.size(); ++j){
                temp_as_path.push_back(as_path[i]);
            }

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
                i == 0,
                // communities, we don't track these rn
                {}
            );
            // TODO: check if seed_asn is in the set of valid_asbns
            announcements.push_back(ann);

            // TODO: if origin_only_seeding and seed_asn in the as graph, break
            // Must check if it's in the graph since we may remove stubs, and
            // the caida graph might not have every AS. Doesn't mean we should
            // discard the announcements
        }
    }

    return announcements;
}
