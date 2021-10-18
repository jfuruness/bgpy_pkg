import yaml
from yamlable import YamlAble, yaml_info

from ...announcements import Announcement


@yaml_info(yaml_tag="LocalRib")
class LocalRib(YamlAble):
    """Local RIB for a BGP AS

    Done separately for easy comparisons in unit testing
    """

    __slots__ = "_info",

    def __init__(self, _info=None):
        self._info = _info if _info is not None else dict()

    def __eq__(self, other):
        # Remove this after updating the system tests
        if isinstance(other, dict):
            return self._info == other
        elif isinstance(other, LocalRib):
            return self._info == other._info
        else:
            raise NotImplementedError

    def get_ann(self, prefix: str, default=None):
        return self._info.get(prefix, default)

    def add_ann(self, ann: Announcement):
        self._info[ann.prefix] = ann

    def remove_ann(self, prefix: str):
        del self._info[prefix]

    def prefix_anns(self):
        return self._info.items()

##############
# Yaml funcs #
##############

    def __to_yaml_dict__(self):
        """ This optional method is called when you call yaml.dump()"""

        return self._info

    @classmethod
    def __from_yaml_dict__(cls, dct, yaml_tag):
        """ This optional method is called when you call yaml.load()"""

        return cls(_info=dct)
