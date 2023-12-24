from pathlib import Path
import time

from bgpy.simulation_engines.py_simulation_engine.policies.rov import ROVSimplePolicy
from bgpy.simulation_frameworks.py_simulation_framework import PySimulation, SubprefixHijack, ScenarioConfig
from bgpy.simulation_frameworks.cpp_simulation_framework import CPPASGraphAnalyzer
from bgpy.simulation_engines.cpp_simulation_engine import CPPSimulationEngine, CPPAnnouncement as CPPAnn


def main():
    """Runs the defaults"""


    sim = PySimulation(
        percent_adoptions=(.01, 0.1, 0.2, 0.5, 0.8, .99),
        scenario_configs=(
            ScenarioConfig(ScenarioCls=SubprefixHijack, AdoptPolicyCls=ROVSimplePolicy, AnnCls=CPPAnn),
        ),
        output_dir=Path("~/Desktop/benchmark").expanduser(),
        num_trials=10,
        parse_cpus=1,
        python_hash_seed=0,
        SimulationEngineCls=CPPSimulationEngine,
        ASGraphAnalyzerCls=CPPASGraphAnalyzer,
        as_graph_constructor_kwargs=dict(
            {
                "as_graph_collector_kwargs": dict(
                    {
                        # dl_time: datetime(),
                        "cache_dir": Path("/tmp/as_graph_collector_cache"),
                    }
                ),
                "as_graph_kwargs": dict({"customer_cones": True}),
                "tsv_path": Path.home() / "Desktop" / "caida.tsv",
            }
        ),

    )

    start = time.perf_counter()
    sim._get_data()
    print(time.perf_counter() - start)


    # Simulation for the paper
    sim = PySimulation(
        percent_adoptions=(.01, 0.1, 0.2, 0.5, 0.8, .99),
        scenario_configs=(
            ScenarioConfig(ScenarioCls=SubprefixHijack, AdoptPolicyCls=ROVSimplePolicy),
        ),
        output_dir=Path("~/Desktop/benchmark").expanduser(),
        num_trials=10,
        parse_cpus=1,
        python_hash_seed=0,
    )
    start = time.perf_counter()
    sim._get_data()
    print(time.perf_counter() - start)


if __name__ == "__main__":
    main()
