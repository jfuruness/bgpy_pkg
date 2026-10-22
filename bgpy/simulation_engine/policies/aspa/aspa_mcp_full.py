from bgpy.simulation_engine import ROVFull

from .aspa_mcc import ASPA_MCP


class ASPA_MCP_Full(ASPA_MCP, ROVFull):
    """ASPA-MCP with withdrawals ribs in and ribs out"""

    name = "ASPA-MCP Full"
