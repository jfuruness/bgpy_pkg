#include "bgp_simple_policy.hpp"
#include "rov_simple_policy.hpp"

bool ROVSimplePolicy::valid_ann(const std::shared_ptr<Announcement>& ann, Relationships recv_relationship) const {
    return !ann->invalid_by_roa() && BGPSimplePolicy::valid_ann(ann, recv_relationship);
}
