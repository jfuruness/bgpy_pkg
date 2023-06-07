from caida_collector_pkg import CaidaCollector

graph = CaidaCollector().run()
input(graph.as_dict[112])
input(graph[112])
print(len(graph))
