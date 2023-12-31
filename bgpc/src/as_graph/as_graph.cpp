#include <fstream>
#include <sstream>
#include <chrono>
#include <iostream>
#include <algorithm>
#include <stdexcept>
#include <iomanip>

#include "as.hpp"
#include "as_graph.hpp"


ASGraph::ASGraph() {
    as_dict.reserve(90000);
}

ASGraph::~ASGraph() {}

void ASGraph::calculatePropagationRanks() {
    long long max_rank = 0;
    for (const auto& pair : as_dict) {
        max_rank = std::max(max_rank, pair.second->propagation_rank);
    }

    propagation_ranks.resize(max_rank + 1);

    for (const auto& pair : as_dict) {
        propagation_ranks[pair.second->propagation_rank].push_back(pair.second);
    }

    for (auto& rank : propagation_ranks) {
        std::sort(rank.begin(), rank.end(), [](const std::shared_ptr<AS>& a, const std::shared_ptr<AS>& b) {
            return a->asn < b->asn;
        });
    }
}

void parseASNList(std::unordered_map<int, std::shared_ptr<AS>>& asGraph, const std::string& data, std::vector<std::weak_ptr<AS>>& list) {
    std::istringstream iss(data.substr(1, data.size() - 2)); // Remove braces
    std::string asn_str;
    while (std::getline(iss, asn_str, ',')) {
        int asn = std::stoi(asn_str);
        if (asGraph.find(asn) == asGraph.end()) {
            throw std::runtime_error("ASN " + std::to_string(asn) + " doesn't exist within the graph");
        } else{
            list.push_back(asGraph[asn]);
        }
    }
}

ASGraph readASGraph(const std::string& filename) {
    auto start = std::chrono::high_resolution_clock::now();
    std::cout << "Creating AS Graph" << std::endl;
    ASGraph asGraph;
    std::ifstream file(filename);
    std::string line;

    std::getline(file, line);
    std::string expectedHeaderStart = "asn\tpeers\tcustomers\tproviders\tinput_clique\tixp\tcustomer_cone_size\tpropagation_rank\tstubs\tstub\tmultihomed\ttransit";
    if (line.find(expectedHeaderStart) != 0) {
        throw std::runtime_error("File header does not start with the expected format.");
    }

    // First pass: add all ASNs to as_dict
    while (std::getline(file, line)) {
        std::istringstream iss(line);
        std::vector<std::string> tokens;
        std::string token;

        while (std::getline(iss, token, '\t')) {
            tokens.push_back(token);
        }

        int asn = std::stoi(tokens[0]);
        auto as = std::make_shared<AS>(asn);
        as->initialize();
        asGraph.as_dict[asn] = as;
    }

    // Reset file stream to read the file again
    file.clear();
    file.seekg(0);
    std::getline(file, line); // Skip the header line

    // Second pass: add peers, customers, and providers
    while (std::getline(file, line)) {
        std::istringstream iss(line);
        std::vector<std::string> tokens;
        std::string token;

        while (std::getline(iss, token, '\t')) {
            tokens.push_back(token);
        }

        int asn = std::stoi(tokens[0]);
        auto as = asGraph.as_dict[asn];

        parseASNList(asGraph.as_dict, tokens[1], as->peers);
        parseASNList(asGraph.as_dict, tokens[2], as->customers);
        parseASNList(asGraph.as_dict, tokens[3], as->providers);

        as->input_clique = (tokens[4] == "True");
        as->ixp = (tokens[5] == "True");
        as->customer_cone_size = std::stoll(tokens[6]);
        as->propagation_rank = std::stoll(tokens[7]);
        as->stub = (tokens[9] == "True");
        as->multihomed = (tokens[10] == "True");
        as->transit = (tokens[11] == "True");
    }
    asGraph.calculatePropagationRanks();

    auto end = std::chrono::high_resolution_clock::now();
    std::chrono::duration<double> elapsed = end - start;
    std::cout << "Generated ASGraph in "
              << std::fixed << std::setprecision(2) << elapsed.count() << " seconds." << std::endl;
    return asGraph;
}
