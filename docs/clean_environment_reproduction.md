# Clean-environment reproduction record

This record documents the release verification performed outside the repository
working tree. It is a reproducibility record, not a replacement for the frozen
scientific results under `results/stage3/contract_v2/`.

## Environment

- Host platform: Windows
- Python: 3.13
- Environment: a fresh virtual environment created outside the repository
- Dependencies: `requirements-lock.txt`
- Verification date: 2026-08-04

## Commands

```powershell
$envDir = Join-Path $env:TEMP "ck4p-msp-repro-env"
python -m venv $envDir
& "$envDir\Scripts\python.exe" -m pip install -r requirements-lock.txt
& "$envDir\Scripts\python.exe" tools\reproduce_release.py --mode quick
& "$envDir\Scripts\python.exe" tools\reproduce_release.py --mode full
```

## Outcome

- Quick path: 10/10 smoke tests passed and release preflight passed.
- Full path: compact-baseline, grouped local-mutation, seven-group P/MSP,
  high-k compression, kNN-MI and short-read continuity commands all returned
  code 0.
- Observed wall time for the full path was approximately 39.5 minutes on the
  verification host. This is a host-specific reproduction time, not a claimed
  method benchmark.
- A second clean run of the kNN-MI and seven-block/binset outputs was bytewise
  identical to the first clean run. The current clean outputs were used to
  refresh the affected release summaries where the earlier frozen tables had
  stale columns or estimator values.

The generated verification directory is ignored by Git and is not part of the
public release. Users should expect substantially different wall times on other
hardware and should use the quick path first.
