# Changelog

All notable changes to this project are documented in this file.

Format follows Keep a Changelog principles and semantic versioning (SemVer).

## [1.0.0] - 2026-03-06

### Added
- Python desktop implementation (`ArchiFlow`) with PySide6 GUI and CLI (`scan`, `preview`, `apply`).
- Safe-by-default duplicate workflow (quarantine default, undo-capable transaction journal).
- Multi-stage duplicate detection: size -> quick signature -> sha256 -> byte verification.
- Similar image detection (optional) with dHash and band-bucket candidate search.
- Full reporting pipeline (JSON/CSV auto reports, transaction references).
- Config and profile system (`config.yaml`, CLI profile usage, env overrides).
- Performance suite (dataset generation, benchmark runner, regression checks).
- Packaging and release scripts for wheel/sdist build and Twine pre-checks.

### Changed
- Product naming and UX language standardized around `ArchiFlow`.
- Pipeline internals hardened for large datasets (streaming scan paths, cache strategy, concurrency tuning).
- Hash cache redesigned with invalidation, LRU bounds, and runtime statistics.

### Fixed
- Cancel/interrupt safety in apply flows with persistent transaction checkpoints.
- Progress reporting inconsistencies during hashing and large-file operations.
- Multiple path validation and safety-edge issues around source/target relationships.

### Security
- Destructive operations remain explicitly controlled; delete is not default.
- Quarantine and transaction trail provide auditability and safer recovery.

## [Unreleased]

### Planned
- Release automation polish (7.x phases), legal/compliance pass, and cross-platform release checklist.
