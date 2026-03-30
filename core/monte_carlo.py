"""Monte Carlo simulation for strategy robustness testing.

Performs randomized permutation tests on trade sequences to estimate
the probability distribution of key performance metrics.
"""

import random
import math
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any

from core.metrics import TradeRecord


@dataclass
class MonteCarloConfig:
    """Configuration for Monte Carlo simulation."""

    num_simulations: int = 1000
    confidence_levels: list[float] = field(
        default_factory=lambda: [0.95, 0.99]
    )
    initial_balance: float = 10000.0
    seed: int | None = None


@dataclass
class SimulationPath:
    """Single simulation path result."""

    final_equity: float = 0.0
    max_drawdown_pct: float = 0.0
    total_return_pct: float = 0.0
    peak_equity: float = 0.0
    trough_equity: float = 0.0


@dataclass
class MonteCarloResults:
    """Comprehensive Monte Carlo analysis results."""

    num_simulations: int = 0
    num_trades: int = 0
    initial_balance: float = 0.0

    # Final equity distribution
    equity_mean: float = 0.0
    equity_median: float = 0.0
    equity_std: float = 0.0
    equity_min: float = 0.0
    equity_max: float = 0.0
    equity_percentiles: dict[str, float] = field(default_factory=dict)

    # Return distribution
    return_mean_pct: float = 0.0
    return_median_pct: float = 0.0
    return_std_pct: float = 0.0

    # Drawdown distribution
    drawdown_mean_pct: float = 0.0
    drawdown_median_pct: float = 0.0
    drawdown_worst_pct: float = 0.0
    drawdown_percentiles: dict[str, float] = field(default_factory=dict)

    # Risk of ruin
    ruin_probability_50pct: float = 0.0  # P(losing 50% of capital)
    ruin_probability_75pct: float = 0.0  # P(losing 75% of capital)
    ruin_probability_100pct: float = 0.0  # P(total wipeout)

    # Confidence intervals
    confidence_intervals: dict[str, dict[str, float]] = field(default_factory=dict)

    # Individual paths for charting
    sample_paths: list[list[float]] = field(default_factory=list)

    # Robustness score (0-100)
    robustness_score: float = 0.0


def run_monte_carlo(
    trades: list[TradeRecord],
    config: MonteCarloConfig | None = None,
    progress_callback: Any | None = None,
) -> MonteCarloResults:
    """Run Monte Carlo simulation on trade sequence.

    Shuffles trade order to create alternative equity paths,
    measuring the distribution of outcomes.

    Args:
        trades: Original trade sequence
        config: Simulation configuration
        progress_callback: Optional callable(current, total) for progress

    Returns:
        MonteCarloResults with distribution statistics
    """
    if config is None:
        config = MonteCarloConfig()

    if config.seed is not None:
        random.seed(config.seed)

    results = MonteCarloResults(
        num_simulations=config.num_simulations,
        num_trades=len(trades),
        initial_balance=config.initial_balance,
    )

    if not trades:
        return results

    # Extract P&L values
    pnl_values = [float(t.profit_loss) for t in trades]

    # Run simulations
    paths: list[SimulationPath] = []
    sample_equity_curves: list[list[float]] = []
    max_sample_paths = 50  # Store up to 50 paths for visualization

    for i in range(config.num_simulations):
        # Shuffle trade order
        shuffled_pnl = pnl_values.copy()
        random.shuffle(shuffled_pnl)

        # Build equity curve
        path = _simulate_path(shuffled_pnl, config.initial_balance)
        paths.append(path)

        # Store sample paths for charting
        if i < max_sample_paths:
            equity_curve = _build_equity_list(shuffled_pnl, config.initial_balance)
            sample_equity_curves.append(equity_curve)

        if progress_callback:
            progress_callback(i + 1, config.num_simulations)

    results.sample_paths = sample_equity_curves

    # Analyze final equity distribution
    final_equities = sorted([p.final_equity for p in paths])
    results.equity_mean = _mean(final_equities)
    results.equity_median = _median(final_equities)
    results.equity_std = _std_dev(final_equities)
    results.equity_min = final_equities[0]
    results.equity_max = final_equities[-1]

    # Percentiles
    for pct in [1, 5, 10, 25, 50, 75, 90, 95, 99]:
        results.equity_percentiles[f"p{pct}"] = _percentile(final_equities, pct)

    # Return distribution
    returns = sorted([p.total_return_pct for p in paths])
    results.return_mean_pct = _mean(returns)
    results.return_median_pct = _median(returns)
    results.return_std_pct = _std_dev(returns)

    # Drawdown distribution
    drawdowns = sorted([p.max_drawdown_pct for p in paths])
    results.drawdown_mean_pct = _mean(drawdowns)
    results.drawdown_median_pct = _median(drawdowns)
    results.drawdown_worst_pct = drawdowns[-1] if drawdowns else 0

    for pct in [50, 75, 90, 95, 99]:
        results.drawdown_percentiles[f"p{pct}"] = _percentile(drawdowns, pct)

    # Risk of ruin
    ruin_50 = sum(1 for p in paths if p.final_equity < config.initial_balance * 0.5)
    ruin_75 = sum(1 for p in paths if p.final_equity < config.initial_balance * 0.25)
    ruin_100 = sum(1 for p in paths if p.final_equity <= 0)

    results.ruin_probability_50pct = ruin_50 / config.num_simulations * 100
    results.ruin_probability_75pct = ruin_75 / config.num_simulations * 100
    results.ruin_probability_100pct = ruin_100 / config.num_simulations * 100

    # Confidence intervals
    for cl in config.confidence_levels:
        lower_pct = (1 - cl) / 2 * 100
        upper_pct = (1 + cl) / 2 * 100
        results.confidence_intervals[f"{int(cl * 100)}%"] = {
            "equity_lower": _percentile(final_equities, lower_pct),
            "equity_upper": _percentile(final_equities, upper_pct),
            "return_lower": _percentile(returns, lower_pct),
            "return_upper": _percentile(returns, upper_pct),
            "drawdown_upper": _percentile(drawdowns, upper_pct),
        }

    # Calculate robustness score
    results.robustness_score = _calculate_robustness_score(results, config)

    return results


def run_parameter_sensitivity(
    trades: list[TradeRecord],
    parameter_name: str,
    parameter_values: list[float],
    modify_trades_fn: Any,
    config: MonteCarloConfig | None = None,
) -> dict[str, Any]:
    """Run Monte Carlo across different parameter values.

    Tests how strategy performance changes when a parameter is varied,
    identifying optimal parameter ranges and sensitivity.

    Args:
        trades: Original trade sequence
        parameter_name: Name of the parameter being tested
        parameter_values: Values to test
        modify_trades_fn: Function(trades, value) -> modified_trades
        config: Monte Carlo config

    Returns:
        Dictionary with sensitivity analysis results
    """
    if config is None:
        config = MonteCarloConfig(num_simulations=200)

    results_by_value: dict[float, MonteCarloResults] = {}

    for value in parameter_values:
        modified_trades = modify_trades_fn(trades, value)
        mc_results = run_monte_carlo(modified_trades, config)
        results_by_value[value] = mc_results

    # Find optimal value (best robustness score)
    optimal_value = max(
        results_by_value.keys(),
        key=lambda v: results_by_value[v].robustness_score,
    )

    return {
        "parameter_name": parameter_name,
        "values_tested": parameter_values,
        "optimal_value": optimal_value,
        "optimal_score": results_by_value[optimal_value].robustness_score,
        "results": {
            str(v): {
                "robustness_score": r.robustness_score,
                "return_mean_pct": r.return_mean_pct,
                "drawdown_mean_pct": r.drawdown_mean_pct,
                "ruin_probability_50pct": r.ruin_probability_50pct,
            }
            for v, r in results_by_value.items()
        },
    }


# ─── Internal Helpers ──────────────────────────────────────────────────────────

def _simulate_path(
    pnl_values: list[float],
    initial_balance: float,
) -> SimulationPath:
    """Simulate a single equity path from shuffled P&L values."""
    equity = initial_balance
    peak = initial_balance
    max_drawdown = 0.0
    trough = initial_balance

    for pnl in pnl_values:
        equity += pnl

        if equity > peak:
            peak = equity

        if equity < trough:
            trough = equity

        dd = (peak - equity) / peak * 100 if peak > 0 else 0
        if dd > max_drawdown:
            max_drawdown = dd

    total_return = (
        (equity - initial_balance) / initial_balance * 100
        if initial_balance > 0
        else 0
    )

    return SimulationPath(
        final_equity=equity,
        max_drawdown_pct=max_drawdown,
        total_return_pct=total_return,
        peak_equity=peak,
        trough_equity=trough,
    )


def _build_equity_list(
    pnl_values: list[float],
    initial_balance: float,
) -> list[float]:
    """Build equity list for visualization."""
    equity = [initial_balance]
    current = initial_balance

    for pnl in pnl_values:
        current += pnl
        equity.append(round(current, 2))

    return equity


def _calculate_robustness_score(
    results: MonteCarloResults,
    config: MonteCarloConfig,
) -> float:
    """Calculate overall robustness score (0-100).

    Factors:
    - Consistency of positive returns across simulations
    - Drawdown distribution
    - Risk of ruin
    - Return distribution symmetry
    """
    score = 50.0

    # Positive return probability
    positive_pct = 0
    if results.equity_percentiles:
        # Count percentiles above initial balance
        above_initial = sum(
            1
            for v in results.equity_percentiles.values()
            if v > config.initial_balance
        )
        positive_pct = above_initial / len(results.equity_percentiles) * 100

    score += (positive_pct - 50) * 0.3  # ±15 points

    # Low ruin probability
    if results.ruin_probability_50pct < 5:
        score += 15
    elif results.ruin_probability_50pct < 15:
        score += 5
    elif results.ruin_probability_50pct > 30:
        score -= 15
    elif results.ruin_probability_50pct > 50:
        score -= 25

    # Drawdown distribution
    if results.drawdown_median_pct < 15:
        score += 10
    elif results.drawdown_median_pct < 25:
        score += 5
    elif results.drawdown_median_pct > 40:
        score -= 10

    # Return mean positive
    if results.return_mean_pct > 20:
        score += 10
    elif results.return_mean_pct > 5:
        score += 5
    elif results.return_mean_pct < 0:
        score -= 15

    return max(min(score, 100), 0)


def _mean(values: list[float]) -> float:
    """Calculate arithmetic mean."""
    return sum(values) / len(values) if values else 0


def _median(values: list[float]) -> float:
    """Calculate median of sorted list."""
    if not values:
        return 0
    n = len(values)
    if n % 2 == 0:
        return (values[n // 2 - 1] + values[n // 2]) / 2
    return values[n // 2]


def _percentile(sorted_values: list[float], pct: float) -> float:
    """Calculate percentile from sorted list."""
    if not sorted_values:
        return 0
    idx = (pct / 100) * (len(sorted_values) - 1)
    lower = int(idx)
    upper = min(lower + 1, len(sorted_values) - 1)
    weight = idx - lower
    return sorted_values[lower] * (1 - weight) + sorted_values[upper] * weight


def _std_dev(values: list[float]) -> float:
    """Calculate sample standard deviation."""
    if len(values) < 2:
        return 0
    mean = _mean(values)
    variance = sum((x - mean) ** 2 for x in values) / (len(values) - 1)
    return math.sqrt(variance)
