from .cpp_enums import CPPRelationships, CPPOutcomes
from .py_enums import (
    yamlable_enums,
    YamlAbleEnum,
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
    for x in list(PyEnum):
        assert getattr(CPPEnum, x.name).value == x.value, f"{CPPEnum} values != {PyEnum}"

__all__ = [
    "CPPRelationships",
    "CPPOutcomes",
    "yamlable_enums",
    "YamlAbleEnum",
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
