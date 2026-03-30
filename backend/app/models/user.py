"""User SQLAlchemy model."""

from datetime import datetime
from sqlalchemy import String, Integer, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class User(Base):
    """User model for authentication and credit management."""

    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    name: Mapped[str | None] = mapped_column(String, nullable=True)
    password_hash: Mapped[str] = mapped_column(String, nullable=False)
    credits_balance: Mapped[int] = mapped_column(Integer, default=500, nullable=False)
    role: Mapped[str] = mapped_column(String, default="user", nullable=False)  # user, admin
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    credit_transactions: Mapped[list["CreditTransaction"]] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "CreditTransaction", back_populates="user", cascade="all, delete-orphan"
    )
    strategies: Mapped[list["Strategy"]] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "Strategy", back_populates="user", cascade="all, delete-orphan"
    )
    bot_listings: Mapped[list["BotListing"]] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "BotListing", foreign_keys="BotListing.seller_id", back_populates="seller",
        cascade="all, delete-orphan"
    )
    bot_purchases: Mapped[list["BotPurchase"]] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "BotPurchase", foreign_keys="BotPurchase.buyer_id", back_populates="buyer",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email}>"
