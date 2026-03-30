"""Cybabot Ultra Agent definitions."""

from ai.cybabot.agents.hypothesis_designer import create_hypothesis_designer
from ai.cybabot.agents.data_scout import create_data_scout
from ai.cybabot.agents.risk_specialist import create_risk_specialist
from ai.cybabot.agents.backtesting_agent import create_backtesting_agent
from ai.cybabot.agents.performance_analyst import create_performance_analyst
from ai.cybabot.agents.optimization_guardian import create_optimization_guardian
from ai.cybabot.agents.notebook_assembler import create_notebook_assembler

__all__ = [
    "create_hypothesis_designer",
    "create_data_scout",
    "create_risk_specialist",
    "create_backtesting_agent",
    "create_performance_analyst",
    "create_optimization_guardian",
    "create_notebook_assembler",
]
