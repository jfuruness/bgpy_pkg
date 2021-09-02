from datetime import datetime

from ..engine.bgp_as import BGPAS
from ..engine.simulator_engine import SimulatorEngine


# tmp_path is a pytest fixture
def run_example(tmp_path,
                peers=list(),
                customer_providers=list(),
                as_policies=dict(),
                announcements=list(),
                local_ribs=dict(),
                BaseASCls=BGPAS
                ):
    """Runs an example"""

    print("populating engine")
    start = datetime.now()
    engine = SimulatorEngine(set(customer_providers),
                             set(peers),
                             BaseASCls=BaseASCls,
                             as_policies=as_policies)
    print((start-datetime.now()).total_seconds())
    print("Running engine")
    start = datetime.now()
    engine.run(announcements, clear=False)
    print((start-datetime.now()).total_seconds())
    if local_ribs:
        for as_obj in engine.as_dict.values():
            print("ASN:", as_obj.asn)
        for prefix, ann in as_obj.local_rib.items():
            print(ann)
        as_obj.local_rib.assert_eq(local_ribs[as_obj.asn])
