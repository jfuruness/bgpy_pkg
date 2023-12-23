from .cpp_enums import CPPRelationships, CPPOutcomes
from .py_enums import (
    yamlable_enums,
    PyOutcomes,
    PyRelationships,
    Plane,
    ROAValidity,
    Timestamps,
    Prefixes,
    ASNs,
    ASGroups,
    SpecialPercentAdoptions,
)

for CPPEnum, PyEnum in [(CPPOutcomes, PyOutcomes), (CPPRelationships, PyRelationships)]:
    msg = f"C++ Enum {CPPEnum} out of sync with PyEnum {PyEnum}"
    # https://stackoverflow.com/a/60451617/8903959
    assert {x.name, x.value for x in CPPEnum} == {x.name: x.value for x in PyEnum}, msg

__all__ = [
    "CPPRelationships",
    "CPPOutcomes",
    "yamlable_enums",
    "PyOutcomes",
    "PyRelationships",
    "Plane",
    "ROAValidity",
    "Timestamps",
    "Prefixes",
    "ASNs",
    "ASGroups",
    "SpecialPercentAdoptions",
]
