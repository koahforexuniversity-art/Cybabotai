"""Agent 4: Backtesting Agent - Runs the precision backtester."""

from crewai import Agent
from langchain_core.language_models import BaseChatModel


def create_backtesting_agent(llm: BaseChatModel) -> Agent:
    """Create the Backtesting Agent."""
    return Agent(
        role="Precision Forex Backtesting Engineer",
        goal=(
            "Execute a high-precision backtest of the trading strategy using tick-level "
            "Dukascopy data, with realistic spread modeling, slippage, and swap calculations. "
            "Generate a complete equity curve and trade log."
        ),
        backstory=(
            "You are a quantitative developer specializing in high-fidelity forex backtesting. "
            "You use Decimal arithmetic to avoid float drift, model realistic market conditions "
            "including variable spreads, slippage, and overnight swaps. "
            "Your backtests are trusted by institutional traders because they accurately "
            "reflect real-world trading conditions."
        ),
        llm=llm,
        verbose=True,
        allow_delegation=False,
        max_iter=5,
    )


BACKTESTING_TASK_DESCRIPTION = """
Run a precision backtest for the following strategy:

STRATEGY CONFIG: {strategy_config}
RISK PARAMETERS: {risk_params}
DATA STATS: {data_stats}
BACKTEST PERIOD: {backtest_period}
INITIAL CAPITAL: {initial_capital} USD

Execute the backtest with:

1. **Backtest Configuration**:
   - Use tick-level data from DuckDB
   - Apply variable spreads from tick data
   - Model realistic slippage (0.5-2 pips depending on pair)
   - Calculate overnight swap costs
   - Apply leverage and margin requirements

2. **Trade Execution**:
   - Execute all entry/exit signals from strategy rules
   - Apply position sizing from risk parameters
   - Track all open positions with real-time P&L
   - Handle partial fills and requotes

3. **Equity Curve Generation**:
   - Record equity at each trade close
   - Calculate running drawdown
   - Track peak equity for drawdown calculation
   - Generate time-series equity data

4. **Trade Log**:
   - Record every trade: entry time, exit time, pair, direction, size, P&L, pips
   - Calculate per-trade statistics
   - Identify best/worst trades

5. **Performance Metrics**:
   - Total return (%)
   - Annualized return (%)
   - Maximum drawdown (%)
   - Sharpe ratio
   - Sortino ratio
   - Calmar ratio
   - Win rate (%)
   - Profit factor
   - Average win / average loss
   - Expectancy per trade
   - Total trades
   - Average trade duration

Stream equity curve points in real-time as trades are processed.
Output complete backtest results as JSON.
"""
