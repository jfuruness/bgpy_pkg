from __future__ import annotations
from typing import List, Type


class EngineTestConfig:

    subclasses: List[Type["EngineTestConfig"]] = list()

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
        assert len(set(names)) == len(names), "Duplicate test config names"
