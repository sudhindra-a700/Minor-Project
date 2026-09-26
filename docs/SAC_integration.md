# SAC integration

The baseline FHE notebook is `notebooks/FHE2_ConcreteML_Updated.ipynb`.

The reusable SAC module is `src/sac_optimizer.py`.

In the notebook, SAC should be inserted **after the train/validation/test split and before the existing Concrete ML compilation cell**. The current baseline uses the first 500 rows of `X_train` as calibration. For the experiment, generate an SAC-selected calibration set and run a separate benchmark using the same model, test data, hardware and Concrete ML version.

Keep the baseline notebook and optimization module separate so baseline FHE measurements remain independently reproducible.
