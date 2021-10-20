from collections import defaultdict

from yamlable import YamlAble, yaml_info

from ...announcements import Announcement


@yaml_info(yaml_tag="RecvQueue")
class RecvQueue(YamlAble):
    """Adj_RIBs_In for a BGP AS

    Map prefixes to anns sent
    {prefix: list_of_ann}
    """

    __slots__ = "_info",

    def __init__(self, _info=None):
        self._info = _info if _info is not None else defaultdict(list)

    def __eq__(self, other):
        # Remove this after updating the system tests
        if isinstance(other, dict):
            return self._info == other
        elif isinstance(other, RecvQueue):
            return self._info == other._info
        else:
            raise NotImplementedError

    def add_ann(self, ann: Announcement):
        self._info[ann.prefix].append(ann)

    def prefix_anns(self):
        return self._info.items()

##############
# Yaml funcs #
##############

    def __to_yaml_dict__(self):
        """ This optional method is called when you call yaml.dump()"""

        return self._info
        yaml_dict = dict()
        for prefix, ann_list in self._info.items():
            yaml_dict[prefix] = [yaml.dump(ann) for ann in ann_list]
        return yaml_dict

    @classmethod
    def __from_yaml_dict__(cls, dct, yaml_tag):
        """ This optional method is called when you call yaml.load()"""

        return cls(_info=dct)
