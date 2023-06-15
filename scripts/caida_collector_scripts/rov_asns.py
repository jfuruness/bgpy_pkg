from pathlib import Path

# Done here so that it only happens once
# Really shit should be a singleton or something
# And probably should be a part of the caida graph
# But I no longer have the time to implement


path = Path(__file__).parent.parent / "scripts" / "rov_ases" / "combined.csv"
with path.open() as f:
    reader = csv.DictReader(f)


# Add to caida graph
# Change the stub_asns, my_asns, etc in the caida graph to be just ASes with a hash of their ASN
# Modify the subcategories in the scenario class to account for this
# Modify the subcategories in the scenario class to be ROV or not based on scenario...
# Alert the team to know about it
