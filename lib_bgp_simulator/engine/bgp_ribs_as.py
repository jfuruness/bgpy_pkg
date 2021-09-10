from copy import deepcopy

from lib_caida_collector import AS

from .local_rib import LocalRib
from .bgp_as import BGPAS
from ..announcement import Announcement as Ann
from ..enums import Relationships
from .bgp_ribs_policy import BGPRIBSPolicy


class BGPRIBSAS(BGPAS):

    def __init__(self, *args, **kwargs):
        super(BGPRIBSAS, self).__init__(*args, **kwargs)

