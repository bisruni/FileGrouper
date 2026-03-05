from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from filegrouper.models import OperationTransaction, TransactionAction, TransactionEntry, TransactionStatus
from filegrouper.transaction_service import TransactionService


def test_transaction_service_undo_reverses_done_entries_and_skips_others(tmp_path: Path) -> None:
    source_root = tmp_path / "source"
    target_root = tmp_path / "target"
    source_root.mkdir()
    target_root.mkdir()

    moved_source = source_root / "moved.txt"
    moved_dest = target_root / "archive" / "moved.txt"
    moved_dest.parent.mkdir(parents=True)
    moved_dest.write_text("moved", encoding="utf-8")

    copied_source = source_root / "copied.txt"
    copied_source.write_text("copy-src", encoding="utf-8")
    copied_dest = target_root / "copies" / "copied.txt"
    copied_dest.parent.mkdir(parents=True)
    copied_dest.write_text("copy-dst", encoding="utf-8")

    quarantine_source = source_root / "dup.txt"
    quarantine_dest = target_root / ".filegrouper_quarantine" / "dup.txt"
    quarantine_dest.parent.mkdir(parents=True)
    quarantine_dest.write_text("dup", encoding="utf-8")

    pending_source = source_root / "pending.txt"
    pending_dest = target_root / "pending" / "pending.txt"

    transaction = OperationTransaction(
        transaction_id="tx-undo",
        created_at_utc=datetime.now(tz=timezone.utc),
        source_root=source_root,
        target_root=target_root,
        entries=[
            TransactionEntry(
                action=TransactionAction.MOVED,
                source_path=moved_source,
                destination_path=moved_dest,
                timestamp_utc=datetime.now(tz=timezone.utc),
                status=TransactionStatus.DONE,
            ),
            TransactionEntry(
                action=TransactionAction.COPIED,
                source_path=copied_source,
                destination_path=copied_dest,
                timestamp_utc=datetime.now(tz=timezone.utc),
                status=TransactionStatus.DONE,
            ),
            TransactionEntry(
                action=TransactionAction.QUARANTINED_DUPLICATE,
                source_path=quarantine_source,
                destination_path=quarantine_dest,
                timestamp_utc=datetime.now(tz=timezone.utc),
                status=TransactionStatus.DONE,
            ),
            TransactionEntry(
                action=TransactionAction.MOVED,
                source_path=pending_source,
                destination_path=pending_dest,
                timestamp_utc=datetime.now(tz=timezone.utc),
                status=TransactionStatus.PENDING,
                error_message="cancelled",
            ),
            TransactionEntry(
                action=TransactionAction.DELETED_DUPLICATE,
                source_path=source_root / "deleted.txt",
                destination_path=None,
                timestamp_utc=datetime.now(tz=timezone.utc),
                status=TransactionStatus.DONE,
                reversible=False,
            ),
        ],
    )

    service = TransactionService()
    tx_file = service.save_transaction(transaction)
    summary = service.undo_transaction(tx_file)

    assert summary.files_moved == 1
    assert summary.files_copied == 1
    assert summary.duplicates_quarantined == 1
    assert any("Deleted file cannot be restored" in item for item in summary.errors)

    assert moved_source.exists()
    assert not moved_dest.exists()
    assert not copied_dest.exists()
    assert quarantine_source.exists()
    assert not quarantine_dest.exists()
