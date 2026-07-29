# Historical-descriptor and runtime revision checklist

Date: 2026-07-29

## Completed implementation work

- [x] Preserve the published CK4P-MSP feature contract and optimize only its implementation.
- [x] Add integer canonical k-mer encoding and batched P/MSP construction grouped by read length.
- [x] Verify numerical equivalence against the standalone reference implementation to floating-point tolerance.
- [x] Share P/MSP construction across combined methods instead of recomputing the same blocks.
- [x] Retain the fallback path for ambiguous, empty and invalid sequence inputs.
- [x] Avoid adaptive block weights, learned bin selection or any new model family.

## Completed experiments

- [x] Compare CK4P-MSP with PseKNC, NCP+ANF and PseEIIP under the same paired perturbation protocol.
- [x] Retain PseKNC's lower drift and lower dimension as an explicit boundary result.
- [x] Re-run implementation timing with warm-up, randomized method order, pre-timing garbage collection and one numerical-library thread.
- [x] Report medians and interquartile ranges across five repeats on the declared workstation.
- [x] Generate Supplementary Figure S12 with drift, grouped local-change readability, dimension and runtime.

## Completed manuscript constraints

- [x] State that minimum drift is not the sole representation objective.
- [x] Describe CK4P-MSP as an attributable stability-readability trade-off, not a universal winner.
- [x] Keep global shallow readout as a bounded readability probe rather than evidence of predictive superiority.
- [x] Distinguish canonical local-token composition from database-linked exact read identity.
- [x] Treat historical handcrafted descriptors as prior art and direct empirical boundaries, not as hidden negative results.
- [x] Keep runtime claims implementation- and hardware-specific.

## Verification

- [x] `smoke_tests/test_imports.py`
- [x] `smoke_tests/test_method_contract.py`
- [x] `smoke_tests/test_historical_descriptors.py`
- [x] `smoke_tests/test_repository_layout.py`
- [x] `smoke_tests/test_contract_artifacts.py`
- [x] Main and supplementary LaTeX compilation.
- [x] Page-by-page visual inspection of the main manuscript and Supplementary Data.

## External submission actions

- [ ] Confirm final ethics wording.
- [ ] Confirm funding and acknowledgements.
- [ ] Enable reviewer repository access.
- [ ] Mint and insert a public archival DOI when the release becomes public.
