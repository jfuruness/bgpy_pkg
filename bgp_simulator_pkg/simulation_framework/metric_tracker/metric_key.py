from dataclasses import asdict, dataclass
from typing import Any, Optional

from yamlable import YamlAble, yaml_info

from bgp_simulator_pkg.enums import ASGroups, Plane, Outcomes
from bgp_simulator_pkg.caida_collector.graph.base_as import AS


@yaml_info(yaml_tag="MetricKey")
@dataclass(frozen=True, slots=True)
class MetricKey(YamlAble):
    """Key for storing data within each metric"""

    plane: Plane
    as_group: ASGroups
    outcome: Outcomes
    ASCls: Optional[type[AS]] = None

    ##############
    # Yaml funcs #
    ##############

    def __to_yaml_dict__(self) -> dict[str, Any]:
        """This optional method is called when you call yaml.dump()"""

        name = AS.subclass_to_name_dict[self.ASCls]
        dct = asdict(self)
        dct["ASCls"] = name
        return dct

    @classmethod
    def __from_yaml_dict__(
        cls: type["MetricKey"], dct: dict[str, Any], yaml_tag: Any
    ) -> "MetricKey":
        """This optional method is called when you call yaml.load()"""

        ASCls = AS.name_to_subclass_dict[dct["ASCls"]]
        dct["ASCls"] = ASCls

        return cls(**dct)
