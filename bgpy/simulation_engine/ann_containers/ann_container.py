from collections import UserDict
import pprint
from typing import Any, Optional


class AnnContainer(UserDict):
    """Container for announcement that has slots and equality"""

    subclasses = set()

    def __init_subclass__(cls, *args, **kwargs):
        """This method essentially creates a list of all subclasses
        This is allows us to easily assign yaml tags
        """

        super().__init_subclass__(*args, **kwargs)
        AnnContainer.subclasses.add(cls)

    def __str__(self) -> str:
        """Returns contents of the container as str"""

        # https://stackoverflow.com/a/521545/8903959
        return pprint.pformat(self.data, indent=4)

    @classmethod
    def yaml_suffix(cls):
        return cls.__name__

    def __to_yaml_dict__(self) -> dict[Any, Any]:
        """This optional method is called when you call yaml.dump()"""

        return self.data

    @classmethod
    def __from_yaml_dict__(cls, dct, yaml_tag) -> "AnnContainer":
        """This optional method is called when you call yaml.load()"""

        return cls(dct)
