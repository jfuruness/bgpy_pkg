import csv
from enum import Enum

from bs4 import BeautifulSoup


class Filter(Enum):
    PEERS = "peers"
    ALL = "all"


class AS:
    def __init__(self, asn: int, filtering: Filter, confidence: float, source: str):
        self.asn: int = asn
        self.filtering: str = filtering.value
        self.confidence: float = confidence
        self.source = source

    def __hash__(self):
        return hash(self.asn)

    def __lt__(self, other):
        if isinstance(other, AS):
            return self.asn < other.asn
        else:
            return NotImplemented


ases = set()


with open("cloudflare.csv") as f:
    for row in csv.DictReader(f):
        if "filtering peers" in row["details"]:
            ases.add(
                AS(
                    int(row["asn"]),
                    filtering=Filter.ALL,
                    confidence=1,
                    source="cloudflare",
                )
            )
        elif "filtering" in row["details"]:
            ases.add(
                AS(
                    int(row["asn"]),
                    filtering=Filter.PEERS,
                    confidence=1,
                    source="cloudflare",
                )
            )


with open("tma.csv") as f:
    reader = csv.DictReader(f, delimiter="-")
    reader.fieldnames = [x.strip() for x in reader.fieldnames]  # type: ignore
    for row in reader:
        confidence = 1 if "strong" in row["confidence"] else 0.2
        ases.add(
            AS(
                int(row["asn"].strip()),
                filtering=Filter.ALL,
                confidence=confidence,
                source="tma",
            )
        )


with open("rpki_rov.html") as f:
    soup = BeautifulSoup(f, "html.parser")
    for row in soup.find_all("tr"):
        tds = row.find_all("td")  # type: ignore
        if not tds:
            continue
        asn = int(tds[1].text.strip())
        certainty = float(tds[3].text.strip())
        ases.add(
            AS(asn, filtering=Filter.ALL, confidence=certainty, source="rov.rpki.net")
        )

with open("combined_ases.csv", "w") as f:
    writer = csv.DictWriter(f, fieldnames=["asn", "filtering", "confidence", "source"])
    writer.writeheader()
    writer.writerows([vars(x) for x in sorted(ases)])
