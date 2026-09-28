# FHE Latency Optimization — Progress Repository

This repository records the ongoing work for the **Cloud-Ready Baseline FHE Inference with Initial Speed Optimizations** project. The repository focuses only on the FHE latency-optimization responsibility.

## Current status

The project is in progress. The literature and technology review has been completed for the initial phase, covering Concrete ML, Concrete, Orion, LOHEN, TFHE-BS, AEGIS, TFHE-rs, and related FHE benchmarking resources. The current code is a small reusable practice prototype that ranks possible latency-reduction methods according to expected impact, accuracy constraints, implementation effort, compatibility, and risk.

This repository does **not** claim that a native FHE backend has been modified or that a real encrypted-inference speedup has already been achieved. Actual measurements will be added after the team receives a Concrete ML-compatible model and completes the baseline compilation step.

## Project responsibility

The project team has separate work areas. The data/ML work includes dataset preprocessing, cleartext model training, feature preparation, and accuracy analysis. This repository contains the FHE optimization work: reviewing latency-reduction methods, deciding which methods are realistic for the project, and preparing the first optimization experiment.

The current teammate notebook uses CatBoost for a cleartext baseline. CatBoost is not listed as a built-in Concrete ML tree model. The supported tree-model documentation lists Decision Tree, Random Forest, and XGBoost model families.[1] Therefore, the future FHE experiment will use a Concrete ML-supported model unless the team successfully validates an ONNX conversion path.

## Repository structure

```text
fhe-latency-optimization-progress/
├── README.md
├── STATUS.md
├── src/
│   ├── simple_latency_optimizer.py
│   └── monitoring/
│       ├── resource_monitor.py
│       ├── profiler.py
│       └── metrics_store.py
├── backend/
│   └── app/
│       ├── main.py
│       ├── routes/
│       │   ├── fhe.py
│       │   └── monitoring.py
│       └── services/
│           ├── fhe_server.py
│           └── monitoring_service.py
├── docs/
│   ├── literature_review.md
│   ├── optimization_plan.md
│   ├── monitoring_system.md
│   └── monitoring_backend_integration.md
├── examples/
│   ├── example_output.txt
│   ├── monitor_test.py
│   ├── secure_client.py
│   └── export_concrete_model.py
├── model/
│   └── fhe_deployment/
├── monitoring_results/
└── artifacts/
    └── .gitkeep
```

## Current prototype

`src/simple_latency_optimizer.py` is a small, reusable practice module. It compares candidate methods using the following information:

| Field | Meaning |
|---|---|
| Baseline latency | Reference latency before the candidate method |
| Candidate latency | Latency after applying the candidate method |
| Accuracy | Candidate model accuracy or prediction agreement |
| Supported | Whether the selected FHE/compiler environment supports the method |
| Effort | Approximate student-level implementation effort |
| Score | Transparent ranking value used to select the next candidate |

The example methods are placeholders for practicing the optimization workflow. Their timing values are illustrative and must be replaced with measurements from the actual Concrete ML environment before any speedup is reported.

## Run the current practice prototype

From the repository root:

```bash
python3 src/simple_latency_optimizer.py
```

The program prints a ranked list of feasible and rejected candidates. It currently demonstrates that unsupported native bootstrapping changes and inaccurate low-bit candidates should not be selected merely because they appear faster.

## Planned next step

The next implementation phase is to obtain a Concrete ML-compatible model from the data/ML workstream. The team should provide the preprocessing steps, feature list, calibration data, model artifact, clear accuracy, and exact package versions. After that, the optimization work will compare the default model configuration with one supported candidate, such as representative calibration or a supported quantization setting.

The future experiment will record:

- Clear, simulated, and FHE execution mode where available.
- Baseline and candidate latency.
- Accuracy and prediction agreement.
- Throughput for repeated or batched inputs.
- Model/compiler version and hardware.
- Input/output and key artifact sizes when exposed by the runtime.

## Scope boundaries

The following items are intentionally marked as future or conditional work: native programmable-bootstrapping changes, direct Orion CKKS packing integration, AEGIS-style multi-GPU execution, and a new cryptographic scheme. These require substantially more backend, hardware, or security validation than the current student-level progress stage.

## References

[1]: https://docs.zama.org/concrete-ml/built-in-models/tree "Concrete ML official tree-based model support"

[2]: https://github.com/zama-ai/concrete-ml "Concrete ML repository"

[3]: https://github.com/zama-ai/concrete "Concrete TFHE compiler repository"

[4]: https://eprint.iacr.org/2025/713 "LOHEN research paper"

[5]: https://arxiv.org/html/2311.03470v3 "Orion research paper"


## Monitoring and backend integration

A reusable monitoring subsystem and FastAPI backend scaffold are now included on the monitoring integration branch. The monitoring code is intentionally separate from the ML prediction features: it measures the cost of encrypted execution rather than using CPU or RAM as XGBoost inputs.

The backend exposes:

- `GET /health`
- `GET /api/fhe/status`
- `POST /api/fhe/predict`
- `GET /api/monitor/latest`
- `GET /api/monitor/history`
- `GET /api/monitor/run/{run_id}`

The intended privacy-preserving deployment keeps client secret keys off the server. Client-side code encrypts the financial input, the FastAPI service runs the Concrete ML server artifact on ciphertext, and the client decrypts the encrypted result.

Run the standalone monitor smoke test with:

```bash
python examples/monitor_test.py
```

See `docs/monitoring_system.md` and `docs/monitoring_backend_integration.md` for the complete wiring plan. Real FHE performance results are still not claimed until the compiled Concrete ML model is exported and repeated measurements are collected.
