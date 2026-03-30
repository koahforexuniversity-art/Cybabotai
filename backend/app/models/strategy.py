"""Strategy SQLAlchemy model."""

from datetime import datetime
from sqlalchemy import String, Integer, DateTime, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Strategy(Base):
    """Strategy model for storing user-created trading strategies."""

    __tablename__ = "strategies"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    user_id: Mapped[str] = mapped_column(
        String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Strategy configuration (JSON)
    config: Mapped[str] = mapped_column(Text, default="{}", nullable=False)

    # Input data
    input_type: Mapped[str] = mapped_column(String, nullable=False)  # text, image, pdf, url
    input_data: Mapped[str | None] = mapped_column(Text, nullable=True)

    # LLM configuration
    llm_provider: Mapped[str] = mapped_column(String, nullable=False)  # grok, claude, deepseek, gemini, ollama
    llm_model: Mapped[str] = mapped_column(String, nullable=False)

    # Backtest results (JSON)
    backtest_results: Mapped[str | None] = mapped_column(Text, nullable=True)
    equity_curve: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON array

    # Status tracking
    status: Mapped[str] = mapped_column(String, default="pending", nullable=False, index=True)
    # Status: pending, processing, completed, failed
    progress: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Export files (JSON)
    exports: Mapped[str] = mapped_column(Text, default="{}", nullable=False)

    # Build metadata
    build_type: Mapped[str] = mapped_column(String, nullable=False)  # quick, standard, full
    credits_cost: Mapped[int] = mapped_column(Integer, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="strategies")  # type: ignore[name-defined]  # noqa: F821
    bot_listing: Mapped["BotListing | None"] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "BotListing", back_populates="strategy", uselist=False
    )

    def __repr__(self) -> str:
        return f"<Strategy id={self.id} name={self.name} status={self.status}>"
