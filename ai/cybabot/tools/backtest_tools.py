"""CrewAI tools for backtesting, Monte Carlo, and metrics calculation."""

import json
from decimal import Decimal
from typing import Any, Type

from crewai.tools import BaseTool
from pydantic import BaseModel, Field


class RunBacktestInput(BaseModel):
    """Input schema for running a backtest."""

    symbol: str = Field(description="Forex pair symbol, e.g. EURUSD")
    timeframe: str = Field(description="Timeframe: M1, M5, M15, M30, H1, H4, D1")
    start_date: str = Field(description="Start date YYYY-MM-DD")
    end_date: str = Field(description="End date YYYY-MM-DD")
    initial_balance: float = Field(default=10000.0, description="Starting balance")
    risk_per_trade_pct: float = Field(default=2.0, description="Risk % per trade")
    stop_loss_pips: float = Field(default=30.0, description="Stop loss in pips")
    take_profit_pips: float = Field(default=60.0, description="Take profit in pips")
    strategy_logic: str = Field(
        description=(
            "JSON string describing the strategy entry/exit logic, "
            "including indicators and conditions"
        )
    )


class RunBacktestTool(BaseTool):
    """Run a precision backtest on historical data."""

    name: str = "run_backtest"
    description: str = (
        "Runs a precision backtest using Decimal arithmetic on historical tick/OHLCV data. "
        "Takes strategy parameters and returns full trade list, equity curve, and performance stats."
    )
    args_schema: Type[BaseModel] = RunBacktestInput

    def _run(
        self,
        symbol: str,
        timeframe: str,
        start_date: str,
        end_date: str,
        initial_balance: float = 10000.0,
        risk_per_trade_pct: float = 2.0,
        stop_loss_pips: float = 30.0,
        take_profit_pips: float = 60.0,
        strategy_logic: str = "{}",
    ) -> str:
        """Execute backtest."""
        from core.backtester import PrecisionBacktester, BacktestConfig
        from data.duckdb_store import DuckDBStore

        try:
            # Get OHLCV data
            store = DuckDBStore()
            bars = store.get_ohlcv(
                symbol=symbol,
                timeframe=timeframe,
                start_time=start_date,
                end_time=end_date,
            )
            store.close()

            if not bars:
                return json.dumps({
                    "success": False,
                    "error": f"No OHLCV data found for {symbol} {timeframe} "
                             f"from {start_date} to {end_date}. "
                             "Run data download and aggregation first.",
                })

            # Configure backtester
            config = BacktestConfig(
                symbol=symbol,
                timeframe=timeframe,
                initial_balance=Decimal(str(initial_balance)),
                risk_per_trade_pct=Decimal(str(risk_per_trade_pct)),
                stop_loss_pips=Decimal(str(stop_loss_pips)),
                take_profit_pips=Decimal(str(take_profit_pips)),
                spread_pips=Decimal("1.5"),
                commission_per_lot=Decimal("7.00"),
                slippage_pips=Decimal("0.5"),
            )

            backtester = PrecisionBacktester(config)

            # Convert bars to ticks for the backtester
            from core.backtester import Tick
            ticks = []
            for bar in bars:
                ticks.append(
                    Tick(
                        timestamp=str(bar["timestamp"]),
                        bid=Decimal(str(bar["close"])),
                        ask=Decimal(str(bar["close"])) + config.spread_pips * backtester._pip_size,
                        volume=Decimal(str(bar.get("volume", 0))),
                    )
                )

            # Run backtest
            results = backtester.run(ticks)

            # Serialize results
            output = {
                "success": True,
                "symbol": symbol,
                "timeframe": timeframe,
                "period": f"{start_date} to {end_date}",
                "total_bars": len(bars),
                "total_trades": results.total_trades,
                "winning_trades": results.winning_trades,
                "losing_trades": results.losing_trades,
                "win_rate_pct": float(results.win_rate),
                "net_profit": float(results.net_profit),
                "profit_factor": float(results.profit_factor),
                "max_drawdown_pct": float(results.max_drawdown_pct),
                "sharpe_ratio": float(results.sharpe_ratio),
                "sortino_ratio": float(results.sortino_ratio),
                "calmar_ratio": float(results.calmar_ratio),
                "final_balance": float(results.final_balance),
                "total_return_pct": float(
                    (results.final_balance - config.initial_balance)
                    / config.initial_balance
                    * 100
                ),
                "trades_summary": [
                    {
                        "entry_time": t.entry_time,
                        "exit_time": t.exit_time,
                        "direction": t.direction,
                        "profit_loss": float(t.profit_loss),
                        "profit_pips": float(t.profit_pips),
                    }
                    for t in results.trades[:20]  # First 20 trades
                ],
                "equity_curve_sample": [
                    {"timestamp": e[0], "equity": float(e[1])}
                    for e in list(results.equity_curve)[:100]  # Sample points
                ],
            }

            return json.dumps(output, default=str)

        except Exception as e:
            return json.dumps({"success": False, "error": str(e)})


class RunMonteCarloInput(BaseModel):
    """Input for Monte Carlo simulation."""

    trades_json: str = Field(
        description="JSON array of trade objects with profit_loss field"
    )
    num_simulations: int = Field(default=1000, description="Number of simulations")
    initial_balance: float = Field(default=10000.0, description="Starting balance")


class RunMonteCarloTool(BaseTool):
    """Run Monte Carlo simulation on trade results."""

    name: str = "run_monte_carlo"
    description: str = (
        "Performs Monte Carlo simulation by shuffling trade order to estimate "
        "probability distributions of returns and drawdowns. "
        "Provides robustness score and risk of ruin estimates."
    )
    args_schema: Type[BaseModel] = RunMonteCarloInput

    def _run(
        self,
        trades_json: str,
        num_simulations: int = 1000,
        initial_balance: float = 10000.0,
    ) -> str:
        """Run Monte Carlo simulation."""
        from core.monte_carlo import run_monte_carlo, MonteCarloConfig
        from core.metrics import TradeRecord

        try:
            raw_trades = json.loads(trades_json)

            # Convert to TradeRecord objects
            trades = [
                TradeRecord(
                    entry_time=t.get("entry_time", ""),
                    exit_time=t.get("exit_time", ""),
                    direction=t.get("direction", "long"),
                    entry_price=Decimal(str(t.get("entry_price", 0))),
                    exit_price=Decimal(str(t.get("exit_price", 0))),
                    lot_size=Decimal(str(t.get("lot_size", 0.01))),
                    profit_loss=Decimal(str(t["profit_loss"])),
                    profit_pips=Decimal(str(t.get("profit_pips", 0))),
                )
                for t in raw_trades
            ]

            config = MonteCarloConfig(
                num_simulations=num_simulations,
                initial_balance=initial_balance,
            )

            results = run_monte_carlo(trades, config)

            output = {
                "success": True,
                "num_simulations": results.num_simulations,
                "num_trades": results.num_trades,
                "equity_mean": results.equity_mean,
                "equity_median": results.equity_median,
                "return_mean_pct": results.return_mean_pct,
                "return_median_pct": results.return_median_pct,
                "drawdown_mean_pct": results.drawdown_mean_pct,
                "drawdown_worst_pct": results.drawdown_worst_pct,
                "ruin_probability_50pct": results.ruin_probability_50pct,
                "ruin_probability_75pct": results.ruin_probability_75pct,
                "robustness_score": results.robustness_score,
                "confidence_intervals": results.confidence_intervals,
                "equity_percentiles": results.equity_percentiles,
            }

            return json.dumps(output, default=str)

        except Exception as e:
            return json.dumps({"success": False, "error": str(e)})


class CalculateMetricsInput(BaseModel):
    """Input for metrics calculation."""

    trades_json: str = Field(
        description="JSON array of trade objects"
    )
    equity_json: str = Field(
        default="[]",
        description="JSON array of equity curve points (timestamp, equity)",
    )
    initial_balance: float = Field(default=10000.0, description="Starting balance")


class CalculateMetricsTool(BaseTool):
    """Calculate comprehensive performance metrics."""

    name: str = "calculate_metrics"
    description: str = (
        "Calculates comprehensive performance metrics including Sharpe, Sortino, "
        "Calmar ratios, profit factor, win rate, expectancy, and radar chart scores "
        "for strategy evaluation."
    )
    args_schema: Type[BaseModel] = CalculateMetricsInput

    def _run(
        self,
        trades_json: str,
        equity_json: str = "[]",
        initial_balance: float = 10000.0,
    ) -> str:
        """Calculate all metrics."""
        from core.metrics import (
            calculate_all_metrics,
            TradeRecord,
            EquityPoint,
        )

        try:
            raw_trades = json.loads(trades_json)
            raw_equity = json.loads(equity_json) if equity_json else []

            trades = [
                TradeRecord(
                    entry_time=t.get("entry_time", ""),
                    exit_time=t.get("exit_time", ""),
                    direction=t.get("direction", "long"),
                    entry_price=Decimal(str(t.get("entry_price", 0))),
                    exit_price=Decimal(str(t.get("exit_price", 0))),
                    lot_size=Decimal(str(t.get("lot_size", 0.01))),
                    profit_loss=Decimal(str(t["profit_loss"])),
                    profit_pips=Decimal(str(t.get("profit_pips", 0))),
                    duration_minutes=t.get("duration_minutes", 0),
                )
                for t in raw_trades
            ]

            equity_curve = [
                EquityPoint(
                    timestamp=e.get("timestamp", ""),
                    equity=Decimal(str(e.get("equity", initial_balance))),
                    balance=Decimal(str(e.get("balance", initial_balance))),
                )
                for e in raw_equity
            ]

            metrics = calculate_all_metrics(
                trades=trades,
                equity_curve=equity_curve,
                initial_balance=initial_balance,
            )

            # Convert dataclass to dict
            output = {
                "success": True,
                "metrics": {
                    "total_return_pct": metrics.total_return_pct,
                    "annualized_return_pct": metrics.annualized_return_pct,
                    "sharpe_ratio": metrics.sharpe_ratio,
                    "sortino_ratio": metrics.sortino_ratio,
                    "calmar_ratio": metrics.calmar_ratio,
                    "omega_ratio": metrics.omega_ratio,
                    "profit_factor": metrics.profit_factor,
                    "max_drawdown_pct": metrics.max_drawdown_pct,
                    "recovery_factor": metrics.recovery_factor,
                    "total_trades": metrics.total_trades,
                    "win_rate_pct": metrics.win_rate_pct,
                    "avg_win": metrics.avg_win,
                    "avg_loss": metrics.avg_loss,
                    "largest_win": metrics.largest_win,
                    "largest_loss": metrics.largest_loss,
                    "max_consecutive_wins": metrics.max_consecutive_wins,
                    "max_consecutive_losses": metrics.max_consecutive_losses,
                    "avg_risk_reward": metrics.avg_risk_reward,
                    "expectancy": metrics.expectancy,
                },
                "radar_chart": {
                    "profitability": metrics.radar_profitability,
                    "risk_management": metrics.radar_risk_management,
                    "consistency": metrics.radar_consistency,
                    "robustness": metrics.radar_robustness,
                    "efficiency": metrics.radar_efficiency,
                    "stability": metrics.radar_stability,
                },
            }

            return json.dumps(output, default=str)

        except Exception as e:
            return json.dumps({"success": False, "error": str(e)})
