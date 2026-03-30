"""Credit management API endpoints."""

from fastapi import APIRouter, HTTPException, status, Request
from pydantic import BaseModel

from app.deps import DBSession, CurrentUser
from app.services.credit_service import CreditService
from app.services.stripe_service import StripeService, CREDIT_PACKS

router = APIRouter(prefix="/credits", tags=["credits"])
credit_service = CreditService()
stripe_service = StripeService()


class CheckoutRequest(BaseModel):
    pack_id: str
    success_url: str
    cancel_url: str


class CheckoutResponse(BaseModel):
    session_id: str
    url: str
    pack: dict


class TransactionResponse(BaseModel):
    id: str
    amount: int
    type: str
    description: str | None
    created_at: str


@router.get("/balance")
async def get_balance(current_user: CurrentUser) -> dict:
    """Get current user's credit balance."""
    return {
        "credits_balance": current_user.credits_balance,
        "user_id": current_user.id,
    }


@router.get("/packs")
async def get_credit_packs() -> dict:
    """Get available credit packs for purchase."""
    return {"packs": CREDIT_PACKS}


@router.post("/checkout", response_model=CheckoutResponse)
async def create_checkout(
    request: CheckoutRequest,
    current_user: CurrentUser,
) -> CheckoutResponse:
    """Create a Stripe checkout session for credit purchase."""
    if request.pack_id not in CREDIT_PACKS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid pack ID. Available: {list(CREDIT_PACKS.keys())}",
        )

    try:
        session = stripe_service.create_checkout_session(
            user_id=current_user.id,
            user_email=current_user.email,
            pack_id=request.pack_id,
            success_url=request.success_url,
            cancel_url=request.cancel_url,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create checkout session: {str(e)}",
        ) from e

    return CheckoutResponse(
        session_id=session["session_id"],
        url=session["url"],
        pack=session["pack"],
    )


@router.post("/webhook")
async def stripe_webhook(request: Request, db: DBSession) -> dict:
    """Handle Stripe webhook events."""
    payload = await request.body()
    signature = request.headers.get("stripe-signature", "")

    try:
        result = await stripe_service.handle_webhook(
            payload=payload,
            signature=signature,
            db=db,
        )
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.get("/transactions")
async def get_transactions(
    current_user: CurrentUser,
    db: DBSession,
    limit: int = 50,
    offset: int = 0,
) -> dict:
    """Get credit transaction history."""
    transactions = await credit_service.get_transaction_history(
        db=db,
        user_id=current_user.id,
        limit=limit,
        offset=offset,
    )

    return {
        "transactions": [
            {
                "id": t.id,
                "amount": t.amount,
                "type": t.type,
                "description": t.description,
                "created_at": t.created_at.isoformat(),
            }
            for t in transactions
        ],
        "total": len(transactions),
    }
