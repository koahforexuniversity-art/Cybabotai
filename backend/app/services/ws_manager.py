"""WebSocket connection manager for real-time agent streaming."""

import json
from typing import Any
from fastapi import WebSocket
import structlog

logger = structlog.get_logger()


class ConnectionManager:
    """Manages WebSocket connections for real-time streaming."""

    def __init__(self) -> None:
        # Map of strategy_id -> WebSocket connection
        self.active_connections: dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, strategy_id: str) -> None:
        """Accept and register a WebSocket connection."""
        await websocket.accept()
        self.active_connections[strategy_id] = websocket
        logger.info("WebSocket connected", strategy_id=strategy_id)

    def disconnect(self, strategy_id: str) -> None:
        """Remove a WebSocket connection."""
        if strategy_id in self.active_connections:
            del self.active_connections[strategy_id]
            logger.info("WebSocket disconnected", strategy_id=strategy_id)

    async def send_message(self, strategy_id: str, message: dict[str, Any]) -> None:
        """Send a message to a specific strategy's WebSocket."""
        if strategy_id in self.active_connections:
            websocket = self.active_connections[strategy_id]
            try:
                await websocket.send_text(json.dumps(message))
            except Exception as e:
                logger.error("Failed to send WebSocket message", strategy_id=strategy_id, error=str(e))
                self.disconnect(strategy_id)

    async def send_agent_start(
        self,
        strategy_id: str,
        agent_id: int,
        message: str,
    ) -> None:
        """Send agent start notification."""
        await self.send_message(strategy_id, {
            "type": "agent_start",
            "agent_id": agent_id,
            "message": message,
            "data": {"progress": 0},
        })

    async def send_agent_progress(
        self,
        strategy_id: str,
        agent_id: int,
        message: str,
        progress: int = 0,
        data: dict[str, Any] | None = None,
    ) -> None:
        """Send agent progress update."""
        payload: dict[str, Any] = {
            "type": "agent_progress",
            "agent_id": agent_id,
            "message": message,
            "data": {"progress": progress, **(data or {})},
        }
        await self.send_message(strategy_id, payload)

    async def send_agent_complete(
        self,
        strategy_id: str,
        agent_id: int,
        message: str,
        data: dict[str, Any] | None = None,
    ) -> None:
        """Send agent completion notification."""
        payload: dict[str, Any] = {
            "type": "agent_complete",
            "agent_id": agent_id,
            "message": message,
            "data": {"progress": 100, **(data or {})},
        }
        await self.send_message(strategy_id, payload)

    async def send_agent_error(
        self,
        strategy_id: str,
        agent_id: int,
        message: str,
        error: str,
    ) -> None:
        """Send agent error notification."""
        await self.send_message(strategy_id, {
            "type": "agent_error",
            "agent_id": agent_id,
            "message": message,
            "data": {"error": error},
        })

    async def send_crew_complete(
        self,
        strategy_id: str,
        message: str,
        data: dict[str, Any] | None = None,
    ) -> None:
        """Send crew completion notification."""
        payload: dict[str, Any] = {
            "type": "crew_complete",
            "agent_id": 7,
            "message": message,
            "data": data or {},
        }
        await self.send_message(strategy_id, payload)

    async def send_equity_point(
        self,
        strategy_id: str,
        x: float,
        y: float,
    ) -> None:
        """Send a single equity curve data point (for live drawing)."""
        await self.send_agent_progress(
            strategy_id=strategy_id,
            agent_id=4,
            message="Running backtest...",
            data={"equity_point": {"x": x, "y": y}},
        )

    async def send_radar_data(
        self,
        strategy_id: str,
        radar_data: dict[str, float],
        metrics: dict[str, Any],
    ) -> None:
        """Send radar chart data for performance visualization."""
        await self.send_agent_progress(
            strategy_id=strategy_id,
            agent_id=5,
            message="Analyzing performance...",
            data={"radar_data": radar_data, "metrics": metrics},
        )

    def is_connected(self, strategy_id: str) -> bool:
        """Check if a strategy has an active WebSocket connection."""
        return strategy_id in self.active_connections


# Global connection manager instance
ws_manager = ConnectionManager()
