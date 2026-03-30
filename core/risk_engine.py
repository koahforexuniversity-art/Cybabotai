"""Risk management engine for position sizing and risk analysis.

Handles lot size calculation, margin requirements, drawdown limits,
and position risk validation.
"""

from decimal import Decimal, ROUND_DOWN, ROUND_HALF_UP
from dataclasses import dataclass, field
from typing import Any


# ─── Constants ────────────────────────────────────────────────────────────────

# Standard lot = 100,000 units of base currency
STANDARD_LOT = Decimal("100000")

# Pip values per standard lot for major pairs
PIP_VALUES: dict[str, Decimal] = {
    "EURUSD": Decimal("10.00"),
    "GBPUSD": Decimal("10.00"),
    "AUDUSD": Decimal("10.00"),
    "NZDUSD": Decimal("10.00"),
    "USDJPY": Decimal("9.10"),  # Approximate
    "USDCHF": Decimal("10.20"),  # Approximate
    "USDCAD": Decimal("7.50"),  # Approximate
    "EURGBP": Decimal("12.50"),  # Approximate
    "EURJPY": Decimal("9.10"),
    "GBPJPY": Decimal("9.10"),
    "AUDJPY": Decimal("9.10"),
    "EURAUD": Decimal("6.80"),
    "EURCHF": Decimal("10.20"),
    "GBPCHF": Decimal("10.20"),
    "XAUUSD": Decimal("10.00"),
    "XAGUSD": Decimal("50.00"),
}

# Pip size by symbol
PIP_SIZES: dict[str, Decimal] = {
    "EURUSD": Decimal("0.0001"),
    "GBPUSD": Decimal("0.0001"),
    "AUDUSD": Decimal("0.0001"),
    "NZDUSD": Decimal("0.0001"),
    "USDCHF": Decimal("0.0001"),
    "USDCAD": Decimal("0.0001"),
    "EURGBP": Decimal("0.0001"),
    "EURAUD": Decimal("0.0001"),
    "EURCHF": Decimal("0.0001"),
    "GBPCHF": Decimal("0.0001"),
    "USDJPY": Decimal("0.01"),
    "EURJPY": Decimal("0.01"),
    "GBPJPY": Decimal("0.01"),
    "AUDJPY": Decimal("0.01"),
    "XAUUSD": Decimal("0.01"),
    "XAGUSD": Decimal("0.01"),
}


@dataclass
class RiskProfile:
    """Account risk profile configuration."""

    balance: Decimal = Decimal("10000")
    max_risk_per_trade_pct: Decimal = Decimal("2.0")
    max_daily_risk_pct: Decimal = Decimal("5.0")
    max_total_exposure_pct: Decimal = Decimal("20.0")
    max_correlated_pairs: int = 3
    max_drawdown_limit_pct: Decimal = Decimal("25.0")
    leverage: int = 100
    margin_call_level_pct: Decimal = Decimal("100.0")
    stop_out_level_pct: Decimal = Decimal("50.0")


@dataclass
class PositionSize:
    """Calculated position size result."""

    lots: Decimal = Decimal("0")
    units: Decimal = Decimal("0")
    risk_amount: Decimal = Decimal("0")
    pip_value: Decimal = Decimal("0")
    margin_required: Decimal = Decimal("0")
    risk_reward_ratio: Decimal = Decimal("0")
    max_loss: Decimal = Decimal("0")
    max_profit: Decimal = Decimal("0")
    is_valid: bool = True
    warnings: list[str] = field(default_factory=list)
    rejection_reason: str = ""


@dataclass
class RiskAssessment:
    """Risk assessment for a potential trade."""

    symbol: str = ""
    direction: str = ""
    entry_price: Decimal = Decimal("0")
    stop_loss: Decimal = Decimal("0")
    take_profit: Decimal = Decimal("0")

    # Risk metrics
    stop_loss_pips: Decimal = Decimal("0")
    take_profit_pips: Decimal = Decimal("0")
    risk_reward_ratio: Decimal = Decimal("0")

    # Position sizing
    position: PositionSize = field(default_factory=PositionSize)

    # Account impact
    risk_pct_of_balance: Decimal = Decimal("0")
    margin_pct_of_balance: Decimal = Decimal("0")
    remaining_margin_pct: Decimal = Decimal("0")

    # Scoring
    risk_score: int = 0  # 1-10 (1 = very risky, 10 = very safe)
    risk_level: str = ""  # "low", "medium", "high", "extreme"
    notes: list[str] = field(default_factory=list)

    approved: bool = True


class RiskEngine:
    """Risk management engine for position sizing and validation."""

    def __init__(self, profile: RiskProfile | None = None) -> None:
        self.profile = profile or RiskProfile()
        self._daily_risk_used = Decimal("0")
        self._open_positions: list[dict[str, Any]] = []

    def calculate_position_size(
        self,
        symbol: str,
        entry_price: Decimal,
        stop_loss_price: Decimal,
        take_profit_price: Decimal | None = None,
        risk_pct: Decimal | None = None,
    ) -> PositionSize:
        """Calculate optimal position size based on risk parameters.

        Uses the fixed-percentage risk model:
        Lot Size = (Account Balance × Risk%) / (Stop Loss Pips × Pip Value)

        Args:
            symbol: Trading symbol (e.g., "EURUSD")
            entry_price: Entry price
            stop_loss_price: Stop loss price
            take_profit_price: Optional take profit price
            risk_pct: Override risk percentage (uses profile default if None)

        Returns:
            PositionSize with calculated values
        """
        result = PositionSize()
        symbol = symbol.upper().replace("/", "")

        risk_pct = risk_pct or self.profile.max_risk_per_trade_pct

        # Calculate stop loss in pips
        pip_size = PIP_SIZES.get(symbol, Decimal("0.0001"))
        sl_distance = abs(entry_price - stop_loss_price)
        sl_pips = (sl_distance / pip_size).quantize(
            Decimal("0.1"), rounding=ROUND_HALF_UP
        )

        if sl_pips <= 0:
            result.is_valid = False
            result.rejection_reason = "Stop loss too close to entry"
            return result

        # Risk amount in account currency
        risk_amount = (
            self.profile.balance * risk_pct / Decimal("100")
        ).quantize(Decimal("0.01"), rounding=ROUND_DOWN)

        result.risk_amount = risk_amount

        # Pip value per standard lot
        pip_value_per_lot = PIP_VALUES.get(symbol, Decimal("10.00"))

        # Position size in lots
        lots = (risk_amount / (sl_pips * pip_value_per_lot)).quantize(
            Decimal("0.01"), rounding=ROUND_DOWN
        )

        # Enforce minimum lot size
        if lots < Decimal("0.01"):
            result.is_valid = False
            result.rejection_reason = (
                f"Calculated lot size ({lots}) below minimum 0.01"
            )
            return result

        result.lots = lots
        result.units = lots * STANDARD_LOT
        result.pip_value = (lots * pip_value_per_lot).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )

        # Margin required
        margin = (
            result.units
            * entry_price
            / Decimal(str(self.profile.leverage))
        ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        result.margin_required = margin

        # Max loss
        result.max_loss = (sl_pips * result.pip_value).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )

        # Take profit calculations
        if take_profit_price is not None:
            tp_distance = abs(take_profit_price - entry_price)
            tp_pips = (tp_distance / pip_size).quantize(
                Decimal("0.1"), rounding=ROUND_HALF_UP
            )
            result.max_profit = (tp_pips * result.pip_value).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )

            if sl_pips > 0:
                result.risk_reward_ratio = (tp_pips / sl_pips).quantize(
                    Decimal("0.01"), rounding=ROUND_HALF_UP
                )

        # Validation warnings
        margin_pct = (margin / self.profile.balance * 100).quantize(
            Decimal("0.1"), rounding=ROUND_HALF_UP
        )

        if margin_pct > Decimal("10"):
            result.warnings.append(
                f"Margin uses {margin_pct}% of balance"
            )

        if lots > Decimal("10"):
            result.warnings.append(f"Large position: {lots} lots")

        if result.risk_reward_ratio > 0 and result.risk_reward_ratio < Decimal("1"):
            result.warnings.append(
                f"Poor risk/reward ratio: {result.risk_reward_ratio}"
            )

        return result

    def assess_trade(
        self,
        symbol: str,
        direction: str,
        entry_price: Decimal,
        stop_loss: Decimal,
        take_profit: Decimal,
        risk_pct: Decimal | None = None,
    ) -> RiskAssessment:
        """Perform comprehensive risk assessment for a potential trade.

        Args:
            symbol: Trading symbol
            direction: "long" or "short"
            entry_price: Entry price
            stop_loss: Stop loss price
            take_profit: Take profit price
            risk_pct: Override risk percentage

        Returns:
            RiskAssessment with complete analysis
        """
        assessment = RiskAssessment(
            symbol=symbol.upper(),
            direction=direction,
            entry_price=entry_price,
            stop_loss=stop_loss,
            take_profit=take_profit,
        )

        pip_size = PIP_SIZES.get(symbol.upper(), Decimal("0.0001"))

        # Calculate pip distances
        sl_pips = abs(entry_price - stop_loss) / pip_size
        tp_pips = abs(take_profit - entry_price) / pip_size

        assessment.stop_loss_pips = sl_pips.quantize(
            Decimal("0.1"), rounding=ROUND_HALF_UP
        )
        assessment.take_profit_pips = tp_pips.quantize(
            Decimal("0.1"), rounding=ROUND_HALF_UP
        )

        if sl_pips > 0:
            assessment.risk_reward_ratio = (tp_pips / sl_pips).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )

        # Validate direction vs SL/TP
        if direction == "long":
            if stop_loss >= entry_price:
                assessment.approved = False
                assessment.notes.append("Stop loss must be below entry for long")
            if take_profit <= entry_price:
                assessment.approved = False
                assessment.notes.append("Take profit must be above entry for long")
        elif direction == "short":
            if stop_loss <= entry_price:
                assessment.approved = False
                assessment.notes.append("Stop loss must be above entry for short")
            if take_profit >= entry_price:
                assessment.approved = False
                assessment.notes.append("Take profit must be below entry for short")

        # Calculate position size
        assessment.position = self.calculate_position_size(
            symbol, entry_price, stop_loss, take_profit, risk_pct
        )

        if not assessment.position.is_valid:
            assessment.approved = False
            assessment.notes.append(assessment.position.rejection_reason)

        # Account impact
        assessment.risk_pct_of_balance = (
            assessment.position.risk_amount / self.profile.balance * 100
        ).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)

        assessment.margin_pct_of_balance = (
            assessment.position.margin_required / self.profile.balance * 100
        ).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)

        # Check daily risk limit
        projected_daily_risk = (
            self._daily_risk_used + assessment.position.risk_amount
        )
        daily_risk_limit = (
            self.profile.balance * self.profile.max_daily_risk_pct / 100
        )

        if projected_daily_risk > daily_risk_limit:
            assessment.approved = False
            assessment.notes.append(
                f"Would exceed daily risk limit "
                f"({projected_daily_risk:.2f} > {daily_risk_limit:.2f})"
            )

        # Check total exposure
        total_margin = assessment.position.margin_required + sum(
            Decimal(str(p.get("margin", 0))) for p in self._open_positions
        )
        max_exposure = (
            self.profile.balance * self.profile.max_total_exposure_pct / 100
        )

        if total_margin > max_exposure:
            assessment.notes.append("Would exceed total exposure limit")

        # Risk scoring (1-10)
        score = 10

        # Deductions
        if assessment.risk_reward_ratio < Decimal("1"):
            score -= 3
        elif assessment.risk_reward_ratio < Decimal("1.5"):
            score -= 1

        if assessment.risk_pct_of_balance > Decimal("3"):
            score -= 2
        elif assessment.risk_pct_of_balance > Decimal("2"):
            score -= 1

        if sl_pips > Decimal("100"):
            score -= 1

        if assessment.margin_pct_of_balance > Decimal("15"):
            score -= 2

        score = max(score, 1)
        assessment.risk_score = score

        if score >= 8:
            assessment.risk_level = "low"
        elif score >= 6:
            assessment.risk_level = "medium"
        elif score >= 4:
            assessment.risk_level = "high"
        else:
            assessment.risk_level = "extreme"
            if assessment.approved:
                assessment.notes.append(
                    "WARNING: Trade has extreme risk profile"
                )

        return assessment

    def kelly_criterion(
        self,
        win_rate: float,
        avg_win: float,
        avg_loss: float,
        fraction: float = 0.5,
    ) -> Decimal:
        """Calculate Kelly Criterion optimal bet size.

        Uses half-Kelly by default for more conservative sizing.

        Args:
            win_rate: Win probability (0-1)
            avg_win: Average winning trade amount
            avg_loss: Average losing trade amount (positive number)
            fraction: Kelly fraction (0.5 = half-Kelly)

        Returns:
            Optimal risk percentage as Decimal
        """
        if avg_loss == 0 or win_rate <= 0 or win_rate >= 1:
            return Decimal("0")

        b = avg_win / avg_loss  # Win/loss ratio
        p = win_rate
        q = 1 - p

        kelly = (b * p - q) / b

        if kelly <= 0:
            return Decimal("0")

        # Apply fraction and cap at max risk
        optimal = Decimal(str(kelly * fraction * 100)).quantize(
            Decimal("0.1"), rounding=ROUND_HALF_UP
        )

        return min(optimal, self.profile.max_risk_per_trade_pct)

    def calculate_drawdown_recovery(
        self,
        drawdown_pct: float,
        avg_return_per_trade_pct: float,
        trades_per_day: float = 2.0,
    ) -> dict[str, float]:
        """Estimate recovery time from a drawdown.

        Args:
            drawdown_pct: Current drawdown percentage
            avg_return_per_trade_pct: Average return per trade
            trades_per_day: Average number of trades per day

        Returns:
            Recovery estimates
        """
        if avg_return_per_trade_pct <= 0:
            return {
                "trades_to_recover": float("inf"),
                "days_to_recover": float("inf"),
                "recovery_possible": False,
            }

        # Need to gain back: (1 / (1 - dd/100)) - 1
        dd_decimal = drawdown_pct / 100
        required_gain_pct = (1 / (1 - dd_decimal) - 1) * 100

        trades_needed = required_gain_pct / avg_return_per_trade_pct
        days_needed = trades_needed / trades_per_day

        return {
            "drawdown_pct": drawdown_pct,
            "required_gain_pct": round(required_gain_pct, 2),
            "trades_to_recover": round(trades_needed, 0),
            "days_to_recover": round(days_needed, 1),
            "recovery_possible": True,
        }

    def add_open_position(
        self,
        symbol: str,
        lots: Decimal,
        direction: str,
        margin: Decimal,
        risk_amount: Decimal,
    ) -> None:
        """Register an open position for exposure tracking."""
        self._open_positions.append(
            {
                "symbol": symbol,
                "lots": float(lots),
                "direction": direction,
                "margin": float(margin),
                "risk_amount": float(risk_amount),
            }
        )
        self._daily_risk_used += risk_amount

    def remove_open_position(self, symbol: str) -> None:
        """Remove a closed position from tracking."""
        self._open_positions = [
            p for p in self._open_positions if p["symbol"] != symbol
        ]

    def reset_daily_risk(self) -> None:
        """Reset daily risk counter (call at day boundary)."""
        self._daily_risk_used = Decimal("0")

    def get_exposure_summary(self) -> dict[str, Any]:
        """Get current exposure summary."""
        total_margin = sum(
            Decimal(str(p.get("margin", 0))) for p in self._open_positions
        )
        total_risk = sum(
            Decimal(str(p.get("risk_amount", 0))) for p in self._open_positions
        )

        return {
            "open_positions": len(self._open_positions),
            "total_margin": float(total_margin),
            "total_risk": float(total_risk),
            "margin_utilization_pct": float(
                total_margin / self.profile.balance * 100
            )
            if self.profile.balance > 0
            else 0,
            "daily_risk_used": float(self._daily_risk_used),
            "daily_risk_remaining": float(
                self.profile.balance * self.profile.max_daily_risk_pct / 100
                - self._daily_risk_used
            ),
            "positions": self._open_positions,
        }
