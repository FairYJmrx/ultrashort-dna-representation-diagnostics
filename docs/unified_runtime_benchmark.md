# Unified Long-Duration Runtime Benchmark

## Purpose

This benchmark is the only runtime source used by the manuscript. Earlier
historical-descriptor and positional-kmer candidate timing files are retained
for provenance, but their shorter protocols are not pooled with this result.

## Primary contract

- Input: one seeded batch of 10,000 clean 75-bp sequence strings.
- Source pool: 600 public WGS-derived clean reads, sampled with replacement.
- Timed region: in-memory sequence strings to the returned feature matrix.
- Excluded work: disk input/output, result serialization and plotting.
- Warm-up: one untimed 100-read call per route.
- Scheduling: seeded randomized round-robin order.
- Runtime floor: at least 120 cumulative timed seconds and five calls per route.
- Process policy: one process, one numerical-library thread and garbage
  collection before each call.
- Comparative statistic: full-run median and interquartile range.
- Load diagnostic: second-half/first-half median ratio. This ratio describes
  workstation-state drift and must not be used to rank methods.
- Scaling check: one separate actual 100,000-read pass per route.

The benchmark covers CK4, CK4+P, CK4P-MSP, CK4P-MSP-PKM, hashed k=15,
MinHash k=15, sparse random projection of k=15, PseKNC, NCP+ANF and PseEIIP.

## Reproduction

```powershell
.\.venv\Scripts\python.exe experiments\audits\run_unified_runtime_benchmark.py `
  --output-dir results\stage3\contract_v2\unified_runtime_benchmark `
  --target-seconds 120 --minimum-repeats 5 --skip-scaling

.\.venv\Scripts\python.exe experiments\audits\run_unified_runtime_benchmark.py `
  --output-dir results\stage3\contract_v2\unified_runtime_scaling_pass `
  --scaling-only
```

## Outputs

- `unified_runtime_raw.csv`: every 10,000-read timed call.
- `unified_runtime_summary.csv`: full-run and load-drift summaries.
- `unified_runtime_benchmark_run.json`: hardware, software and protocol metadata.
- `unified_runtime_scaling.csv`: one 100,000-read scaling pass per route.

Runtime is implementation- and hardware-specific. The reported values are
engineering measurements, not hardware-independent algorithmic complexity.
