"""Command-line entry points for scanning, preview, apply and GUI launch."""

from __future__ import annotations

import argparse
import json
import sys
import threading
from pathlib import Path

from .errors import OperationCancelledError
from .logger import configure_logging, get_logger
from .models import DedupeMode, ExecutionScope, OperationProgress, OrganizationMode, ScanFilterOptions
from .pause_controller import PauseController
from .pipeline import FileGrouperEngine, RunOptions, RunResult
from .utils import format_size
from .validators import (
    ValidationError,
    validate_paths_separated,
    validate_similarity_max_distance,
    validate_source_path,
    validate_target_path,
)


def build_parser() -> argparse.ArgumentParser:
    """Build the top-level CLI argument parser.

    Returns:
        argparse.ArgumentParser: Parser instance with subcommands.

    Example:
        >>> parser = build_parser()
        >>> parser.prog
        'archiflow'
    """
    parser = argparse.ArgumentParser(prog="archiflow", description="File grouping and duplicate cleanup")
    sub = parser.add_subparsers(dest="command")

    scan = sub.add_parser("scan", help="Scan source and print summary")
    scan.add_argument("--source", required=True)
    scan.add_argument("--report")

    preview = sub.add_parser("preview", help="Scan + duplicate analysis")
    preview.add_argument("--source", required=True)
    preview.add_argument("--report")

    apply_cmd = sub.add_parser("apply", help="Apply grouping and/or duplicate cleanup")
    apply_cmd.add_argument("--source", required=True)
    apply_cmd.add_argument("--target")
    apply_cmd.add_argument(
        "--mode", choices=[item.value for item in OrganizationMode], default=OrganizationMode.COPY.value
    )
    apply_cmd.add_argument("--dedupe", choices=[item.value for item in DedupeMode], default=DedupeMode.QUARANTINE.value)
    apply_cmd.add_argument(
        "--scope",
        choices=[item.value for item in ExecutionScope],
        default=ExecutionScope.GROUP_AND_DEDUPE.value,
    )
    apply_cmd.add_argument("--dry-run", action="store_true")
    apply_cmd.add_argument("--similar-images", action="store_true")
    apply_cmd.add_argument("--report")

    sub.add_parser("gui", help="Open desktop GUI")
    return parser


def main(argv: list[str] | None = None) -> int:
    """Execute CLI command and return process exit code.

    Args:
        argv: Optional command-line argument list.

    Returns:
        int: Process exit code.

    Example:
        >>> # main(["scan", "--source", "/tmp/data"])
        >>> # Returns 0 on success.
    """
    log_file = configure_logging()
    app_logger = get_logger("cli")
    app_logger.info("CLI started", extra={"transaction_id": ""})
    args = build_parser().parse_args(argv)
    if args.command in {None, "gui"}:
        try:
            from .gui import launch_gui
        except ModuleNotFoundError as exc:
            missing_name = getattr(exc, "name", None)
            if isinstance(missing_name, str) and missing_name.startswith("PySide6"):  # pylint: disable=no-member
                print(
                    "GUI icin PySide6 gerekli. Once bir sanal ortam acip bagimliliklari kurun:\n"
                    "  python3 -m venv .venv\n"
                    "  source .venv/bin/activate\n"
                    "  python3 -m pip install -r requirements.txt",
                    file=sys.stderr,
                )
                app_logger.error("GUI dependency missing: PySide6", extra={"transaction_id": ""})
                return 1
            raise

        app_logger.info("Launching GUI", extra={"transaction_id": ""})
        launch_gui()
        return 0

    engine = FileGrouperEngine()
    cancel_event = threading.Event()
    pause_controller = PauseController()

    def log(message: str) -> None:
        print(message)
        app_logger.info(message, extra={"transaction_id": ""})

    def progress(item: OperationProgress) -> None:
        if item.total_files > 0:
            percent = item.processed_files / item.total_files * 100
            print(f"[{item.stage.value}] {percent:0.0f}% - {item.message}")

    # Early input validation for CLI commands
    try:
        # Validate source path (required for all commands)
        source_path = validate_source_path(args.source)

        # Determine scope to check if grouping is included
        if args.command == "scan":
            scope = ExecutionScope.GROUP_ONLY
            target_path = None
        elif args.command == "preview":
            scope = ExecutionScope.GROUP_AND_DEDUPE
            target_path = None
        else:  # apply
            scope = ExecutionScope(args.scope)
            # Validate target path (may be required depending on scope)
            target_path = validate_target_path(args.target, scope.includes_grouping)

        # Ensure source and target are properly separated
        validate_paths_separated(source_path, target_path)

        # Validate image similarity parameter if specified
        if getattr(args, "similar_images", False):
            validate_similarity_max_distance(10)  # Default hamming distance

    except ValidationError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        app_logger.error(f"Input validation failed: {exc}", extra={"transaction_id": ""})
        return 1

    if args.command == "scan":
        run_options = RunOptions(
            source_path=source_path,
            target_path=None,
            organization_mode=OrganizationMode.COPY,
            dedupe_mode=DedupeMode.OFF,
            execution_scope=ExecutionScope.GROUP_ONLY,
            dry_run=True,
            detect_similar_images=False,
            apply_changes=False,
            filter_options=ScanFilterOptions(),
        )
    elif args.command == "preview":
        run_options = RunOptions(
            source_path=source_path,
            target_path=None,
            organization_mode=OrganizationMode.COPY,
            dedupe_mode=DedupeMode.QUARANTINE,
            execution_scope=ExecutionScope.GROUP_AND_DEDUPE,
            dry_run=True,
            detect_similar_images=False,
            apply_changes=False,
            filter_options=ScanFilterOptions(),
        )
    else:
        run_options = RunOptions(
            source_path=source_path,
            target_path=target_path,
            organization_mode=OrganizationMode(args.mode),
            dedupe_mode=DedupeMode(args.dedupe),
            execution_scope=scope,
            dry_run=bool(args.dry_run),
            detect_similar_images=bool(args.similar_images),
            apply_changes=True,
            filter_options=ScanFilterOptions(),
        )

    error = engine.validate_paths(run_options.source_path, run_options.target_path, run_options.execution_scope)
    if error and run_options.apply_changes:
        print(f"Error: {error}", file=sys.stderr)
        app_logger.error(f"Path validation failed: {error}", extra={"transaction_id": ""})
        return 1

    try:
        app_logger.info(
            "Engine run started",
            extra={"transaction_id": ""},
        )
        result = engine.run(
            run_options,
            log=log,
            progress=progress,
            cancel_event=cancel_event,
            pause_controller=pause_controller,
        )
    except OperationCancelledError:
        print("Cancelled", file=sys.stderr)
        app_logger.warning("Operation cancelled", extra={"transaction_id": ""})
        return 2
    except (KeyboardInterrupt, SystemExit):
        app_logger.warning("Termination signal received", extra={"transaction_id": ""})
        raise  # Always propagate termination signals
    except Exception as exc:  # Intentionally broad for CLI error handling
        print(f"Error: {exc}", file=sys.stderr)
        app_logger.exception("Unhandled CLI error", extra={"transaction_id": ""})
        return 1

    print_summary(result)

    if getattr(args, "report", None):
        report_path = Path(args.report).expanduser().resolve()
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report = engine.build_report(result)
        with report_path.open("w", encoding="utf-8") as stream:
            json.dump(report.to_dict(), stream, ensure_ascii=True, indent=2)
        print(f"Report written: {report_path}")
        app_logger.info(f"Report written: {report_path}", extra={"transaction_id": result.transaction_id or ""})

    app_logger.info(
        f"CLI finished. log_file={log_file}",
        extra={"transaction_id": result.transaction_id or ""},
    )

    return 0


def print_summary(result: RunResult) -> None:
    """Print run summary to stdout in a human-readable layout.

    Args:
        result: Completed run result to render.

    Returns:
        None
    """
    summary = result.summary
    print("== Summary ==")
    print(f"Source: {result.source_path}")
    print(f"Target: {result.target_path}")
    print(f"Scanned files: {summary.total_files_scanned}")
    print(f"Scanned size: {format_size(summary.total_bytes_scanned)}")
    print(f"Duplicate groups: {summary.duplicate_group_count}")
    print(f"Duplicate files: {summary.duplicate_files_found}")
    print(f"Reclaimable: {format_size(summary.duplicate_bytes_reclaimable)}")
    print(f"Copied: {summary.files_copied}")
    print(f"Moved: {summary.files_moved}")
    print(f"Quarantined: {summary.duplicates_quarantined}")
    print(f"Deleted duplicates: {summary.duplicates_deleted}")
    print(f"Errors: {len(summary.errors)}")


if __name__ == "__main__":
    raise SystemExit(main())
