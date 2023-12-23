#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
//#include <pybind11/optional.h>
#include <relationships.hpp>
#include <announcement.hpp>



#include <iostream>
#include <fstream>
#include <sstream>
#include <vector>
#include <map>
#include <string>
#include <functional>
#include <chrono>
#include <iomanip>
#include <memory>
#include <algorithm>
#include <optional>
#include <stdexcept> // for std::runtime_error
#include <set>
#include <type_traits>  // for std::is_base_of


// Disable threading since we don't use it
// drastically improves weak pointer times...
//https://stackoverflow.com/a/8966130
//weak pointer is still slow according to this https://stackoverflow.com/a/35137265
//althought hat doesn't show the BOOST_DISBALE_THREADS
//I replicated the results, it's about 2x as slow
//Still, for good design, since I'm terrible at C++, I'm keeping it
//esp since it's probably negligable since this timing test
//was with 100000000U times
#define BOOST_DISABLE_THREADS

class LocalRIB {
protected:
    std::map<std::string, std::shared_ptr<Announcement>> _info;

public:
    LocalRIB() {}

    std::shared_ptr<Announcement> get_ann(const std::string& prefix, const std::shared_ptr<Announcement>& default_ann = nullptr) const {
        // Returns announcement or nullptr from the local rib by prefix
        auto it = _info.find(prefix);
        if (it != _info.end()) {
            return it->second;
        }
        return default_ann;
    }

    void add_ann(const std::shared_ptr<Announcement>& ann) {
        // Adds an announcement to local rib with prefix as key
        _info[ann->prefix] = ann;
    }

    void remove_ann(const std::string& prefix) {
        // Removes announcement from local rib based on prefix
        _info.erase(prefix);
    }

    const std::map<std::string, std::shared_ptr<Announcement>>& prefix_anns() const {
        // Returns all prefixes and announcements zipped
        return _info;
    }
};


class RecvQueue {
protected:
    std::map<std::string, std::vector<std::shared_ptr<Announcement>>> _info;

public:
    RecvQueue() {}

    void add_ann(const std::shared_ptr<Announcement>& ann) {
        // Appends ann to the list of received announcements for that prefix
        _info[ann->prefix].push_back(ann);
    }

    const std::map<std::string, std::vector<std::shared_ptr<Announcement>>>& prefix_anns() const {
        // Returns all prefixes and announcement lists
        return _info;
    }

    const std::vector<std::shared_ptr<Announcement>>& get_ann_list(const std::string& prefix) const {
        // Returns received announcement list for a given prefix
        static const std::vector<std::shared_ptr<Announcement>> empty; // To return in case of no match
        auto it = _info.find(prefix);
        if (it != _info.end()) {
            return it->second;
        }
        return empty;
    }
};



class AS; // Forward declaration

class Policy {
public:
    std::weak_ptr<AS> as;
    LocalRIB localRIB;
    RecvQueue recvQueue;

    Policy() {}

    virtual void receive_ann(const std::shared_ptr<Announcement>& ann) = 0;
    virtual void process_incoming_anns(Relationships from_rel, int propagation_round, bool reset_q = true) = 0;
    virtual void propagate_to_providers() = 0;
    virtual void propagate_to_customers() = 0;
    virtual void propagate_to_peers() = 0;

    // You need virtual destructors in base class or else derived classes
    // won't clean up properly
    virtual ~Policy() = default; // Virtual and uses the default implementation
};


class BGPSimplePolicy : public Policy {
public:
    BGPSimplePolicy() : Policy() {
        std::cout<<"in bgpsimple"<<std::endl;
        initialize_gao_rexford_functions();

        std::cout<<"out bgpsimple"<<std::endl;
    }
    // You need virtual destructors in base class or else derived classes
    // won't clean up properly
    virtual ~BGPSimplePolicy() override = default; // Virtual and uses the default implementation

    void process_incoming_anns(Relationships from_rel, int propagation_round, bool reset_q = true) override;
    void propagate_to_providers() override;
    void propagate_to_customers() override;
    void propagate_to_peers() override;
    void receive_ann(const std::shared_ptr<Announcement>& ann) override;
protected:
    std::vector<std::function<std::shared_ptr<Announcement>(const std::shared_ptr<Announcement>&, const std::shared_ptr<Announcement>&)>> gao_rexford_functions;

    bool valid_ann(const std::shared_ptr<Announcement>& ann, Relationships recv_relationship) const;
    std::shared_ptr<Announcement> copy_and_process(const std::shared_ptr<Announcement>& ann, Relationships recv_relationship);
    void reset_queue(bool reset_q);
    /////////////////////////////////////////// gao rexford
    virtual void initialize_gao_rexford_functions();
    std::shared_ptr<Announcement> get_best_ann_by_gao_rexford(const std::shared_ptr<Announcement>& current_ann, const std::shared_ptr<Announcement>& new_ann);
    std::shared_ptr<Announcement> get_best_ann_by_local_pref(const std::shared_ptr<Announcement>& current_ann, const std::shared_ptr<Announcement>& new_ann);
    std::shared_ptr<Announcement> get_best_ann_by_as_path(const std::shared_ptr<Announcement>& current_ann, const std::shared_ptr<Announcement>& new_ann);
    std::shared_ptr<Announcement> get_best_ann_by_lowest_neighbor_asn_tiebreaker(const std::shared_ptr<Announcement>& current_ann, const std::shared_ptr<Announcement>& new_ann);
    ///////////////////////////////// propagate
    void propagate(Relationships propagate_to, const std::set<Relationships>& send_rels);
    bool policy_propagate(const std::weak_ptr<AS>& neighbor_weak, const std::shared_ptr<Announcement>& ann, Relationships propagate_to, const std::set<Relationships>& send_rels);
    bool prev_sent(const std::weak_ptr<AS>& neighbor_weak, const std::shared_ptr<Announcement>& ann);
    void process_outgoing_ann(const std::weak_ptr<AS>& neighbor_weak, const std::shared_ptr<Announcement>& ann, Relationships propagate_to, const std::set<Relationships>& send_rels);
};



class AS : public std::enable_shared_from_this<AS> {
public:
    int asn;
    std::unique_ptr<Policy> policy;
    std::vector<std::weak_ptr<AS>> peers;
    std::vector<std::weak_ptr<AS>> customers;
    std::vector<std::weak_ptr<AS>> providers;
    bool input_clique;
    bool ixp;
    bool stub;
    bool multihomed;
    bool transit;
    long long customer_cone_size;
    long long propagation_rank;

    AS(int asn) : asn(asn), policy(std::make_unique<BGPSimplePolicy>()), input_clique(false), ixp(false), stub(false), multihomed(false), transit(false), customer_cone_size(0), propagation_rank(0) {
        //Can't set this here. AS must already be accessed by shared ptr before calling else err
        //policy->as = std::weak_ptr<AS>(this->shared_from_this());
    }
    // Method to initialize weak_ptr after object is managed by shared_ptr
    void initialize() {
        policy->as = std::weak_ptr<AS>(shared_from_this());
    }
};


class ASGraph {
public:
    std::map<int, std::shared_ptr<AS>> as_dict;
    std::vector<std::vector<std::shared_ptr<AS>>> propagation_ranks;

    void calculatePropagationRanks() {
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
    ~ASGraph() {
        // No need to manually delete shared_ptr objects; they will be automatically deleted when they go out of scope.
    }
};

void parseASNList(std::map<int, std::shared_ptr<AS>>& asGraph, const std::string& data, std::vector<std::weak_ptr<AS>>& list) {
    std::istringstream iss(data.substr(1, data.size() - 2)); // Remove braces
    std::string asn_str;
    while (std::getline(iss, asn_str, ',')) {
        int asn = std::stoi(asn_str);
        if (asGraph.find(asn) != asGraph.end()) {
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

    while (std::getline(file, line)) {
        std::istringstream iss(line);
        std::vector<std::string> tokens;
        std::string token;

        while (std::getline(iss, token, '\t')) {
            tokens.push_back(token);
        }

        int asn = std::stoi(tokens[0]);
        // Shared between as_dict and propagation_ranks
        auto as = std::make_shared<AS>(asn);
        as->initialize();

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

        asGraph.as_dict[asn] = as;
    }
    asGraph.calculatePropagationRanks();

    auto end = std::chrono::high_resolution_clock::now();
    std::chrono::duration<double> elapsed = end - start;
    std::cout << "Generated ASGraph in "
              << std::fixed << std::setprecision(2) << elapsed.count() << " seconds." << std::endl;
    return asGraph;
}






///////////BGPSimple implementation. Done outside of the class to avoid circular ref with AS
void BGPSimplePolicy::process_incoming_anns(Relationships from_rel, int propagation_round, bool reset_q) {
    // Process all announcements that were incoming from a specific relationship

    // For each prefix, get all announcements received
    for (const auto& [prefix, ann_list] : recvQueue.prefix_anns()) {
        // Get announcement currently in local RIB
        auto current_ann = localRIB.get_ann(prefix);

        // Check if current announcement is seeded; if so, continue
        if (current_ann && current_ann->seed_asn.has_value()) {
            continue;
        }

        std::shared_ptr<Announcement> og_ann = current_ann;

        // For each announcement that was incoming
        for (const auto& new_ann : ann_list) {
            // Make sure there are no loops
            if (valid_ann(new_ann, from_rel)) {
                auto new_ann_processed = copy_and_process(new_ann, from_rel);

                current_ann = get_best_ann_by_gao_rexford(current_ann, new_ann_processed);
            }
        }

        // This is a new best announcement. Process it and add it to the local RIB
        if (og_ann != current_ann) {
            // Save to local RIB
            localRIB.add_ann(current_ann);
        }
    }

    reset_queue(reset_q);
}
void BGPSimplePolicy::propagate_to_providers() {
    std::set<Relationships> send_rels = {Relationships::ORIGIN, Relationships::CUSTOMERS};
    propagate(Relationships::PROVIDERS, send_rels);
}

void BGPSimplePolicy::propagate_to_customers() {
    std::set<Relationships> send_rels = {Relationships::ORIGIN, Relationships::CUSTOMERS, Relationships::PEERS, Relationships::PROVIDERS};
    propagate(Relationships::CUSTOMERS, send_rels);
}

void BGPSimplePolicy::propagate_to_peers() {
    std::set<Relationships> send_rels = {Relationships::ORIGIN, Relationships::CUSTOMERS};
    propagate(Relationships::PEERS, send_rels);
}

void BGPSimplePolicy::receive_ann(const std::shared_ptr<Announcement>& ann) {
    recvQueue.add_ann(ann);
}

bool BGPSimplePolicy::valid_ann(const std::shared_ptr<Announcement>& ann, Relationships recv_relationship) const {
    // BGP Loop Prevention Check
    if (auto as_ptr = as.lock()) { // Safely obtain a shared_ptr from weak_ptr
        return std::find(ann->as_path.begin(), ann->as_path.end(), as_ptr->asn) == ann->as_path.end();
    }else{
        throw std::runtime_error("AS pointer is not valid.");
    }
}
std::shared_ptr<Announcement> BGPSimplePolicy::copy_and_process(const std::shared_ptr<Announcement>& ann, Relationships recv_relationship) {
    // Check for a valid 'AS' pointer
    auto as_ptr = as.lock();
    if (!as_ptr) {
        throw std::runtime_error("AS pointer is not valid.");
    }

    // Creating a new announcement with modified attributes
    std::vector<int> new_as_path = {as_ptr->asn};
    new_as_path.insert(new_as_path.end(), ann->as_path.begin(), ann->as_path.end());

    // Return a new Announcement object with the modified AS path and recv_relationship
    return std::make_shared<Announcement>(
        ann->prefix,
        new_as_path,
        ann->timestamp,
        ann->seed_asn,
        ann->roa_valid_length,
        ann->roa_origin,
        recv_relationship,
        ann->withdraw,
        ann->traceback_end,
        ann->communities
    );
}

void BGPSimplePolicy::reset_queue(bool reset_q) {
    if (reset_q) {
        // Reset the recvQueue by replacing it with a new instance
        recvQueue = RecvQueue();
    }
}


/////////////////////////////////////////// gao rexford

void BGPSimplePolicy::initialize_gao_rexford_functions() {

    std::cout<<"in init gao"<<std::endl;
    gao_rexford_functions = {
        std::bind(&BGPSimplePolicy::get_best_ann_by_local_pref, this, std::placeholders::_1, std::placeholders::_2),
        std::bind(&BGPSimplePolicy::get_best_ann_by_as_path, this, std::placeholders::_1, std::placeholders::_2),
        std::bind(&BGPSimplePolicy::get_best_ann_by_lowest_neighbor_asn_tiebreaker, this, std::placeholders::_1, std::placeholders::_2)
    };

    std::cout<<"end init gao"<<std::endl;
}
std::shared_ptr<Announcement> BGPSimplePolicy::get_best_ann_by_gao_rexford(const std::shared_ptr<Announcement>& current_ann, const std::shared_ptr<Announcement>& new_ann) {
    if (!new_ann) {
        throw std::runtime_error("New announcement can't be null.");
    }

    if (!current_ann) {
        return new_ann;
    } else {
        for (auto& func : gao_rexford_functions) {
            auto best_ann = func(current_ann, new_ann);
            if (best_ann) {
                return best_ann;
            }
        }
        throw std::runtime_error("No announcement was chosen.");
    }
}

std::shared_ptr<Announcement> BGPSimplePolicy::get_best_ann_by_local_pref(const std::shared_ptr<Announcement>& current_ann, const std::shared_ptr<Announcement>& new_ann) {
    if (!current_ann || !new_ann) {
        throw std::runtime_error("Announcement is null in get_best_ann_by_local_pref.");
    }

    if (current_ann->recv_relationship > new_ann->recv_relationship) {
        return current_ann;
    } else if (current_ann->recv_relationship < new_ann->recv_relationship) {
        return new_ann;
    } else {
        return nullptr;
    }
}

std::shared_ptr<Announcement> BGPSimplePolicy::get_best_ann_by_as_path(const std::shared_ptr<Announcement>& current_ann, const std::shared_ptr<Announcement>& new_ann) {
    if (!current_ann || !new_ann) {
        throw std::runtime_error("Announcement is null in get_best_ann_by_as_path.");
    }

    if (current_ann->as_path.size() < new_ann->as_path.size()) {
        return current_ann;
    } else if (current_ann->as_path.size() > new_ann->as_path.size()) {
        return new_ann;
    } else {
        return nullptr;
    }
}

std::shared_ptr<Announcement> BGPSimplePolicy::get_best_ann_by_lowest_neighbor_asn_tiebreaker(const std::shared_ptr<Announcement>& current_ann, const std::shared_ptr<Announcement>& new_ann) {
    // Determines if the new announcement is better than the current announcement by Gao-Rexford criteria for ties
    if (!current_ann || current_ann->as_path.empty() || !new_ann || new_ann->as_path.empty()) {
        throw std::runtime_error("Invalid announcement or empty AS path in get_best_ann_by_lowest_neighbor_asn_tiebreaker.");
    }

    int current_neighbor_asn = current_ann->as_path.size() > 1 ? current_ann->as_path[1] : current_ann->as_path[0];
    int new_neighbor_asn = new_ann->as_path.size() > 1 ? new_ann->as_path[1] : new_ann->as_path[0];

    if (current_neighbor_asn <= new_neighbor_asn) {
        return current_ann;
    } else {
        return new_ann;
    }
}

///////////////////////////////// propagate
void BGPSimplePolicy::propagate(Relationships propagate_to, const std::set<Relationships>& send_rels) {
    std::vector<std::weak_ptr<AS>> neighbors;

    auto as_shared = as.lock();
    if (!as_shared) {
        // Handle the case where the AS object is no longer valid
        throw std::runtime_error("Weak ref from policy to as no longer exists");
    }

    switch (propagate_to) {
        case Relationships::PROVIDERS:
            neighbors = as_shared->providers;
            break;
        case Relationships::PEERS:
            neighbors = as_shared->peers;
            break;
        case Relationships::CUSTOMERS:
            neighbors = as_shared->customers;
            break;
        default:
            throw std::runtime_error("Unsupported relationship type.");
    }

    for (const auto& neighbor_weak : neighbors) {
        for (const auto& [prefix, ann] : localRIB.prefix_anns()) {
            if (send_rels.find(ann->recv_relationship) != send_rels.end() && !prev_sent(neighbor_weak, ann)) {
                if (policy_propagate(neighbor_weak, ann, propagate_to, send_rels)) {
                    continue;
                } else {
                    process_outgoing_ann(neighbor_weak, ann, propagate_to, send_rels);
                }
            }
        }
    }
}

bool BGPSimplePolicy::policy_propagate(const std::weak_ptr<AS>& neighbor_weak, const std::shared_ptr<Announcement>& ann, Relationships propagate_to, const std::set<Relationships>& send_rels) {
    // This method simply returns false and does not use the neighbor_weak reference
    return false;
}

bool BGPSimplePolicy::prev_sent(const std::weak_ptr<AS>& neighbor_weak, const std::shared_ptr<Announcement>& ann) {
    // This method simply returns false and does not use the neighbor_weak reference
    return false;
}

void BGPSimplePolicy::process_outgoing_ann(const std::weak_ptr<AS>& neighbor_weak, const std::shared_ptr<Announcement>& ann, Relationships propagate_to, const std::set<Relationships>& send_rels) {
    auto neighbor = neighbor_weak.lock();
    if (!neighbor || !neighbor->policy) {
        throw std::runtime_error("weak ref no longer exists");
    }
    neighbor->policy->receive_ann(ann);
}


// Factory function type for creating Policy objects
using PolicyFactoryFunc = std::function<std::unique_ptr<Policy>()>;

class CPPSimulationEngine {
public:
    std::unique_ptr<ASGraph> as_graph;
    int ready_to_run_round;


    // Constructor now accepts a unique_ptr to ASGraph
    CPPSimulationEngine(std::unique_ptr<ASGraph> as_graph, int ready_to_run_round = -1)
        : as_graph(std::move(as_graph)), ready_to_run_round(ready_to_run_round) {

        register_policies();  // Register policy types upon construction
    }

    // Disable copy semantics
    CPPSimulationEngine(const CPPSimulationEngine&) = delete;
    CPPSimulationEngine& operator=(const CPPSimulationEngine&) = delete;

    // Enable move semantics
    CPPSimulationEngine(CPPSimulationEngine&&) = default;
    CPPSimulationEngine& operator=(CPPSimulationEngine&&) = default;


    void setup(const std::vector<std::shared_ptr<Announcement>>& announcements,
               const std::string& base_policy_class_str = "BGPSimplePolicy",
               const std::map<int, std::string>& non_default_asn_cls_str_dict = {}) {
        std::cout<<"in here"<<std::endl;
        set_as_classes(base_policy_class_str, non_default_asn_cls_str_dict);

        std::cout<<"here"<<std::endl;
        seed_announcements(announcements);

        std::cout<<"out here"<<std::endl;
        ready_to_run_round = 0;
    }

    void run(int propagation_round = 0) {

        auto start = std::chrono::high_resolution_clock::now();
        // Ensure that the simulator is ready to run this round
        if (ready_to_run_round != propagation_round) {
            throw std::runtime_error("Engine not set up to run for round " + std::to_string(propagation_round));
        }

        // Propagate announcements
        propagate(propagation_round);

        // Increment the ready to run round
        ready_to_run_round++;
        auto end = std::chrono::high_resolution_clock::now();
        std::chrono::duration<double> elapsed = end - start;
        std::cout << "Propagated in "
                  << std::fixed << std::setprecision(2) << elapsed.count() << " seconds." << std::endl;

    }

    std::vector<std::shared_ptr<Announcement>> get_announcements_from_tsv(const std::string& path) {
        std::vector<std::shared_ptr<Announcement>> announcements;
        std::ifstream file(path);
        std::string line;

        // Skip the header line
        std::getline(file, line);
        std::string expectedHeaderStart = "prefix\tas_path\ttimestamp\tseed_asn\troa_valid_length\troa_origin\trecv_relationship\twithdraw\ttraceback_end\tcommunities";
        if (line.find(expectedHeaderStart) != 0) {
            throw std::runtime_error("TSV file header does not start with the expected format.");
        }



        while (std::getline(file, line)) {
            std::istringstream iss(line);
            std::string token;

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
                prefix, as_path, timestamp, seed_asn, roa_valid_length,
                roa_origin, recv_relationship, withdraw, traceback_end, communities
            );
            announcements.push_back(ann);
        }

        return announcements;
    }

protected:

    ///////////////////////setup funcs
    std::map<std::string, PolicyFactoryFunc> name_to_policy_func_dict;
    // Method to register policy factory functions
    void register_policy_factory(const std::string& name, const PolicyFactoryFunc& factory) {
        name_to_policy_func_dict[name] = factory;
    }
    // Method to register all policies
    void register_policies() {
        // Example of registering a base policy
        register_policy_factory("BGPSimplePolicy", []() -> std::unique_ptr<Policy>{
            std::cout <<"in register_policy"<<std::endl;
            return std::make_unique<BGPSimplePolicy>();
        });
        // Register other policies similarly
        // e.g., register_policy_factory("SpecificPolicy", ...);
    }
    void set_as_classes(const std::string& base_policy_class_str, const std::map<int, std::string>& non_default_asn_cls_str_dict) {
        std::cout << "in set_as_classes" << std::endl;
        for (auto& [asn, as_obj] : as_graph->as_dict) {

                std::cout << "in set_as_classes loop" << std::endl;
            // Determine the policy class string to use
            auto cls_str_it = non_default_asn_cls_str_dict.find(as_obj->asn);

            std::cout << "a" << std::endl;
            std::string policy_class_str = (cls_str_it != non_default_asn_cls_str_dict.end()) ? cls_str_it->second : base_policy_class_str;
            std::cout << "b" << std::endl;

            // Find the factory function in the dictionary
            auto factory_it = name_to_policy_func_dict.find(policy_class_str);

            std::cout << "c" << std::endl;
            if (factory_it == name_to_policy_func_dict.end()) {
                throw std::runtime_error("Policy class not implemented: " + policy_class_str);
            }

            std::cout << "d" << std::endl;
            // Create and set the new policy object

            // Create the policy object using the factory function
            auto policy_object = factory_it->second();
            std::cout << "Policy object created" << std::endl; // Print statement
            // Assign the created policy object to as_obj->policy
            as_obj->policy = std::move(policy_object);

            std::cout << "g" << std::endl;
            //set the reference to the AS
            as_obj->policy->as = std::weak_ptr<AS>(as_obj->shared_from_this());

            std::cout << "f" << std::endl;
        }
    }
    void seed_announcements(const std::vector<std::shared_ptr<Announcement>>& announcements) {
        auto start = std::chrono::high_resolution_clock::now();
        for (const auto& ann : announcements) {
            if (!ann || !ann->seed_asn.has_value()) {
                throw std::runtime_error("Announcement seed ASN is not set.");
            }

            auto as_it = as_graph->as_dict.find(ann->seed_asn.value());
            if (as_it == as_graph->as_dict.end()) {
                throw std::runtime_error("AS object not found in ASGraph.");
            }

            auto& obj_to_seed = as_it->second;
            if (obj_to_seed->policy->localRIB.get_ann(ann->prefix)) {
                throw std::runtime_error("Seeding conflict: Announcement already exists in the local RIB.");
            }

            obj_to_seed->policy->localRIB.add_ann(ann);
        }
        auto end = std::chrono::high_resolution_clock::now();
        std::chrono::duration<double> elapsed = end - start;
        std::cout << "Seeded " << announcements.size() << " announcements in "
                  << std::fixed << std::setprecision(2) << elapsed.count() << " seconds." << std::endl;

    }

    ///////////////////propagation funcs

    void propagate(int propagation_round) {
        propagate_to_providers(propagation_round);
        propagate_to_peers(propagation_round);
        propagate_to_customers(propagation_round);
    }
    void propagate_to_providers(int propagation_round) {
        for (size_t i = 0; i < as_graph->propagation_ranks.size(); ++i) {
            auto& rank = as_graph->propagation_ranks[i];

            if (i > 0) {
                for (auto& as_obj : rank) {
                    as_obj->policy->process_incoming_anns(Relationships::CUSTOMERS, propagation_round);
                }
            }

            for (auto& as_obj : rank) {
                as_obj->policy->propagate_to_providers();
            }
        }
    }
    void propagate_to_peers(int propagation_round) {
        for (auto& [asn, as_obj] : as_graph->as_dict) {
            as_obj->policy->propagate_to_peers();
        }

        for (auto& [asn, as_obj] : as_graph->as_dict) {
            as_obj->policy->process_incoming_anns(Relationships::PEERS, propagation_round);
        }
    }

    void propagate_to_customers(int propagation_round) {
        auto& ranks = as_graph->propagation_ranks;
        size_t i = 0; // Initialize i to 0

        for (auto it = ranks.rbegin(); it != ranks.rend(); ++it, ++i) {
            auto& rank = *it;
            // There are no incoming anns in the top row
            if (i > 0) {
                for (auto& as_obj : rank) {
                    as_obj->policy->process_incoming_anns(Relationships::PROVIDERS, propagation_round);
                }
            }

            for (auto& as_obj : rank) {
                as_obj->policy->propagate_to_customers();
            }
        }
    }
};

CPPSimulationEngine get_engine(std::string filename = "/home/anon/Desktop/caida.tsv") {
    auto asGraph = std::make_unique<ASGraph>(readASGraph(filename));
    return CPPSimulationEngine(std::move(asGraph));
}

int main() {
    std::string filename = "/home/anon/Desktop/caida.tsv";
    std::string announcementsFilename = "/home/anon/Desktop/anns_1000_mod.tsv";
    try {
        //ASGraph asGraph = readASGraph(filename);
        //CPPSimulationEngine engine = CPPSimulationEngine(asGraph);
        auto engine = get_engine(filename);
        // Get announcements from TSV file
        std::vector<std::shared_ptr<Announcement>> announcements = engine.get_announcements_from_tsv(announcementsFilename);

        // Setup the engine with the loaded announcements
        // Assuming setup function takes announcements and other necessary parameters
        engine.setup(announcements);  // Add additional parameters as required
        engine.run(0);
        std::cout << "done" << std::endl;

        // Further processing with asGraph...
    } catch (const std::runtime_error& e) {
        std::cerr << "Error: " << e.what() << std::endl;
        return 1;
    }

    return 0;
}

namespace py = pybind11;
#define PYBIND11_DETAILED_ERROR_MESSAGES

PYBIND11_MODULE(bgpc, m) {
    m.def("main", &main, "what is this desc for?");
    m.def("get_engine", &get_engine, py::arg("filename") = "/home/anon/Desktop/caida.tsv");
    py::enum_<Relationships>(m, "Relationships")
        .value("PROVIDERS", Relationships::PROVIDERS)
        .value("PEERS", Relationships::PEERS)
        .value("CUSTOMERS", Relationships::CUSTOMERS)
        .value("ORIGIN", Relationships::ORIGIN)
        .value("UNKNOWN", Relationships::UNKNOWN)
        .export_values();

    py::class_<CPPSimulationEngine>(m, "CPPSimulationEngine")
        //.def(py::init<ASGraph&, int>(), py::arg("as_graph"), py::arg("ready_to_run_round") = -1)
        //.def("setup", &CPPSimulationEngine::setup,
        //     py::arg("announcements"),
        //     py::arg("base_policy_class_str") = "BGPSimplePolicy",
        //     py::arg("non_default_asn_cls_str_dict") = std::map<int, std::string>{})
        //.def("setup", [](CPPSimulationEngine& engine, const std::vector<py::object>& py_announcements, const std::string& base_policy_class_str, const std::map<int, std::string>& non_default_asn_cls_str_dict) {
        //    std::vector<std::shared_ptr<Announcement>> announcements;
        //    for (auto& py_ann : py_announcements) {
        //        announcements.push_back(py_ann.cast<std::shared_ptr<Announcement>>());
        //    }
        //    engine.setup(announcements, base_policy_class_str, non_default_asn_cls_str_dict);
        //}, py::arg("announcements"), py::arg("base_policy_class_str") = "BGPSimplePolicy", py::arg("non_default_asn_cls_str_dict") = std::map<int, std::string>{})

        .def("setup", [](CPPSimulationEngine& engine, const std::vector<std::shared_ptr<Announcement>>& announcements, const std::string& base_policy_class_str, const std::map<int, std::string>& non_default_asn_cls_str_dict) {
            // Debug: Print the number of announcements
            std::cout << "Setting up engine with " << announcements.size() << " announcements." << std::endl;

            // Check for null pointers
            for (const auto& ann : announcements) {
                if (!ann) {
                    throw std::runtime_error("Null announcement in the list");
                }
            }

            // Call the actual setup method
            engine.setup(announcements, base_policy_class_str, non_default_asn_cls_str_dict);
        }, py::arg("announcements"), py::arg("base_policy_class_str") = "BGPSimplePolicy", py::arg("non_default_asn_cls_str_dict") = std::map<int, std::string>{})
        .def("run", &CPPSimulationEngine::run,
             py::arg("propagation_round") = 0);

    py::class_<Announcement, std::shared_ptr<Announcement>>(m, "Announcement")
        .def(py::init<const std::string&, const std::vector<int>&, int,
                      const std::optional<int>&, const std::optional<bool>&,
                      const std::optional<int>&, Relationships, bool, bool,
                      const std::vector<std::string>&>())
        .def_readonly("prefix", &Announcement::prefix)
        .def_readonly("as_path", &Announcement::as_path)
        .def_readonly("timestamp", &Announcement::timestamp)
        .def_readonly("seed_asn", &Announcement::seed_asn)
        .def_readonly("roa_valid_length", &Announcement::roa_valid_length)
        .def_readonly("roa_origin", &Announcement::roa_origin)
        .def_readonly("recv_relationship", &Announcement::recv_relationship)
        .def_readonly("withdraw", &Announcement::withdraw)
        .def_readonly("traceback_end", &Announcement::traceback_end)
        .def_readonly("communities", &Announcement::communities)
        .def("prefix_path_attributes_eq", &Announcement::prefix_path_attributes_eq)
        .def("invalid_by_roa", &Announcement::invalid_by_roa)
        .def("valid_by_roa", &Announcement::valid_by_roa)
        .def("unknown_by_roa", &Announcement::unknown_by_roa)
        .def("covered_by_roa", &Announcement::covered_by_roa)
        .def("roa_routed", &Announcement::roa_routed)
        .def("origin", &Announcement::origin);
}
