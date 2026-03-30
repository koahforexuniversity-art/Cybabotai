"""Marketplace SQLAlchemy models."""

from datetime import datetime
from sqlalchemy import String, Integer, Float, DateTime, Boolean, Text, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class BotListing(Base):
    """Bot marketplace listing model."""

    __tablename__ = "bot_listings"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    seller_id: Mapped[str] = mapped_column(
        String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    strategy_id: Mapped[str] = mapped_column(
        String, ForeignKey("strategies.id", ondelete="CASCADE"), nullable=False, unique=True
    )

    # Listing details
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(String, nullable=False, index=True)
    # Categories: scalping, swing, trend_following, mean_reversion, grid, arbitrage

    # Pricing
    price_credits: Mapped[int] = mapped_column(Integer, nullable=False)
    price_usd: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Performance highlights
    sharpe_ratio: Mapped[float | None] = mapped_column(Float, nullable=True)
    max_drawdown: Mapped[float | None] = mapped_column(Float, nullable=True)
    win_rate: Mapped[float | None] = mapped_column(Float, nullable=True)
    total_return: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Marketplace metadata
    sales_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    rating: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    review_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    featured: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    # Images
    thumbnail_url: Mapped[str | None] = mapped_column(String, nullable=True)
    equity_curve_url: Mapped[str | None] = mapped_column(String, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    seller: Mapped["User"] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "User", foreign_keys=[seller_id], back_populates="bot_listings"
    )
    strategy: Mapped["Strategy"] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "Strategy", back_populates="bot_listing"
    )
    purchases: Mapped[list["BotPurchase"]] = relationship(
        "BotPurchase", back_populates="listing", cascade="all, delete-orphan"
    )
    reviews: Mapped[list["BotReview"]] = relationship(
        "BotReview", back_populates="listing", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<BotListing id={self.id} title={self.title}>"


class BotPurchase(Base):
    """Bot purchase record model."""

    __tablename__ = "bot_purchases"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    buyer_id: Mapped[str] = mapped_column(
        String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    listing_id: Mapped[str] = mapped_column(
        String, ForeignKey("bot_listings.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Payment details
    credits_paid: Mapped[int] = mapped_column(Integer, nullable=False)
    usd_paid: Mapped[float | None] = mapped_column(Float, nullable=True)
    stripe_session_id: Mapped[str | None] = mapped_column(String, nullable=True)

    # Commission breakdown
    platform_fee: Mapped[int] = mapped_column(Integer, nullable=False)
    seller_earnings: Mapped[int] = mapped_column(Integer, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    buyer: Mapped["User"] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "User", foreign_keys=[buyer_id], back_populates="bot_purchases"
    )
    listing: Mapped["BotListing"] = relationship("BotListing", back_populates="purchases")

    def __repr__(self) -> str:
        return f"<BotPurchase id={self.id} buyer_id={self.buyer_id}>"


class BotReview(Base):
    """Bot review and rating model."""

    __tablename__ = "bot_reviews"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    listing_id: Mapped[str] = mapped_column(
        String, ForeignKey("bot_listings.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id: Mapped[str] = mapped_column(String, nullable=False)

    rating: Mapped[int] = mapped_column(Integer, nullable=False)  # 1-5 stars
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    listing: Mapped["BotListing"] = relationship("BotListing", back_populates="reviews")

    __table_args__ = (
        UniqueConstraint("listing_id", "user_id", name="uq_listing_user_review"),
    )

    def __repr__(self) -> str:
        return f"<BotReview id={self.id} rating={self.rating}>"
