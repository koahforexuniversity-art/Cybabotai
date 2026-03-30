"""Agent 2: Data Scout - Fetches and validates tick data from Dukascopy."""

from crewai import Agent
from langchain_core.language_models import BaseChatModel


def create_data_scout(llm: BaseChatModel) -> Agent:
    """Create the Data Scout agent."""
    return Agent(
        role="Forex Data Scout & Validator",
        goal=(
            "Fetch high-quality tick data from Dukascopy for the specified currency pairs "
            "and timeframes, validate data quality, and prepare it for backtesting."
        ),
        backstory=(
            "You are a data engineering specialist with deep expertise in forex market data. "
            "You know every nuance of Dukascopy's tick data format, understand bid/ask spreads, "
            "and can identify data quality issues like gaps, outliers, and corporate actions. "
            "You ensure that backtests use the most accurate, realistic data possible."
        ),
        llm=llm,
        verbose=True,
        allow_delegation=False,
        max_iter=3,
    )


DATA_SCOUT_TASK_DESCRIPTION = """
Fetch and validate tick data for the following strategy:

STRATEGY CONFIG: {strategy_config}
CURRENCY PAIRS: {currency_pairs}
TIMEFRAMES: {timeframes}
BACKTEST PERIOD: {backtest_period}

Tasks:
1. **Download Tick Data**: Fetch Dukascopy tick data for each currency pair
   - Use the DukascopyDownloader tool
   - Download bid/ask tick data for the specified period
   - Store in DuckDB for fast querying

2. **Data Quality Check**:
   - Check for gaps in data (missing periods)
   - Identify outlier ticks (price spikes)
   - Validate spread reasonableness
   - Check for sufficient data volume

3. **Data Statistics**:
   - Total ticks per pair
   - Average spread per pair
   - Data coverage percentage
   - Any quality issues found

4. **Prepare OHLCV Data**:
   - Aggregate ticks to required timeframes
   - Calculate OHLCV bars from tick data
   - Store aggregated data in DuckDB

Output a JSON report with:
- data_stats: Statistics for each currency pair
- quality_score: 0-100 data quality score
- issues: List of any data quality issues
- ready_for_backtest: boolean
"""
