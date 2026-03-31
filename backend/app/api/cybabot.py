"""Cybabot bot builder API endpoints."""

import json
import asyncio
import cuid
from fastapi import APIRouter, HTTPException, status, BackgroundTasks
from pydantic import BaseModel
from sqlalchemy import select

from app.deps import DBSession, CurrentUser
from app.models.strategy import Strategy
from app.services.credit_service import CreditService
from app.services.ws_manager import ws_manager
import structlog

router = APIRouter(prefix="/cybabot", tags=["cybabot"])
credit_service = CreditService()
logger = structlog.get_logger()


class BuildRequest(BaseModel):
    name: str
    input_text: str | None = None
    input_type: str = "text"  # text, image, pdf, url
    llm_provider: str = "claude"
    llm_model: str | None = None
    build_type: str = "standard"  # quick, standard, full
    backtest_config: dict | None = None


class StrategyResponse(BaseModel):
    id: str
    name: str
    status: str
    progress: int
    build_type: str
    credits_cost: int
    created_at: str


@router.post("/build", response_model=StrategyResponse, status_code=status.HTTP_201_CREATED)
async def start_build(
    request: BuildRequest,
    current_user: CurrentUser,
    db: DBSession,
    background_tasks: BackgroundTasks,
) -> StrategyResponse:
    """Start a new strategy build."""
    from ai.cybabot.llm_router import llm_router

    # Pre-flight: validate LLM provider key before deducting credits
    if not llm_router._check_provider_key(request.llm_provider):
        provider_key_map = {
            "claude": "ANTHROPIC_API_KEY",
            "grok": "XAI_API_KEY",
            "deepseek": "DEEPSEEK_API_KEY",
            "gemini": "GOOGLE_API_KEY",
        }
        key_name = provider_key_map.get(request.llm_provider, f"{request.llm_provider.upper()}_API_KEY")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"{key_name} is not configured on the server. Add it to the backend .env file.",
        )

    # Calculate credit cost
    credits_cost = credit_service.get_build_cost(request.build_type)

    # Deduct credits
    await credit_service.deduct_credits(
        db=db,
        user=current_user,
        amount=credits_cost,
        transaction_type=f"usage_{request.build_type}",
        description=f"Strategy build: {request.name} ({request.build_type})",
    )

    # Create strategy record
    strategy = Strategy(
        id=cuid.cuid(),
        user_id=current_user.id,
        name=request.name,
        input_type=request.input_type,
        input_data=request.input_text,
        llm_provider=request.llm_provider,
        llm_model=request.llm_model or "default",
        status="processing",
        progress=0,
        build_type=request.build_type,
        credits_cost=credits_cost,
        config=json.dumps(request.backtest_config or {}),
    )
    db.add(strategy)
    await db.flush()

    strategy_id = strategy.id

    # Start background build task
    background_tasks.add_task(
        run_build_task,
        strategy_id=strategy_id,
        user_input=request.input_text or "",
        input_type=request.input_type,
        llm_provider=request.llm_provider,
        llm_model=request.llm_model,
        build_type=request.build_type,
        backtest_config=request.backtest_config,
    )

    return StrategyResponse(
        id=strategy.id,
        name=strategy.name,
        status=strategy.status,
        progress=strategy.progress,
        build_type=strategy.build_type,
        credits_cost=strategy.credits_cost,
        created_at=strategy.created_at.isoformat(),
    )


async def run_build_task(
    strategy_id: str,
    user_input: str,
    input_type: str,
    llm_provider: str,
    llm_model: str | None,
    build_type: str,
    backtest_config: dict | None,
) -> None:
    """Background task to run the Cybabot crew."""
    from app.database import AsyncSessionLocal
    from app.models.strategy import Strategy as StrategyModel
    from ai.cybabot.crew import CybabotCrew

    async def progress_callback(
        agent_id: int,
        event_type: str,
        message: str,
        data: dict,
    ) -> None:
        """Send progress updates via WebSocket."""
        await ws_manager.send_message(strategy_id, {
            "type": event_type,
            "agent_id": agent_id,
            "message": message,
            "data": data,
        })

    try:
        # Create and run crew
        crew = CybabotCrew(
            provider=llm_provider,
            model=llm_model,
            build_type=build_type,
            progress_callback=progress_callback,
        )

        results = await crew.run(
            user_input=user_input,
            input_type=input_type,
            backtest_config=backtest_config,
        )

        # Update strategy with results
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(StrategyModel).where(StrategyModel.id == strategy_id)
            )
            strategy = result.scalar_one_or_none()
            if strategy:
                strategy.status = "completed"
                strategy.progress = 100
                strategy.backtest_results = json.dumps(results.get("backtest_results") or {})
                strategy.equity_curve = json.dumps(
                    results.get("backtest_results", {}).get("equity_curve", [])
                    if results.get("backtest_results") else []
                )
                strategy.exports = json.dumps(results.get("exports") or {})
                await db.commit()

        # Send completion notification
        await ws_manager.send_crew_complete(
            strategy_id=strategy_id,
            message="🤖 Strategy build complete! Your bot is ready.",
            data={
                "strategy_id": strategy_id,
                "exports": results.get("exports"),
                "metrics": results.get("backtest_results"),
            },
        )

    except Exception as e:
        logger.error("Build task failed", strategy_id=strategy_id, error=str(e))

        # Update strategy with error
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(StrategyModel).where(StrategyModel.id == strategy_id)
            )
            strategy = result.scalar_one_or_none()
            if strategy:
                strategy.status = "failed"
                strategy.error_message = str(e)
                await db.commit()

        # Send error notification
        await ws_manager.send_message(strategy_id, {
            "type": "crew_error",
            "agent_id": 0,
            "message": f"Build failed: {str(e)}",
            "data": {"error": str(e)},
        })


@router.get("/strategies", response_model=list[StrategyResponse])
async def get_strategies(
    current_user: CurrentUser,
    db: DBSession,
    limit: int = 20,
    offset: int = 0,
) -> list[StrategyResponse]:
    """Get user's strategy history."""
    result = await db.execute(
        select(Strategy)
        .where(Strategy.user_id == current_user.id)
        .order_by(Strategy.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    strategies = result.scalars().all()

    return [
        StrategyResponse(
            id=s.id,
            name=s.name,
            status=s.status,
            progress=s.progress,
            build_type=s.build_type,
            credits_cost=s.credits_cost,
            created_at=s.created_at.isoformat(),
        )
        for s in strategies
    ]


@router.get("/strategies/{strategy_id}")
async def get_strategy(
    strategy_id: str,
    current_user: CurrentUser,
    db: DBSession,
) -> dict:
    """Get a specific strategy with full details."""
    result = await db.execute(
        select(Strategy).where(
            Strategy.id == strategy_id,
            Strategy.user_id == current_user.id,
        )
    )
    strategy = result.scalar_one_or_none()

    if not strategy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Strategy not found",
        )

    return {
        "id": strategy.id,
        "name": strategy.name,
        "description": strategy.description,
        "status": strategy.status,
        "progress": strategy.progress,
        "build_type": strategy.build_type,
        "credits_cost": strategy.credits_cost,
        "llm_provider": strategy.llm_provider,
        "llm_model": strategy.llm_model,
        "config": json.loads(strategy.config) if strategy.config else {},
        "backtest_results": json.loads(strategy.backtest_results) if strategy.backtest_results else None,
        "equity_curve": json.loads(strategy.equity_curve) if strategy.equity_curve else [],
        "exports": json.loads(strategy.exports) if strategy.exports else {},
        "error_message": strategy.error_message,
        "created_at": strategy.created_at.isoformat(),
        "updated_at": strategy.updated_at.isoformat(),
    }
