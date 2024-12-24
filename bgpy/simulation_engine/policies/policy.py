from abc import ABCMeta, abstractmethod
from ipaddress import ip_network
from typing import TYPE_CHECKING, Any, ClassVar

from roa_checker import ROAChecker, ROAOutcome, ROARouted, ROAValidity
from yamlable import YamlAble, yaml_info_decorate

if TYPE_CHECKING:
    from bgpy.shared.enums import Relationships
    from bgpy.simulation_engine import Announcement as Ann
    from bgpy.simulation_framework import Scenario


class Policy(YamlAble, metaclass=ABCMeta):
    name: str = "AbstractPolicy"
    subclass_to_name_dict: ClassVar[dict[type["Policy"], str]] = dict()
    name_to_subclass_dict: ClassVar[dict[str, type["Policy"]]] = dict()
    # Simulates RPKI and something like routinator that is globally available
    roa_checker: ROAChecker = ROAChecker()

    def __init_subclass__(cls: type["Policy"], *args, **kwargs) -> None:
        """This method essentially creates a list of all subclasses

        This allows us to know all AS types that have been created
        """

        super().__init_subclass__(*args, **kwargs)
        assert hasattr(cls, "name"), "Policy must have a name"
        yaml_info_decorate(cls, yaml_tag=cls.name)
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
    def receive_ann(self, ann: "Ann") -> None:
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

    #############
    # ROA Funcs #
    #############

    def get_roa_outcome(self, ann: "Ann") -> ROAOutcome:
        return self.roa_checker.get_roa_outcome_w_prefix_str_cached(
            ann.prefix, ann.origin
        )

    def ann_is_invalid_by_roa(self, ann: "Ann") -> bool:
        """Returns True if Ann is invalid by ROA

        False means ann is either valid or unknown
        """

        roa_outcome = self.roa_checker.get_roa_outcome_w_prefix_str_cached(
            ann.prefix, ann.origin
        )
        return ROAValidity.is_invalid(roa_outcome.validity)

    def ann_is_valid_by_roa(self, ann: "Ann") -> bool:
        """Returns True if Ann is valid by ROA

        False means ann is either invalid or unknown
        """

        roa_outcome = self.roa_checker.get_roa_outcome_w_prefix_str_cached(
            ann.prefix, ann.origin
        )
        return ROAValidity.is_valid(roa_outcome.validity)

    def ann_is_unknown_by_roa(self, ann: "Ann") -> bool:
        """Returns True if ann is not covered by roa"""

        roa_outcome = self.roa_checker.get_roa_outcome_w_prefix_str_cached(
            ann.prefix, ann.origin
        )
        return ROAValidity.is_unknown(roa_outcome.validity)

    def ann_is_covered_by_roa(self, ann: "Ann") -> bool:
        """Returns if an announcement has a roa"""

        return not self.ann_is_unknown_by_roa(ann)

    def ann_is_roa_non_routed(self, ann: "Ann") -> bool:
        """Returns bool for if announcement is routed according to ROA

        Need if statements in this fashion since there are three levels:
        valid invalid and unknown

        so not invalid != valid
        """

        if self.ann_is_invalid_by_roa(ann):
            relevant_roas = self.roa_checker.get_relevant_roas(ip_network(ann.prefix))
            return any(
                roa.routed_status == ROARouted.NON_ROUTED for roa in relevant_roas
            )
        return False

    ##############
    # YAML Funcs #
    ##############

    @abstractmethod
    def __to_yaml_dict__(self) -> dict[Any, Any]:
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def __from_yaml_dict__(cls, dct, yaml_tag) -> "Policy":
        raise NotImplementedError
