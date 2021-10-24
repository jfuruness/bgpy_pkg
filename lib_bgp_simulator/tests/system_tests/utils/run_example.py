from datetime import datetime

from ....engine import BGPSimpleAS
from ....engine import SimulatorEngine
from ....engine_input import EngineInput

class EngineInputEasy(EngineInput):
    def __init__(self, announcements, as_cls_dict):
        self.announcements = announcements
        self.as_cls_dict = as_cls_dict

    def get_as_classes(self, *args, **kwargs):
        return self.as_cls_dict

# tmp_path is a pytest fixture
def run_example(peers=list(),
                customer_providers=list(),
                as_policies=dict(),
                announcements=list(),
                local_ribs=dict(),
                outcomes=dict(),
                BaseASCls=BGPSimpleAS,
                ):
    """Runs an example"""

    print("populating engine")
    start = datetime.now()
    engine = SimulatorEngine(set(customer_providers),
                             set(peers),
                             BaseASCls=BaseASCls)
    engine_input = EngineInputEasy(announcements, as_policies)
    print((start-datetime.now()).total_seconds())
    print("Running engine")
    start = datetime.now()
    engine.setup(engine_input, BaseASCls, None)
    engine.run(engine_input=engine_input)
    print((start-datetime.now()).total_seconds())
    if local_ribs:
        for as_obj in engine:
            print("ASN:", as_obj.asn)
            print("computed local rib:")
            for prefix, ann in as_obj._local_rib.prefix_anns():
                print(ann)
            print("Actual local rib:")
            for prefix, ann in local_ribs[as_obj.asn].items():
                print(ann)
            assert as_obj._local_rib == local_ribs[as_obj.asn]
    if outcomes:
        pass
