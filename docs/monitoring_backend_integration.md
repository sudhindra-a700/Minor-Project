# Monitoring and Backend Integration

## Recommended repository placement

```text
Minor-Project/
├── backend/
│   └── app/
│       ├── main.py
│       ├── config.py
│       ├── routes/
│       │   ├── fhe.py
│       │   └── monitoring.py
│       └── services/
│           ├── fhe_server.py
│           └── monitoring_service.py
├── src/
│   ├── simple_latency_optimizer.py
│   └── monitoring/
│       ├── resource_monitor.py
│       ├── profiler.py
│       └── metrics_store.py
├── examples/
│   ├── monitor_test.py
│   ├── secure_client.py
│   └── export_concrete_model.py
├── model/fhe_deployment/
├── monitoring_results/
└── docs/
```

## Privacy-preserving request flow

```text
Client laptop
  FHEModelClient
      |
      | quantize + encrypt
      | secret key stays local
      v
encrypted_data + evaluation keys
      |
      v
FastAPI backend
      |
      v
FHEModelServer.run(...)
      |
      +--> monitoring profiler
      |      ├ CPU
      |      ├ RAM
      |      └ latency
      |
      v
encrypted result
      |
      v
Client laptop
  decrypt + dequantize
      |
      v
credit-risk output
```

## API endpoints

- `GET /health`
- `GET /api/fhe/status`
- `POST /api/fhe/predict`
- `GET /api/monitor/latest`
- `GET /api/monitor/history?limit=50`
- `GET /api/monitor/run/{run_id}`

## Local setup

From the repository root:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r backend\requirements.txt
pip install concrete-ml
uvicorn backend.app.main:app --reload --port 8000
```

Open FastAPI docs:

```text
http://127.0.0.1:8000/docs
```

## Smoke-test monitoring without Concrete ML

```powershell
python examples\monitor_test.py
```

## Export a compiled model

After model training and Concrete ML compilation:

```python
from concrete.ml.deployment import FHEModelDev

dev = FHEModelDev(
    path_dir="model/fhe_deployment",
    model=concrete_model,
)
dev.save()
```

For Random-vs-SAC benchmarking, use separate deployment folders so one artifact
set does not overwrite the other.

## Frontend integration

History:

```javascript
const runs = await fetch(
  "http://127.0.0.1:8000/api/monitor/history?limit=50"
).then(r => r.json());
```

Detailed CPU/RAM samples:

```javascript
const detail = await fetch(
  `http://127.0.0.1:8000/api/monitor/run/${runId}`
).then(r => r.json());

const points = detail.samples;
```

The frontend should plot measured values directly and must not hard-code example
CPU, RAM, or latency numbers.

## GCP notes

For a later GCP deployment:

1. Deploy the FastAPI service together with the compatible Concrete ML
   server-side deployment artifact.
2. Keep client secret keys off GCP.
3. Use HTTPS.
4. For multiple backend instances, replace local CSV/JSON storage with a shared
   datastore such as Firestore, Cloud SQL, or BigQuery.
5. Keep the Concrete ML version and CPU architecture compatible with the
   compiled artifact.
