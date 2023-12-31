#include <iostream>
#include <algorithm>
#include <stdexcept>

#include "policy.hpp"
#include "bgp_simple_policy.hpp"
#include "as.hpp"

BGPSimplePolicy::BGPSimplePolicy(int max_prefix_block_id) : Policy(max_prefix_block_id) {
    // NOTE: this is incredibly slow and really slows down the setting of AS classes
    // don't use this
    //initialize_gao_rexford_functions();
}

BGPSimplePolicy::BGPSimplePolicy(int max_prefix_block_id, LocalRIB&& local_rib, RecvQueue&& recv_queue) : Policy(max_prefix_block_id, std::move(local_rib), std::move(recv_queue)) {
    // NOTE: this is incredibly slow and really slows down the setting of AS classes
    // don't use this
    //initialize_gao_rexford_functions();
}

