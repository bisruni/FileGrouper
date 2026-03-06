from __future__ import annotations

from pathlib import Path
from typing import Iterable
from unittest.mock import MagicMock

import pytest


@pytest.fixture
def sample_source_tree(tmp_path: Path) -> Path:
    source = tmp_path / "source"
    (source / "docs").mkdir(parents=True)
    (source / "images").mkdir(parents=True)
    (source / "docs" / "a.txt").write_text("alpha", encoding="utf-8")
    (source / "docs" / "b.txt").write_text("beta", encoding="utf-8")
    (source / "images" / "img.jpg").write_bytes(b"\xff\xd8\xff\xd9")
    return source


@pytest.fixture
def make_files(tmp_path: Path):
    def _make(base: Path, relative_paths: Iterable[str]) -> list[Path]:
        created: list[Path] = []
        for rel_path in relative_paths:
            target = base / rel_path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(rel_path, encoding="utf-8")
            created.append(target)
        return created

    return _make


@pytest.fixture
def mocked_cancel_event() -> MagicMock:
    event = MagicMock()
    event.is_set.return_value = False
    return event
