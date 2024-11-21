class GaoRexfordError(RuntimeError):
    """Error that occurs during gao rexford, such as failing to choose an ann"""

    pass


class NoCAIDAURLError(RuntimeError):
    """Exception that covers the case when CAIDA returns nothing"""

    pass


class AnnouncementNotFoundError(RuntimeError):
    """Exception that covers when an Announcement isn't findable

    ex: in local RIB, in RIBsIn, etc
    """

    pass
