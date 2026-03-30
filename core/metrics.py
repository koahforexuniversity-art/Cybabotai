"""Performance metrics calculations for trading strategies.

All calculations use Decimal for precision where monetary values are involved.
"""

import math
from decimal import Decimal, ROUND_HALF_UP
from dataclasses import dataclass, field
from typing import Any


@dataclass
class TradeRecord:
    """Single trade record for metric calculation."""

    entry_time: str
    exit_time: str
    direction: str  # "long" or "short"
    entry_price: Decimal
    exit_price: Decimal
    lot_size: Decimal
    profit_loss: Decimal
    profit_pips: Decimal
    duration_minutes: int = 0
    max_adverse_excursion: Decimal = Decimal("0")
    max_favorable_excursion: Decimal = Decimal("0")


@dataclass
class EquityPoint:
    """Single equity curve point."""

    timestamp: str
    equity: Decimal
    balance: Decimal
    drawdown_pct: Decimal = Decimal("0")


@dataclass
class PerformanceMetrics:
    """Comprehensive strategy performance metrics."""

    # Core returns
    total_return_pct: float = 0.0
    annualized_return_pct: float = 0.0
    monthly_return_avg: float = 0.0

    # Risk metrics
    sharpe_ratio: float = 0.0
    sortino_ratio: float = 0.0
    calmar_ratio: float = 0.0
    omega_ratio: float = 0.0
    profit_factor: float = 0.0

    # Drawdown
    max_drawdown_pct: float = 0.0
    max_drawdown_duration_days: int = 0
    avg_drawdown_pct: float = 0.0
    recovery_factor: float = 0.0

    # Trade statistics
    total_trades: int = 0
    winning_trades: int = 0
    losing_trades: int = 0
    win_rate_pct: float = 0.0
    avg_win: float = 0.0
    avg_loss: float = 0.0
    largest_win: float = 0.0
    largest_loss: float = 0.0
    avg_trade_duration_minutes: float = 0.0
    max_consecutive_wins: int = 0
    max_consecutive_losses: int = 0

    # Risk-reward
    avg_risk_reward: float = 0.0
    expectancy: float = 0.0
    expectancy_per_dollar: float = 0.0

    # Distribution
    skewness: float = 0.0
    kurtosis: float = 0.0

    # Radar chart values (0-100 scale)
    radar_profitability: float = 0.0
    radar_risk_management: float = 0.0
    radar_consistency: float = 0.0
    radar_robustness: float = 0.0
    radar_efficiency: float = 0.0
    radar_stability: float = 0.0


def calculate_sharpe_ratio(
    returns: list[float],
    risk_free_rate: float = 0.0,
    periods_per_year: int = 252,
) -> float:
    """Calculate annualized Sharpe ratio.

    Args:
        returns: List of periodic returns
        risk_free_rate: Annual risk-free rate
        periods_per_year: Number of periods per year (252 for daily, 12 for monthly)

    Returns:
        Annualized Sharpe ratio
    """
    if not returns or len(returns) < 2:
        return 0.0

    periodic_rf = risk_free_rate / periods_per_year
    excess_returns = [r - periodic_rf for r in returns]
    mean_excess = sum(excess_returns) / len(excess_returns)
    std_dev = _std_dev(excess_returns)

    if std_dev == 0:
        return 0.0

    return (mean_excess / std_dev) * math.sqrt(periods_per_year)


def calculate_sortino_ratio(
    returns: list[float],
    risk_free_rate: float = 0.0,
    periods_per_year: int = 252,
) -> float:
    """Calculate annualized Sortino ratio (downside deviation only).

    Args:
        returns: List of periodic returns
        risk_free_rate: Annual risk-free rate
        periods_per_year: Number of periods per year

    Returns:
        Annualized Sortino ratio
    """
    if not returns or len(returns) < 2:
        return 0.0

    periodic_rf = risk_free_rate / periods_per_year
    excess_returns = [r - periodic_rf for r in returns]
    mean_excess = sum(excess_returns) / len(excess_returns)

    # Downside deviation: only negative returns
    downside_returns = [min(r, 0) ** 2 for r in excess_returns]
    downside_dev = math.sqrt(sum(downside_returns) / len(downside_returns))

    if downside_dev == 0:
        return 0.0

    return (mean_excess / downside_dev) * math.sqrt(periods_per_year)


def calculate_calmar_ratio(
    total_return_pct: float,
    max_drawdown_pct: float,
    years: float,
) -> float:
    """Calculate Calmar ratio (annualized return / max drawdown).

    Args:
        total_return_pct: Total return percentage
        max_drawdown_pct: Maximum drawdown percentage (positive number)
        years: Number of years in the period

    Returns:
        Calmar ratio
    """
    if max_drawdown_pct == 0 or years == 0:
        return 0.0

    annualized_return = total_return_pct / years
    return annualized_return / abs(max_drawdown_pct)


def calculate_omega_ratio(
    returns: list[float],
    threshold: float = 0.0,
) -> float:
    """Calculate Omega ratio.

    Ratio of gains above threshold to losses below threshold.

    Args:
        returns: List of periodic returns
        threshold: Minimum acceptable return

    Returns:
        Omega ratio
    """
    if not returns:
        return 0.0

    gains = sum(max(r - threshold, 0) for r in returns)
    losses = sum(max(threshold - r, 0) for r in returns)

    if losses == 0:
        return float("inf") if gains > 0 else 0.0

    return gains / losses


def calculate_profit_factor(trades: list[TradeRecord]) -> float:
    """Calculate profit factor (gross profits / gross losses)."""
    gross_profit = sum(float(t.profit_loss) for t in trades if t.profit_loss > 0)
    gross_loss = abs(sum(float(t.profit_loss) for t in trades if t.profit_loss < 0))

    if gross_loss == 0:
        return float("inf") if gross_profit > 0 else 0.0

    return gross_profit / gross_loss


def calculate_max_drawdown(equity_curve: list[EquityPoint]) -> tuple[float, int]:
    """Calculate maximum drawdown percentage and duration in days.

    Returns:
        Tuple of (max_drawdown_pct, max_drawdown_duration_days)
    """
    if not equity_curve:
        return 0.0, 0

    peak = float(equity_curve[0].equity)
    max_dd = 0.0
    max_dd_duration = 0
    current_dd_start = 0
    in_drawdown = False

    for i, point in enumerate(equity_curve):
        equity = float(point.equity)

        if equity > peak:
            peak = equity
            if in_drawdown:
                duration = i - current_dd_start
                max_dd_duration = max(max_dd_duration, duration)
                in_drawdown = False

        dd = (peak - equity) / peak * 100 if peak > 0 else 0.0
        if dd > max_dd:
            max_dd = dd

        if dd > 0 and not in_drawdown:
            current_dd_start = i
            in_drawdown = True

    # Handle case where drawdown continues to the end
    if in_drawdown:
        duration = len(equity_curve) - 1 - current_dd_start
        max_dd_duration = max(max_dd_duration, duration)

    return max_dd, max_dd_duration


def calculate_expectancy(trades: list[TradeRecord]) -> float:
    """Calculate mathematical expectancy per trade."""
    if not trades:
        return 0.0

    wins = [float(t.profit_loss) for t in trades if t.profit_loss > 0]
    losses = [float(t.profit_loss) for t in trades if t.profit_loss < 0]

    win_rate = len(wins) / len(trades) if trades else 0
    avg_win = sum(wins) / len(wins) if wins else 0
    avg_loss = abs(sum(losses) / len(losses)) if losses else 0

    return (win_rate * avg_win) - ((1 - win_rate) * avg_loss)


def calculate_consecutive_runs(trades: list[TradeRecord]) -> tuple[int, int]:
    """Calculate maximum consecutive wins and losses.

    Returns:
        Tuple of (max_consecutive_wins, max_consecutive_losses)
    """
    if not trades:
        return 0, 0

    max_wins = 0
    max_losses = 0
    current_wins = 0
    current_losses = 0

    for trade in trades:
        if trade.profit_loss > 0:
            current_wins += 1
            current_losses = 0
            max_wins = max(max_wins, current_wins)
        elif trade.profit_loss < 0:
            current_losses += 1
            current_wins = 0
            max_losses = max(max_losses, current_losses)
        else:
            current_wins = 0
            current_losses = 0

    return max_wins, max_losses


def calculate_all_metrics(
    trades: list[TradeRecord],
    equity_curve: list[EquityPoint],
    initial_balance: float = 10000.0,
    risk_free_rate: float = 0.0,
    trading_days: int = 252,
) -> PerformanceMetrics:
    """Calculate comprehensive performance metrics.

    Args:
        trades: List of trade records
        equity_curve: Equity curve points
        initial_balance: Starting account balance
        risk_free_rate: Annual risk-free rate
        trading_days: Trading days per year

    Returns:
        PerformanceMetrics with all values computed
    """
    metrics = PerformanceMetrics()

    if not trades:
        return metrics

    # Trade statistics
    metrics.total_trades = len(trades)
    winning = [t for t in trades if t.profit_loss > 0]
    losing = [t for t in trades if t.profit_loss < 0]
    metrics.winning_trades = len(winning)
    metrics.losing_trades = len(losing)
    metrics.win_rate_pct = (
        (len(winning) / len(trades)) * 100 if trades else 0
    )

    # P&L stats
    all_pnl = [float(t.profit_loss) for t in trades]
    win_pnl = [float(t.profit_loss) for t in winning]
    loss_pnl = [float(t.profit_loss) for t in losing]

    metrics.avg_win = sum(win_pnl) / len(win_pnl) if win_pnl else 0
    metrics.avg_loss = sum(loss_pnl) / len(loss_pnl) if loss_pnl else 0
    metrics.largest_win = max(win_pnl) if win_pnl else 0
    metrics.largest_loss = min(loss_pnl) if loss_pnl else 0

    # Duration
    durations = [t.duration_minutes for t in trades if t.duration_minutes > 0]
    metrics.avg_trade_duration_minutes = (
        sum(durations) / len(durations) if durations else 0
    )

    # Consecutive runs
    max_wins, max_losses = calculate_consecutive_runs(trades)
    metrics.max_consecutive_wins = max_wins
    metrics.max_consecutive_losses = max_losses

    # Returns
    final_equity = float(equity_curve[-1].equity) if equity_curve else initial_balance
    metrics.total_return_pct = (
        ((final_equity - initial_balance) / initial_balance) * 100
    )

    # Estimate years
    if equity_curve and len(equity_curve) > 1:
        # Approximate days from equity curve
        days = len(equity_curve)  # Simplified — one point per bar
        years = max(days / trading_days, 1 / 12)  # At least 1 month
    else:
        years = 1.0

    metrics.annualized_return_pct = metrics.total_return_pct / years

    # Daily returns for ratio calculations
    daily_returns: list[float] = []
    if equity_curve and len(equity_curve) > 1:
        for i in range(1, len(equity_curve)):
            prev = float(equity_curve[i - 1].equity)
            curr = float(equity_curve[i].equity)
            if prev > 0:
                daily_returns.append((curr - prev) / prev)

    # Risk ratios
    metrics.sharpe_ratio = calculate_sharpe_ratio(
        daily_returns, risk_free_rate, trading_days
    )
    metrics.sortino_ratio = calculate_sortino_ratio(
        daily_returns, risk_free_rate, trading_days
    )

    # Drawdown
    max_dd, max_dd_dur = calculate_max_drawdown(equity_curve)
    metrics.max_drawdown_pct = max_dd
    metrics.max_drawdown_duration_days = max_dd_dur

    metrics.calmar_ratio = calculate_calmar_ratio(
        metrics.total_return_pct, metrics.max_drawdown_pct, years
    )

    # Recovery factor
    if metrics.max_drawdown_pct > 0:
        metrics.recovery_factor = metrics.total_return_pct / metrics.max_drawdown_pct

    # Profit factor
    metrics.profit_factor = calculate_profit_factor(trades)

    # Omega ratio
    metrics.omega_ratio = calculate_omega_ratio(daily_returns)

    # Expectancy
    metrics.expectancy = calculate_expectancy(trades)
    if metrics.avg_loss != 0:
        metrics.expectancy_per_dollar = metrics.expectancy / abs(metrics.avg_loss)

    # Risk-reward
    if metrics.avg_loss != 0:
        metrics.avg_risk_reward = abs(metrics.avg_win / metrics.avg_loss)

    # Distribution stats
    if len(all_pnl) > 2:
        metrics.skewness = _skewness(all_pnl)
        metrics.kurtosis = _kurtosis(all_pnl)

    # Radar chart scores (0-100 scale)
    metrics.radar_profitability = _score_profitability(metrics)
    metrics.radar_risk_management = _score_risk_management(metrics)
    metrics.radar_consistency = _score_consistency(metrics)
    metrics.radar_robustness = _score_robustness(metrics)
    metrics.radar_efficiency = _score_efficiency(metrics)
    metrics.radar_stability = _score_stability(metrics)

    return metrics


# ─── Radar Scoring Helpers ─────────────────────────────────────────────────────

def _score_profitability(m: PerformanceMetrics) -> float:
    """Score profitability on 0-100 scale."""
    score = 0.0
    # Profit factor: 1.0=0, 1.5=30, 2.0=60, 3.0+=100
    score += min(max((m.profit_factor - 1.0) * 50, 0), 40)
    # Win rate: 40%=0, 55%=30, 70%+=50
    score += min(max((m.win_rate_pct - 40) * 1.67, 0), 30)
    # Total return: 0%=0, 50%=15, 100%+=30
    score += min(max(m.total_return_pct * 0.3, 0), 30)
    return min(score, 100)


def _score_risk_management(m: PerformanceMetrics) -> float:
    """Score risk management on 0-100 scale."""
    score = 100.0
    # Max drawdown penalty: 0-10% = no penalty, 10-30% = medium, 30%+ = heavy
    score -= min(max(m.max_drawdown_pct - 10, 0) * 2, 50)
    # Consecutive losses penalty: >5 = -10, >10 = -25
    if m.max_consecutive_losses > 10:
        score -= 25
    elif m.max_consecutive_losses > 5:
        score -= 10
    # Bonus for good risk-reward
    if m.avg_risk_reward > 1.5:
        score += 15
    return max(min(score, 100), 0)


def _score_consistency(m: PerformanceMetrics) -> float:
    """Score consistency on 0-100 scale."""
    score = 50.0
    # Win rate contribution
    score += (m.win_rate_pct - 50) * 0.5
    # Expectancy contribution
    if m.expectancy > 0:
        score += min(m.expectancy * 10, 25)
    else:
        score -= min(abs(m.expectancy) * 10, 25)
    return max(min(score, 100), 0)


def _score_robustness(m: PerformanceMetrics) -> float:
    """Score robustness on 0-100 scale."""
    score = 50.0
    # Sharpe contribution
    score += min(max(m.sharpe_ratio * 15, -25), 25)
    # Calmar contribution
    score += min(max(m.calmar_ratio * 10, -15), 15)
    # Recovery factor
    if m.recovery_factor > 2:
        score += 10
    return max(min(score, 100), 0)


def _score_efficiency(m: PerformanceMetrics) -> float:
    """Score efficiency on 0-100 scale."""
    score = 50.0
    # Omega ratio: 1.0=neutral, 2.0+=good
    score += min(max((m.omega_ratio - 1.0) * 20, -25), 25)
    # Profit factor: 1.5=neutral, 2.5+=good
    score += min(max((m.profit_factor - 1.5) * 15, -15), 25)
    return max(min(score, 100), 0)


def _score_stability(m: PerformanceMetrics) -> float:
    """Score stability on 0-100 scale."""
    score = 70.0
    # Drawdown duration penalty
    score -= min(m.max_drawdown_duration_days * 0.5, 30)
    # Skewness bonus (positive skew = more large wins)
    if m.skewness > 0:
        score += min(m.skewness * 5, 15)
    else:
        score -= min(abs(m.skewness) * 5, 15)
    # Kurtosis penalty (high kurtosis = fat tails = unpredictable)
    score -= min(max(m.kurtosis - 3, 0) * 2, 15)
    return max(min(score, 100), 0)


# ─── Statistical Helpers ──────────────────────────────────────────────────────

def _std_dev(values: list[float]) -> float:
    """Calculate sample standard deviation."""
    if len(values) < 2:
        return 0.0
    mean = sum(values) / len(values)
    variance = sum((x - mean) ** 2 for x in values) / (len(values) - 1)
    return math.sqrt(variance)


def _skewness(values: list[float]) -> float:
    """Calculate Fisher's skewness."""
    n = len(values)
    if n < 3:
        return 0.0

    mean = sum(values) / n
    std = _std_dev(values)

    if std == 0:
        return 0.0

    m3 = sum((x - mean) ** 3 for x in values) / n
    return m3 / (std ** 3)


def _kurtosis(values: list[float]) -> float:
    """Calculate excess kurtosis."""
    n = len(values)
    if n < 4:
        return 0.0

    mean = sum(values) / n
    std = _std_dev(values)

    if std == 0:
        return 0.0

    m4 = sum((x - mean) ** 4 for x in values) / n
    return (m4 / (std ** 4)) - 3.0
