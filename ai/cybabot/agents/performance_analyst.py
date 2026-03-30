"""Agent 5: Performance Analyst - Analyzes backtest results and generates insights."""

from crewai import Agent
from langchain_core.language_models import BaseChatModel


def create_performance_analyst(llm: BaseChatModel) -> Agent:
    """Create the Performance Analyst agent."""
    return Agent(
        role="Quantitative Performance Analyst",
        goal=(
            "Deeply analyze backtest results to identify strategy strengths, weaknesses, "
            "market regime dependencies, and provide actionable insights for improvement."
        ),
        backstory=(
            "You are a quantitative analyst who has evaluated thousands of trading strategies. "
            "You understand the difference between genuine edge and curve-fitting, "
            "can identify regime-dependent performance, and know how to interpret "
            "statistical significance in trading results. "
            "You provide honest, data-driven assessments that help traders understand "
            "exactly what they have and what to expect in live trading."
        ),
        llm=llm,
        verbose=True,
        allow_delegation=False,
        max_iter=3,
    )


PERFORMANCE_ANALYST_TASK_DESCRIPTION = """
Perform deep performance analysis on the following backtest results:

BACKTEST RESULTS: {backtest_results}
STRATEGY CONFIG: {strategy_config}
RISK PARAMETERS: {risk_params}

Analyze:

1. **Overall Performance Assessment**:
   - Grade the strategy (A/B/C/D/F) with justification
   - Identify if performance is statistically significant
   - Compare to buy-and-hold benchmark
   - Assess risk-adjusted returns

2. **Radar Chart Data** (normalize all to 0-100 scale):
   - Profitability score (based on total return and profit factor)
   - Risk Management score (based on drawdown and Sharpe)
   - Consistency score (based on win rate and expectancy)
   - Robustness score (based on trade count and distribution)
   - Efficiency score (based on Calmar and Sortino)
   - Adaptability score (based on performance across market conditions)

3. **Strengths**:
   - What the strategy does well
   - Best performing market conditions
   - Most profitable setups

4. **Weaknesses**:
   - Where the strategy struggles
   - Worst performing conditions
   - Risk factors to monitor

5. **Market Regime Analysis**:
   - Performance in trending markets
   - Performance in ranging markets
   - Performance during high volatility
   - Performance during low volatility

6. **Statistical Significance**:
   - T-test on returns
   - Minimum trades for significance
   - Confidence intervals

7. **Improvement Recommendations**:
   - Top 3 specific improvements to test
   - Parameters to optimize
   - Filters to add

Output JSON with radar_data (6 scores), metrics summary, and analysis text.
"""
