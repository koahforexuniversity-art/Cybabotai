"""Precision Forex Backtester Engine.

Uses Decimal arithmetic for all price calculations to avoid float drift.
Processes tick-level Dukascopy data with realistic spread, slippage, and swap modeling.
"""

from decimal import Decimal, ROUND_HALF_UP
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable
import structlog

logger = structlog.get_logger()


@dataclass
class Tick:
    """A single price tick with bid/ask."""
    timestamp: datetime
    bid: Decimal
    ask: Decimal
    volume: Decimal = Decimal("0")

    @property
    def mid(self) -> Decimal:
        return (self.bid + self.ask) / Decimal("2")

    @property
    def spread(self) -> Decimal:
        return self.ask - self.bid


@dataclass
class Trade:
    """A completed trade record."""
    id: str
    symbol: str
    direction: str  # "long" or "short"
    entry_time: datetime
    exit_time: datetime | None = None
    entry_price: Decimal = Decimal("0")
    exit_price: Decimal = Decimal("0")
    stop_loss: Decimal = Decimal("0")
    take_profit: Decimal = Decimal("0")
    lot_size: Decimal = Decimal("0.01")
    pnl_pips: Decimal = Decimal("0")
    pnl_usd: Decimal = Decimal("0")
    swap: Decimal = Decimal("0")
    commission: Decimal = Decimal("0")
    status: str = "open"  # open, closed, stopped, tp_hit
    bars_held: int = 0


@dataclass
class BacktestConfig:
    """Configuration for a backtest run."""
    symbol: str = "EURUSD"
    timeframe: str = "H1"
    start_date: datetime = field(default_factory=datetime.utcnow)
    end_date: datetime = field(default_factory=datetime.utcnow)
    initial_capital: Decimal = Decimal("10000")
    leverage: int = 100
    risk_per_trade: Decimal = Decimal("0.02")  # 2% per trade
    max_concurrent_trades: int = 3
    slippage_pips: Decimal = Decimal("0.5")
    commission_per_lot: Decimal = Decimal("7")  # $7 per lot round trip
    swap_long: Decimal = Decimal("-0.5")  # pips per day
    swap_short: Decimal = Decimal("0.3")  # pips per day
    pip_value: Decimal = Decimal("10")  # $10 per pip for standard lot


@dataclass
class BacktestResults:
    """Complete backtest results."""
    # Capital
    initial_capital: Decimal = Decimal("10000")
    final_capital: Decimal = Decimal("10000")
    total_return_pct: Decimal = Decimal("0")
    annualized_return_pct: Decimal = Decimal("0")

    # Drawdown
    max_drawdown_pct: Decimal = Decimal("0")
    max_drawdown_usd: Decimal = Decimal("0")
    peak_capital: Decimal = Decimal("10000")

    # Trade Statistics
    total_trades: int = 0
    winning_trades: int = 0
    losing_trades: int = 0
    win_rate: Decimal = Decimal("0")

    # P&L
    gross_profit: Decimal = Decimal("0")
    gross_loss: Decimal = Decimal("0")
    net_profit: Decimal = Decimal("0")
    profit_factor: Decimal = Decimal("0")
    expectancy: Decimal = Decimal("0")

    # Risk Metrics
    sharpe_ratio: Decimal = Decimal("0")
    sortino_ratio: Decimal = Decimal("0")
    calmar_ratio: Decimal = Decimal("0")

    # Trade Details
    avg_win_pips: Decimal = Decimal("0")
    avg_loss_pips: Decimal = Decimal("0")
    avg_trade_duration_hours: Decimal = Decimal("0")
    largest_win: Decimal = Decimal("0")
    largest_loss: Decimal = Decimal("0")

    # Equity Curve
    equity_curve: list[dict[str, Any]] = field(default_factory=list)
    trade_log: list[dict[str, Any]] = field(default_factory=list)


class PrecisionBacktester:
    """High-precision forex backtester using Decimal arithmetic."""

    # Pip sizes for major pairs
    PIP_SIZES = {
        "EURUSD": Decimal("0.0001"),
        "GBPUSD": Decimal("0.0001"),
        "USDJPY": Decimal("0.01"),
        "USDCHF": Decimal("0.0001"),
        "AUDUSD": Decimal("0.0001"),
        "NZDUSD": Decimal("0.0001"),
        "USDCAD": Decimal("0.0001"),
        "EURGBP": Decimal("0.0001"),
        "EURJPY": Decimal("0.01"),
        "GBPJPY": Decimal("0.01"),
    }

    def __init__(self, config: BacktestConfig) -> None:
        self.config = config
        self.pip_size = self.PIP_SIZES.get(config.symbol, Decimal("0.0001"))
        self.results = BacktestResults(
            initial_capital=config.initial_capital,
            final_capital=config.initial_capital,
            peak_capital=config.initial_capital,
        )
        self.open_trades: list[Trade] = []
        self.closed_trades: list[Trade] = []
        self.current_capital = config.initial_capital
        self.peak_capital = config.initial_capital
        self._trade_counter = 0

        # Equity tracking
        self._equity_points: list[dict[str, Any]] = []
        self._returns: list[Decimal] = []

        # Progress callback
        self._progress_callback: Callable[[float, dict[str, Any]], None] | None = None

    def set_progress_callback(
        self,
        callback: Callable[[float, dict[str, Any]], None],
    ) -> None:
        """Set callback for progress updates."""
        self._progress_callback = callback

    def _to_pips(self, price_diff: Decimal) -> Decimal:
        """Convert price difference to pips."""
        return (price_diff / self.pip_size).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)

    def _from_pips(self, pips: Decimal) -> Decimal:
        """Convert pips to price difference."""
        return pips * self.pip_size

    def _calculate_lot_size(self, stop_loss_pips: Decimal) -> Decimal:
        """Calculate position size based on risk per trade."""
        if stop_loss_pips <= 0:
            return Decimal("0.01")

        risk_amount = self.current_capital * self.config.risk_per_trade
        pip_value_per_lot = self.config.pip_value
        lot_size = risk_amount / (stop_loss_pips * pip_value_per_lot)

        # Round to 2 decimal places (0.01 lot minimum)
        lot_size = max(Decimal("0.01"), lot_size.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))

        # Apply leverage constraint
        max_lots = (self.current_capital * self.config.leverage) / Decimal("100000")
        lot_size = min(lot_size, max_lots)

        return lot_size

    def open_trade(
        self,
        tick: Tick,
        direction: str,
        stop_loss_pips: Decimal,
        take_profit_pips: Decimal,
    ) -> Trade | None:
        """Open a new trade."""
        if len(self.open_trades) >= self.config.max_concurrent_trades:
            return None

        self._trade_counter += 1
        lot_size = self._calculate_lot_size(stop_loss_pips)

        # Apply slippage
        slippage = self._from_pips(self.config.slippage_pips)

        if direction == "long":
            entry_price = tick.ask + slippage
            stop_loss = entry_price - self._from_pips(stop_loss_pips)
            take_profit = entry_price + self._from_pips(take_profit_pips)
        else:
            entry_price = tick.bid - slippage
            stop_loss = entry_price + self._from_pips(stop_loss_pips)
            take_profit = entry_price - self._from_pips(take_profit_pips)

        trade = Trade(
            id=f"T{self._trade_counter:06d}",
            symbol=self.config.symbol,
            direction=direction,
            entry_time=tick.timestamp,
            entry_price=entry_price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            lot_size=lot_size,
        )

        self.open_trades.append(trade)
        return trade

    def process_tick(self, tick: Tick) -> list[Trade]:
        """Process a tick and check for trade exits."""
        closed_trades = []

        for trade in self.open_trades[:]:
            closed = self._check_trade_exit(trade, tick)
            if closed:
                closed_trades.append(trade)
                self.open_trades.remove(trade)
                self.closed_trades.append(trade)
                self._update_equity(tick, trade)

        return closed_trades

    def _check_trade_exit(self, trade: Trade, tick: Tick) -> bool:
        """Check if a trade should be closed."""
        if trade.direction == "long":
            current_price = tick.bid  # Close long at bid

            # Check stop loss
            if current_price <= trade.stop_loss:
                self._close_trade(trade, tick, trade.stop_loss, "stopped")
                return True

            # Check take profit
            if current_price >= trade.take_profit:
                self._close_trade(trade, tick, trade.take_profit, "tp_hit")
                return True

        else:  # short
            current_price = tick.ask  # Close short at ask

            # Check stop loss
            if current_price >= trade.stop_loss:
                self._close_trade(trade, tick, trade.stop_loss, "stopped")
                return True

            # Check take profit
            if current_price <= trade.take_profit:
                self._close_trade(trade, tick, trade.take_profit, "tp_hit")
                return True

        return False

    def _close_trade(
        self,
        trade: Trade,
        tick: Tick,
        exit_price: Decimal,
        status: str,
    ) -> None:
        """Close a trade and calculate P&L."""
        trade.exit_time = tick.timestamp
        trade.exit_price = exit_price
        trade.status = status

        # Calculate P&L in pips
        if trade.direction == "long":
            trade.pnl_pips = self._to_pips(exit_price - trade.entry_price)
        else:
            trade.pnl_pips = self._to_pips(trade.entry_price - exit_price)

        # Calculate P&L in USD
        trade.pnl_usd = trade.pnl_pips * self.config.pip_value * trade.lot_size

        # Apply commission
        trade.commission = self.config.commission_per_lot * trade.lot_size

        # Calculate swap (overnight holding cost)
        if trade.entry_time and trade.exit_time:
            days_held = (trade.exit_time - trade.entry_time).total_seconds() / 86400
            if trade.direction == "long":
                trade.swap = self.config.swap_long * Decimal(str(days_held)) * trade.lot_size
            else:
                trade.swap = self.config.swap_short * Decimal(str(days_held)) * trade.lot_size

        # Net P&L
        net_pnl = trade.pnl_usd - trade.commission + trade.swap
        self.current_capital += net_pnl

        # Update peak capital
        if self.current_capital > self.peak_capital:
            self.peak_capital = self.current_capital

    def _update_equity(self, tick: Tick, trade: Trade) -> None:
        """Update equity curve after trade close."""
        equity_point = {
            "x": tick.timestamp.timestamp() * 1000,  # milliseconds for Chart.js
            "y": float(self.current_capital),
            "trade_id": trade.id,
            "pnl": float(trade.pnl_usd),
        }
        self._equity_points.append(equity_point)

        # Track returns for Sharpe calculation
        if len(self._equity_points) > 1:
            prev_equity = Decimal(str(self._equity_points[-2]["y"]))
            if prev_equity > 0:
                ret = (self.current_capital - prev_equity) / prev_equity
                self._returns.append(ret)

        # Notify progress
        if self._progress_callback:
            self._progress_callback(
                len(self.closed_trades) / max(1, len(self.closed_trades) + len(self.open_trades)),
                equity_point,
            )

    def calculate_metrics(self) -> BacktestResults:
        """Calculate final backtest metrics."""
        results = self.results
        results.final_capital = self.current_capital
        results.peak_capital = self.peak_capital
        results.equity_curve = self._equity_points

        if not self.closed_trades:
            return results

        # Basic stats
        results.total_trades = len(self.closed_trades)
        winning = [t for t in self.closed_trades if t.pnl_usd > 0]
        losing = [t for t in self.closed_trades if t.pnl_usd <= 0]
        results.winning_trades = len(winning)
        results.losing_trades = len(losing)

        if results.total_trades > 0:
            results.win_rate = Decimal(str(results.winning_trades / results.total_trades * 100))

        # P&L
        results.gross_profit = sum(t.pnl_usd for t in winning)
        results.gross_loss = abs(sum(t.pnl_usd for t in losing))
        results.net_profit = results.final_capital - results.initial_capital
        results.total_return_pct = (results.net_profit / results.initial_capital * 100).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )

        if results.gross_loss > 0:
            results.profit_factor = (results.gross_profit / results.gross_loss).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )

        if results.total_trades > 0:
            results.expectancy = (results.net_profit / results.total_trades).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )

        # Drawdown
        max_dd = Decimal("0")
        peak = results.initial_capital
        for point in self._equity_points:
            equity = Decimal(str(point["y"]))
            if equity > peak:
                peak = equity
            dd = (peak - equity) / peak * 100
            if dd > max_dd:
                max_dd = dd
                results.max_drawdown_usd = peak - equity

        results.max_drawdown_pct = max_dd.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        # Average trade stats
        if winning:
            results.avg_win_pips = (sum(t.pnl_pips for t in winning) / len(winning)).quantize(
                Decimal("0.1"), rounding=ROUND_HALF_UP
            )
            results.largest_win = max(t.pnl_usd for t in winning)

        if losing:
            results.avg_loss_pips = abs(
                (sum(t.pnl_pips for t in losing) / len(losing)).quantize(
                    Decimal("0.1"), rounding=ROUND_HALF_UP
                )
            )
            results.largest_loss = abs(min(t.pnl_usd for t in losing))

        # Sharpe Ratio (annualized, assuming daily returns)
        if len(self._returns) > 1:
            import statistics
            returns_float = [float(r) for r in self._returns]
            avg_return = statistics.mean(returns_float)
            std_return = statistics.stdev(returns_float)
            if std_return > 0:
                # Annualize (assuming ~252 trading days)
                sharpe = (avg_return / std_return) * (252 ** 0.5)
                results.sharpe_ratio = Decimal(str(round(sharpe, 2)))

                # Sortino (only downside deviation)
                downside_returns = [r for r in returns_float if r < 0]
                if downside_returns:
                    downside_std = statistics.stdev(downside_returns) if len(downside_returns) > 1 else abs(downside_returns[0])
                    if downside_std > 0:
                        sortino = (avg_return / downside_std) * (252 ** 0.5)
                        results.sortino_ratio = Decimal(str(round(sortino, 2)))

        # Calmar Ratio
        if results.max_drawdown_pct > 0:
            results.calmar_ratio = (results.total_return_pct / results.max_drawdown_pct).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )

        # Trade log
        results.trade_log = [
            {
                "id": t.id,
                "direction": t.direction,
                "entry_time": t.entry_time.isoformat() if t.entry_time else None,
                "exit_time": t.exit_time.isoformat() if t.exit_time else None,
                "entry_price": float(t.entry_price),
                "exit_price": float(t.exit_price),
                "lot_size": float(t.lot_size),
                "pnl_pips": float(t.pnl_pips),
                "pnl_usd": float(t.pnl_usd),
                "status": t.status,
            }
            for t in self.closed_trades
        ]

        return results

    def to_dict(self) -> dict[str, Any]:
        """Convert results to dictionary."""
        results = self.calculate_metrics()
        return {
            "initial_capital": float(results.initial_capital),
            "final_capital": float(results.final_capital),
            "total_return_pct": float(results.total_return_pct),
            "max_drawdown_pct": float(results.max_drawdown_pct),
            "total_trades": results.total_trades,
            "winning_trades": results.winning_trades,
            "losing_trades": results.losing_trades,
            "win_rate": float(results.win_rate),
            "profit_factor": float(results.profit_factor),
            "expectancy": float(results.expectancy),
            "sharpe_ratio": float(results.sharpe_ratio),
            "sortino_ratio": float(results.sortino_ratio),
            "calmar_ratio": float(results.calmar_ratio),
            "avg_win_pips": float(results.avg_win_pips),
            "avg_loss_pips": float(results.avg_loss_pips),
            "largest_win": float(results.largest_win),
            "largest_loss": float(results.largest_loss),
            "equity_curve": results.equity_curve,
            "trade_log": results.trade_log,
        }
