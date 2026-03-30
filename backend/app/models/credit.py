"""Credit transaction SQLAlchemy model."""

from datetime import datetime
from sqlalchemy import String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class CreditTransaction(Base):
    """Credit transaction model for tracking all credit movements."""

    __tablename__ = "credit_transactions"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    user_id: Mapped[str] = mapped_column(
        String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    amount: Mapped[int] = mapped_column(Integer, nullable=False)  # Positive = credit, Negative = debit
    type: Mapped[str] = mapped_column(String, nullable=False)
    # Types: purchase, usage_quick, usage_standard, usage_full, marketplace_listing,
    #        marketplace_sale, marketplace_purchase, refund, free_tier_reset
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    stripe_session_id: Mapped[str | None] = mapped_column(String, nullable=True)
    related_strategy_id: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="credit_transactions")  # type: ignore[name-defined]  # noqa: F821

    def __repr__(self) -> str:
        return f"<CreditTransaction id={self.id} user_id={self.user_id} amount={self.amount}>"
