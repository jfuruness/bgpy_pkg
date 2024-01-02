#include <fstream>
#include <sstream>
#include <stdexcept>
#include <optional>
#include <memory>
#include <string>
#include <climits>

#include "announcement.hpp"
#include "utils.hpp"

CPPSimulationEngine get_engine(std::string as_graph_tsv_path) {
    auto asGraph = std::make_unique<ASGraph>(readASGraph(as_graph_tsv_path));
    return CPPSimulationEngine(std::move(asGraph));
}

std::vector<std::shared_ptr<Announcement>> get_announcements_from_tsv(const std::string& path) {
    std::vector<std::shared_ptr<Announcement>> announcements;
    std::ifstream file(path);
    std::string line;

    // Skip the header line
    std::getline(file, line);
    std::string expectedHeaderStart = "prefix_block_id\tprefix\tas_path\ttimestamp\tseed_asn\troa_valid_length\troa_origin\trecv_relationship\twithdraw\ttraceback_end\tcommunities";
    if (line.find(expectedHeaderStart) != 0) {
        throw std::runtime_error("TSV file header does not start with the expected format.");
    }



    while (std::getline(file, line)) {
        std::istringstream iss(line);
        std::string token;

        unsigned short int prefix_block_id;
        std::string prefix;
        std::vector<int> as_path;
        int timestamp;
        std::optional<int> seed_asn;
        std::optional<bool> roa_valid_length;
        std::optional<int> roa_origin;
        Relationships recv_relationship;
        bool withdraw;
        bool traceback_end;
        std::vector<std::string> communities;

        // Parse each field
        std::getline(iss, token, '\t');
        errno = 0;  // Clear errno
        unsigned long temp = std::strtoul(token.c_str(), nullptr, 10);  // Using base 10 for decimal

        if (errno == ERANGE || temp > USHRT_MAX) {
            // Handle error: Value out of range for unsigned short
            throw std::runtime_error("Invalid prefix_block_id: " + token);
        } else {
            prefix_block_id = static_cast<unsigned short>(temp);
        }

        std::getline(iss, prefix, '\t');

        // Parse as_path
        if (std::getline(iss, token, '\t')) {
            std::istringstream as_path_stream(token.substr(1, token.size() - 2)); // Strip braces
            std::string as_num;
            while (std::getline(as_path_stream, as_num, ',')) {
                as_path.push_back(std::stoi(as_num));
            }
        }

        // Parse timestamp, etc.
        std::getline(iss, token, '\t'); timestamp = std::stoi(token);
        // Similar parsing for other fields

        if (std::getline(iss, token, '\t') && !token.empty()) {
            seed_asn = std::stoi(token);
        }

        // Parse roa_valid_length (optional)
        if (std::getline(iss, token, '\t') && !token.empty()) {
            roa_valid_length = (token == "True");
        }

        // Parse roa_origin (optional)
        if (std::getline(iss, token, '\t') && !token.empty()) {
            roa_origin = std::stoi(token);
        }

        // Parse recv_relationship (convert to enum)
        if (std::getline(iss, token, '\t') && !token.empty()) {
            int rel_value = std::stoi(token);
            switch (rel_value) {
                case 1: recv_relationship = Relationships::PROVIDERS; break;
                case 2: recv_relationship = Relationships::PEERS; break;
                case 3: recv_relationship = Relationships::CUSTOMERS; break;
                case 4: recv_relationship = Relationships::ORIGIN; break;
                default:
                    throw std::runtime_error("Invalid recv_relationship value: " + token);
            }
        } else {
            throw std::runtime_error("Missing or empty recv_relationship value.");
        }
        // Assuming Relationships can be converted from int/string
        // recv_relationship = ...

        // Parse withdraw
        std::getline(iss, token, '\t');
        withdraw = (token == "True");

        // Parse traceback_end
        std::getline(iss, token, '\t');
        traceback_end = (token == "True");

        // Parse communities
        if (std::getline(iss, token, '\t') && !token.empty()) {
            std::istringstream communities_stream(token.substr(1, token.size() - 2)); // Strip braces
            std::string community;
            while (std::getline(communities_stream, community, ',')) {
                communities.push_back(community);
            }
        }

        std::shared_ptr<Announcement> ann = std::make_shared<Announcement>(
            prefix_block_id, prefix, as_path, timestamp, seed_asn, roa_valid_length,
            roa_origin, recv_relationship, withdraw, traceback_end, communities
        );
        announcements.push_back(ann);
    }

    return announcements;
}

