"""Pins the semantics of ASPA/ASRA records being separate from the policies.

The distinction protected here is the RFC's "No Attestation" vs "Not Provider+":
an AS that published no record must never cause a failure, while an AS that
published a record omitting the hop must. Before records were split out this was
expressed as isinstance(as_obj.policy, ASPA), which conflated publishing with
verifying and made "No Attestation" unreachable for any adopter.
"""

import pytest

from bgpy.shared.aspa_records import (
    ASPARecord,
    ASRACLPRecord,
    ASRACRecord,
    ASRALPRecord,
)
from bgpy.simulation_engine import Policy


class RecordTestPolicy(Policy):
    """Minimal concrete Policy so aspa_not_provider_plus can be called"""

    name: str = "record test policy"

    def receive_ann(self, ann) -> None:  # pragma: no cover
        raise NotImplementedError

    def process_incoming_anns(self, **kwargs) -> None:  # pragma: no cover
        raise NotImplementedError

    def propagate_to_providers(self) -> None:  # pragma: no cover
        raise NotImplementedError

    def propagate_to_customers(self) -> None:  # pragma: no cover
        raise NotImplementedError

    def propagate_to_peers(self) -> None:  # pragma: no cover
        raise NotImplementedError

    def __to_yaml_dict__(self) -> dict:  # pragma: no cover
        return {}

    @classmethod
    def __from_yaml_dict__(cls, dct, yaml_tag):  # pragma: no cover
        return cls()


@pytest.fixture
def policy():
    """A verifying policy plus populated registries, cleared afterwards"""

    for registry in (
        Policy.aspa_records,
        Policy.asra_c_records,
        Policy.asra_lp_records,
        Policy.asra_clp_records,
    ):
        registry.clear()

    # 1 publishes an ASPA authorizing 2 only, and no ASRA at all
    Policy.aspa_records[1] = ASPARecord(asn=1, provider_asns=frozenset({2}))
    # 3 publishes an ASPA and an ASRA-CLP
    Policy.aspa_records[3] = ASPARecord(asn=3, provider_asns=frozenset({4}))
    Policy.asra_clp_records[3] = ASRACLPRecord(asn=3, asns=frozenset({4, 5}))
    # 6 splits its ASRA across the two distinguishing variants
    Policy.asra_c_records[6] = ASRACRecord(asn=6, asns=frozenset({61}))
    Policy.asra_lp_records[6] = ASRALPRecord(asn=6, asns=frozenset({62}))
    # 9 publishes nothing at all

    yield RecordTestPolicy()

    for registry in (
        Policy.aspa_records,
        Policy.asra_c_records,
        Policy.asra_lp_records,
        Policy.asra_clp_records,
    ):
        registry.clear()


class TestASPARecords:
    def test_lookup_gives_the_provider_set(self, policy):
        assert policy.aspa_records[1].provider_asns == frozenset({2})

    def test_authorized_provider_is_not_a_failure(self, policy):
        assert policy.aspa_not_provider_plus(1, 2) is False

    def test_omitted_provider_is_not_provider_plus(self, policy):
        """A published record that omits the hop is a real failure"""

        assert policy.aspa_not_provider_plus(1, 7) is True

    def test_no_record_is_no_attestation_not_failure(self, policy):
        """The case that could not exist before the split"""

        assert policy.aspa_records.get(9) is None
        assert policy.aspa_not_provider_plus(9, 7) is False

    def test_unknown_asn_is_no_attestation(self, policy):
        assert policy.aspa_not_provider_plus(123456, 7) is False

    def test_none_hop_is_not_authorized(self, policy):
        """_provider_check passes None when the next ASN is not in the graph"""

        assert policy.aspa_not_provider_plus(1, None) is True

    def test_path_attestations_ride_on_the_record(self):
        """ASPA++ path fields are published data, not graph ground truth"""

        with_paths = ASPARecord(
            asn=1,
            provider_asns=frozenset({2}),
            max_provider_path=3,
            max_customer_path=4,
        )
        assert with_paths.max_provider_path == 3
        assert with_paths.max_customer_path == 4

        plain = ASPARecord(asn=1, provider_asns=frozenset({2}))
        assert plain.max_provider_path is None
        assert plain.max_customer_path is None


class TestASRARecords:
    """Each variant is its own registry, looked up directly by ASN"""

    def test_clp_lookup_gives_customers_and_peers_merged(self, policy):
        record = policy.asra_clp_records.get(3)
        assert record is not None
        assert record.asns == frozenset({4, 5})
        # Nothing on the record says which entry is a customer vs a peer
        assert not hasattr(record, "customer_asns")
        assert not hasattr(record, "peer_asns")

    def test_c_and_lp_lookups_are_separate(self, policy):
        """A policy that distinguishes reads the two registries independently"""

        assert policy.asra_c_records[6].asns == frozenset({61})
        assert policy.asra_lp_records[6].asns == frozenset({62})

    def test_registries_do_not_bleed_into_each_other(self, policy):
        """3 published only a CLP, 6 published only a C and an LP"""

        assert policy.asra_c_records.get(3) is None
        assert policy.asra_lp_records.get(3) is None
        assert policy.asra_clp_records.get(6) is None

    def test_missing_publisher_is_absent_everywhere(self, policy):
        for registry in (
            policy.asra_c_records,
            policy.asra_lp_records,
            policy.asra_clp_records,
        ):
            assert registry.get(9) is None

    def test_an_as_can_publish_without_verifying(self, policy):
        """Nothing on a record references a policy class"""

        record = policy.asra_clp_records[3]
        assert not hasattr(record, "policy")
