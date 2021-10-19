from lib_caida_collector import CaidaCollector
from lib_bgp_simulator import Simulator, Graph, ROVAS, SubprefixHijack, BGPAS, SimulatorEngine, YamlAbleEnum
from datetime import datetime
from pathlib import Path

class YamlSystemTestRunner:

    def __init__(self, dir_):
        """dir_ should be the dir_ with the yaml"""
        self.dir_ = dir_
        self.codec = SimulatorCodec()

    def run_test(self, empty_engine_kwargs, engine_input_kwargs):

        engine, engine_input = self.write_load_engine(empty_engine_kwargs,
                                                      engine_input_kwargs)

        scenario, engine_output_guess = self.get_results(engine, engine_input)

        self.write_check_results(engine, scenario, engine_output_guess)

    def write_load_engine(self, empty_engine_kwargs, engine_input_kwargs):

        # Write the graph if it does not exist
        if not self.empty_engine_yaml_path.exists():
            self.write_empty_engine_yaml(**empty_engine_kwargs)

        if not self.engine_input_yaml_path.exists():
            self.write_engine_input_yaml(**engine_input_kwargs)

        return self.load_engine_and_input()

    def get_results(self, engine, engine_input):
        scenario = Scenario(engine=engine, engine_input=engine_input)
        subgraphs = {"all_ases": [x.asn for x in engine]}

        # 0 for the propagation round. Change this later
        traceback_guess = scenario.run(subgraphs, 0, engine_setup=True)

        return scenario, traceback_guess

    def write_check_results(self, engine, scenario, traceback_guess):
        if not self.engine_output_yaml_path.exists():
            self.write_engine_output_yaml(engine)

        if not self.traceback_yaml_path.exists():
            self.write_traceback_yaml(traceback_guess)

        self.validate_engine_output(engine)
        self.validate_scenario(scenario)
        self.validate_traceback_guess(traceback_guess)

    def write_empty_engine_yaml(self,
                                customer_provider_links: set,
                                peer_links: set,
                                BaseASCls=None,
                                ixps=set(),
                                input_clique=set()
                                adopting_as_dict={}):
        """Writes yaml empty engine graph"""

        engine = SimulatorEngine(customer_provider_links,
                                 peer_links,
                                 ixps,
                                 BaseASCls=BaseASCls,
                                 ixps=ixps,
                                 input_clique=input_clique)
        self.codec.dump(engine, path=self.empty_engine_yaml_path)

    def write_engine_input_yaml(self,
                                EngineInputCls,
                                attacker_asn,
                                victim_asn,
                                as_classes: dict):
        """Writes engine input yaml"""

        engine_input = EngineInputCls(attacker_asn=attacker_asn,
                                      victim_asn=victim_asn,
                                      as_classes=as_classes)
        self.codec.dump(engine_input, path=self.engine_input_yaml_path)

    def write_engine_output_yaml(self, engine):
        logging.warning("Writing unverified engine output yaml")
        self.codec.dump(engine, path=self.engine_output_yaml_path)

    def write_traceback_yaml(self, traceback_output: dict):
        logging.warning("Writing unverified traceback yaml")
        self.codec.dump(traceback_output, path=self.traceback_yaml_path)

    def validate_engine_output(self, engine):
        raise NotImplementedError

    def validate_scenario(self, scenario):
        pass

    def validate_traceback_guess(traceback_guess):
        raise NotImplementedError

    @property
    def empty_engine_yaml_path(self):
        return self.dir_ / "empty_engine_graph.yaml"

    @property
    def engine_input_yaml_path(self):
        return self.dir_ / "engine_input.yaml"

    @property
    def engine_output_yaml_path(self):
        return self.dir_ / "engine_output.yaml"

    @property
    def traceback_yaml_path(self):
        return self.dir_ / "engine_traceback.yaml"


def run_yaml_system_test(_dir, links=None, BaseASCls



def _get_engine_and_subgraphs(_dir, BaseASCls):
    # Done just to get subgraphs, change this later
    engine = CaidaCollector(BaseASCls=BaseASCls,
                            GraphCls=SimulatorEngine,
                            _dir=_dir,
                            _dir_exist_ok=True).run(tsv=False)
    subgraphs = Graph._get_subgraphs(None, engine)
    return engine, subgraphs


def _get_and_run_engine(_dir, BaseASCls, engine):
    engine_input = SubprefixHijack(subgraphs, engine, 20)
    engine.setup(engine_input, BGPAS, ROVAS)
    engine.run(propagation_round=0, engine_input=engine_input)
    return engine

def main():

    # YAML STUFF
    from yamlable import YamlCodec
    from typing import Type, Any, Iterable, Tuple

    # 2-way mappings between the types and the yaml tags
    types_to_yaml_tags = {X: X.yaml_suffix() for X in YamlAbleEnum.yamlable_enums()}
    yaml_tags_to_types = {v: k for k, v in types_to_yaml_tags.items()}

    class MyCodec(YamlCodec):
        @classmethod
        def get_yaml_prefix(cls):
            return "!yamlable_codec/"  # This is our root yaml tag

        # ---- 

        @classmethod
        def get_known_types(cls) -> Iterable[Type[Any]]:
            # return the list of types that we know how to encode
            return types_to_yaml_tags.keys()

        @classmethod
        def is_yaml_tag_supported(cls, yaml_tag_suffix: str) -> bool:
            # return True if the given yaml tag suffix is supported
            return yaml_tag_suffix in yaml_tags_to_types.keys()

        # ----

        @classmethod
        def from_yaml_dict(cls, yaml_tag_suffix: str, dct, **kwargs):
            # Create an object corresponding to the given tag, from the decoded dict
            typ = yaml_tags_to_types[yaml_tag_suffix]
            if issubclass(typ, YamlAbleEnum):
                # Don't use unessecary name
                return typ(value=dct["value"])
            else:
                return typ(**dct)

        @classmethod
        def to_yaml_dict(cls, obj) -> Tuple[str, Any]:
            if isinstance(obj, YamlAbleEnum):
                return types_to_yaml_tags[type(obj)], {"value": obj.value, "name": obj.name}
            else:
                # Encode the given object and also return the tag that it should have
                return types_to_yaml_tags[type(obj)], vars(obj)

    MyCodec.register_with_pyyaml()
    import yaml
    from yaml import dump, load, safe_load, SafeLoader

    engine = _get_and_run_engine()
    # Turns off references in the yaml which makes it hard to read for enums
    yaml.Dumper.ignore_aliases = lambda *args : True
    dump_str = dump(engine)
    print(dump_str)

    class PrettySafeLoader(SafeLoader):
        def construct_python_tuple(self, node):
            return tuple(self.construct_sequence(node))

    PrettySafeLoader.add_constructor(
        u'tag:yaml.org,2002:python/tuple',
        PrettySafeLoader.construct_python_tuple)
    load(dump_str, Loader=PrettySafeLoader)

if __name__ == "__main__":
    main()
