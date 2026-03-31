"""Paystack payment integration service."""

from typing import Any
import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.config import get_settings
from app.models.user import User
from app.services.credit_service import CreditService
import structlog

settings = get_settings()
logger = structlog.get_logger()

PAYSTACK_API = "https://api.paystack.co"

# Credit pack definitions — prices in kobo (NGN × 100) for Paystack
CREDIT_PACKS = {
    "starter":    {"price_kobo": 500000,  "price_display": "₦5,000",  "credits": 500,   "name": "Starter Pack"},
    "builder":    {"price_kobo": 1000000, "price_display": "₦10,000", "credits": 2000,  "name": "Builder Pack",  "popular": True},
    "pro":        {"price_kobo": 2500000, "price_display": "₦25,000", "credits": 6000,  "name": "Pro Pack",      "bonus": 1000},
    "enterprise": {"price_kobo": 5000000, "price_display": "₦50,000", "credits": 15000, "name": "Enterprise Pack","bonus": 3000},
}


class PaystackService:
    """Service for Paystack payment processing."""

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {settings.paystack_secret_key}",
            "Content-Type": "application/json",
        }

    def is_configured(self) -> bool:
        return bool(
            settings.paystack_secret_key
            and not settings.paystack_secret_key.startswith("sk_test_REPLACE")
        )

    async def initialize_transaction(
        self,
        user_id: str,
        user_email: str,
        pack_id: str,
        callback_url: str,
    ) -> dict[str, Any]:
        """Initialize a Paystack transaction and return the authorization URL."""
        if pack_id not in CREDIT_PACKS:
            raise ValueError(f"Invalid pack ID: {pack_id}")

        pack = CREDIT_PACKS[pack_id]
        total_credits = pack["credits"] + pack.get("bonus", 0)

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{PAYSTACK_API}/transaction/initialize",
                headers=self._headers(),
                json={
                    "email": user_email,
                    "amount": pack["price_kobo"],
                    "currency": "NGN",
                    "callback_url": callback_url,
                    "metadata": {
                        "user_id": user_id,
                        "pack_id": pack_id,
                        "credits": total_credits,
                        "pack_name": pack["name"],
                    },
                },
                timeout=30.0,
            )
            response.raise_for_status()
            data = response.json()

        if not data.get("status"):
            raise ValueError(data.get("message", "Paystack initialization failed"))

        return {
            "authorization_url": data["data"]["authorization_url"],
            "reference": data["data"]["reference"],
            "pack": pack,
        }

    async def verify_transaction(
        self,
        reference: str,
        db: AsyncSession,
    ) -> dict[str, Any]:
        """Verify a Paystack transaction and credit the user."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{PAYSTACK_API}/transaction/verify/{reference}",
                headers=self._headers(),
                timeout=30.0,
            )
            response.raise_for_status()
            data = response.json()

        if not data.get("status"):
            raise ValueError("Transaction verification failed")

        tx = data["data"]
        if tx["status"] != "success":
            raise ValueError(f"Payment not successful: {tx['status']}")

        metadata = tx.get("metadata", {})
        user_id = metadata.get("user_id")
        credits = int(metadata.get("credits", 0))
        pack_name = metadata.get("pack_name", "Credit Pack")

        if not user_id or not credits:
            raise ValueError("Invalid transaction metadata")

        # Check if already processed (idempotency)
        from app.models.credit import CreditTransaction
        existing = await db.execute(
            select(CreditTransaction).where(
                CreditTransaction.stripe_session_id == reference
            )
        )
        if existing.scalar_one_or_none():
            return {"status": "already_processed", "credits": credits}

        # Get user and add credits
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            raise ValueError(f"User not found: {user_id}")

        credit_service = CreditService()
        await credit_service.add_credits(
            db=db,
            user=user,
            amount=credits,
            transaction_type="purchase",
            description=f"Purchased {pack_name} ({credits:,} credits)",
            stripe_session_id=reference,  # reusing field for Paystack reference
        )
        await db.commit()

        logger.info("Credits added", user_id=user_id, credits=credits, reference=reference)
        return {"status": "success", "credits": credits, "user_id": user_id}


paystack_service = PaystackService()
