# FHE Monitoring System

## Purpose

The monitoring subsystem measures the computational cost of encrypted inference.
It is intentionally separate from the credit-risk XGBoost features.

The credit-risk model predicts a privacy-sensitive financial outcome. The monitor
records the cost of FHE itself: latency, CPU usage, RAM usage, and thread count.

## Modules

### `src/monitoring/resource_monitor.py`

Samples the machine every 0.10 seconds by default and records:

- system CPU usage
- current Python process CPU usage
- current Python process RSS memory
- total system RAM usage
- process thread count

### `src/monitoring/profiler.py`

Wraps one callable and measures both wall-clock latency and resource samples.

### `src/monitoring/metrics_store.py`

Stores:

- one summary row in `monitoring_results/runs.csv`
- one JSON file per run containing the summary and full CPU/RAM time series

## Runtime flow

```text
Encrypted request
      |
      v
FastAPI /api/fhe/predict
      |
      v
ResourceMonitor.start()
      |
      v
FHEModelServer.run(...)
      |
      v
ResourceMonitor.stop()
      |
      +--> summary metrics
      +--> full CPU/RAM samples
      |
      v
monitoring_results/
```

## What is measured on the server

- FHE server inference latency
- average and peak system CPU
- average and peak process CPU
- average and peak process RSS memory
- average and peak system RAM percentage
- peak process thread count

## What should be measured on the client

The final privacy design keeps encryption and decryption on the client, so those
costs should be measured there:

- key generation
- input encryption
- output decryption
- client CPU/RAM
- network round-trip time

The provided `examples/secure_client.py` measures encryption/decryption latency
and reports the server metrics returned in response headers.

## Important experimental rule

Do not claim that SAC reduces FHE cost until repeated Random-vs-SAC measurements
show a reproducible difference under the same model, input, machine, and runtime.
