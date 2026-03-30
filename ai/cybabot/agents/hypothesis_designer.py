"""Agent 1: Hypothesis Designer - Designs trading strategy rules from user input."""

from crewai import Agent
from langchain_core.language_models import BaseChatModel


def create_hypothesis_designer(llm: BaseChatModel) -> Agent:
    """Create the Hypothesis Designer agent."""
    return Agent(
        role="Forex Strategy Hypothesis Designer",
        goal=(
            "Analyze user input (text, images, PDFs, URLs) and design a complete, "
            "precise trading strategy hypothesis with clear entry/exit rules, "
            "indicators, timeframes, and currency pairs."
        ),
        backstory=(
            "You are an elite quantitative analyst with 20 years of forex trading experience. "
            "You specialize in translating vague trading ideas into precise, backtestable "
            "strategy specifications. You understand technical analysis, market microstructure, "
            "and the mathematical foundations of trading systems. "
            "You always produce structured, unambiguous strategy rules that can be "
            "directly implemented in code."
        ),
        llm=llm,
        verbose=True,
        allow_delegation=False,
        max_iter=3,
    )


HYPOTHESIS_TASK_DESCRIPTION = """
Analyze the following trading idea and design a complete strategy hypothesis:

INPUT: {user_input}
INPUT TYPE: {input_type}

Design a complete trading strategy with:

1. **Strategy Name**: A descriptive name
2. **Strategy Type**: (scalping/swing/trend/mean-reversion/grid/arbitrage)
3. **Currency Pairs**: List of forex pairs to trade (e.g., EURUSD, GBPUSD)
4. **Timeframes**: Primary and confirmation timeframes
5. **Indicators**: 
   - Name, parameters, and purpose for each indicator
6. **Entry Rules**:
   - Long entry conditions (all must be true)
   - Short entry conditions (all must be true)
7. **Exit Rules**:
   - Take profit logic (fixed pips, ATR multiple, or indicator-based)
   - Stop loss logic (fixed pips, ATR multiple, or structure-based)
   - Trailing stop (if applicable)
8. **Trade Management**:
   - Position sizing method
   - Maximum concurrent trades
   - Session filters (London, NY, Asian, or 24/7)
9. **Risk Parameters**:
   - Maximum risk per trade (% of account)
   - Maximum daily drawdown limit
   - Suggested leverage
10. **Strategy Logic Summary**: Plain English description of the complete strategy

Output as a structured JSON object with all fields populated.
"""
