from lib_caida_collector import CaidaCollector
from lib_bgp_simulator import Simulator, Graph, ROVAS, SubprefixHijack, BGPAS, SimulatorEngine, YamlAbleEnum
from datetime import datetime
from pathlib import Path


def _get_and_run_engine():
    # Done just to get subgraphs, change this later
    engine = CaidaCollector(BaseASCls=BGPAS,
                            GraphCls=SimulatorEngine,
                            _dir_exist_ok=True).run(tsv=False)
    subgraphs = Graph._get_subgraphs(None, engine)
    engine_input = SubprefixHijack(subgraphs, engine, 20)
    engine.setup(engine_input, BGPAS, ROVAS)
    engine.run(propagation_round=0, engine_input=engine_input)
    return engine

def main():

    # YAML STUFF
    from yamlable import YamlCodec
    from typing import Type, Any, Iterable, Tuple

    # 2-way mappings between the types and the yaml tags
    types_to_yaml_tags = {X: X.yaml_tag() for X in YamlAbleEnum.yamlable_enums()}
    types_to_yaml_tags[tuple] = "!!python/tuple"
    yaml_tags_to_types = {v: k for k, v in types_to_yaml_tags.items()}

    class MyCodec(YamlCodec):
        @classmethod
        def get_yaml_prefix(cls):
            return "!mycodec/"  # This is our root yaml tag

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
            if typ is tuple:
                input("asfda")
            return typ(**dct)

        @classmethod
        def to_yaml_dict(cls, obj) -> Tuple[str, Any]:
            if isinstance(obj, YamlAbleEnum):
                return types_to_yaml_tags[type(obj)], {"value": obj.value}
            else:
                # Encode the given object and also return the tag that it should have
                return types_to_yaml_tags[type(obj)], vars(obj)

    MyCodec.register_with_pyyaml()
    from yaml import dump, load, safe_load, SafeLoader

    engine = _get_and_run_engine()
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
