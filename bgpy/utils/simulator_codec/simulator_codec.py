# YAML STUFF
from yamlable import YamlCodec
from typing import Any, Iterable
import yaml

from .simulator_loader import SimulatorLoader
from bgpy.enums import YamlAbleEnum
from bgpy.simulation_engine.ann_containers.ann_container import AnnContainer

# 2-way mappings between the types and the yaml tags
types_to_yaml_tags = {X: X.yaml_suffix() for X in YamlAbleEnum.yamlable_enums()}
types_to_yaml_tags.update(
    {Cls: Cls.__name__ for Cls in AnnContainer.subclasses}  # type: ignore
)

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
        try:
            if issubclass(typ, YamlAbleEnum):
                # Don't use unessecary name
                return typ(value=dct["value"])
            elif issubclass(typ, AnnContainer):
                return typ.__from_yaml_dict__(dct=dct, yaml_tag=yaml_tag_suffix)
            else:
                return typ(**dct)
        except Exception as e:
            # For some reason YamlAble library suppresses these errors...
            print(e)
            raise

    @classmethod
    def to_yaml_dict(cls, obj) -> tuple[str, Any]:
        """Converts objects to yaml dicts"""

        if isinstance(obj, YamlAbleEnum):
            return types_to_yaml_tags[type(obj)], {"value": obj.value, "name": obj.name}
        elif isinstance(obj, AnnContainer):
            rv = types_to_yaml_tags[type(obj)], obj.__to_yaml_dict__()
            return rv
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
