class EngineTestConfig:

    subclasses = list()

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

        names = [x.name for x in cls.subclasses]
        assert len(set(names)) == len(names), "Duplicate test config names"
