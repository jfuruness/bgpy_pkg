from typing import Optional

from lib_caida_collector import BGPDAG

from .as_classes import BGPAS
from ..engine_input import EngineInput
from ..enums import Relationships
from ..announcements import Announcement

class SimulatorEngine(BGPDAG):
    __slots__ = "_setup",

    def __init__(self,
                 *args,
                 BaseASCls=BGPAS,
                 **kwargs):
        super(SimulatorEngine, self).__init__(*args,
                                              BaseASCls=BaseASCls,
                                              **kwargs)
        self._setup: bool = False

    def __eq__(self, other):
        if isinstance(other, SimulatorEngine):
            return self.as_dict == other.as_dict
        else:
            raise NotImplementedError

    def setup(self,
              engine_input: EngineInput,
              BaseASCls: BGPAS,
              AdoptingASCls: BGPAS):
        self._reset_as_classes(engine_input, BaseASCls, AdoptingASCls)
        engine_input.seed(self)
        self._setup = True

    def run(self,
            propagation_round=0,
            engine_input=None):
        """Propogates announcements"""

        assert self._setup
        self._propagate(propagation_round, engine_input)

    def _reset_as_classes(self,
                          engine_input: EngineInput,
                          BaseASCls: BGPAS,
                          AdoptASCls: BGPAS):
        as_cls_dict: dict = engine_input.get_as_classes(self,
                                                        BaseASCls,
                                                        AdoptASCls)
        for as_obj in self:
            as_obj.__class__ = as_cls_dict.get(as_obj.asn, BaseASCls)
            # Reset base is false to avoid overriding AS info
            as_obj.__init__(reset_base=False)

    def _propagate(self,
                   propagation_round: Optional[int],
                   engine_input: Optional[EngineInput]):
        """Propogates announcements"""

        kwargs = {"propagation_round": propagation_round,
                  "engine_input": engine_input}

        self._propagate_to_providers(**kwargs)
        self._propagate_to_peers(**kwargs)
        self._propagate_to_customers(**kwargs)

    def _propagate_to_providers(self, **kwargs):
        for i, rank in enumerate(self.propagation_ranks):
            # Nothing to process at the start
            if i > 0:
                # Process first because maybe it recv from lower ranks
                for as_obj in rank:
                    as_obj.process_incoming_anns(Relationships.CUSTOMERS,
                                                 **kwargs)
            # Send to the higher ranks
            for as_obj in rank:
                as_obj.propagate_to_providers()

    def _propagate_to_peers(self, **kwargs):
        # The reason you must separate this for loop here
        # is because propagation ranks do not take into account peering
        # It'd be impossible to take into account peering
        # since different customers peer to different ranks
        # So first do customer to provider propagation, then peer propagation
        for as_obj in self:
            as_obj.propagate_to_peers()
        for as_obj in self:
            as_obj.process_incoming_anns(Relationships.PEERS, **kwargs)

    def _propagate_to_customers(self, **kwargs):
        for i, rank in enumerate(reversed(self.propagation_ranks)):
            # There are no incomming Anns at the top
            if i > 0:
                for as_obj in rank:
                    as_obj.process_incoming_anns(Relationships.PROVIDERS,
                                                 **kwargs)
            for as_obj in rank:
                as_obj.propagate_to_customers()
