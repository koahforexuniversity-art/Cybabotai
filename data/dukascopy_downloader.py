"""Dukascopy tick data downloader.

Downloads historical tick data from Dukascopy's free data feed.
Data is downloaded as compressed binary (bi5) files, decompressed,
and parsed into tick records.

Dukascopy URL pattern:
  https://datafeed.dukascopy.com/datafeed/{SYMBOL}/{YYYY}/{MM-1}/{DD}/{HH}h_ticks.bi5

Note: Dukascopy months are 0-indexed (January = 00).
"""

import struct
import asyncio
import logging
from datetime import datetime, timedelta
from io import BytesIO
from pathlib import Path
from typing import Any

import httpx
import lzma

logger = logging.getLogger(__name__)

DUKASCOPY_BASE_URL = "https://datafeed.dukascopy.com/datafeed"

# Pip size lookup for major pairs
PIP_SIZES: dict[str, float] = {
    "EURUSD": 0.00001,
    "GBPUSD": 0.00001,
    "USDJPY": 0.001,
    "USDCHF": 0.00001,
    "AUDUSD": 0.00001,
    "NZDUSD": 0.00001,
    "USDCAD": 0.00001,
    "EURGBP": 0.00001,
    "EURJPY": 0.001,
    "GBPJPY": 0.001,
    "AUDJPY": 0.001,
    "EURAUD": 0.00001,
    "EURCHF": 0.00001,
    "GBPCHF": 0.00001,
    "XAUUSD": 0.01,
    "XAGUSD": 0.001,
}


def _parse_bi5(data: bytes, hour_start: datetime, pip_size: float) -> list[dict[str, Any]]:
    """Parse Dukascopy bi5 binary tick data.

    Each tick record is 20 bytes:
      - 4 bytes: milliseconds offset from hour start (uint32, big-endian)
      - 4 bytes: ask price as integer (uint32, big-endian)
      - 4 bytes: bid price as integer (uint32, big-endian)
      - 4 bytes: ask volume (float32, big-endian)
      - 4 bytes: bid volume (float32, big-endian)
    """
    ticks: list[dict[str, Any]] = []
    record_size = 20
    num_records = len(data) // record_size

    for i in range(num_records):
        offset = i * record_size
        record = data[offset : offset + record_size]

        if len(record) < record_size:
            break

        ms_offset, ask_int, bid_int, ask_vol, bid_vol = struct.unpack(
            ">IIIff", record
        )

        timestamp = hour_start + timedelta(milliseconds=ms_offset)
        ask_price = ask_int * pip_size
        bid_price = bid_int * pip_size

        ticks.append(
            {
                "timestamp": timestamp.isoformat(),
                "bid": round(bid_price, 6),
                "ask": round(ask_price, 6),
                "bid_volume": round(bid_vol, 2),
                "ask_volume": round(ask_vol, 2),
            }
        )

    return ticks


def _decompress_bi5(compressed: bytes) -> bytes:
    """Decompress LZMA-compressed bi5 data."""
    try:
        return lzma.decompress(compressed)
    except lzma.LZMAError:
        logger.warning("Failed to decompress bi5 data, trying raw LZMA")
        try:
            decompressor = lzma.LZMADecompressor(format=lzma.FORMAT_AUTO)
            return decompressor.decompress(compressed)
        except Exception:
            logger.error("All decompression attempts failed")
            return b""


class DukascopyDownloader:
    """Async downloader for Dukascopy tick data."""

    def __init__(
        self,
        max_concurrent: int = 10,
        cache_dir: str | Path | None = None,
        timeout: float = 30.0,
    ) -> None:
        self.max_concurrent = max_concurrent
        self.cache_dir = Path(cache_dir or Path(__file__).parent / "raw" / "bi5_cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.timeout = timeout
        self._semaphore = asyncio.Semaphore(max_concurrent)

    def _build_url(self, symbol: str, dt: datetime) -> str:
        """Build Dukascopy data URL for a specific hour.

        Months are 0-indexed in Dukascopy URLs.
        """
        month_zero = dt.month - 1  # Dukascopy months: 0-indexed
        return (
            f"{DUKASCOPY_BASE_URL}/{symbol}/"
            f"{dt.year:04d}/{month_zero:02d}/{dt.day:02d}/"
            f"{dt.hour:02d}h_ticks.bi5"
        )

    def _cache_path(self, symbol: str, dt: datetime) -> Path:
        """Get cache file path for a specific hour."""
        month_zero = dt.month - 1
        return (
            self.cache_dir
            / symbol
            / f"{dt.year:04d}"
            / f"{month_zero:02d}"
            / f"{dt.day:02d}"
            / f"{dt.hour:02d}h_ticks.bi5"
        )

    async def _download_hour(
        self,
        client: httpx.AsyncClient,
        symbol: str,
        dt: datetime,
    ) -> bytes:
        """Download data for one hour, with caching."""
        cache = self._cache_path(symbol, dt)

        # Check cache first
        if cache.exists() and cache.stat().st_size > 0:
            return cache.read_bytes()

        url = self._build_url(symbol, dt)

        async with self._semaphore:
            try:
                response = await client.get(url, timeout=self.timeout)
                if response.status_code == 200 and len(response.content) > 0:
                    cache.parent.mkdir(parents=True, exist_ok=True)
                    cache.write_bytes(response.content)
                    return response.content
                elif response.status_code == 404:
                    # No data for this hour (weekend/holiday)
                    return b""
                else:
                    logger.warning(
                        "Unexpected status %d for %s", response.status_code, url
                    )
                    return b""
            except (httpx.TimeoutException, httpx.ConnectError) as e:
                logger.warning("Download failed for %s: %s", url, str(e))
                return b""

    async def download_ticks(
        self,
        symbol: str,
        start_date: datetime,
        end_date: datetime,
        progress_callback: Any | None = None,
    ) -> list[dict[str, Any]]:
        """Download tick data for a symbol and date range.

        Args:
            symbol: Forex pair symbol (e.g., "EURUSD")
            start_date: Start of the range (inclusive)
            end_date: End of the range (inclusive)
            progress_callback: Optional async callable(current, total) for progress

        Returns:
            List of tick dicts sorted by timestamp
        """
        symbol = symbol.upper().replace("/", "")
        pip_size = PIP_SIZES.get(symbol, 0.00001)

        # Generate hour slots
        hours: list[datetime] = []
        current = start_date.replace(minute=0, second=0, microsecond=0)
        while current <= end_date:
            hours.append(current)
            current += timedelta(hours=1)

        total_hours = len(hours)
        logger.info(
            "Downloading %d hours of tick data for %s (%s to %s)",
            total_hours,
            symbol,
            start_date.isoformat(),
            end_date.isoformat(),
        )

        all_ticks: list[dict[str, Any]] = []
        completed = 0

        async with httpx.AsyncClient(
            http2=True,
            follow_redirects=True,
            headers={"User-Agent": "Mozilla/5.0"},
        ) as client:
            # Process in batches to avoid overwhelming the server
            batch_size = self.max_concurrent * 2
            for batch_start in range(0, total_hours, batch_size):
                batch = hours[batch_start : batch_start + batch_size]

                tasks = [
                    self._download_hour(client, symbol, hour_dt) for hour_dt in batch
                ]

                results = await asyncio.gather(*tasks, return_exceptions=True)

                for hour_dt, result in zip(batch, results):
                    if isinstance(result, Exception):
                        logger.warning(
                            "Error for %s: %s", hour_dt.isoformat(), str(result)
                        )
                        continue

                    if result and len(result) > 0:
                        decompressed = _decompress_bi5(result)
                        if decompressed:
                            hour_ticks = _parse_bi5(decompressed, hour_dt, pip_size)
                            all_ticks.extend(hour_ticks)

                    completed += 1
                    if progress_callback:
                        await progress_callback(completed, total_hours)

        # Sort by timestamp
        all_ticks.sort(key=lambda t: t["timestamp"])

        logger.info(
            "Downloaded %d ticks for %s", len(all_ticks), symbol
        )

        return all_ticks

    async def download_and_store(
        self,
        symbol: str,
        start_date: datetime,
        end_date: datetime,
        store: Any,
        progress_callback: Any | None = None,
    ) -> int:
        """Download ticks and store them in DuckDB.

        Args:
            symbol: Forex pair symbol
            start_date: Start date
            end_date: End date
            store: DuckDBStore instance
            progress_callback: Optional progress callback

        Returns:
            Number of ticks stored
        """
        ticks = await self.download_ticks(
            symbol, start_date, end_date, progress_callback
        )

        if not ticks:
            logger.warning("No ticks downloaded for %s", symbol)
            return 0

        # Insert in batches for memory efficiency
        batch_size = 100_000
        total_inserted = 0

        for i in range(0, len(ticks), batch_size):
            batch = ticks[i : i + batch_size]
            inserted = store.insert_ticks(symbol, batch)
            total_inserted += inserted

        logger.info("Stored %d ticks for %s", total_inserted, symbol)
        return total_inserted

    def get_available_symbols(self) -> list[str]:
        """Return list of known forex symbols."""
        return sorted(PIP_SIZES.keys())

    def clear_cache(self, symbol: str | None = None) -> int:
        """Clear downloaded cache files.

        Args:
            symbol: If provided, only clear cache for this symbol

        Returns:
            Number of files deleted
        """
        count = 0
        target = self.cache_dir / symbol if symbol else self.cache_dir

        if target.exists():
            for f in target.rglob("*.bi5"):
                f.unlink()
                count += 1

        logger.info("Cleared %d cache files", count)
        return count
