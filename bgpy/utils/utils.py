import json
import os
import random
from pathlib import Path

from frozendict import frozendict
from rov_collector import rov_collector_classes

from bgpy.simulation_engine import ROV, PeerROV, Policy


def max_prob_rov(asn, info_list) -> None | type[Policy]:
    """Takes the max probability from all datasets and adopts probabilistically"""

    # AT&T famously only filters peers
    if int(asn) == 7018:
        return PeerROV

    max_percent: float = 0
    # Calculate max_percent for each ASN
    for info in info_list:
        max_percent = max(max_percent, float(info["percent"]))

    # Use max_percent as the probability for inclusion
    # Ignore random generation err
    adopt = max_percent == 100 or random.random() * 100 < max_percent  # noqa: S311
    return ROV if adopt else None


def get_real_world_rov_asn_cls_dict(
    json_path: Path = Path.home() / "Desktop" / "rov_info.json",
    requests_cache_db_path: Path | None = None,
    get_adopt_policy_cls_func=max_prob_rov,
) -> frozendict[int, type[ROV]]:
    if not json_path.exists():
        for CollectorCls in rov_collector_classes:
            CollectorCls(
                json_path=json_path,
                requests_cache_db_path=requests_cache_db_path,
            ).run()

    python_hash_seed = os.environ.get("PYTHONHASHSEED")
    if python_hash_seed:
        random.seed(int(python_hash_seed))

    with json_path.open() as f:
        data = json.load(f)
        hardcoded_dict = dict()
        for asn, info_list in data.items():
            AdoptPolicyCls = get_adopt_policy_cls_func(asn, info_list)
            if AdoptPolicyCls:
                hardcoded_dict[int(asn)] = AdoptPolicyCls

    return frozendict(hardcoded_dict)
