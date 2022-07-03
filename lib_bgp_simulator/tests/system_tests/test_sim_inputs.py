from itertools import product

import pytest

from ...engine import BGPSimpleAS
from ...engine import BGPAS
from ...engine import ROVAS
from ...engine import ROVSimpleAS

from ...scenarios import NonRoutedPrefixHijack
from ...scenarios import NonRoutedSuperprefixHijack
from ...scenarios import PrefixHijack
from ...scenarios import SubprefixHijack
from ...scenarios import SuperprefixPrefixHijack

from ...simulation import Simulation

AS_CLASSES = (BGPSimpleAS, BGPAS, ROVAS, ROVSimpleAS)
SCENARIOS = (NonRoutedPrefixHijack,
             NonRoutedSuperprefixHijack,
             PrefixHijack,
             SubprefixHijack,
             SuperprefixPrefixHijack)
PARSE_CPUS = (1, 2)


# Really does need all these combos
# Since certain as classes might break with mp
@pytest.mark.slow
@pytest.mark.parametrize("AdoptASCls, BaseASCls, ScenarioCls, parse_cpus",
                         [x for x in product(*[AS_CLASSES,
                                               AS_CLASSES,
                                               SCENARIOS,
                                               PARSE_CPUS])
                          # Where BaseASCls != AdoptASCls
                          if x[0] != x[1]])
def test_sim_inputs(AdoptASCls,
                    BaseASCls,
                    ScenarioCls,
                    parse_cpus,
                    tmp_path):
    """Test basic functionality of process_incoming_anns"""

    sim = Simulation(percent_adoptions=(0, 50, 100),
                     scenarios=[ScenarioCls(AdoptASCls=AdoptASCls,
                                            BaseASCls=BaseASCls)],
                     num_trials=2,
                     output_path=tmp_path / "test_sim_inputs",
                     parse_cpus=parse_cpus)
    sim.run()
