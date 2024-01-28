import re
from datetime import date
from pathlib import Path
from requests_cache import CachedSession


def get_country_asns(
    country_code: str, requests_cache_path: Path = Path(f"/tmp/{date.today()}.db")
) -> list[int]:
    """
    Returns all the ASNs associated with a specific region. A region is given by a
    two-letter country code defined in the ISO 3166-1 standard. More details about
    country codes can be found here: https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2.
    """

    with CachedSession(str(requests_cache_path)) as session:
        response = session.get(
            f"https://stat.ripe.net/data/country-asns/data.json?resource={country_code.lower()}&lod=1"
        )
        if response.status_code != 200:
            print("Unable to fetch data from RIPEstat API")
            return []

        data = response.json()

        # Extract both routed and non-routed ASNs using regex
        country_info = data["data"]["countries"][0]
        asns = re.findall(r"AsnSingle\((\d+)\)", country_info["routed"])
        asns += re.findall(r"AsnSingle\((\d+)\)", country_info["non_routed"])

        return [int(asn) for asn in asns]
