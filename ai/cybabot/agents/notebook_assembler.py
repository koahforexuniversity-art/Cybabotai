"""Agent 7: Notebook Assembler - Assembles all outputs into export files."""

from crewai import Agent
from langchain_core.language_models import BaseChatModel


def create_notebook_assembler(llm: BaseChatModel) -> Agent:
    """Create the Notebook Assembler agent."""
    return Agent(
        role="Strategy Export & Documentation Assembler",
        goal=(
            "Assemble all strategy components into production-ready export files: "
            "MQL5 Expert Advisor, PineScript v6 indicator, Python trading class, "
            "Jupyter notebook, and comprehensive PDF report."
        ),
        backstory=(
            "You are a full-stack trading systems developer who can translate "
            "strategy specifications into production-ready code in any trading platform. "
            "You write clean, well-documented MQL5 EAs, PineScript indicators, "
            "and Python trading classes. Your code is used by professional traders "
            "on MetaTrader 5, TradingView, and algorithmic trading platforms."
        ),
        llm=llm,
        verbose=True,
        allow_delegation=False,
        max_iter=5,
    )


NOTEBOOK_ASSEMBLER_TASK_DESCRIPTION = """
Assemble all strategy components into export files:

STRATEGY CONFIG: {strategy_config}
RISK PARAMETERS: {risk_params}
BACKTEST RESULTS: {backtest_results}
PERFORMANCE ANALYSIS: {performance_analysis}
OPTIMIZATION RESULTS: {optimization_results}

Generate the following exports:

1. **MQL5 Expert Advisor** (mql5_ea.mq5):
   - Complete, compilable MQL5 EA code
   - All strategy rules implemented
   - Risk management built-in
   - Input parameters for all key settings
   - Proper error handling
   - Comments explaining each section

2. **PineScript v6 Strategy** (strategy.pine):
   - Complete PineScript v6 strategy script
   - All entry/exit rules
   - Risk management overlays
   - Performance metrics display
   - Alerts for signals

3. **Python Trading Class** (strategy.py):
   - Clean Python class with type hints
   - Compatible with backtrader/zipline/freqtrade
   - All indicators implemented
   - Entry/exit signal methods
   - Risk management methods
   - Docstrings for all methods

4. **Jupyter Notebook** (analysis.ipynb):
   - Complete analysis notebook
   - Data loading and preprocessing
   - Strategy implementation
   - Backtest execution
   - Performance visualization
   - All charts and metrics

5. **PDF Report** (report.pdf):
   - Executive summary
   - Strategy description
   - Backtest results with charts
   - Risk analysis
   - Optimization results
   - Recommendations
   - Appendix with full trade log

Generate all files and return their content as base64-encoded strings in JSON.
"""
