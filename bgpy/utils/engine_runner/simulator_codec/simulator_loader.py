from yaml import SafeLoader


# https://stackoverflow.com/a/39554610/8903959
class SimulatorLoader(SafeLoader):
    def construct_python_tuple(self, node):
        return tuple(self.construct_sequence(node))


SimulatorLoader.add_constructor(
    "tag:yaml.org,2002:python/tuple", SimulatorLoader.construct_python_tuple
)
