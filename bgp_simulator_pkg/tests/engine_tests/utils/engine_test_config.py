from __future__ import annotations
from typing import List, Type

from ....simulation_framework import Subgraph


def unique_names_msg(names) -> str:
    """Returns which names are not unique"""

    bad_names = set()
    single_name_set = set()
    for name in names:
        if name in single_name_set:
            bad_names.add(name)
        else:
            single_name_set.add(name)
    return f'{", ".join(bad_names)} not unique config names'


class EngineTestConfig:

    subclasses: List[Type["EngineTestConfig"]] = list()
    SubgraphCls: Type[Subgraph] = Subgraph

    def __init_subclass__(cls, *args, **kwargs):
        """Ensures subclass has proper attrs

        Doing it this way instead of abstract class
        because it's way less typing to use class attrs
        rather than entire functions
        """

        super().__init_subclass__(*args, **kwargs)
        for attr in ("name",
                     "desc",
                     "scenario",
                     "graph",
                     "non_default_as_cls_dict",
                     "propagation_rounds"):
            assert getattr(cls, attr, None) is not None, attr

        cls.subclasses.append(cls)

        # Ignore type since all subclasses must have names
        # Mypy doesn't recognize that this class is not a subclass
        names = [x.name for x in cls.subclasses]  # type: ignore
        assert len(set(names)) == len(names), unique_names_msg(names)
