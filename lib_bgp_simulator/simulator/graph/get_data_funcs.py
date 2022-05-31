from copy import deepcopy
from collections import defaultdict
from itertools import product
from multiprocessing import Pool

from lib_caida_collector import CaidaCollector


from ...scenarios import Scenario

from ...engine import BGPSimpleAS, BGPAS, SimulatorEngine


def run(self, parse_cpus):
    """Runs trials for graph and aggregates data"""

    # Single process
    if parse_cpus == 1:
        print("Running single proc (DELETE")
        results = self._get_single_process_results()
    # Multiprocess
    else:
        print("Running multi proc (DELETE")
        results = self._get_mp_results(parse_cpus)

    for result in results:
        for self_subgraph, result_subgraph in zip(self.subgraphs, result):
            print("Adding trial info (DELETE")
            self_subgraph.add_trial_info(result_subgraph)

    print("\nGraph complete")

######################################
# Multiprocessing/clustering methods #
######################################

def _get_chunks(self, parse_cpus):
    """Returns chunks of trial inputs based on number of CPUs running

    Not a generator since we need this for multiprocessing

    We also don't multiprocess one by one because the start up cost of
    each process is huge (since each process must generate it's own engine
    ) so we must divy up the work beforehand
    """

    # https://stackoverflow.com/a/34032549/8903959
    percents_trials = list(product(self.percent_adoptions,
                                   list(range(self.num_trials))))

    # https://stackoverflow.com/a/2136090/8903959
    return [percents_trials[i::parse_cpus] for i in range(parse_cpus)]

def _get_single_process_results(self):
    """Get all results when using single processing"""

    return [self._run_chunk(x) for x in self._get_chunks(1)]

def _get_mp_results(self, parse_cpus):
    """Get results from multiprocessing"""

    # Pool is much faster than ProcessPoolExecutor
    with Pool(parse_cpus) as pool:
        return pool.map(self._run_chunk, self._get_chunks(parse_cpus))

def _run_chunk(self, percent_adopt_trials):
    """Runs a chunk of trial inputs"""

    # Engine is not picklable or dillable AT ALL, so do it here
    # (after the multiprocess process has started)
    # Changing recursion depth does nothing
    # Making nothing a reference does nothing
    engine = CaidaCollector(BaseASCls=BGPSimpleAS,
                            GraphCls=SimulatorEngine,
                            ).run(tsv_path=None)
    # Must deepcopy here to have the same behavior between single
    # And multiprocessing
    subgraphs = deepcopy(self.subgraphs)

    prev_scenario = None
    for scenario in self.scenarios:
        for percent_adopt, trial in percent_adopt_trials:
            # Deep copy scenario to ensure it's fresh
            scenario = deepcopy(scenario)

            print(f"{percent_adopt}% {scenario.graph_label}, #{trial}",
                  end="                             " + "\r")

            # Change AS Classes, seed announcements before propagation
            scenario.setup_engine(engine, percent_adopt, prev_scenario)

            for propagation_round in range(self.propagation_rounds):
                # Run the engine
                engine.run(propagation_round=propagation_round,
                           scenario=scenario)

                kwargs = {"engine": engine,
                          "percent_adopt": percent_adopt,
                          "trial": trial,
                          "scenario": scenario,
                          "propagation_round": propagation_round}
                # Save all engine run info
                # The reason we aggregate info right now, instead of saving
                # the engine and doing it later, is because doing it all
                # in RAM is MUCH faster, and speed is important
                self._aggregate_data_from_engine_run(subgraphs, **kwargs)

                # By default, this is a no op
                scenario.post_propagation_hook(**kwargs)
    return self.subgraphs

def _aggregate_engine_run_data(self, subgraphs, **kwargs):
    """For each subgraph, aggregate data

    Some data aggregation is shared to speed up runs
    For example, traceback might be useful across
    Multiple subgraphs
    """

    shared_data = dict()
    for subgraph in subgraphs:
        subgraph.aggregate_engine_run_data(shared_data, **kwargs)
