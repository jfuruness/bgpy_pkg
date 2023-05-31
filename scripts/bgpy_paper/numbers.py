from caida_collector_pkg import CaidaCollector

graph = CaidaCollector().run()
print(len(graph))
