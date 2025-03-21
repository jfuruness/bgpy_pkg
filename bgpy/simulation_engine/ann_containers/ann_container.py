import pprint
from collections import UserDict
from typing import Any, ClassVar, Generic, TypeVar

KeyType = TypeVar("KeyType")
ValueType = TypeVar("ValueType")


class AnnContainer(UserDict[KeyType, ValueType], Generic[KeyType, ValueType]):
    """Container for announcements that can dump to YamlAble

    Inherits from UserDict so that it can easily be dumped to YAML
    and also avoid the PyPy changes to the way it accesses dict values

    Where PyPy differs for accessing dictionary subclasses:
    https://doc.pypy.org/en/latest/cpython_differences.html#subclasses-of-built-in-types
    UserDict source (notice how it's implemented get, which won't conflict with PyPy):
    https://github.com/python/cpython/blob/main/Lib/collections/__init__.py#L1117
    """

    subclasses: ClassVar[set[type["AnnContainer[Any, Any]"]]] = set()

    def __init_subclass__(cls: type["AnnContainer[Any, Any]"], *args, **kwargs):
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
    def __from_yaml_dict__(cls, dct, yaml_tag) -> "AnnContainer[KeyType, ValueType]":
        """This optional method is called when you call yaml.load()"""

        return cls(dct)
