from datetime import datetime

from ....engine import BGPAS
from ....engine import SimulatorEngine


# tmp_path is a pytest fixture
def run_example(peers=list(),
                customer_providers=list(),
                as_policies=dict(),
                announcements=list(),
                local_ribs=dict(),
                BaseASCls=BGPAS,
                ):
    """Runs an example"""

    print("populating engine")
    start = datetime.now()
    engine = SimulatorEngine(set(customer_providers),
                             set(peers),
                             BaseASCls=BaseASCls)
    for asn, as_policy in as_policies.items():
        engine.as_dict[asn].__class__ = as_policy
        engine.as_dict[asn].__init__(reset_base=False)
    print((start-datetime.now()).total_seconds())
    print("Running engine")
    start = datetime.now()
    engine.run(announcements)
    print((start-datetime.now()).total_seconds())
    if local_ribs:
        for as_obj in engine:
            print("ASN:", as_obj.asn)
            for prefix, ann in as_obj.local_rib.prefix_anns():
                print(ann)
            assert as_obj.local_rib == local_ribs[as_obj.asn]
