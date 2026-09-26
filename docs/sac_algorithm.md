# SAC — Sensitivity-Adaptive Calibration

SAC is a model-aware calibration-data selection method for the Concrete ML/FHE workflow. It operates **before Concrete ML compilation** and does not modify the cryptographic backend.

Pipeline: `X_train → reference XGBoost → feature sensitivity → sample sensitivity → weighted calibration sampling → Concrete ML compilation → FHE inference`.

For feature j, sensitivity is estimated by perturbing that feature in both directions and measuring the change in predicted probability:

`S_j = mean(|P_plus - P_minus|)`

Sample sensitivity combines the feature-sensitivity component with prediction uncertainty. The resulting scores define sampling probabilities for the calibration set.

Recommended controlled experiment:
1. Random calibration
2. Uncertainty-only calibration
3. Feature-sensitivity calibration
4. SAC combined calibration

Measure compilation time, key generation, encryption, FHE inference, decryption, plaintext accuracy, FHE accuracy, plaintext/FHE agreement, and measurable resource usage.

SAC currently selects calibration samples. It does **not** implement per-feature cryptographic precision, ciphertext packing control, bootstrapping optimization, or changes to the Concrete ML cryptographic backend.
