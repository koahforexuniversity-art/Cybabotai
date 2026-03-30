"""DuckDB storage layer for tick data.

Provides fast columnar storage and querying for forex tick data.
"""

from typing import Any
from pathlib import Path
import duckdb
import structlog

logger = structlog.get_logger()

DB_PATH = Path(__file__).parent / "raw" / "ticks.duckdb"


class DuckDBStore:
    """DuckDB-based tick data storage."""

    def __init__(self, db_path: str | Path | None = None) -> None:
        self.db_path = str(db_path or DB_PATH)
        self._conn: duckdb.DuckDBPyConnection | None = None

    def connect(self) -> duckdb.DuckDBPyConnection:
        """Get or create database connection."""
        if self._conn is None:
            Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
            self._conn = duckdb.connect(self.db_path)
            self._init_tables()
        return self._conn

    def _init_tables(self) -> None:
        """Initialize database tables."""
        conn = self._conn
        if conn is None:
            return

        conn.execute("""
            CREATE TABLE IF NOT EXISTS ticks (
                symbol VARCHAR NOT NULL,
                timestamp TIMESTAMP NOT NULL,
                bid DOUBLE NOT NULL,
                ask DOUBLE NOT NULL,
                bid_volume DOUBLE DEFAULT 0,
                ask_volume DOUBLE DEFAULT 0
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS ohlcv (
                symbol VARCHAR NOT NULL,
                timeframe VARCHAR NOT NULL,
                timestamp TIMESTAMP NOT NULL,
                open DOUBLE NOT NULL,
                high DOUBLE NOT NULL,
                low DOUBLE NOT NULL,
                close DOUBLE NOT NULL,
                volume DOUBLE DEFAULT 0,
                tick_count INTEGER DEFAULT 0
            )
        """)

        # Create indexes for fast querying
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_ticks_symbol_time 
            ON ticks(symbol, timestamp)
        """)

        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_ohlcv_symbol_tf_time 
            ON ohlcv(symbol, timeframe, timestamp)
        """)

    def insert_ticks(
        self,
        symbol: str,
        ticks: list[dict[str, Any]],
    ) -> int:
        """Insert tick data into the database."""
        conn = self.connect()

        if not ticks:
            return 0

        # Use batch insert for performance
        values = [
            (
                symbol,
                t["timestamp"],
                t["bid"],
                t["ask"],
                t.get("bid_volume", 0),
                t.get("ask_volume", 0),
            )
            for t in ticks
        ]

        conn.executemany(
            "INSERT INTO ticks VALUES (?, ?, ?, ?, ?, ?)",
            values,
        )

        logger.info("Inserted ticks", symbol=symbol, count=len(values))
        return len(values)

    def get_ticks(
        self,
        symbol: str,
        start_time: str,
        end_time: str,
        limit: int | None = None,
    ) -> list[dict[str, Any]]:
        """Query tick data."""
        conn = self.connect()

        query = """
            SELECT timestamp, bid, ask, bid_volume, ask_volume
            FROM ticks
            WHERE symbol = ? AND timestamp >= ? AND timestamp <= ?
            ORDER BY timestamp
        """
        params: list[Any] = [symbol, start_time, end_time]

        if limit:
            query += " LIMIT ?"
            params.append(limit)

        result = conn.execute(query, params).fetchall()

        return [
            {
                "timestamp": row[0],
                "bid": row[1],
                "ask": row[2],
                "bid_volume": row[3],
                "ask_volume": row[4],
            }
            for row in result
        ]

    def aggregate_to_ohlcv(
        self,
        symbol: str,
        timeframe: str,
        start_time: str,
        end_time: str,
    ) -> int:
        """Aggregate tick data to OHLCV bars."""
        conn = self.connect()

        # Map timeframe to interval
        interval_map = {
            "M1": "1 minute",
            "M5": "5 minutes",
            "M15": "15 minutes",
            "M30": "30 minutes",
            "H1": "1 hour",
            "H4": "4 hours",
            "D1": "1 day",
        }
        interval = interval_map.get(timeframe, "1 hour")

        query = f"""
            INSERT INTO ohlcv (symbol, timeframe, timestamp, open, high, low, close, volume, tick_count)
            SELECT 
                '{symbol}' as symbol,
                '{timeframe}' as timeframe,
                time_bucket(INTERVAL '{interval}', timestamp) as bar_time,
                FIRST(bid) as open,
                MAX(bid) as high,
                MIN(bid) as low,
                LAST(bid) as close,
                SUM(bid_volume) as volume,
                COUNT(*) as tick_count
            FROM ticks
            WHERE symbol = ? AND timestamp >= ? AND timestamp <= ?
            GROUP BY bar_time
            ORDER BY bar_time
        """

        result = conn.execute(query, [symbol, start_time, end_time])
        count = result.fetchone()
        return count[0] if count else 0

    def get_ohlcv(
        self,
        symbol: str,
        timeframe: str,
        start_time: str,
        end_time: str,
    ) -> list[dict[str, Any]]:
        """Get OHLCV data."""
        conn = self.connect()

        result = conn.execute(
            """
            SELECT timestamp, open, high, low, close, volume, tick_count
            FROM ohlcv
            WHERE symbol = ? AND timeframe = ? AND timestamp >= ? AND timestamp <= ?
            ORDER BY timestamp
            """,
            [symbol, timeframe, start_time, end_time],
        ).fetchall()

        return [
            {
                "timestamp": row[0],
                "open": row[1],
                "high": row[2],
                "low": row[3],
                "close": row[4],
                "volume": row[5],
                "tick_count": row[6],
            }
            for row in result
        ]

    def get_data_stats(self, symbol: str) -> dict[str, Any]:
        """Get statistics about stored tick data for a symbol."""
        conn = self.connect()

        result = conn.execute(
            """
            SELECT 
                COUNT(*) as total_ticks,
                MIN(timestamp) as earliest,
                MAX(timestamp) as latest,
                AVG(ask - bid) as avg_spread,
                MIN(ask - bid) as min_spread,
                MAX(ask - bid) as max_spread
            FROM ticks
            WHERE symbol = ?
            """,
            [symbol],
        ).fetchone()

        if not result or result[0] == 0:
            return {"symbol": symbol, "total_ticks": 0, "has_data": False}

        return {
            "symbol": symbol,
            "total_ticks": result[0],
            "earliest": str(result[1]),
            "latest": str(result[2]),
            "avg_spread": result[3],
            "min_spread": result[4],
            "max_spread": result[5],
            "has_data": True,
        }

    def close(self) -> None:
        """Close database connection."""
        if self._conn:
            self._conn.close()
            self._conn = None
