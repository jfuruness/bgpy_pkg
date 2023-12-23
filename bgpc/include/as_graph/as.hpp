#ifndef AS_HPP
#define AS_HPP

#include <memory>
#include <vector>
#include "policy.hpp"

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

    AS(int asn);
    void initialize();

    // Add other methods and members as needed
};

#endif // AS_HPP
