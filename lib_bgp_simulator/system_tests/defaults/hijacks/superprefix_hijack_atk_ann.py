from .prefix_hijack_atk_ann import PrefixHijackAtkAnn
from ..enums import Prefixes
from ....roa_validity import ROAValidity


class SuperprefixHijackAtkAnn(PrefixHijackAtkAnn):
    """Superprefix of a hijack. ROA validity is unknown, not invalid"""

    def __init__(self,
                 prefix=Prefixes.SUPERPREFIX.value,
                 roa_validity=ROAValidity.UNKNOWN,
                 **kwargs):
        all_kwargs = {"prefix": prefix, "roa_validity": roa_validity, **kwargs}
        super(SuperprefixHijackAtkAnn, self).__init__(**all_kwargs)
