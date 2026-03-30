"""Marketplace API endpoints."""

import cuid
import json
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select, func

from app.deps import DBSession, CurrentUser
from app.models.marketplace import BotListing, BotPurchase, BotReview
from app.models.strategy import Strategy
from app.services.credit_service import CreditService

router = APIRouter(prefix="/marketplace", tags=["marketplace"])
credit_service = CreditService()


class CreateListingRequest(BaseModel):
    strategy_id: str
    title: str
    description: str
    category: str
    price_credits: int
    price_usd: float | None = None


class ReviewRequest(BaseModel):
    rating: int
    comment: str | None = None


@router.get("/listings")
async def get_listings(
    db: DBSession,
    category: str | None = None,
    sort_by: str = "created_at",
    limit: int = 20,
    offset: int = 0,
) -> dict:
    """Get marketplace listings."""
    query = select(BotListing).where(BotListing.active == True)  # noqa: E712

    if category:
        query = query.where(BotListing.category == category)

    if sort_by == "rating":
        query = query.order_by(BotListing.rating.desc())
    elif sort_by == "sales":
        query = query.order_by(BotListing.sales_count.desc())
    elif sort_by == "price_asc":
        query = query.order_by(BotListing.price_credits.asc())
    elif sort_by == "price_desc":
        query = query.order_by(BotListing.price_credits.desc())
    else:
        query = query.order_by(BotListing.created_at.desc())

    result = await db.execute(query.limit(limit).offset(offset))
    listings = result.scalars().all()

    return {
        "listings": [
            {
                "id": l.id,
                "title": l.title,
                "description": l.description[:200] + "..." if len(l.description) > 200 else l.description,
                "category": l.category,
                "price_credits": l.price_credits,
                "price_usd": l.price_usd,
                "sharpe_ratio": l.sharpe_ratio,
                "max_drawdown": l.max_drawdown,
                "win_rate": l.win_rate,
                "total_return": l.total_return,
                "sales_count": l.sales_count,
                "rating": l.rating,
                "review_count": l.review_count,
                "featured": l.featured,
                "thumbnail_url": l.thumbnail_url,
                "created_at": l.created_at.isoformat(),
            }
            for l in listings
        ],
        "total": len(listings),
    }


@router.get("/listings/{listing_id}")
async def get_listing(listing_id: str, db: DBSession) -> dict:
    """Get a specific marketplace listing."""
    result = await db.execute(
        select(BotListing).where(BotListing.id == listing_id, BotListing.active == True)  # noqa: E712
    )
    listing = result.scalar_one_or_none()

    if not listing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Listing not found")

    # Get strategy details
    strategy_result = await db.execute(
        select(Strategy).where(Strategy.id == listing.strategy_id)
    )
    strategy = strategy_result.scalar_one_or_none()

    return {
        "id": listing.id,
        "title": listing.title,
        "description": listing.description,
        "category": listing.category,
        "price_credits": listing.price_credits,
        "price_usd": listing.price_usd,
        "sharpe_ratio": listing.sharpe_ratio,
        "max_drawdown": listing.max_drawdown,
        "win_rate": listing.win_rate,
        "total_return": listing.total_return,
        "sales_count": listing.sales_count,
        "rating": listing.rating,
        "review_count": listing.review_count,
        "featured": listing.featured,
        "thumbnail_url": listing.thumbnail_url,
        "equity_curve_url": listing.equity_curve_url,
        "backtest_results": json.loads(strategy.backtest_results) if strategy and strategy.backtest_results else None,
        "created_at": listing.created_at.isoformat(),
    }


@router.post("/listings", status_code=status.HTTP_201_CREATED)
async def create_listing(
    request: CreateListingRequest,
    current_user: CurrentUser,
    db: DBSession,
) -> dict:
    """Create a new marketplace listing."""
    # Verify strategy belongs to user and is completed
    strategy_result = await db.execute(
        select(Strategy).where(
            Strategy.id == request.strategy_id,
            Strategy.user_id == current_user.id,
            Strategy.status == "completed",
        )
    )
    strategy = strategy_result.scalar_one_or_none()

    if not strategy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Strategy not found or not completed",
        )

    # Check if already listed
    existing_result = await db.execute(
        select(BotListing).where(BotListing.strategy_id == request.strategy_id)
    )
    if existing_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Strategy is already listed",
        )

    # Deduct listing fee
    from app.config import get_settings
    settings = get_settings()
    await credit_service.deduct_credits(
        db=db,
        user=current_user,
        amount=settings.credit_cost_marketplace_listing,
        transaction_type="marketplace_listing",
        description=f"Listed bot: {request.title}",
        related_strategy_id=request.strategy_id,
    )

    # Extract performance metrics from backtest results
    backtest = json.loads(strategy.backtest_results) if strategy.backtest_results else {}

    listing = BotListing(
        id=cuid.cuid(),
        seller_id=current_user.id,
        strategy_id=request.strategy_id,
        title=request.title,
        description=request.description,
        category=request.category,
        price_credits=request.price_credits,
        price_usd=request.price_usd,
        sharpe_ratio=backtest.get("sharpe_ratio"),
        max_drawdown=backtest.get("max_drawdown_pct"),
        win_rate=backtest.get("win_rate"),
        total_return=backtest.get("total_return_pct"),
    )
    db.add(listing)
    await db.flush()

    return {
        "id": listing.id,
        "title": listing.title,
        "status": "active",
        "created_at": listing.created_at.isoformat(),
    }


@router.post("/listings/{listing_id}/purchase")
async def purchase_listing(
    listing_id: str,
    current_user: CurrentUser,
    db: DBSession,
) -> dict:
    """Purchase a bot listing."""
    # Get listing
    listing_result = await db.execute(
        select(BotListing).where(BotListing.id == listing_id, BotListing.active == True)  # noqa: E712
    )
    listing = listing_result.scalar_one_or_none()

    if not listing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Listing not found")

    if listing.seller_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot purchase your own listing",
        )

    # Check if already purchased
    purchase_result = await db.execute(
        select(BotPurchase).where(
            BotPurchase.buyer_id == current_user.id,
            BotPurchase.listing_id == listing_id,
        )
    )
    if purchase_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Already purchased this listing",
        )

    # Get seller
    from app.models.user import User
    seller_result = await db.execute(select(User).where(User.id == listing.seller_id))
    seller = seller_result.scalar_one_or_none()

    if not seller:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Seller not found")

    # Process purchase
    from app.config import get_settings
    settings = get_settings()
    platform_fee = int(listing.price_credits * settings.platform_commission_rate)
    seller_earnings = listing.price_credits - platform_fee

    buyer_tx, seller_tx = await credit_service.process_marketplace_purchase(
        db=db,
        buyer=current_user,
        seller=seller,
        listing_id=listing_id,
        price_credits=listing.price_credits,
    )

    # Create purchase record
    purchase = BotPurchase(
        id=cuid.cuid(),
        buyer_id=current_user.id,
        listing_id=listing_id,
        credits_paid=listing.price_credits,
        platform_fee=platform_fee,
        seller_earnings=seller_earnings,
    )
    db.add(purchase)

    # Update sales count
    listing.sales_count += 1
    await db.flush()

    return {
        "purchase_id": purchase.id,
        "listing_id": listing_id,
        "credits_paid": listing.price_credits,
        "message": "Purchase successful! Check your strategy library.",
    }


@router.post("/listings/{listing_id}/reviews")
async def add_review(
    listing_id: str,
    request: ReviewRequest,
    current_user: CurrentUser,
    db: DBSession,
) -> dict:
    """Add a review to a listing."""
    if not 1 <= request.rating <= 5:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Rating must be between 1 and 5",
        )

    # Check if listing exists
    listing_result = await db.execute(
        select(BotListing).where(BotListing.id == listing_id)
    )
    listing = listing_result.scalar_one_or_none()

    if not listing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Listing not found")

    # Check if user purchased this listing
    purchase_result = await db.execute(
        select(BotPurchase).where(
            BotPurchase.buyer_id == current_user.id,
            BotPurchase.listing_id == listing_id,
        )
    )
    if not purchase_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Must purchase before reviewing",
        )

    # Create or update review
    review = BotReview(
        id=cuid.cuid(),
        listing_id=listing_id,
        user_id=current_user.id,
        rating=request.rating,
        comment=request.comment,
    )
    db.add(review)

    # Update listing rating
    listing.review_count += 1
    # Simple average (in production, recalculate from all reviews)
    listing.rating = (listing.rating * (listing.review_count - 1) + request.rating) / listing.review_count
    await db.flush()

    return {
        "review_id": review.id,
        "rating": request.rating,
        "message": "Review submitted successfully",
    }
