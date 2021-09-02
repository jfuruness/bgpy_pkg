from .prefix_hijack_atk_ann import PrefixHijackAtkAnn
from ..enums import Prefixes


class SubprefixHijackAtkAnn(PrefixHijackAtkAnn):
    def __init__(self, prefix=Prefixes.SUBPREFIX.value, **kwargs):
        super(SubprefixHijackAtkAnn, self).__init__(prefix=prefix, **kwargs)
