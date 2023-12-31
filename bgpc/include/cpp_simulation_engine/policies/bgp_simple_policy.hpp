#ifndef BGP_SIMPLE_POLICY_HPP
#define BGP_SIMPLE_POLICY_HPP


#include <functional>
#include <vector>
#include <set>
#include <memory>

#include "policy.hpp"
#include "announcement.hpp"

// Forward declaration
class AS;

class BGPSimplePolicy : public Policy {
public:
    explicit BGPSimplePolicy(int max_prefix_block_id);
    virtual ~BGPSimplePolicy() override = default;

    void process_incoming_anns(Relationships from_rel, int propagation_round, bool reset_q = true) override;
    void propagate_to_providers() override;
    void propagate_to_customers() override;
    void propagate_to_peers() override;
    void receive_ann(const std::shared_ptr<Announcement>& ann) override;

protected:
    std::vector<std::function<std::shared_ptr<Announcement>(const std::shared_ptr<Announcement>&, const std::shared_ptr<Announcement>&)>> gao_rexford_functions;

    virtual bool valid_ann(const std::shared_ptr<Announcement>& ann, Relationships recv_relationship) const;
    std::shared_ptr<Announcement> copy_and_process(const std::shared_ptr<Announcement>& ann, Relationships recv_relationship);
    void reset_queue(bool reset_q);
    void initialize_gao_rexford_functions();
    std::shared_ptr<Announcement> get_best_ann_by_gao_rexford(const std::shared_ptr<Announcement>& current_ann, const std::shared_ptr<Announcement>& new_ann);
    std::shared_ptr<Announcement> get_best_ann_by_local_pref(const std::shared_ptr<Announcement>& current_ann, const std::shared_ptr<Announcement>& new_ann);
    std::shared_ptr<Announcement> get_best_ann_by_as_path(const std::shared_ptr<Announcement>& current_ann, const std::shared_ptr<Announcement>& new_ann);
    std::shared_ptr<Announcement> get_best_ann_by_lowest_neighbor_asn_tiebreaker(const std::shared_ptr<Announcement>& current_ann, const std::shared_ptr<Announcement>& new_ann);
    void propagate(Relationships propagate_to, const std::set<Relationships>& send_rels);
    bool policy_propagate(const std::weak_ptr<AS>& neighbor_weak, const std::shared_ptr<Announcement>& ann, Relationships propagate_to, const std::set<Relationships>& send_rels);
    bool prev_sent(const std::weak_ptr<AS>& neighbor_weak, const std::shared_ptr<Announcement>& ann);
    void process_outgoing_ann(const std::weak_ptr<AS>& neighbor_weak, const std::shared_ptr<Announcement>& ann, Relationships propagate_to, const std::set<Relationships>& send_rels);
};

#endif // BGP_SIMPLE_POLICY_HPP
