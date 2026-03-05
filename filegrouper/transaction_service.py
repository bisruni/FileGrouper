"""Transaction journal persistence and undo execution logic."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Callable

from .constants import transactions_dir
from .errors import TransactionError, record_error
from .models import OperationSummary, OperationTransaction, TransactionAction, TransactionStatus

LogFn = Callable[[str], None]


class TransactionService:
    """Handle save/load/find/undo operations for transaction journals."""

    def save_transaction(self, transaction: OperationTransaction) -> Path:
        """Persist a new transaction journal under target transaction directory.

        Args:
            transaction: Transaction journal model to persist.

        Returns:
            Path: Saved journal path.
        """
        tx_root = transactions_dir(transaction.target_root)
        tx_root.mkdir(parents=True, exist_ok=True)
        filename = f"{transaction.created_at_utc.strftime('%Y%m%d_%H%M%S')}_{transaction.transaction_id}.json"
        destination = tx_root / filename
        self.save_transaction_to_path(transaction, destination)
        return destination

    def save_transaction_to_path(self, transaction: OperationTransaction, destination: Path) -> Path:
        """Atomically persist transaction payload to an explicit path.

        Args:
            transaction: Transaction journal model to persist.
            destination: Destination file path.

        Returns:
            Path: Saved destination path.
        """
        destination.parent.mkdir(parents=True, exist_ok=True)
        payload = transaction.to_dict()
        temp_path = destination.with_name(f".{destination.name}.tmp")

        with temp_path.open("w", encoding="utf-8") as stream:
            json.dump(payload, stream, ensure_ascii=True, indent=2)
            stream.flush()
            os.fsync(stream.fileno())

        os.replace(temp_path, destination)
        try:
            dir_fd = os.open(destination.parent, os.O_RDONLY)
            try:
                os.fsync(dir_fd)
            finally:
                os.close(dir_fd)
        except OSError:
            # Directory fsync is not available on all platforms.
            pass
        return destination

    def find_latest_transaction_file(self, target_root: Path) -> Path | None:
        """Return most recently modified transaction journal file or ``None``.

        Args:
            target_root: Target root folder.

        Returns:
            Path | None: Latest transaction file path.
        """
        tx_root = transactions_dir(target_root)
        if not tx_root.is_dir():
            return None

        files = sorted(tx_root.glob("*.json"), key=lambda item: item.stat().st_mtime, reverse=True)
        return files[0] if files else None

    def load(self, transaction_file: Path) -> OperationTransaction:
        """Load a transaction journal JSON file into model object.

        Args:
            transaction_file: Transaction JSON path.

        Returns:
            OperationTransaction: Parsed transaction model.
        """
        with transaction_file.open("r", encoding="utf-8") as stream:
            payload = json.load(stream)
        return OperationTransaction.from_dict(payload)

    def undo_last_transaction(self, target_root: Path, log: LogFn | None = None) -> OperationSummary:
        """Undo latest transaction under target root and return summary.

        Args:
            target_root: Root folder that contains transaction journals.
            log: Optional log callback.

        Returns:
            OperationSummary: Undo summary counters and errors.
        """
        latest = self.find_latest_transaction_file(target_root)
        if latest is None:
            raise TransactionError(f"No transaction file found for undo under '{target_root}'.")
        return self.undo_transaction(latest, log=log)

    def undo_transaction(self, transaction_file: Path, log: LogFn | None = None) -> OperationSummary:
        """Undo a specific transaction file, continuing through recoverable errors.

        Args:
            transaction_file: Transaction file to undo.
            log: Optional log callback.

        Returns:
            OperationSummary: Undo summary.

        Example:
            >>> # service.undo_transaction(Path(".../tx.json"))
            >>> # Replays journal entries in reverse order.
        """
        transaction = self.load(transaction_file)
        summary = OperationSummary()

        for entry in reversed(transaction.entries):
            if entry.status is not TransactionStatus.DONE:
                if log:
                    detail = f" reason={entry.error_message}" if entry.error_message else ""
                    log(
                        f"Undo skipped ({entry.status.value}) for '{entry.source_path}' "
                        f"[{entry.action.value}]{detail}"
                    )
                continue
            try:
                if entry.action is TransactionAction.COPIED:
                    if entry.destination_path and entry.destination_path.exists():
                        entry.destination_path.unlink(missing_ok=True)
                        summary.files_copied += 1
                elif entry.action is TransactionAction.MOVED:
                    if entry.destination_path and entry.destination_path.exists():
                        entry.source_path.parent.mkdir(parents=True, exist_ok=True)
                        entry.destination_path.rename(entry.source_path)
                        summary.files_moved += 1
                elif entry.action is TransactionAction.QUARANTINED_DUPLICATE:
                    if entry.destination_path and entry.destination_path.exists():
                        entry.source_path.parent.mkdir(parents=True, exist_ok=True)
                        entry.destination_path.rename(entry.source_path)
                        summary.duplicates_quarantined += 1
                elif entry.action is TransactionAction.DELETED_DUPLICATE:
                    summary.errors.append(
                        f"Deleted file cannot be restored ({entry.source_path}). "
                        f"Backup your data before using delete mode."
                    )
                    if log:
                        log(f"Cannot restore deleted duplicate: {entry.source_path}")
            except (OSError, IOError, PermissionError) as exc:  # File operation failures
                record_error(
                    summary.errors,
                    log=log,
                    operation="Undo failed",
                    path=entry.source_path,
                    error=exc,
                    context={"action": entry.action.value},
                )

        return summary
