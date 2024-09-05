import re
from pathlib import Path
from typing import Iterable

from requests_cache import CachedSession

from bgpy.shared.constants import SINGLE_DAY_CACHE_DIR
from bgpy.shared.enums import ASGroups, InAdoptingASNs, Outcomes, Plane
from bgpy.simulation_framework.graph_data_aggregator.graph_category import GraphCategory


def get_all_graph_categories() -> Iterable[GraphCategory]:
    """Returns all possible metric key combos"""

    for plane in [Plane.DATA]:
        for as_group in [ASGroups.ALL_WOUT_IXPS]:
            for outcome in [x for x in Outcomes if x != Outcomes.UNDETERMINED]:
                for in_adopting_asns_enum in list(InAdoptingASNs):
                    yield GraphCategory(
                        plane=plane,
                        as_group=as_group,
                        outcome=outcome,
                        in_adopting_asns=in_adopting_asns_enum,
                    )


def get_country_asns(
    country_code: str,
    requests_cache_path: Path = SINGLE_DAY_CACHE_DIR / "requests_cache.db",
) -> list[int]:
    """
    Returns all the ASNs associated with a specific region. A region is given by a
    two-letter country code defined in the ISO 3166-1 standard. More details about
    country codes can be found here: https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2.
    """

    with CachedSession(str(requests_cache_path)) as session:
        response = session.get(
            "https://stat.ripe.net/data/country-asns/"
            f"data.json?resource={country_code.lower()}&lod=1"
        )
        assert response.status_code == 200

        # Extract both routed and non-routed ASNs using regex
        country_info = response.json()["data"]["countries"][0]
        asns = re.findall(r"AsnSingle\((\d+)\)", country_info["routed"])
        asns += re.findall(r"AsnSingle\((\d+)\)", country_info["non_routed"])

        return [int(asn) for asn in asns]
