# Performance Suite

This folder contains the Phase 3.5 benchmark suite:

- Synthetic dataset generator
- Speed benchmark runner
- Peak memory profiling (`tracemalloc`)
- Optional process RSS peak reporting (`resource`, platform dependent)
- Regression detection against baseline JSON

Benchmark output now includes:
- `throughput` (files/s and MB/s)
- `peak_mem_avg` (`tracemalloc`)
- optional `peak_rss_avg` (process RSS, platform-dependent)

## Quick Start

Generate dataset + run benchmark:

```bash
python tests/performance/run_benchmark.py \
  --source /tmp/archiflow_perf \
  --generate \
  --files 5000 \
  --duplicate-ratio 0.2 \
  --same-size-ratio 0.1 \
  --iterations 2
```

Run benchmark on an existing dataset:

```bash
python tests/performance/run_benchmark.py \
  --source /tmp/archiflow_perf \
  --scope group_only \
  --iterations 3
```

Regression check against baseline:

```bash
python tests/performance/run_benchmark.py \
  --source /tmp/archiflow_perf \
  --iterations 3 \
  --baseline tests/performance/baseline_example.json \
  --max-time-regression 1.2 \
  --max-memory-regression 1.2
```

AsyncIO exploration probe:

```bash
python tests/performance/asyncio_probe.py \
  --source /tmp/archiflow_perf \
  --limit 1000 \
  --workers 8
```

## Phase 8.2 Real-World Run (10K+ Files)

Generate and benchmark a 10,000-file dataset:

```bash
python tests/performance/run_benchmark.py \
  --source /tmp/archiflow_realworld_10k \
  --generate \
  --files 10000 \
  --duplicate-ratio 0.2 \
  --same-size-ratio 0.1 \
  --iterations 1 \
  --output tests/performance/real_world_10k_benchmark.json
```

Current sample output file:

- `tests/performance/real_world_10k_benchmark.json`

## Phase 8.4 Baseline Files and Guidelines

Current baseline artifacts:

- `tests/performance/baseline_5k_group_only.json`
- `tests/performance/baseline_5k_group_and_dedupe.json`
- `tests/performance/baseline_10k_cold_group_and_dedupe.json`
- `tests/performance/baseline_10k_group_and_dedupe.json`

Regression gate example:

```bash
python tests/performance/run_benchmark.py \
  --source /tmp/archiflow_realworld_10k \
  --iterations 2 \
  --scope group_and_dedupe \
  --baseline tests/performance/baseline_10k_group_and_dedupe.json \
  --max-time-regression 1.2 \
  --max-memory-regression 1.2
```

Detailed performance expectations and optimization recommendations:

- `docs/development/phase8-performance-baselines.rst`
