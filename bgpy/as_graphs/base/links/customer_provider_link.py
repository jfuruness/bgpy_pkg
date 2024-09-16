from .link import Link


class CustomerProviderLink(Link):
    """Stores the customer and provider information"""

    def __init__(self, *, customer_asn: int, provider_asn: int) -> None:
        """Saves the link info"""

        self.__customer_asn: int = int(customer_asn)
        self.__provider_asn: int = int(provider_asn)
        super().__init__(customer_asn, provider_asn)

    @property
    def customer_asn(self) -> int:
        """Returns customer asn. Done this way for immutability/hashing"""

        return self.__customer_asn

    @property
    def provider_asn(self) -> int:
        """Returns provider asn. Done this way for immutability/hashing"""

        return self.__provider_asn

    @property
    def asns(self) -> tuple[int, ...]:
        """Returns asns associated with this link. Used for hashing"""

        asns = sorted([self.customer_asn, self.provider_asn])
        assert len(asns) == 2, "mypy type check"
        return tuple(asns)
