#include <iostream>
#include <algorithm>
#include <stdexcept>

#include "policy.hpp"
#include "bgp_simple_policy.hpp"
#include "as.hpp"

BGPSimplePolicy::BGPSimplePolicy() : Policy() {
    std::cout << "in bgpsimple" << std::endl;
    initialize_gao_rexford_functions();
    std::cout << "out bgpsimple" << std::endl;
}
