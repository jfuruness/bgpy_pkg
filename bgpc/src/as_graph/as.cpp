#include "as.hpp"
#include "policy.hpp" // Include the Policy header
#include "bgp_simple_policy.hpp" // Include the BGPSimplePolicy header

AS::AS(int asn)
    : asn(asn),
      policy(std::make_unique<BGPSimplePolicy>(0)),
      input_clique(false),
      ixp(false),
      stub(false),
      multihomed(false),
      transit(false),
      customer_cone_size(0),
      as_rank(0),
      propagation_rank(0) {
    // Can't set 'policy->as' here, AS must already be accessed by shared_ptr before calling else err
}

void AS::initialize() {
    policy->as = shared_from_this();
}
