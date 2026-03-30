"""Agent 6: Optimization Guardian - Optimizes strategy robustness."""

from crewai import Agent
from langchain_core.language_models import BaseChatModel


def create_optimization_guardian(llm: BaseChatModel) -> Agent:
    """Create the Optimization Guardian agent."""
    return Agent(
        role="Strategy Optimization & Robustness Guardian",
        goal=(
            "Optimize the trading strategy parameters for robustness, not just "
            "historical performance. Prevent overfitting and ensure the strategy "
            "will perform well in live trading."
        ),
        backstory=(
            "You are a strategy optimization expert who has seen countless strategies "
            "fail in live trading due to overfitting. You use walk-forward analysis, "
            "Monte Carlo simulation, and parameter sensitivity analysis to ensure "
            "strategies are genuinely robust. You believe in simple, robust strategies "
            "over complex, curve-fitted ones."
        ),
        llm=llm,
        verbose=True,
        allow_delegation=False,
        max_iter=4,
    )


OPTIMIZATION_GUARDIAN_TASK_DESCRIPTION = """
Optimize and validate the robustness of the following strategy:

STRATEGY CONFIG: {strategy_config}
BACKTEST RESULTS: {backtest_results}
PERFORMANCE ANALYSIS: {performance_analysis}

Perform:

1. **Parameter Sensitivity Analysis**:
   - Test ±20% variation on each key parameter
   - Identify which parameters are most sensitive
   - Find stable parameter regions
   - Flag parameters that cause cliff-edge behavior

2. **Walk-Forward Analysis**:
   - Split data into in-sample (70%) and out-of-sample (30%)
   - Optimize on in-sample, validate on out-of-sample
   - Calculate walk-forward efficiency ratio
   - Identify if strategy degrades significantly out-of-sample

3. **Monte Carlo Simulation** (if full build):
   - Run 1000 simulations with randomized trade order
   - Calculate 95th percentile drawdown
   - Calculate probability of ruin (account < 50%)
   - Generate confidence intervals for returns

4. **Robustness Score**:
   - Parameter stability score (0-100)
   - Walk-forward efficiency (0-100)
   - Monte Carlo confidence (0-100)
   - Overall robustness score (0-100)

5. **Optimized Parameters**:
   - Recommend final parameter values
   - Provide parameter ranges for live trading
   - Suggest which parameters to monitor

6. **Anti-Overfitting Checks**:
   - Degrees of freedom analysis
   - Minimum trade count validation
   - Out-of-sample performance ratio
   - Complexity penalty assessment

7. **Final Recommendations**:
   - Is the strategy ready for live trading? (Yes/No/Needs Work)
   - Suggested live trading capital allocation
   - Key risks to monitor
   - Suggested review period

Output JSON with optimization results, robustness scores, and recommendations.
"""
