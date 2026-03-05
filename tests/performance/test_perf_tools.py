from __future__ import annotations

from pathlib import Path

from tests.performance.perf_utils import compare_with_baseline, generate_perf_dataset, run_preview_benchmark


def test_generate_perf_dataset_creates_expected_file_count(tmp_path: Path) -> None:
    dataset = tmp_path / "dataset"
    stats = generate_perf_dataset(
        dataset,
        files=120,
        duplicate_ratio=0.2,
        same_size_ratio=0.1,
        seed=7,
    )
    assert stats.files_created == 120
    assert len([path for path in dataset.rglob("*") if path.is_file()]) == 120


def test_run_preview_benchmark_returns_expected_structure(tmp_path: Path) -> None:
    dataset = tmp_path / "dataset"
    generate_perf_dataset(dataset, files=80, duplicate_ratio=0.2, same_size_ratio=0.1, seed=9)
    result = run_preview_benchmark(source=dataset, iterations=1)

    assert result["iterations"] == 1
    assert "elapsed_seconds" in result
    assert "peak_memory_bytes" in result
    assert "summary" in result
    assert result["summary"]["total_files_scanned"] == 80


def test_compare_with_baseline_detects_regressions() -> None:
    baseline = {
        "elapsed_seconds": {"avg": 1.0},
        "peak_memory_bytes": {"avg": 100.0},
    }
    current = {
        "elapsed_seconds": {"avg": 1.5},
        "peak_memory_bytes": {"avg": 130.0},
    }
    issues = compare_with_baseline(
        current,
        baseline,
        max_time_regression=1.2,
        max_memory_regression=1.2,
    )
    assert len(issues) == 2
