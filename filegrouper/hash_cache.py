"""Persistent hash cache with rate-limited disk flush semantics."""

from __future__ import annotations

import json
import os
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Callable


class HashCacheService:
    """Store and reuse expensive file hashes keyed by path/size/mtime."""

    def __init__(self, cache_path: Path) -> None:
        """Initialize cache service bound to given JSON cache path.

        Args:
            cache_path: Cache file path.
        """
        self._cache_path = cache_path
        self._lock = threading.Lock()
        self._cache: dict[str, dict[str, str | int]] | None = None
        self._dirty = False
        self._updates_since_save = 0
        self._last_save_monotonic = 0.0
        self._save_update_threshold = 50
        self._save_interval_seconds = 1.0

    def get_or_compute_sha256(
        self,
        path: Path,
        size_bytes: int,
        last_write_utc: datetime,
        compute_hash: Callable[[], str],
    ) -> str:
        """Return cached SHA-256 or compute/update it for a file snapshot.

        Args:
            path: File path.
            size_bytes: File size in bytes.
            last_write_utc: File last modified timestamp.
            compute_hash: Callback used when cache miss occurs.

        Returns:
            str: Lower-cased SHA-256 value.
        """
        key = self._make_key(path, size_bytes, last_write_utc)
        legacy_key = str(path.resolve()).lower()
        ticks = int(last_write_utc.timestamp() * 1_000_000)

        with self._lock:
            self._load_if_needed()
            assert self._cache is not None
            current = self._cache.get(key)
            if current and current.get("sha256"):
                return str(current["sha256"]).lower()
            legacy = self._cache.get(legacy_key)
            if legacy and legacy.get("size") == size_bytes and legacy.get("mtime") == ticks and legacy.get("sha256"):
                return str(legacy["sha256"]).lower()

        sha256_hash = compute_hash().lower()

        with self._lock:
            self._load_if_needed()
            assert self._cache is not None
            current = self._cache.get(key) or {}
            current["path"] = str(path.resolve())
            current["size"] = size_bytes
            current["mtime"] = ticks
            current["sha256"] = sha256_hash
            self._cache[key] = current
            self._mark_dirty_and_maybe_save()

        return sha256_hash

    def get_or_compute_quick_signature(
        self,
        path: Path,
        size_bytes: int,
        last_write_utc: datetime,
        compute_signature: Callable[[], str],
    ) -> str:
        """Return cached quick signature or compute/update it for a file snapshot.

        Args:
            path: File path.
            size_bytes: File size in bytes.
            last_write_utc: File last modified timestamp.
            compute_signature: Callback used when cache miss occurs.

        Returns:
            str: Lower-cased quick signature value.
        """
        key = self._make_key(path, size_bytes, last_write_utc)
        legacy_key = str(path.resolve()).lower()
        ticks = int(last_write_utc.timestamp() * 1_000_000)

        with self._lock:
            self._load_if_needed()
            assert self._cache is not None
            current = self._cache.get(key)
            if current and current.get("quick_signature"):
                return str(current["quick_signature"]).lower()
            legacy = self._cache.get(legacy_key)
            if (
                legacy
                and legacy.get("size") == size_bytes
                and legacy.get("mtime") == ticks
                and legacy.get("quick_signature")
            ):
                return str(legacy["quick_signature"]).lower()

        quick_signature = compute_signature().lower()

        with self._lock:
            self._load_if_needed()
            assert self._cache is not None
            current = self._cache.get(key) or {}
            current["path"] = str(path.resolve())
            current["size"] = size_bytes
            current["mtime"] = ticks
            current["quick_signature"] = quick_signature
            self._cache[key] = current
            self._mark_dirty_and_maybe_save()

        return quick_signature

    def flush(self) -> None:
        """Persist pending cache updates to disk when dirty.

        Returns:
            None

        Example:
            >>> # cache.flush()
            >>> # Ensures buffered cache updates are written to disk.
        """
        with self._lock:
            self._save(force=False)

    def _load_if_needed(self) -> None:
        if self._cache is not None:
            return

        if not self._cache_path.exists():
            self._cache = {}
            return

        try:
            with self._cache_path.open("r", encoding="utf-8") as stream:
                payload = json.load(stream)
            self._cache = payload if isinstance(payload, dict) else {}
        except (OSError, IOError, json.JSONDecodeError):  # File I/O or invalid JSON
            self._cache = {}

    def _mark_dirty_and_maybe_save(self) -> None:
        self._dirty = True
        self._updates_since_save += 1
        now = time.monotonic()
        if (
            self._updates_since_save >= self._save_update_threshold
            or (now - self._last_save_monotonic) >= self._save_interval_seconds
        ):
            self._save(force=True)

    def _save(self, *, force: bool) -> None:
        if not force and not self._dirty:
            return
        self._cache_path.parent.mkdir(parents=True, exist_ok=True)
        temp_path = self._cache_path.with_name(f".{self._cache_path.name}.tmp")
        with temp_path.open("w", encoding="utf-8") as stream:
            json.dump(self._cache or {}, stream, ensure_ascii=True, separators=(",", ":"))
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp_path, self._cache_path)
        self._dirty = False
        self._updates_since_save = 0
        self._last_save_monotonic = time.monotonic()

    @staticmethod
    def _make_key(path: Path, size_bytes: int, last_write_utc: datetime) -> str:
        ticks = int(last_write_utc.timestamp() * 1_000_000)
        return f"{str(path.resolve()).lower()}|{size_bytes}|{ticks}"
