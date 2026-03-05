from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from filegrouper.hash_cache import HashCacheService


def _last_write_utc(path: Path) -> datetime:
    return datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)


def test_hash_cache_reuses_cached_sha256(tmp_path: Path) -> None:
    file_path = tmp_path / "sample.txt"
    file_path.write_text("alpha", encoding="utf-8")
    cache = HashCacheService(tmp_path / ".filegrouper" / "cache" / "hash-cache.json")

    calls = 0

    def compute_hash() -> str:
        nonlocal calls
        calls += 1
        return "ABCDEF"

    first = cache.get_or_compute_sha256(
        file_path,
        file_path.stat().st_size,
        _last_write_utc(file_path),
        compute_hash,
    )
    second = cache.get_or_compute_sha256(
        file_path,
        file_path.stat().st_size,
        _last_write_utc(file_path),
        compute_hash,
    )

    assert first == "abcdef"
    assert second == "abcdef"
    assert calls == 1


def test_hash_cache_invalidates_when_size_or_mtime_changes(tmp_path: Path) -> None:
    file_path = tmp_path / "sample.txt"
    file_path.write_text("alpha", encoding="utf-8")
    cache = HashCacheService(tmp_path / ".filegrouper" / "cache" / "hash-cache.json")

    calls = 0

    def compute_hash() -> str:
        nonlocal calls
        calls += 1
        return f"hash-{calls}"

    first = cache.get_or_compute_sha256(
        file_path,
        file_path.stat().st_size,
        _last_write_utc(file_path),
        compute_hash,
    )

    file_path.write_text("alpha-beta", encoding="utf-8")
    second = cache.get_or_compute_sha256(
        file_path,
        file_path.stat().st_size,
        _last_write_utc(file_path),
        compute_hash,
    )

    assert first == "hash-1"
    assert second == "hash-2"
    assert calls == 2


def test_hash_cache_supports_legacy_key_format(tmp_path: Path) -> None:
    file_path = tmp_path / "legacy.bin"
    file_path.write_bytes(b"legacy")
    snapshot = _last_write_utc(file_path)
    ticks = int(snapshot.timestamp() * 1_000_000)

    cache_path = tmp_path / ".filegrouper" / "cache" / "hash-cache.json"
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    legacy_key = str(file_path.resolve()).lower()
    cache_path.write_text(
        ("{" f'"{legacy_key}":{{"size":{file_path.stat().st_size},"mtime":{ticks},"sha256":"LEGACYHASH"}}' "}"),
        encoding="utf-8",
    )

    cache = HashCacheService(cache_path)
    value = cache.get_or_compute_sha256(
        file_path,
        file_path.stat().st_size,
        snapshot,
        lambda: "SHOULD_NOT_RUN",
    )

    assert value == "legacyhash"
