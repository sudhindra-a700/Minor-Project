"""Reference client for privacy-preserving Concrete ML inference.

The client keeps its secret key locally, encrypts the financial input, sends only
ciphertext + evaluation keys to the backend, receives encrypted output, and
decrypts locally.
"""

import time
from pathlib import Path

import numpy as np
import psutil
import requests
from concrete.ml.deployment import FHEModelClient

BACKEND = "http://127.0.0.1:8000"
DEPLOYMENT_DIR = Path("model/fhe_deployment")
KEY_DIR = Path(".client_keys")


def timed(fn, *args):
    process = psutil.Process()
    before_ram = process.memory_info().rss / (1024 ** 2)
    start = time.perf_counter()
    result = fn(*args)
    elapsed = time.perf_counter() - start
    after_ram = process.memory_info().rss / (1024 ** 2)
    return result, elapsed, max(before_ram, after_ram)


client = FHEModelClient(
    path_dir=str(DEPLOYMENT_DIR),
    key_dir=str(KEY_DIR),
)

evaluation_keys = client.get_serialized_evaluation_keys()

# Must match the model's 13-feature training order.
x = np.array([[
    31,        # age
    65000,     # monthly_income
    5.0,       # employment_years
    0,         # employment_type_code
    120000,    # existing_debt
    250000,    # loan_amount
    36,        # loan_term_months
    720,       # credit_score
    8.0,       # credit_history_years
    0,         # missed_payments_12m
    2,         # num_open_credit_accounts
    0.1538,    # debt_to_income_ratio
    0.1300,    # emi_to_income_ratio
]], dtype=np.float32)

encrypted_data, encryption_s, encryption_ram_mb = timed(
    client.quantize_encrypt_serialize,
    x,
)

network_start = time.perf_counter()
response = requests.post(
    f"{BACKEND}/api/fhe/predict",
    files={
        "encrypted_data": (
            "encrypted.bin",
            encrypted_data,
            "application/octet-stream",
        ),
        "evaluation_keys": (
            "evaluation_keys.bin",
            evaluation_keys,
            "application/octet-stream",
        ),
    },
    timeout=600,
)
network_roundtrip_s = time.perf_counter() - network_start
response.raise_for_status()

prediction, decryption_s, decryption_ram_mb = timed(
    client.deserialize_decrypt_dequantize,
    response.content,
)

print("Decrypted model output:", prediction)
print("Client encryption time (s):", round(encryption_s, 6))
print("Client decryption time (s):", round(decryption_s, 6))
print("Network round-trip time (s):", round(network_roundtrip_s, 6))
print("Encryption process RAM (MB):", round(encryption_ram_mb, 3))
print("Decryption process RAM (MB):", round(decryption_ram_mb, 3))
print("Server run ID:", response.headers.get("X-FHE-Run-Id"))
print("Server FHE latency:", response.headers.get("X-FHE-Latency-Seconds"))
print("Server peak CPU:", response.headers.get("X-Peak-CPU-Percent"))
print("Server peak RAM MB:", response.headers.get("X-Peak-RAM-MB"))
