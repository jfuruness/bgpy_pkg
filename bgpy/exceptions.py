class GaoRexfordException(RuntimeError):
    """Error that occurs during gao rexford, such as failing to choose an ann"""
    pass


class NoCAIDAURLException(RuntimeError):
    """Exception that covers the case when CAIDA returns nothing"""
    pass
