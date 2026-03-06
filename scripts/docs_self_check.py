#!/usr/bin/env python3
"""Validate documentation links and executable command samples."""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
MARKDOWN_FILES = [
    "README.md",
    "CHANGELOG.md",
    "CONTRIBUTING.md",
    "DEPENDENCY_LICENSES.md",
    "MARKETING.md",
    "MIGRATION_GUIDE.md",
    "PACKAGING.md",
    "RELEASE_NOTES_1.0.0.md",
    "TUTORIALS.md",
]


def _run(cmd: list[str], *, cwd: Path | None = None) -> None:
    subprocess.run(cmd, cwd=str(cwd or REPO_ROOT), check=True)


def _iter_doc_files() -> list[Path]:
    files = [REPO_ROOT / rel for rel in MARKDOWN_FILES if (REPO_ROOT / rel).exists()]
    files.extend(sorted((REPO_ROOT / "assets").rglob("*.md")))
    files.extend(sorted((REPO_ROOT / "docs").rglob("*.rst")))
    return files


def check_local_links() -> list[str]:
    errors: list[str] = []
    markdown_link_re = re.compile(r"\[[^\]]+\]\(([^)]+)\)")

    for doc_path in _iter_doc_files():
        text = doc_path.read_text(encoding="utf-8")
        if doc_path.suffix == ".md":
            for match in markdown_link_re.finditer(text):
                link = match.group(1).strip()
                if not link or link.startswith(("http://", "https://", "mailto:", "#")):
                    continue
                target_rel = link.split("#", 1)[0].split("?", 1)[0]
                target = (doc_path.parent / target_rel).resolve()
                if not target.exists():
                    errors.append(f"{doc_path.relative_to(REPO_ROOT)} -> {link}")
        elif doc_path.suffix == ".rst":
            lines = text.splitlines()
            in_toctree = False
            for line in lines:
                if line.strip().startswith(".. toctree::"):
                    in_toctree = True
                    continue
                if in_toctree:
                    if not line.strip():
                        continue
                    if line.strip().startswith(":"):
                        continue
                    if not line.startswith((" ", "\t")):
                        in_toctree = False
                        continue
                    item = line.strip()
                    if item.startswith("http://") or item.startswith("https://"):
                        continue
                    candidate = (doc_path.parent / item).resolve()
                    exists = (
                        candidate.exists()
                        or candidate.with_suffix(".rst").exists()
                        or candidate.with_suffix(".md").exists()
                    )
                    if not exists:
                        errors.append(f"{doc_path.relative_to(REPO_ROOT)} -> toctree:{item}")
    return errors


def check_command_samples() -> None:
    _run([sys.executable, "main.py", "-h"])
    _run([sys.executable, "tests/performance/run_benchmark.py", "--help"])
    _run([sys.executable, "main.py", "profiles", "--json"])

    with tempfile.TemporaryDirectory(prefix="archiflow_docs_") as temp_dir:
        root = Path(temp_dir)
        source = root / "source"
        target = root / "target"
        source.mkdir()
        target.mkdir()
        (source / "a.txt").write_text("dup", encoding="utf-8")
        (source / "b.txt").write_text("dup", encoding="utf-8")
        (source / "c.txt").write_text("solo", encoding="utf-8")

        _run([sys.executable, "main.py", "scan", "--source", str(source)])
        _run(
            [
                sys.executable,
                "main.py",
                "preview",
                "--source",
                str(source),
                "--report",
                str(root / "preview.json"),
            ]
        )
        _run(
            [
                sys.executable,
                "main.py",
                "apply",
                "--source",
                str(source),
                "--target",
                str(target),
                "--scope",
                "dedupe_only",
                "--dedupe",
                "quarantine",
                "--dry-run",
            ]
        )


def build_sphinx_docs() -> None:
    if shutil.which("sphinx-build") is None:
        raise RuntimeError("sphinx-build not found in active environment.")
    _run(["make", "-C", "docs", "html"])


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run documentation quality checks.")
    parser.add_argument("--skip-sphinx-build", action="store_true", help="Skip `make -C docs html` step.")
    args = parser.parse_args(argv)

    errors = check_local_links()
    if errors:
        print("Broken local documentation links detected:", file=sys.stderr)
        for item in errors:
            print(f"- {item}", file=sys.stderr)
        return 1

    check_command_samples()

    if not args.skip_sphinx_build:
        build_sphinx_docs()

    print("Docs self-check passed: links + commands + docs build.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
