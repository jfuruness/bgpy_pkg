#include "policy.hpp"

Policy::Policy(int max_prefix_block_id) : max_prefix_block_id(max_prefix_block_id), localRIB(max_prefix_block_id), recvQueue(max_prefix_block_id) {
    // Constructor implementation (if any logic is needed)

}

Policy::Policy(int max_prefix_block_id, LocalRIB&& rib, RecvQueue&& queue)
    : max_prefix_block_id(max_prefix_block_id),
      localRIB(std::move(rib)),
      recvQueue(std::move(queue)) {
    // Constructor implementation to clear out old anns
    localRIB.reset(max_prefix_block_id);
    recvQueue.reset(max_prefix_block_id);
}

// No other implementations are needed here as the methods are pure virtual
