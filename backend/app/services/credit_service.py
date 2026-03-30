"""Credit management service."""

import cuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status

from app.config import get_settings
from app.models.user import User
from app.models.credit import CreditTransaction

settings = get_settings()


class CreditService:
    """Service for managing user credits."""

    async def get_balance(self, db: AsyncSession, user_id: str) -> int:
        """Get current credit balance for a user."""
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return user.credits_balance

    async def deduct_credits(
        self,
        db: AsyncSession,
        user: User,
        amount: int,
        transaction_type: str,
        description: str,
        related_strategy_id: str | None = None,
    ) -> CreditTransaction:
        """Deduct credits from user balance."""
        if user.credits_balance < amount:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail=f"Insufficient credits. Required: {amount}, Available: {user.credits_balance}",
            )

        # Deduct from balance
        user.credits_balance -= amount

        # Record transaction
        transaction = CreditTransaction(
            id=cuid.cuid(),
            user_id=user.id,
            amount=-amount,  # Negative for deductions
            type=transaction_type,
            description=description,
            related_strategy_id=related_strategy_id,
        )
        db.add(transaction)
        await db.flush()
        return transaction

    async def add_credits(
        self,
        db: AsyncSession,
        user: User,
        amount: int,
        transaction_type: str,
        description: str,
        stripe_session_id: str | None = None,
    ) -> CreditTransaction:
        """Add credits to user balance."""
        user.credits_balance += amount

        transaction = CreditTransaction(
            id=cuid.cuid(),
            user_id=user.id,
            amount=amount,  # Positive for additions
            type=transaction_type,
            description=description,
            stripe_session_id=stripe_session_id,
        )
        db.add(transaction)
        await db.flush()
        return transaction

    async def get_transaction_history(
        self,
        db: AsyncSession,
        user_id: str,
        limit: int = 50,
        offset: int = 0,
    ) -> list[CreditTransaction]:
        """Get credit transaction history for a user."""
        result = await db.execute(
            select(CreditTransaction)
            .where(CreditTransaction.user_id == user_id)
            .order_by(CreditTransaction.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())

    def get_build_cost(self, build_type: str) -> int:
        """Get credit cost for a build type."""
        costs = {
            "quick": settings.credit_cost_quick_build,
            "standard": settings.credit_cost_standard_build,
            "full": settings.credit_cost_full_build,
        }
        return costs.get(build_type, settings.credit_cost_standard_build)

    async def process_marketplace_purchase(
        self,
        db: AsyncSession,
        buyer: User,
        seller: User,
        listing_id: str,
        price_credits: int,
    ) -> tuple[CreditTransaction, CreditTransaction]:
        """Process a marketplace purchase with platform commission."""
        platform_fee = int(price_credits * settings.platform_commission_rate)
        seller_earnings = price_credits - platform_fee

        # Deduct from buyer
        buyer_transaction = await self.deduct_credits(
            db=db,
            user=buyer,
            amount=price_credits,
            transaction_type="marketplace_purchase",
            description=f"Purchased bot listing {listing_id}",
        )

        # Add to seller (minus commission)
        seller_transaction = await self.add_credits(
            db=db,
            user=seller,
            amount=seller_earnings,
            transaction_type="marketplace_sale",
            description=f"Sale of bot listing {listing_id} (after {int(settings.platform_commission_rate * 100)}% commission)",
        )

        return buyer_transaction, seller_transaction
