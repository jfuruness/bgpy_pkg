#ifndef ROV_SIMPLE_POLICY_HPP
#define ROV_SIMPLE_POLICY_HPP


#include <functional>
#include <vector>
#include <set>
#include <memory>

#include "bgp_simple_policy.hpp"
#include "announcement.hpp"

// Forward declaration
class AS;

class ROVSimplePolicy : public BGPSimplePolicy {
public:
    using BGPSimplePolicy::BGPSimplePolicy;
protected:
    virtual bool valid_ann(const std::shared_ptr<Announcement>& ann, Relationships recv_relationship) const override;
};

#endif // ROV_SIMPLE_POLICY_HPP
