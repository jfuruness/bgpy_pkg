import pprint

from yamlable import YamlAble, yaml_info_decorate


class AnnContainer(YamlAble):
    """Container for announcement that has slots and equality"""

    __slots__ = "_info",

    def __init_subclass__(cls, *args, **kwargs):
        """This method essentially creates a list of all subclasses
        This is allows us to easily assign yaml tags
        """

        super().__init_subclass__(*args, **kwargs)
        yaml_info_decorate(cls, yaml_tag=cls.__name__)

    def __eq__(self, other):
        # Remove this after updating the system tests
        if isinstance(other, self.__class__):
            return self._info == other._info
        else:
            return NotImplemented

    def __str__(self):
        """Returns contents of the container as str"""

        # https://stackoverflow.com/a/521545/8903959
        return pprint.pformat(self._info, indent=4)

    def __to_yaml_dict__(self):
        """ This optional method is called when you call yaml.dump()"""

        return self._info

    @classmethod
    def __from_yaml_dict__(cls, dct, yaml_tag):
        """ This optional method is called when you call yaml.load()"""

        return cls(_info=dct)
