from statistics import mean

from frozendict import frozendict

from bgpy.as_graphs import CAIDAASGraphConstructor, AS

def main():
    bgp_dag = CAIDAASGraphConstructor(
        as_graph_kwargs=frozendict({
            "store_customer_cone_size": True,
            "store_customer_cone_asns": True,
            "store_provider_cone_size": True,
            "store_provider_cone_asns": True,
        })
    ).run()
    for as_ in bgp_dag:
        if as_.stub:
            # print(len(as_.customer_cone_asns))
            # print(len(as_.provider_cone_asns))
            # input()
            pass
    customer_cone_sizes = [len(x.customer_cone_asns) for x in bgp_dag]
    provider_cone_sizes = [len(x.provider_cone_asns) for x in bgp_dag]
    provider_cone_size_attrs = [x.provider_cone_size for x in bgp_dag]


    mean_cc = sum(provider_cone_sizes) / len(provider_cone_sizes)
    # for c, p in zip(customer_cone_sizes, provider_cone_sizes):
    #     input(c)
    #     input(p)
    print(f"{mean(customer_cone_sizes)} mean cc")
    print(f"{sum(customer_cone_sizes)} mean cc")
    print(f"{mean(provider_cone_sizes)} mean pc")
    print(f"{sum(provider_cone_sizes)} mean pc")

if __name__ == "__main__":
    main()
