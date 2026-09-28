"""Export an already-trained and already-compiled Concrete ML model.

Run this after Random or SAC calibration compilation. Use separate deployment
directories when benchmarking both methods.
"""

from pathlib import Path

from concrete.ml.deployment import FHEModelDev

# Replace this placeholder with the compiled Concrete ML XGBoost object from
# your notebook or training module.
concrete_model = None

if concrete_model is None:
    raise RuntimeError(
        "Assign the already-trained and compiled Concrete ML model to concrete_model."
    )

output_dir = Path("model/fhe_deployment")
output_dir.mkdir(parents=True, exist_ok=True)

if any(output_dir.iterdir()):
    raise RuntimeError(
        "model/fhe_deployment must be empty before FHEModelDev.save()."
    )

FHEModelDev(
    path_dir=str(output_dir),
    model=concrete_model,
).save()

print("Saved Concrete ML deployment artifacts to:", output_dir)
