from .link import Link


class CustomerProviderLink(Link):
    """Stores the customer and provider information"""

    def __init__(self, *, customer_asn: int, provider_asn: int) -> None:
        """Saves the link info"""

        self.__customer_asn: int = int(customer_asn)
        self.__provider_asn: int = int(provider_asn)
        super().__init__(customer_asn, provider_asn)

    def __hash__(self) -> int:
        """Hashes used in sets

        NOTE: python disables hash if __eq__ is defined so you MUST explicitly redef
        """

        return hash(self.asns)

    def __eq__(self, other) -> bool:
        if isinstance(other, CustomerProviderLink):
            return (
                self.customer_asn == other.customer_asn
                and self.provider_asn == other.provider_asn
            )
        else:
            return NotImplemented

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
