#!/usr/bin/env python3
"""Generate a dependency license report from local installed metadata."""

from __future__ import annotations

import argparse
import datetime as dt
import importlib.metadata as importlib_metadata
import re
import sys
from pathlib import Path

try:
    from packaging.requirements import Requirement
except ImportError:  # pragma: no cover - packaging is available in normal dev envs
    Requirement = None  # type: ignore[assignment]

REVIEW_TOKENS = ("GPL", "LGPL", "AGPL", "UNKNOWN")


def _extract_package(requirement_line: str) -> str | None:
    line = requirement_line.strip()
    if not line or line.startswith("#"):
        return None
    if line.startswith("-r") or line.startswith("--"):
        return None
    line = line.split("#", 1)[0].strip()
    if not line:
        return None
    if Requirement is not None:
        try:
            requirement = Requirement(line)
            if requirement.marker and not requirement.marker.evaluate():
                return None
            return requirement.name
        except Exception:
            pass
    match = re.match(r"^([A-Za-z0-9_.-]+)", line)
    if not match:
        return None
    return match.group(1)


def _load_packages(requirement_files: list[Path]) -> dict[str, str]:
    packages: dict[str, str] = {}
    for req_file in requirement_files:
        if not req_file.exists():
            continue
        for raw_line in req_file.read_text(encoding="utf-8").splitlines():
            package = _extract_package(raw_line)
            if package:
                packages.setdefault(package.lower(), package)
    return dict(sorted(packages.items()))


def _license_from_metadata(meta: importlib_metadata.PackageMetadata) -> str:
    license_expression = (meta.get("License-Expression") or "").strip()
    if license_expression:
        return license_expression

    declared_license = (meta.get("License") or "").strip()
    if declared_license:
        return declared_license

    classifiers = meta.get_all("Classifier") or []
    for classifier in classifiers:
        if classifier.startswith("License ::"):
            return classifier.replace("License ::", "", 1).strip()

    return "UNKNOWN"


def _status_for_license(license_name: str) -> str:
    upper_name = license_name.upper()
    for token in REVIEW_TOKENS:
        if token in upper_name:
            return "REVIEW"
    return "OK"


def _note_for_license(license_name: str) -> str:
    upper_name = license_name.upper()
    if "LGPL" in upper_name:
        return "LGPL compliance review required for redistribution."
    if "GPL" in upper_name or "AGPL" in upper_name:
        return "Copyleft license requires legal review before distribution."
    if "UNKNOWN" in upper_name:
        return "No explicit license metadata found."
    return ""


def generate_report(requirements: list[Path], output_path: Path, strict: bool) -> int:
    package_map = _load_packages(requirements)
    rows: list[tuple[str, str, str, str]] = []
    missing: list[str] = []

    for _, package in package_map.items():
        try:
            dist = importlib_metadata.distribution(package)
        except importlib_metadata.PackageNotFoundError:
            missing.append(package)
            rows.append((package, "-", "NOT INSTALLED", "REVIEW"))
            continue

        metadata = dist.metadata
        license_name = _license_from_metadata(metadata)
        status = _status_for_license(license_name)
        note = _note_for_license(license_name)
        rows.append((package, dist.version, license_name, status if not note else f"{status} ({note})"))

    now = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    lines = [
        "# Dependency License Verification",
        "",
        "This report is generated from local installed package metadata.",
        "",
        f"- Generated at: `{now}`",
        f"- Requirement sources: {', '.join(str(path) for path in requirements)}",
        "",
        "| Package | Version | License | Status |",
        "| --- | --- | --- | --- |",
    ]
    for package, version, license_name, status in rows:
        lines.append(f"| `{package}` | `{version}` | `{license_name}` | `{status}` |")

    review_count = sum(1 for _, _, _, status in rows if status.startswith("REVIEW"))
    ok_count = sum(1 for _, _, _, status in rows if status.startswith("OK"))
    lines.extend(
        [
            "",
            "## Summary",
            "",
            f"- Total packages checked: `{len(rows)}`",
            f"- OK: `{ok_count}`",
            f"- Review required: `{review_count}`",
            "",
            "## Notes",
            "",
            "- `REVIEW` means legal validation is needed before commercial distribution.",
            "- For `PySide6` (LGPL/GPL dual terms), redistribution must comply with LGPL obligations or a commercial Qt license.",
        ]
    )

    if missing:
        lines.extend(
            [
                "",
                "## Missing Locally",
                "",
                "These packages were listed in requirements but not installed in the current environment:",
                "",
            ]
        )
        lines.extend([f"- `{name}`" for name in missing])

    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    if strict and (review_count > 0 or bool(missing)):
        return 1
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate dependency license verification report.")
    parser.add_argument(
        "--requirements",
        nargs="+",
        default=["requirements.txt", "requirements-release.txt"],
        help="Requirement files to inspect.",
    )
    parser.add_argument(
        "--output",
        default="DEPENDENCY_LICENSES.md",
        help="Output markdown report path.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Return non-zero if any package requires legal review or is missing.",
    )
    args = parser.parse_args()

    requirement_paths = [Path(path) for path in args.requirements]
    output_path = Path(args.output)
    return generate_report(requirement_paths, output_path, strict=args.strict)


if __name__ == "__main__":
    sys.exit(main())
