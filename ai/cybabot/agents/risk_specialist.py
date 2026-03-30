"""Agent 3: Risk Specialist - Calculates and validates risk parameters."""

from crewai import Agent
from langchain_core.language_models import BaseChatModel


def create_risk_specialist(llm: BaseChatModel) -> Agent:
    """Create the Risk Specialist agent."""
    return Agent(
        role="Forex Risk Management Specialist",
        goal=(
            "Calculate optimal risk parameters for the trading strategy, including "
            "position sizing, stop loss levels, maximum drawdown limits, and "
            "risk-adjusted return targets."
        ),
        backstory=(
            "You are a certified risk manager with expertise in forex trading risk. "
            "You've managed risk for institutional forex desks and understand the "
            "mathematics of position sizing, Kelly criterion, Value at Risk (VaR), "
            "and drawdown management. You always prioritize capital preservation "
            "while maximizing risk-adjusted returns."
        ),
        llm=llm,
        verbose=True,
        allow_delegation=False,
        max_iter=3,
    )


RISK_SPECIALIST_TASK_DESCRIPTION = """
Calculate comprehensive risk parameters for the following strategy:

STRATEGY CONFIG: {strategy_config}
ACCOUNT SIZE: {account_size} USD
TARGET RETURN: {target_return}% annually
MAX ACCEPTABLE DRAWDOWN: {max_drawdown}%

Calculate and validate:

1. **Position Sizing**:
   - Recommended risk per trade (% of account)
   - Maximum position size in lots
   - Kelly criterion calculation
   - Fixed fractional position sizing formula

2. **Stop Loss Analysis**:
   - Minimum stop loss distance (based on ATR)
   - Maximum stop loss distance
   - Recommended stop loss placement
   - Stop loss to take profit ratio analysis

3. **Drawdown Management**:
   - Maximum consecutive losses before pause
   - Daily loss limit (% of account)
   - Weekly loss limit (% of account)
   - Recovery factor requirements

4. **Risk Metrics Targets**:
   - Target Sharpe Ratio (minimum acceptable)
   - Target Sortino Ratio
   - Target Calmar Ratio
   - Target Profit Factor (minimum 1.5)
   - Target Win Rate range

5. **Leverage Analysis**:
   - Recommended leverage
   - Maximum safe leverage
   - Margin requirements per trade

6. **Correlation Risk**:
   - Currency pair correlation analysis
   - Maximum correlated exposure
   - Portfolio heat calculation

Output a JSON object with all risk parameters and recommendations.
"""
