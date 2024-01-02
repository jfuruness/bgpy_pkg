#ifndef POLICY_HPP
#define POLICY_HPP

#include <memory>
#include "enums.hpp"
#include "local_rib.hpp"
#include "recv_queue.hpp"
#include "announcement.hpp"

// Forward declaration of AS and Relationships
class AS;

class Policy {
public:
    std::weak_ptr<AS> as;
    LocalRIB localRIB;
    RecvQueue recvQueue;
    const int max_prefix_block_id;


    explicit Policy(int max_prefix_block_id, LocalRIB&& rib, RecvQueue&& queue);
    explicit Policy(int max_prefix_block_id);
    // You need virtual destructors in base class or else derived classes
    // won't clean up properly
    virtual ~Policy() = default; // Virtual and uses the default implementation

    virtual void receive_ann(const std::shared_ptr<Announcement>& ann) = 0;
    virtual void process_incoming_anns(Relationships from_rel, int propagation_round, bool reset_q = true) = 0;
    virtual void propagate_to_providers() = 0;
    virtual void propagate_to_customers() = 0;
    virtual void propagate_to_peers() = 0;

    virtual bool valid_ann(const std::shared_ptr<Announcement>& ann, Relationships recv_relationship) const = 0;
    virtual std::shared_ptr<Announcement> copy_and_process(const std::shared_ptr<Announcement>& ann, Relationships recv_relationship) = 0;

    virtual bool new_ann_better_gao_rexford(const std::shared_ptr<Announcement>& current_ann, const bool& current_ann_processed, const std::shared_ptr<Announcement>& new_ann) = 0;
};

#endif // POLICY_HPP
