from datetime import datetime

from bs4 import BeautifulSoup as Soup
import requests


def _get_url(self, dl_time: datetime) -> str:
    """Gets urls to download relationship files"""

    # Api url
    prepend: str = "http://data.caida.org/datasets/as-relationships/serial-2/"
    # Gets all URLs. Keeps only the link for the proper download time
    urls = [
        prepend + x for x in self._get_hrefs(prepend) if dl_time.strftime("%Y%m01") in x
    ]
    if len(urls) > 0:
        return urls[0]  # type: ignore
    else:  # pragma: no cover
        raise Exception("No Urls")


def _get_hrefs(self, url: str) -> list[str]:
    """Returns hrefs from a tags at a given url"""

    try:
        # Query URL
        with requests.get(url, stream=True, timeout=30) as r:
            # Check for errors
            r.raise_for_status()  # type: ignore
            # Get soup
            soup = Soup(r.text, "html.parser")  # type: ignore
            # Extract hrefs from a tags
            return [
                x.get("href") for x in soup.select("a") if x.get("href") is not None
            ]
    except requests.exceptions.ReadTimeout:
        print("Failed to get {url}")
        raise
