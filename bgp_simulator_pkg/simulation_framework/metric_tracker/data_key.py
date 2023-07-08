from dataclasses import asdict, dataclass
from typing import Any, Union

from yamlable import YamlAble, yaml_info

from .metric_key import MetricKey

from bgp_simulator_pkg.enums import SpecialPercentAdoptions
from bgp_simulator_pkg.simulation_framework.scenarios import ScenarioConfig


@yaml_info(yaml_tag="data_key")
@dataclass(frozen=True, slots=True)
class DataKey(YamlAble):
    """Key for storing data within the MetricTracker"""

    propagation_round: int
    percent_adopt: Union[float, SpecialPercentAdoptions]
    scenario_config: ScenarioConfig
    metric_key: MetricKey

    ##############
    # Yaml funcs #
    ##############

    def __to_yaml_dict__(self) -> dict[str, Any]:
        """This optional method is called when you call yaml.dump()"""

        return asdict(self)

    @classmethod
    def __from_yaml_dict__(
        cls: type["DataKey"], dct: dict[str, Any], yaml_tag: Any
    ) -> "DataKey":
        """This optional method is called when you call yaml.load()"""

        return cls(**dct)
