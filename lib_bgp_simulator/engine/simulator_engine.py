from typing import Optional

from lib_caida_collector import BGPDAG

from .as_classes import BGPAS
from ..engine_input import EngineInput
from ..enums import Relationships


class SimulatorEngine(BGPDAG):
    """BGPDAG subclass that supports announcement propogation

    This class must be first setup with the _setup function
    This resets all the ASes to their base state, and changes
    the classes to be adopting specific defensive policies
    Then the run function can be called, and propagation occurs
    """


    __slots__ = "_ready_to_run",

    def __init__(self,
                 *args,
                 # Default AS class in the BGPDAG
                 BaseASCls=BGPAS,
                 **kwargs):
        """Saves read_to_run_rund attr and inits superclass"""

        super(SimulatorEngine, self).__init__(*args,
                                              BaseASCls=BaseASCls,
                                              **kwargs)
        # This indicates whether or not the simulator has been set up for a run
        # We use a number instead of a bool so that we can indicate for
        # each round whether it is ready to run or not
        self._ready_to_run_round: int = -1

    def __eq__(self, other):
        """Returns if two simulators contain the same BGPDAG's"""

        if isinstance(other, SimulatorEngine):
            return self.as_dict == other.as_dict
        else:
            return NotImplemented

    def setup(self,
              engine_input: EngineInput,
              BaseASCls: BGPAS,
              AdoptingASCls: BGPAS):
        """Sets up the simulator to be run

        This resets the AS objects to their base state,
        clearing all their RIB's,
        and setting adopting ASes.
        
        Then it seeds the engine_input's announcments
        """

        # Reset AS objects to their base state, clears RIBs,
        # and sets adopting ASes
        self._reset_as_classes(engine_input, BaseASCls, AdoptingASCls)
        # Seed the attacker and victim announcements
        # The AdoptingASCls was added here for subclasses, such as in Ez
        # (not located within this repo)
        engine_input.seed(self, AdoptingASCls)
        # Indicate that the engine is ready to run
        self._ready_to_run_round = 0

    def run(self,
            propagation_round=0,
            engine_input=None):
        """Propogates announcements and ensures proper setup"""

        # Ensure that the simulator is ready to run this round
        if self._ready_to_run_round != propagation_round:
            raise Exception(
                "Engine not set up to run for {propagation_round} round")
        # Propogate anns
        self._propagate(propagation_round, engine_input)
        # Increment the ready to run round
        self._ready_to_run_round += 1

    def _reset_as_classes(self,
                          engine_input: EngineInput,
                          BaseASCls: BGPAS,
                          AdoptASCls: BGPAS):
        """Resets AS classes within the simulator engine

        Gets the as_class_dict from the engine input
        indicating the proper class for each AS

        reset the AS class (which can be either back to BaseASCls,
        or some AdoptASCls (as defined by the engine input)

        Then reset all attributes back to base
        (clears RIBs, etc, but not things like customers, peers)
        """

        # Get mapping of asn to as policy
        as_cls_dict: dict = engine_input.get_as_classes(self,
                                                        BaseASCls,
                                                        AdoptASCls)
        for as_obj in self:
            # Set the AS class to be the proper type of AS
            as_obj.__class__ = as_cls_dict.get(as_obj.asn, BaseASCls)
            # Clears all RIBs, etc
            # Reset base is false to avoid overriding Base AS info
            as_obj.__init__(reset_base=False)

    def _propagate(self,
                   propagation_round: Optional[int],
                   engine_input: Optional[EngineInput]):
        """Propogates announcements

        to stick with Gao Rexford, we propagate to
        1. providers
        2. peers
        3. customers
        """

        kwargs = {"propagation_round": propagation_round,
                  "engine_input": engine_input}

        self._propagate_to_providers(**kwargs)
        self._propagate_to_peers(**kwargs)
        self._propagate_to_customers(**kwargs)

    def _propagate_to_providers(self, **kwargs):
        """Propogate to providers"""

        # Propogation ranks go from stubs to input_clique in ascending order
        # By customer provider pairs (peers are ignored for the ranks)
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
        """Propagate to peers"""

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
        """Propagate to customers"""

        # Propogation ranks go from stubs to input_clique in ascending order
        # By customer provider pairs (peers are ignored for the ranks)
        # So here we start at the highest rank(input_clique) and propagate down
        for i, rank in enumerate(reversed(self.propagation_ranks)):
            # There are no incomming Anns at the top
            if i > 0:
                for as_obj in rank:
                    as_obj.process_incoming_anns(Relationships.PROVIDERS,
                                                 **kwargs)
            for as_obj in rank:
                as_obj.propagate_to_customers()
