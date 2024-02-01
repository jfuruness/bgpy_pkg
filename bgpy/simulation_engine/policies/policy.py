from abc import ABCMeta, abstractmethod
from typing import Any, TYPE_CHECKING

from yamlable import YamlAble, yaml_info_decorate

if TYPE_CHECKING:
    from bgpy.enums import Relationships
    from bgpy.simulation_engine import Announcement as Ann
    from bgpy.simulation_framework import Scenario


class Policy(YamlAble, metaclass=ABCMeta):
    name: str = "AbstractPolicy"
    subclass_to_name_dict: dict[type["Policy"], str] = {}
    name_to_subclass_dict: dict[str, type["Policy"]] = {}

    def __init_subclass__(cls, *args, **kwargs):
        """This method essentially creates a list of all subclasses

        This allows us to know all AS types that have been created
        """

        super().__init_subclass__(*args, **kwargs)
        assert hasattr(cls, "name"), "Policy must have a name"
        # yamlable not up to date with mypy
        yaml_info_decorate(cls, yaml_tag=cls.name)  # type: ignore
        cls.subclass_to_name_dict[cls] = cls.name
        cls.name_to_subclass_dict[cls.name] = cls

        msg: str = (
            f"Duplicate name {cls.name} with {cls.__name__}."
            "Please make a class attr "
            "name for the policy something else"
        )
        names = list(cls.name_to_subclass_dict)
        assert len(set(names)) == len(names), msg

    def __eq__(self, other) -> bool:
        if isinstance(other, Policy):
            return self.__to_yaml_dict__() == other.__to_yaml_dict__()
        else:
            return NotImplemented

    ##########################
    # Process incoming funcs #
    ##########################

    @abstractmethod
    def receive_ann(self, ann: "Ann", accept_withdrawals: bool = False) -> None:
        """Function for recieving announcements"""

        raise NotImplementedError

    @abstractmethod
    def process_incoming_anns(
        self,
        *,
        from_rel: "Relationships",
        propagation_round: int,
        scenario: "Scenario",
        reset_q: bool = True,
    ) -> None:
        """Process all announcements that were incoming from a specific rel"""

        raise NotImplementedError

    #####################
    # Propagation funcs #
    #####################

    @abstractmethod
    def propagate_to_providers(self) -> None:
        """Propogates to providers

        Propogate ann's that have a recv_rel of origin or customer to providers
        """

        raise NotImplementedError

    @abstractmethod
    def propagate_to_customers(self) -> None:
        """Propogates to customers"""

        raise NotImplementedError

    @abstractmethod
    def propagate_to_peers(self) -> None:
        """Propogates to peers"""

        raise NotImplementedError

    @abstractmethod
    def __to_yaml_dict__(self) -> dict[Any, Any]:
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def __from_yaml_dict__(cls, dct, yaml_tag) -> "Policy":
        raise NotImplementedError
