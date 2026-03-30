"""Admin API endpoints."""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select, func

from app.deps import DBSession, CurrentAdmin
from app.models.user import User
from app.models.strategy import Strategy
from app.models.marketplace import BotListing, BotPurchase
from app.models.credit import CreditTransaction

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/stats")
async def get_stats(current_admin: CurrentAdmin, db: DBSession) -> dict:
    """Get platform statistics."""
    # User stats
    user_count_result = await db.execute(select(func.count(User.id)))
    user_count = user_count_result.scalar() or 0

    # Strategy stats
    strategy_count_result = await db.execute(select(func.count(Strategy.id)))
    strategy_count = strategy_count_result.scalar() or 0

    completed_result = await db.execute(
        select(func.count(Strategy.id)).where(Strategy.status == "completed")
    )
    completed_count = completed_result.scalar() or 0

    # Marketplace stats
    listing_count_result = await db.execute(select(func.count(BotListing.id)))
    listing_count = listing_count_result.scalar() or 0

    purchase_count_result = await db.execute(select(func.count(BotPurchase.id)))
    purchase_count = purchase_count_result.scalar() or 0

    # Revenue stats
    revenue_result = await db.execute(
        select(func.sum(CreditTransaction.amount)).where(
            CreditTransaction.type == "purchase",
            CreditTransaction.amount > 0,
        )
    )
    total_credits_sold = revenue_result.scalar() or 0

    return {
        "users": {
            "total": user_count,
        },
        "strategies": {
            "total": strategy_count,
            "completed": completed_count,
            "success_rate": round(completed_count / max(strategy_count, 1) * 100, 1),
        },
        "marketplace": {
            "listings": listing_count,
            "purchases": purchase_count,
        },
        "credits": {
            "total_sold": total_credits_sold,
        },
    }


@router.get("/users")
async def get_users(
    current_admin: CurrentAdmin,
    db: DBSession,
    limit: int = 50,
    offset: int = 0,
) -> dict:
    """Get all users."""
    result = await db.execute(
        select(User).order_by(User.created_at.desc()).limit(limit).offset(offset)
    )
    users = result.scalars().all()

    return {
        "users": [
            {
                "id": u.id,
                "email": u.email,
                "name": u.name,
                "credits_balance": u.credits_balance,
                "role": u.role,
                "is_active": u.is_active,
                "created_at": u.created_at.isoformat(),
            }
            for u in users
        ],
        "total": len(users),
    }


class UpdateUserRequest(BaseModel):
    credits_balance: int | None = None
    role: str | None = None
    is_active: bool | None = None


@router.patch("/users/{user_id}")
async def update_user(
    user_id: str,
    request: UpdateUserRequest,
    current_admin: CurrentAdmin,
    db: DBSession,
) -> dict:
    """Update a user's settings."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if request.credits_balance is not None:
        user.credits_balance = request.credits_balance
    if request.role is not None:
        user.role = request.role
    if request.is_active is not None:
        user.is_active = request.is_active

    await db.flush()

    return {
        "id": user.id,
        "email": user.email,
        "credits_balance": user.credits_balance,
        "role": user.role,
        "is_active": user.is_active,
    }


@router.patch("/listings/{listing_id}/feature")
async def toggle_featured(
    listing_id: str,
    current_admin: CurrentAdmin,
    db: DBSession,
) -> dict:
    """Toggle featured status of a listing."""
    result = await db.execute(select(BotListing).where(BotListing.id == listing_id))
    listing = result.scalar_one_or_none()

    if not listing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Listing not found")

    listing.featured = not listing.featured
    await db.flush()

    return {
        "id": listing.id,
        "featured": listing.featured,
    }


@router.delete("/listings/{listing_id}")
async def deactivate_listing(
    listing_id: str,
    current_admin: CurrentAdmin,
    db: DBSession,
) -> dict:
    """Deactivate a marketplace listing."""
    result = await db.execute(select(BotListing).where(BotListing.id == listing_id))
    listing = result.scalar_one_or_none()

    if not listing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Listing not found")

    listing.active = False
    await db.flush()

    return {"message": "Listing deactivated"}
