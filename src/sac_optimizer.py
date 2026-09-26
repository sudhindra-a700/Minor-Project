"""SAC - Sensitivity-Adaptive Calibration.
Standalone calibration-selection module for the Concrete ML/FHE experiment.
"""
from dataclasses import dataclass
from pathlib import Path
from typing import Optional
import numpy as np
import pandas as pd
from xgboost import XGBClassifier

@dataclass
class SACConfig:
    perturbation_scale: float = 0.05
    calibration_size: int = 500
    sensitivity_weight: float = 0.70
    uncertainty_weight: float = 0.30
    random_state: int = 42

class SACOptimizer:
    def __init__(self, config: Optional[SACConfig] = None, output_dir="artifacts/sac"):
        self.config = config or SACConfig()
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.model = None
        self.feature_names = None
        self.feature_sensitivity_ = None
        self.sample_sensitivity_ = None

    @staticmethod
    def _df(X, names=None):
        if isinstance(X, pd.DataFrame): return X.copy()
        X = np.asarray(X)
        if names is None: names = [f"feature_{i}" for i in range(X.shape[1])]
        return pd.DataFrame(X, columns=names)

    @staticmethod
    def _minmax(v):
        v = np.asarray(v, dtype=float); lo, hi = np.nanmin(v), np.nanmax(v)
        return np.zeros_like(v) if np.isclose(lo, hi) else (v-lo)/(hi-lo)

    def fit_reference_model(self, X_train, y_train, model=None):
        X = self._df(X_train); self.feature_names = list(X.columns)
        self.model = model or XGBClassifier(
            n_estimators=100, max_depth=4, learning_rate=0.05,
            min_child_weight=2, subsample=.90, colsample_bytree=.90,
            objective="binary:logistic", eval_metric="logloss",
            tree_method="hist", random_state=self.config.random_state, n_jobs=-1)
        self.model.fit(X, np.asarray(y_train)); return self

    def compute_feature_sensitivity(self, X_reference):
        if self.model is None: raise RuntimeError("Call fit_reference_model() first.")
        X = self._df(X_reference, self.feature_names); a = X.to_numpy(np.float32)
        std = np.std(a, axis=0); std = np.where(std > 0, std, 1.0)
        scores = []
        for j in range(a.shape[1]):
            d = self.config.perturbation_scale * std[j]
            xp, xm = a.copy(), a.copy(); xp[:,j] += d; xm[:,j] -= d
            pp = self.model.predict_proba(xp)[:,1]; pm = self.model.predict_proba(xm)[:,1]
            scores.append(float(np.mean(np.abs(pp-pm))))
        out = pd.DataFrame({"feature":self.feature_names,"sensitivity":scores}).sort_values("sensitivity",ascending=False).reset_index(drop=True)
        self.feature_sensitivity_ = out; out.to_csv(self.output_dir/"SAC_feature_sensitivity.csv",index=False); return out

    def compute_sample_sensitivity(self, X_reference):
        if self.feature_sensitivity_ is None: self.compute_feature_sensitivity(X_reference)
        X = self._df(X_reference, self.feature_names); a = X.to_numpy(np.float32)
        smap = dict(zip(self.feature_sensitivity_.feature, self.feature_sensitivity_.sensitivity))
        fs = self._minmax([smap[f] for f in self.feature_names])
        nx = np.column_stack([self._minmax(a[:,j]) for j in range(a.shape[1])])
        feature_component = self._minmax(nx @ fs)
        p = self.model.predict_proba(X)[:,1]
        uncertainty = self._minmax(1.0 - np.abs(2*p-1.0))
        aw, bw = self.config.sensitivity_weight, self.config.uncertainty_weight
        if aw+bw <= 0: raise ValueError("Weights must sum to > 0.")
        score = (aw*feature_component + bw*uncertainty)/(aw+bw)
        out = pd.DataFrame({"sample_index":np.arange(len(X)),"feature_sensitivity_component":feature_component,"uncertainty_component":uncertainty,"sample_sensitivity":score})
        self.sample_sensitivity_ = out; out.to_csv(self.output_dir/"SAC_sample_sensitivity.csv",index=False); return out

    def select_calibration_data(self, X_train, y_train):
        X = self._df(X_train, self.feature_names); y = np.asarray(y_train); n=len(X); k=min(self.config.calibration_size,n)
        if self.sample_sensitivity_ is None: self.compute_sample_sensitivity(X)
        rng=np.random.default_rng(self.config.random_state)
        p=self.sample_sensitivity_.sample_sensitivity.to_numpy()+1e-8; p/=p.sum()
        selected=np.sort(rng.choice(n,size=k,replace=False,p=p)); random_selected=np.sort(rng.choice(n,size=k,replace=False))
        sac=X.iloc[selected].copy(); random=X.iloc[random_selected].copy()
        sac.to_csv(self.output_dir/"SAC_calibration_dataset.csv",index=False)
        random.to_csv(self.output_dir/"Random_calibration_dataset.csv",index=False)
        return sac, y[selected], random

    def run(self, X_train, y_train):
        self.fit_reference_model(X_train,y_train)
        self.compute_feature_sensitivity(X_train)
        self.compute_sample_sensitivity(X_train)
        return self.select_calibration_data(X_train,y_train)
