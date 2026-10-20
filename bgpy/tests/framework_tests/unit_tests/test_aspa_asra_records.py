"""Pins the semantics of ASPA/ASRA records being separate from the policies.

The distinction protected here is the RFC's "No Attestation" vs "Not Provider+":
an AS that published no record must never cause a failure, while an AS that
published a record omitting the hop must. Before records were split out this was
expressed as isinstance(as_obj.policy, ASPA), which conflated publishing with
verifying and made "No Attestation" unreachable for any adopter.
"""

from types import SimpleNamespace

import pytest

from bgpy.shared.aspa_records import (
    ASPAPPRecord,
    ASPARecord,
    ASRACLPRecord,
    ASRACRecord,
    ASRALPRecord,
)
from bgpy.simulation_engine import ASPA, Policy


class RecordTestPolicy(Policy):
    """Minimal concrete Policy so the class level registries can be read"""

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
    Policy.asra_clp_records[3] = ASRACLPRecord(
        asn=3, customer_and_peer_asns=frozenset({4, 5})
    )
    # 6 splits its ASRA across the two distinguishing variants
    Policy.asra_c_records[6] = ASRACRecord(asn=6, customer_asns=frozenset({61}))
    Policy.asra_lp_records[6] = ASRALPRecord(asn=6, peer_asns=frozenset({62}))
    # 9 publishes nothing at all

    yield RecordTestPolicy()

    for registry in (
        Policy.aspa_records,
        Policy.asra_c_records,
        Policy.asra_lp_records,
        Policy.asra_clp_records,
    ):
        registry.clear()


def provider_check(asn1, asn2, graph_asns=(1, 2, 3, 4, 7, 9)) -> bool:
    """Calls ASPA._provider_check against the class level ASPA registry

    _provider_check only touches self.aspa_records and self.as_.as_graph, so a
    stand-in self with a small as_dict is enough to exercise the real method.
    True means "No Attestation or Provider+", False means "Not Provider+".
    """

    stand_in = SimpleNamespace(
        aspa_records=Policy.aspa_records,
        as_=SimpleNamespace(
            as_graph=SimpleNamespace(
                as_dict={asn: SimpleNamespace(asn=asn) for asn in graph_asns}
            )
        ),
    )
    return ASPA._provider_check(stand_in, asn1, asn2)


class TestASPARecords:
    def test_lookup_gives_the_provider_set(self, policy):
        assert policy.aspa_records[1].provider_asns == frozenset({2})

    def test_authorized_provider_passes(self, policy):
        assert provider_check(1, 2) is True

    def test_omitted_provider_is_not_provider_plus(self, policy):
        """A published record that omits the hop is a real failure"""

        assert provider_check(1, 7) is False

    def test_no_record_is_no_attestation_not_failure(self, policy):
        """The case that could not exist before the split"""

        assert policy.aspa_records.get(9) is None
        assert provider_check(9, 7) is True

    def test_unknown_asn_is_no_attestation(self, policy):
        assert provider_check(123456, 7) is True

    def test_hop_missing_from_graph_is_not_authorized(self, policy):
        """A next hop absent from the graph can never be a listed provider"""

        assert provider_check(1, 555) is False

    def test_path_attestations_are_their_own_record(self):
        """ASPA++ path fields live on ASPAPPRecord, not on the ASPA record"""

        with_paths = ASPAPPRecord(asn=1, max_provider_path=3, max_customer_path=4)
        assert with_paths.max_provider_path == 3
        assert with_paths.max_customer_path == 4

        plain = ASPAPPRecord(asn=1)
        assert plain.max_provider_path is None
        assert plain.max_customer_path is None

        assert not hasattr(ASPARecord(asn=1), "max_provider_path")


class TestASRARecords:
    """Each variant is its own registry, looked up directly by ASN"""

    def test_clp_lookup_gives_customers_and_peers_merged(self, policy):
        record = policy.asra_clp_records.get(3)
        assert record is not None
        assert record.customer_and_peer_asns == frozenset({4, 5})
        # Nothing on the record says which entry is a customer vs a peer
        assert not hasattr(record, "customer_asns")
        assert not hasattr(record, "peer_asns")

    def test_c_and_lp_lookups_are_separate(self, policy):
        """A policy that distinguishes reads the two registries independently"""

        assert policy.asra_c_records[6].customer_asns == frozenset({61})
        assert policy.asra_lp_records[6].peer_asns == frozenset({62})

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
