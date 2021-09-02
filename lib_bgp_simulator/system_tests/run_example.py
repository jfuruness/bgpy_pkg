from datetime import datetime

from .graph_writer import write_graph

from ...bgp_as import BGPAS
from ...simulator_engine import SimulatorEngine


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
    engine = SimulatorEngine(customer_providers,
                             peers,
                             BaseAsCls=BaseAsCls,
                             as_policies=as_policies)
    print((start-datetime.now()).total_seconds())
    print("Running engine")
    start = datetime.now()
    engine.run(announcements, clear=False)
    input((start-datetime.now()).total_seconds())
    for as_obj in engine:
        print("ASN:", as_obj.asn)
        for prefix, ann in as_obj.local_rib.items():
            print(ann)
        if local_ribs:
            as_obj.local_rib.assert_eq(local_ribs[as_obj.asn])
