import csv

from lib_caida_collector import CaidaCollector

from .defaults import SubprefixHijackAtkAnn, PrefixHijackVicAnn
from .utils import CustomerProviderLink, PeerLink, run_example

def test_proof_of_concept(tmp_path):
    collector = CaidaCollector()
    collector.run()
    path = collector.tsv_path

    peers = set()
    cps = set()

    with open(path, "r") as f:
        reader = csv.DictReader(f, delimiter="\t")
        asns = []
        for row in reader:
            asns.append(int(row["asn"]))
            if row["peers"] == "{}":
                row_peers = []
            else:
                row_peers = [int(x) for x in row["peers"][1:-1].split(",")]
            if row["customers"] == "{}":
                row_customers = []
            else:
                row_customers = [int(x) for x in row["customers"][1:-1].split(",")]
            if row["providers"] == "{}":
                row_providers = []
            else:
                row_providers = [int(x) for x in row["providers"][1:-1].split(",")]

            for peer in row_peers:
                peers.add(tuple(list(sorted([int(row["asn"]), peer]))))
            for customer in row_customers:
                cps.add(tuple(list(sorted([customer, int(row["asn"])]))))
            for provider in row_providers:
                cps.add(tuple(list(sorted([int(row["asn"]), provider]))))

    peer_classes = [PeerLink(*x) for x in sorted(peers)]
    cp_classes = [CustomerProviderLink(customer=x[0], provider=x[1]) for x in sorted(cps)]
    as_types = {asn: 0 for asn in asns}
    # These ASes are mh with lots of providers
    #announcements = [PrefixHijackVicAnn(as_path=(393226,)),
    #                 SubprefixHijackAtkAnn(as_path=(262194,))]
    # Lets cheat and just make prefixes ints for now for this proof of concept
    stubs = [393216,262146,262148,131078,393222,393226,393229,262158,131088,17,
             22,131095,131097,131089,131099,393244,262169,26,262167,393248,
             262176,262173,393251,393247,38,262183,393257,393258,393256,262188,
             131117,393255,48,262194,131122,393267,393261,262196,56,262201,
             393273,131128,393276,393278,262207,262208,65,393283,262212,262213,
             262214,262216,393289,393290,262221,262223,393296,262225,83,393303,
             88,393305,262231,91,92,131164,393310,93,131168,262241,393313,
             393315,262238,131169,262245,393321,104,262252,393325,131182,
             262254,262255,262256,393323,393332,118,131183,393336,393337,121,
             393341,131197,131199,393344,262272,393346,262278,262280,393355]
    announcements = []
    for i, stub in enumerate(stubs):
        prefix = str(i) * len("1.2.0.0/16")
        announcements.append(PrefixHijackVicAnn(prefix=prefix, as_path=(stub,)))

    run_example(tmp_path, peers=peer_classes, customer_providers=cp_classes,
                as_types=as_types, announcements=announcements)
