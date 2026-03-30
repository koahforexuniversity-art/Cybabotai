"""CrewAI tools for data operations — downloading, querying, and aggregating tick data."""

import asyncio
import json
from datetime import datetime
from typing import Any, Type

from crewai.tools import BaseTool
from pydantic import BaseModel, Field


class DownloadTickDataInput(BaseModel):
    """Input schema for tick data download."""

    symbol: str = Field(description="Forex pair symbol, e.g. EURUSD")
    start_date: str = Field(description="Start date in YYYY-MM-DD format")
    end_date: str = Field(description="End date in YYYY-MM-DD format")


class DownloadTickDataTool(BaseTool):
    """Download historical tick data from Dukascopy."""

    name: str = "download_tick_data"
    description: str = (
        "Downloads historical tick data from Dukascopy for a given forex pair "
        "and date range. Returns statistics about downloaded data."
    )
    args_schema: Type[BaseModel] = DownloadTickDataInput

    def _run(self, symbol: str, start_date: str, end_date: str) -> str:
        """Download tick data synchronously (wraps async)."""
        from data.dukascopy_downloader import DukascopyDownloader
        from data.duckdb_store import DuckDBStore

        try:
            downloader = DukascopyDownloader()
            store = DuckDBStore()

            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")

            # Run async download in event loop
            loop = asyncio.new_event_loop()
            try:
                count = loop.run_until_complete(
                    downloader.download_and_store(
                        symbol=symbol,
                        start_date=start_dt,
                        end_date=end_dt,
                        store=store,
                    )
                )
            finally:
                loop.close()

            # Get stats
            stats = store.get_data_stats(symbol)
            store.close()

            return json.dumps(
                {
                    "success": True,
                    "ticks_downloaded": count,
                    "symbol": symbol,
                    "stats": stats,
                },
                default=str,
            )

        except Exception as e:
            return json.dumps(
                {
                    "success": False,
                    "error": str(e),
                    "symbol": symbol,
                }
            )


class GetDataStatsInput(BaseModel):
    """Input for getting data statistics."""

    symbol: str = Field(description="Forex pair symbol, e.g. EURUSD")


class GetDataStatsTool(BaseTool):
    """Get statistics about stored tick data."""

    name: str = "get_data_stats"
    description: str = (
        "Returns statistics about stored tick data for a symbol, "
        "including total ticks, date range, and spread info."
    )
    args_schema: Type[BaseModel] = GetDataStatsInput

    def _run(self, symbol: str) -> str:
        """Get data stats."""
        from data.duckdb_store import DuckDBStore

        try:
            store = DuckDBStore()
            stats = store.get_data_stats(symbol)
            store.close()

            return json.dumps(stats, default=str)

        except Exception as e:
            return json.dumps({"error": str(e), "symbol": symbol})


class AggregateOHLCVInput(BaseModel):
    """Input for OHLCV aggregation."""

    symbol: str = Field(description="Forex pair symbol")
    timeframe: str = Field(
        description="Timeframe for bars: M1, M5, M15, M30, H1, H4, D1"
    )
    start_date: str = Field(description="Start date in YYYY-MM-DD format")
    end_date: str = Field(description="End date in YYYY-MM-DD format")


class AggregateOHLCVTool(BaseTool):
    """Aggregate tick data into OHLCV bars."""

    name: str = "aggregate_to_ohlcv"
    description: str = (
        "Aggregates stored tick data into OHLCV (candlestick) bars at a "
        "specified timeframe. Supports M1, M5, M15, M30, H1, H4, D1."
    )
    args_schema: Type[BaseModel] = AggregateOHLCVInput

    def _run(
        self,
        symbol: str,
        timeframe: str,
        start_date: str,
        end_date: str,
    ) -> str:
        """Aggregate ticks to OHLCV."""
        from data.duckdb_store import DuckDBStore

        try:
            store = DuckDBStore()
            count = store.aggregate_to_ohlcv(
                symbol=symbol,
                timeframe=timeframe,
                start_time=start_date,
                end_time=end_date,
            )

            # Get the bars
            bars = store.get_ohlcv(
                symbol=symbol,
                timeframe=timeframe,
                start_time=start_date,
                end_time=end_date,
            )
            store.close()

            return json.dumps(
                {
                    "success": True,
                    "bars_created": len(bars),
                    "symbol": symbol,
                    "timeframe": timeframe,
                    "sample_bars": bars[:5] if bars else [],
                },
                default=str,
            )

        except Exception as e:
            return json.dumps({"success": False, "error": str(e)})
