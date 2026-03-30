"""WebSocket endpoint for real-time agent streaming."""

import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import AsyncSessionLocal
from app.models.user import User
from app.services.auth_service import AuthService
from app.services.ws_manager import ws_manager
import structlog

router = APIRouter(tags=["websocket"])
auth_service = AuthService()
logger = structlog.get_logger()


@router.websocket("/ws/{strategy_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    strategy_id: str,
    token: str = Query(...),
) -> None:
    """WebSocket endpoint for real-time strategy building updates."""
    # Authenticate the WebSocket connection
    try:
        payload = auth_service.decode_token(token)
        user_id = payload.get("sub", "")
        if not user_id:
            await websocket.close(code=4001, reason="Invalid token")
            return
    except Exception:
        await websocket.close(code=4001, reason="Authentication failed")
        return

    # Verify user exists
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            await websocket.close(code=4001, reason="User not found")
            return

    # Connect to WebSocket manager
    await ws_manager.connect(websocket, strategy_id)
    logger.info("WebSocket connected", strategy_id=strategy_id, user_id=user_id)

    try:
        # Keep connection alive and handle incoming messages
        while True:
            try:
                data = await websocket.receive_text()
                message = json.loads(data)

                # Handle ping/pong for keepalive
                if message.get("type") == "ping":
                    await websocket.send_text(json.dumps({"type": "pong"}))

            except WebSocketDisconnect:
                break
            except json.JSONDecodeError:
                logger.warning("Invalid JSON received", strategy_id=strategy_id)
                continue

    except Exception as e:
        logger.error("WebSocket error", strategy_id=strategy_id, error=str(e))
    finally:
        ws_manager.disconnect(strategy_id)
        logger.info("WebSocket disconnected", strategy_id=strategy_id)
