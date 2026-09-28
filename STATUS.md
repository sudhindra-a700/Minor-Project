# Project Status

## Completed

- Completed the initial literature and technology review of FHE latency challenges and optimization approaches.
- Compared Concrete ML, Concrete, Orion, LOHEN, TFHE-BS, AEGIS, TFHE-rs, HECO, T2, OpenFHE, and FHE benchmarking resources.
- Identified the difference between model/compiler-level optimization and native cryptographic-backend optimization.
- Selected representative calibration, supported quantization comparison, and packing/batching analysis as realistic first-phase methods.
- Created and ran a small Python method-selection prototype.
- Documented that CatBoost from the cleartext teammate notebook is not listed as a built-in Concrete ML tree model.

## In progress

- Obtaining a Concrete ML-compatible model and preprocessing handoff from the data/ML workstream.
- Confirming the exact Concrete ML and Python versions for the first FHE compilation experiment.
- Replacing illustrative values in the practice prototype with real baseline and candidate measurements.

## Not yet claimed

This repository does not yet claim a real FHE speedup, encrypted CatBoost inference, a native bootstrapping optimization, direct Orion integration, or multi-GPU execution. Those claims require additional implementation and validation.

## Next milestone

Compile one small Concrete ML-supported model, measure its default latency, test one supported candidate method, and compare correctness and latency using the same inputs and hardware.


## Monitoring/backend integration branch

- Added reusable CPU/RAM monitoring modules under `src/monitoring/`.
- Added per-call profiling and CSV/JSON metric storage.
- Added a FastAPI scaffold for encrypted Concrete ML server inference.
- Added monitoring API endpoints for latest run, history, and detailed CPU/RAM samples.
- Added a client-side reference script for encrypted request/decryption flow.
- Added model-export and monitoring smoke-test examples.
- Added documentation for local backend integration and later GCP deployment.

The monitoring code is implemented as infrastructure, but real FHE measurements still require an exported compiled Concrete ML model. No Random-vs-SAC speedup is claimed by these code changes alone.
