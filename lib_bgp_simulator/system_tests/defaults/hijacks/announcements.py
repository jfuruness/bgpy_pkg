from .prefix_hijack_vic_ann import PrefixHijackVicAnn
from .prefix_hijack_atk_ann import PrefixHijackAtkAnn
from .subprefix_hijack_atk_ann import SubprefixHijackAtkAnn
from .superprefix_hijack_atk_ann import SuperprefixHijackAtkAnn

prefix_hijack_anns = [PrefixHijackVicAnn(), PrefixHijackAtkAnn()]
subprefix_hijack_anns = [PrefixHijackVicAnn(), SubprefixHijackAtkAnn()]
superprefix_hijack_anns = [PrefixHijackVicAnn(), SuperprefixHijackAtkAnn()]
prefix_superprefix_hijack_anns = [PrefixHijackVicAnn(),
                                  SuperprefixHijackAtkAnn(),
                                  PrefixHijackAtkAnn()]
prefix_subprefix_hijack_anns = [PrefixHijackVicAnn(),
                                SubprefixHijackAtkAnn(),
                                PrefixHijackAtkAnn()]
non_routed_prefix_hijack_anns = [PrefixHijackAtkAnn()]
