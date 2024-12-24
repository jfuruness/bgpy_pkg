from .bgp_full import BGPFull


class BGPFullIgnoreInvalid(BGPFull):
    """Ignores invalid routes, such as those that occur with withdrawal suppression"""

    name = "BGP Full Ignore Invalid"

    error_on_invalid_routes = False
