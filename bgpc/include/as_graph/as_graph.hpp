#ifndef AS_GRAPH_HPP
#define AS_GRAPH_HPP

#include <unordered_map>
#include <memory>
#include <vector>
#include <string>
#include "as.hpp"

class ASGraph {
public:
    std::unordered_map<int, std::shared_ptr<AS>> as_dict;
    std::vector<std::vector<std::shared_ptr<AS>>> propagation_ranks;

    ASGraph();
    ~ASGraph();

    void calculatePropagationRanks();
};

void parseASNList(std::unordered_map<int, std::shared_ptr<AS>>& asGraph, const std::string& data, std::vector<std::weak_ptr<AS>>& list);
ASGraph readASGraph(const std::string& filename);

#endif // AS_GRAPH_HPP
