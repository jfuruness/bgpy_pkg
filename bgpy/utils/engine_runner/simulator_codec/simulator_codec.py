# YAML STUFF
from collections.abc import Iterable
from enum import Enum
import importlib
from typing import Any

import yaml
from yamlable import YamlCodec

import json

from bgpy.shared.constants import bgpy_logger
from bgpy.shared.enums import YamlAbleEnum
from bgpy.simulation_engine.ann_containers.ann_container import AnnContainer
from bgpy.utils.engine_runner.simulator_codec.output_format import OutputFormat

from .simulator_loader import SimulatorLoader

# 2-way mappings between the types and the yaml tags
types_to_yaml_tags: dict[type[Any], str] = {
    X: X.yaml_suffix() for X in YamlAbleEnum.yamlable_enums()
}
types_to_yaml_tags.update({Cls: Cls.__name__ for Cls in AnnContainer.subclasses})

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

        return yaml_tag_suffix in yaml_tags_to_types

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
            bgpy_logger.exception(str(e))
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

    def dump(self, obj, output_format: OutputFormat, path=None):
        match output_format:
            case OutputFormat.YAML:
                # https://stackoverflow.com/a/30682604/8903959
                # Ignores references for more readable output
                yaml.Dumper.ignore_aliases = lambda *args: True  # type: ignore
                if path is None:
                    yaml.dump(obj)
                else:
                    with path.open(mode="w") as f:
                        yaml.dump(obj, f)
            case OutputFormat.JSON:

                def json_serializer(o):
                    if hasattr(o, "__to_yaml_dict__"):
                        obj_dict = {
                            "class": o.__class__.__name__,
                            "module": o.__module__,
                        }
                        obj_dict.update(o.__to_yaml_dict__())
                        return obj_dict
                    elif isinstance(o, Enum):
                        return {
                            "class": o.__class__.__name__,
                            "module": o.__module__,
                            "EnumValue": o.value,
                        }

                if path is None:
                    json.dumps(obj, default=json_serializer)
                else:
                    with path.open(mode="w") as f:
                        json.dump(obj, f, default=json_serializer)

    def load(self, path, output_format: OutputFormat):
        with path.open(mode="r") as f:
            match output_format:
                case OutputFormat.YAML:
                    # This isn't insecure, ignore S506
                    return yaml.load(f, Loader=SimulatorLoader)  # noqa: S506
                case OutputFormat.JSON:

                    def json_deserializer(obj_dict: dict) -> Any:
                        if "class" in obj_dict and "module" in obj_dict:
                            module = importlib.import_module(obj_dict.pop("module"))
                            class_instance = getattr(module, obj_dict.pop("class"))
                            if "EnumValue" in obj_dict:
                                return class_instance(obj_dict.get("EnumValue"))
                            if hasattr(class_instance, "__from_yaml_dict__"):
                                return class_instance.__from_yaml_dict__(
                                    obj_dict, yaml_tag=""
                                )
                            else:
                                return class_instance(**obj_dict)
                        return obj_dict

                    return json.load(f, object_hook=json_deserializer)


SimulatorCodec.register_with_pyyaml()
