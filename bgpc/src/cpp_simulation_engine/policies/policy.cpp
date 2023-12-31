#include "policy.hpp"

Policy::Policy(int max_prefix_block_id) : max_prefix_block_id(max_prefix_block_id), localRIB(max_prefix_block_id), recvQueue(max_prefix_block_id) {
    // Constructor implementation (if any logic is needed)

}

// No other implementations are needed here as the methods are pure virtual
