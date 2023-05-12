import random

from caida_collector_pkg import CaidaCollector

bgp_dag = CaidaCollector().run()
base = None
temp_nodes = list(bgp_dag)
random.shuffle(temp_nodes)
for node in temp_nodes:
    if node.input_clique:
        base = node
        break

base_customers = []
temp_nodes = list(base.customers)
random.shuffle(temp_nodes)

for node in temp_nodes[:5]:
    base_customers.append(node)

secondary_customers = []
for node in base_customers:
    temp_nodes = list(node.customers)
    random.shuffle(temp_nodes)

    for i, customer in enumerate(temp_nodes):
        if i > 2:
            break
        else:
            secondary_customers.append(customer)

    temp_nodes = list(node.peers)
    random.shuffle(temp_nodes)

    for i, peer in enumerate(temp_nodes):
        if i > 1:
            break
        else:
            secondary_customers.append(peer)


tertiary_customers = []
for node in secondary_customers:
    temp_nodes = list(node.customers)
    random.shuffle(temp_nodes)

    for i, customer in enumerate(temp_nodes):
        if i > 1:
            break
        else:
            tertiary_customers.append(customer)

    temp_nodes = list(node.peers)
    random.shuffle(temp_nodes)

    for i, peer in enumerate(temp_nodes):
        if i > 1:
            break
        else:
            tertiary_customers.append(peer)

forth_customers = []
for node in secondary_customers:
    temp_nodes = list(node.customers)
    random.shuffle(temp_nodes)

    for i, customer in enumerate(temp_nodes):
        if i > 1:
            break
        else:
            forth_customers.append(customer)

    temp_nodes = list(node.peers)
    random.shuffle(temp_nodes)

    for i, peer in enumerate(temp_nodes):
        if i > 1:
            break
        else:
            forth_customers.append(peer)

fifth_customers = []
for node in secondary_customers:
    temp_nodes = list(node.customers)
    random.shuffle(temp_nodes)

    for i, customer in enumerate(temp_nodes):
        if i > 1:
            break
        else:
            fifth_customers.append(customer)

    temp_nodes = list(node.peers)
    random.shuffle(temp_nodes)

    for i, peer in enumerate(temp_nodes):
        if i > 1:
            break
        else:
            fifth_customers.append(peer)


all_asns = set([x.asn for x in [base] +
                base_customers +
                secondary_customers +
                tertiary_customers +
                forth_customers +
                fifth_customers])
print(len(all_asns))

bgp_dag_nodes = list(bgp_dag)
for node in bgp_dag_nodes:
    if node.asn in all_asns:
        for customer in node.customers:
            if customer.asn in all_asns:
                print(f"CPLink(provider_asn={node.asn}, "
                      f"customer_asn={customer.asn}),")

for node in bgp_dag_nodes:
    if node.asn in all_asns:
        for peer in node.peers:
            if peer.asn in all_asns:
                print(f"PeerLink({node.asn}, {peer.asn}),")
