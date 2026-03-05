# Performance Suite

This folder contains the Phase 3.5 benchmark suite:

- Synthetic dataset generator
- Speed benchmark runner
- Peak memory profiling (`tracemalloc`)
- Regression detection against baseline JSON

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
