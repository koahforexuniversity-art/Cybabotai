"""Credit management API endpoints."""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from app.deps import DBSession, CurrentUser
from app.services.credit_service import CreditService
from app.services.paystack_service import paystack_service, CREDIT_PACKS
from app.config import get_settings

router = APIRouter(prefix="/credits", tags=["credits"])
credit_service = CreditService()
settings = get_settings()


class CheckoutRequest(BaseModel):
    pack_id: str
    callback_url: str


class CheckoutResponse(BaseModel):
    authorization_url: str
    reference: str
    pack: dict


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
    return {
        "packs": CREDIT_PACKS,
        "paystack_public_key": settings.paystack_public_key,
    }


@router.post("/checkout", response_model=CheckoutResponse)
async def create_checkout(
    request: CheckoutRequest,
    current_user: CurrentUser,
) -> CheckoutResponse:
    """Initialize a Paystack transaction for credit purchase."""
    if not paystack_service.is_configured():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Payment service not configured. Add PAYSTACK_SECRET_KEY to backend .env",
        )

    if request.pack_id not in CREDIT_PACKS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid pack ID. Available: {list(CREDIT_PACKS.keys())}",
        )

    try:
        result = await paystack_service.initialize_transaction(
            user_id=current_user.id,
            user_email=current_user.email,
            pack_id=request.pack_id,
            callback_url=request.callback_url,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Payment initialization failed: {str(e)}",
        ) from e

    return CheckoutResponse(
        authorization_url=result["authorization_url"],
        reference=result["reference"],
        pack=result["pack"],
    )


@router.get("/verify")
async def verify_payment(
    reference: str,
    db: DBSession,
) -> dict:
    """Verify a Paystack payment and credit the user. Called after Paystack redirect."""
    try:
        result = await paystack_service.verify_transaction(reference=reference, db=db)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Verification failed: {str(e)}",
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
