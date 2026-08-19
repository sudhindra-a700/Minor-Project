# Literature and Technology Review

## Purpose

The initial review focused on methods for reducing the cost of FHE inference and on deciding which methods can realistically be practiced in the current project.

## Findings

| Resource | Main idea reviewed | Decision |
|---|---|---|
| Concrete ML | Quantized ML models, representative compilation data, simulation, and FHE execution | Primary practical baseline |
| Concrete | Lower-level TFHE compiler and performance-analysis boundary | Study for later integration |
| LOHEN | Layer/configuration cost comparison and transition-aware selection | Use as inspiration for method ranking |
| Orion | Packing, graph planning, and refresh-placement concepts | Use as architectural reference; CKKS-specific details remain conditional |
| TFHE-BS | Native bootstrapping and block-binary key optimization | Future backend research |
| AEGIS | Multi-GPU encrypted Transformer scheduling | Future distributed-runtime research |
| TFHE-rs | High-performance Boolean and integer TFHE runtime | Future native microbenchmark target |
| HECO/T2 | Compiler IR and standardized cross-backend benchmarking | Architecture and methodology references |

## Practical conclusion

The first implementation should not attempt to modify bootstrapping or build a new compiler. A realistic student-level optimization contribution is to organize possible methods, apply correctness and compatibility constraints, and prepare a baseline-versus-candidate experiment.

The first candidate methods are representative calibration, a supported quantization comparison, and packing or batching analysis. Native bootstrapping, CKKS-specific packing, and multi-GPU execution are recorded as future work.

## Compatibility note

The teammate’s current notebook uses CatBoost. Concrete ML’s official tree-model documentation lists Decision Tree, Random Forest, and XGBoost model families but does not list CatBoost. A future model handoff must therefore confirm whether CatBoost can be imported successfully through an ONNX graph or provide a Concrete ML-supported replacement.

## References

- [Concrete ML](https://github.com/zama-ai/concrete-ml)
- [Concrete](https://github.com/zama-ai/concrete)
- [LOHEN](https://eprint.iacr.org/2025/713)
- [Orion](https://arxiv.org/html/2311.03470v3)
- [TFHE-BS](https://eprint.iacr.org/2023/958)
- [AEGIS](https://arxiv.org/html/2604.03425)
- [Concrete ML tree-model documentation](https://docs.zama.org/concrete-ml/built-in-models/tree)
