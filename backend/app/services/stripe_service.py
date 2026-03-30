"""Stripe payment integration service."""

from typing import Any
import stripe
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.config import get_settings
from app.models.user import User
from app.services.credit_service import CreditService

settings = get_settings()

# Credit pack definitions
CREDIT_PACKS = {
    "starter": {"price_usd": 500, "credits": 500, "name": "Starter Pack"},      # $5.00
    "builder": {"price_usd": 1000, "credits": 2000, "name": "Builder Pack"},    # $10.00
    "pro": {"price_usd": 2500, "credits": 6000, "name": "Pro Pack"},            # $25.00
    "enterprise": {"price_usd": 5000, "credits": 15000, "name": "Enterprise Pack"},  # $50.00
}


class StripeService:
    """Service for Stripe payment processing."""

    def __init__(self) -> None:
        if settings.stripe_secret_key:
            stripe.api_key = settings.stripe_secret_key

    def create_checkout_session(
        self,
        user_id: str,
        user_email: str,
        pack_id: str,
        success_url: str,
        cancel_url: str,
    ) -> dict[str, Any]:
        """Create a Stripe checkout session for credit purchase."""
        if pack_id not in CREDIT_PACKS:
            raise ValueError(f"Invalid pack ID: {pack_id}")

        pack = CREDIT_PACKS[pack_id]

        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": "usd",
                        "product_data": {
                            "name": pack["name"],
                            "description": f"{pack['credits']:,} credits for Cybabot Ultra",
                        },
                        "unit_amount": pack["price_usd"],
                    },
                    "quantity": 1,
                }
            ],
            mode="payment",
            success_url=success_url,
            cancel_url=cancel_url,
            customer_email=user_email,
            metadata={
                "user_id": user_id,
                "pack_id": pack_id,
                "credits": str(pack["credits"]),
            },
        )

        return {
            "session_id": session.id,
            "url": session.url,
            "pack": pack,
        }

    async def handle_webhook(
        self,
        payload: bytes,
        signature: str,
        db: AsyncSession,
    ) -> dict[str, Any]:
        """Handle Stripe webhook events."""
        if not settings.stripe_webhook_secret:
            raise ValueError("Stripe webhook secret not configured")

        try:
            event = stripe.Webhook.construct_event(
                payload, signature, settings.stripe_webhook_secret
            )
        except stripe.error.SignatureVerificationError as e:
            raise ValueError(f"Invalid webhook signature: {e}") from e

        if event["type"] == "checkout.session.completed":
            session = event["data"]["object"]
            await self._handle_successful_payment(session, db)

        return {"status": "processed", "event_type": event["type"]}

    async def _handle_successful_payment(
        self,
        session: dict[str, Any],
        db: AsyncSession,
    ) -> None:
        """Process a successful payment and add credits."""
        metadata = session.get("metadata", {})
        user_id = metadata.get("user_id")
        pack_id = metadata.get("pack_id")
        credits = int(metadata.get("credits", 0))

        if not user_id or not credits:
            return

        # Get user
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            return

        # Add credits
        credit_service = CreditService()
        await credit_service.add_credits(
            db=db,
            user=user,
            amount=credits,
            transaction_type="purchase",
            description=f"Purchased {CREDIT_PACKS.get(pack_id, {}).get('name', 'credit pack')}",
            stripe_session_id=session.get("id"),
        )
        await db.commit()

    def get_credit_packs(self) -> dict[str, Any]:
        """Get available credit packs."""
        return CREDIT_PACKS
