# YAML STUFF
from yamlable import YamlCodec
from typing import Any, Iterable
import yaml

from .simulator_loader import SimulatorLoader
from bgpy.enums import CPPRelationships, CPPOutcomes, YamlAbleEnum
from bgpy.simulation_engines.cpp_simulation_engine import CPPAnnouncement

# 2-way mappings between the types and the yaml tags
types_to_yaml_tags = {X: X.yaml_suffix() for X in YamlAbleEnum.yamlable_enums()}
types_to_yaml_tags[CPPOutcomes] = CPPOutcomes.__name__
types_to_yaml_tags[CPPRelationships] = CPPRelationships.__name__
types_to_yaml_tags[CPPAnnouncement] = CPPAnnouncement.__name__
yaml_tags_to_types = {v: k for k, v in types_to_yaml_tags.items()}


class SimulatorCodec(YamlCodec):
    @classmethod
    def get_yaml_prefix(cls):
        """Root yaml tag"""

        return "!simulator_codec/"

    @classmethod
    def get_known_types(cls) -> Iterable[type[Any]]:
        """return the list of types that we know how to encode"""

        return types_to_yaml_tags.keys()

    @classmethod
    def is_yaml_tag_supported(cls, yaml_tag_suffix: str) -> bool:
        """return True if the given yaml tag suffix is supported"""

        return yaml_tag_suffix in yaml_tags_to_types.keys()

    @classmethod
    def from_yaml_dict(cls, yaml_tag_suffix: str, dct, **kwargs):
        """Creates object related to the given tag, from decoded dict"""

        typ = yaml_tags_to_types[yaml_tag_suffix]
        if issubclass(typ, YamlAbleEnum) or typ in (CPPOutcomes, CPPRelationships):
            # Don't use unessecary name
            return typ(value=dct["value"])
        else:
            return typ(**dct)

    @classmethod
    def to_yaml_dict(cls, obj) -> tuple[str, Any]:
        """Converts objects to yaml dicts"""

        if isinstance(obj, YamlAbleEnum) or isinstance(
            obj, (CPPOutcomes, CPPRelationships)
        ):
            return types_to_yaml_tags[type(obj)], {"value": obj.value, "name": obj.name}
        elif isinstance(obj, CPPAnnouncement):
            return types_to_yaml_tags[type(obj)], {
                "prefix_block_id": obj.prefix_block_id,
                "prefix": obj.prefix,
                "as_path": obj.as_path,
                "timestamp": obj.timestamp,
                "seed_asn": obj.seed_asn,
                "roa_valid_length": obj.roa_valid_length,
                "roa_origin": obj.roa_origin,
                "recv_relationship": obj.recv_relationship,
                "withdraw": obj.withdraw,
                "traceback_end": obj.traceback_end,
                # "communities": obj.communities,
            }
        else:
            # Encode the given object and also return the tag it should have
            return types_to_yaml_tags[type(obj)], vars(obj)

    def dump(self, obj, path=None):
        # https://stackoverflow.com/a/30682604/8903959
        # Ignores references for more readable output
        yaml.Dumper.ignore_aliases = lambda *args: True  # type: ignore
        if path is None:
            yaml.dump(obj)
        else:
            with path.open(mode="w") as f:
                yaml.dump(obj, f)

    def load(self, path):
        with path.open(mode="r") as f:
            return yaml.load(f, Loader=SimulatorLoader)


SimulatorCodec.register_with_pyyaml()
