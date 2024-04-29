from dataclasses import replace  # noqa
from typing import Union

from bgpy.as_graphs.base import ASGraph


from .metric_tracker import MetricTracker
from .simulation import Simulation

from bgpy.enums import SpecialPercentAdoptions


class DependentSimulation(Simulation):
    """Trials across percent adoptions are no longer independent

    Some researchers besides myself want lines to be flat, regardless
    of variance. So this achieves that, at the cost of dependent trials,
    by making attacker victim pairs the same across any percent adoption

    The other downside is that it doesn't parallelize across percent
    adoptions. Not a problem for large runs, but for quick runs
    the other simulation class is better.

    Additionally, if your attacker victim pairs are meant to change from
    one scenario config to the next, you're out of luck here. That's the
    main reason why this isn't a first class citizen and isn't included
    in the documentation - it uses the attacker victim pair from the first
    scenario config, and at 50% adoption, and then just reuses that across
    all percent adoptions.

    In particular, if a single scenario_config already is using the override
    attacker or override victim attributes, this will completely overwrite that
    and it also acts a little janky in the way it sets these attributes on a
    frozen scenario config, since the scenario config instance is used to track
    data elsewhere.

    Useful to some researchers for specific purposes, but
    not I think for general use unless you really understand the inner
    workings of this repo, and can determine if these edge cases will affect
    you
    """

    ###########################
    # Multiprocessing Methods #
    ###########################

    def _get_chunks(  # type: ignore
        self, cpus: int
    ) -> list[list[Union[float, SpecialPercentAdoptions]]]:
        """Returns chunks of trial inputs based on number of CPUs running

        Not a generator since we need this for multiprocessing

        We also don't multiprocess one by one because the start up cost of
        each process is huge (since each process must generate it's own engine
        ) so we must divy up the work beforehand
        """

        trials_list = list(range(self.num_trials))
        return [trials_list[i::cpus] for i in range(cpus)]  # type: ignore

    ############################
    # Data Aggregation Methods #
    ############################

    def _run_chunk(  # type: ignore
        self,
        chunk_id: int,
        trials_list: list[Union[float, SpecialPercentAdoptions]],
    ) -> MetricTracker:
        """Runs a chunk of trial inputs"""

        # Must also seed randomness here since we don't want multiproc to be the same
        self._seed_random(seed_suffix=str(chunk_id))

        # Engine is not picklable or dillable AT ALL, so do it here
        # (after the multiprocess process has started)
        # Changing recursion depth does nothing
        # Making nothing a reference does nothing
        constructor_kwargs = dict(self.as_graph_constructor_kwargs)
        constructor_kwargs["tsv_path"] = None
        as_graph: ASGraph = self.ASGraphConstructorCls(**constructor_kwargs).run()
        engine = self.SimulationEngineCls(
            as_graph,
            cached_as_graph_tsv_path=self.as_graph_constructor_kwargs.get("tsv_path"),
        )

        metric_tracker = self.MetricTrackerCls(metric_keys=self.metric_keys)

        prev_scenario = None

        for trial in trials_list:
            assert self.scenario_configs[0].ScenarioCls, "ScenarioCls is None"
            og_scenario = self.scenario_configs[0].ScenarioCls(
                scenario_config=self.scenario_configs[0],
                percent_adoption=0.5,
                engine=engine,
                prev_scenario=prev_scenario,
                preprocess_anns_func=self.scenario_configs[0].preprocess_anns_func,
            )

            for percent_adopt in self.percent_adoptions:
                for scenario_config in self.scenario_configs:
                    assert scenario_config.ScenarioCls, "ScenarioCls is None"
                    new_scenario_config = scenario_config
                    old_attacker_asns = new_scenario_config.override_attacker_asns
                    old_victim_asns = new_scenario_config.override_victim_asns
                    object.__setattr__(
                        new_scenario_config,
                        "override_attacker_asns",
                        og_scenario.attacker_asns,
                    )
                    object.__setattr__(
                        new_scenario_config,
                        "override_victim_asns",
                        og_scenario.victim_asns,
                    )
                    # This method doesn't work since the metric tracker uses
                    # the scenario_config as a data_key
                    # new_scenario_config = replace(
                    #     scenario_config,
                    #     override_attacker_asns=og_scenario.attacker_asns,
                    #     override_victim_asns=og_scenario.victim_asns
                    # )
                    # Create the scenario for this trial
                    scenario = new_scenario_config.ScenarioCls(
                        scenario_config=new_scenario_config,
                        percent_adoption=percent_adopt,
                        engine=engine,
                        prev_scenario=prev_scenario,
                        preprocess_anns_func=new_scenario_config.preprocess_anns_func,
                    )

                    object.__setattr__(
                        new_scenario_config, "override_attacker_asns", old_attacker_asns
                    )
                    object.__setattr__(
                        new_scenario_config, "override_victim_asns", old_victim_asns
                    )

                    self._print_progress(percent_adopt, scenario, trial)  # type: ignore

                    # Change AS Classes, seed announcements before propagation
                    scenario.setup_engine(engine, prev_scenario)
                    # For each round of propagation run the engine
                    for propagation_round in range(
                        new_scenario_config.propagation_rounds
                    ):
                        self._single_engine_run(
                            engine=engine,
                            percent_adopt=percent_adopt,
                            trial=trial,  # type: ignore
                            scenario=scenario,
                            propagation_round=propagation_round,
                            metric_tracker=metric_tracker,
                        )
                    prev_scenario = scenario
                # Reset scenario for next round of trials
                prev_scenario = None

        return metric_tracker
