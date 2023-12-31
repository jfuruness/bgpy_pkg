#include <iostream>
#include <algorithm>
#include <stdexcept>

#include "policy.hpp"
#include "bgp_simple_policy.hpp"
#include "as.hpp"

BGPSimplePolicy::BGPSimplePolicy(int max_prefix_block_id) : Policy(max_prefix_block_id) {
    initialize_gao_rexford_functions();
}
