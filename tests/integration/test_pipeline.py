from __future__ import annotations

import threading
from pathlib import Path

from filegrouper.models import DedupeMode, ExecutionScope, OrganizationMode, ScanFilterOptions
from filegrouper.pause_controller import PauseController
from filegrouper.pipeline import FileGrouperEngine, RunOptions


def test_pipeline_preview_and_apply_quarantine_with_undo(tmp_path: Path) -> None:
    source = tmp_path / "source"
    target = tmp_path / "target"
    source.mkdir()
    target.mkdir()

    (source / "a.txt").write_text("dup", encoding="utf-8")
    (source / "b.txt").write_text("dup", encoding="utf-8")
    (source / "c.txt").write_text("solo", encoding="utf-8")

    engine = FileGrouperEngine()
    cancel_event = threading.Event()
    pause_controller = PauseController()

    preview = engine.run(
        RunOptions(
            source_path=source,
            target_path=None,
            organization_mode=OrganizationMode.COPY,
            dedupe_mode=DedupeMode.QUARANTINE,
            execution_scope=ExecutionScope.GROUP_AND_DEDUPE,
            dry_run=True,
            detect_similar_images=False,
            apply_changes=False,
            filter_options=ScanFilterOptions(),
        ),
        log=None,
        progress=None,
        cancel_event=cancel_event,
        pause_controller=pause_controller,
    )

    assert preview.summary.total_files_scanned == 3
    assert preview.summary.duplicate_group_count == 1
    assert preview.summary.duplicate_files_found == 1
    assert preview.summary.duplicates_quarantined == 0
    assert preview.auto_report_json_path is not None and preview.auto_report_json_path.exists()
    assert preview.auto_report_csv_path is not None and preview.auto_report_csv_path.exists()

    applied = engine.run(
        RunOptions(
            source_path=source,
            target_path=target,
            organization_mode=OrganizationMode.COPY,
            dedupe_mode=DedupeMode.QUARANTINE,
            execution_scope=ExecutionScope.DEDUPE_ONLY,
            dry_run=False,
            detect_similar_images=False,
            apply_changes=True,
            filter_options=ScanFilterOptions(),
        ),
        log=None,
        progress=None,
        cancel_event=cancel_event,
        pause_controller=pause_controller,
    )

    assert applied.summary.duplicates_quarantined == 1
    assert applied.transaction_file_path is not None and applied.transaction_file_path.exists()
    assert any((target / ".filegrouper_quarantine").rglob("*.txt"))

    undo_summary = engine.transaction_service.undo_last_transaction(target)
    assert undo_summary.duplicates_quarantined == 1
    assert sorted(item.name for item in source.glob("*.txt")) == ["a.txt", "b.txt", "c.txt"]
