# Literature Review

## 1. Overview

Fully Homomorphic Encryption (FHE) enables computation on encrypted data while keeping the input hidden from the party performing the computation. The foundational construction introduced by Gentry established the possibility of evaluating general computations over ciphertexts, although the original approach was too costly for routine machine-learning deployment [1]. Later work improved practicality through lattice-based constructions such as BGV and related schemes [3], while TFHE focused on efficient Boolean, integer, and programmable-bootstrapping operations [4]. CKKS introduced approximate arithmetic for real-valued numerical workloads and became influential for encrypted neural-network inference [5]. These foundations establish the privacy mechanism for the present project: a client can encrypt selected features of a private record, a remote service can evaluate a compatible model, and the client can recover the prediction without exposing the plaintext input to the cloud evaluator.

Early encrypted-machine-learning systems demonstrated the feasibility of privacy-preserving inference but also exposed the central performance challenge. CryptoNets showed that neural-network prediction could be performed over encrypted inputs, but the computational cost and latency were substantially higher than ordinary cleartext inference [6]. This trade-off remains important for the proposed project. FHE provides confidentiality during model evaluation, but every additional feature, operation, bit-width, ciphertext transfer, and cryptographic refresh can increase runtime. Therefore, the project should not treat encryption as a complete solution by itself. It must also establish a measurable baseline, separate client, server, and communication costs, and investigate a small latency optimization that preserves acceptable prediction quality.

## 2. Concrete ML as the practical implementation path

Concrete ML provides a practical bridge between conventional machine-learning development and FHE execution. It offers model APIs related to common machine-learning workflows, supports quantization and compilation into FHE circuits, and provides clear, simulated, and encrypted execution modes [7]. Its documented deployment workflow separates model development from client/server serving: the model is trained and compiled during development, client-side artifacts support key generation, encryption, decryption, and preprocessing, and server-side artifacts contain the compiled model used for encrypted execution [8] [9]. This division is directly relevant to the revised architecture. The client or frontend should encrypt a small feature vector before transmission, the cloud API should forward the ciphertext to the Concrete ML FHE service, and the client should decrypt the returned storage-policy prediction.

Concrete ML also makes the model-compatibility boundary explicit. A model must use supported classes or operations and must be compiled successfully before it can be treated as an FHE model. The current CatBoost notebook is therefore not automatically an FHE implementation. It can remain an earlier cleartext investigation, but the main experiment should use a small Concrete ML-supported classifier, such as LogisticRegression or another verified model [10]. Quantization and representative calibration are important because FHE circuits operate under restricted numerical representations. Lower-cost settings may reduce runtime, but they can also alter predictions; the candidate must therefore be checked against a cleartext reference before expensive compilation and encrypted benchmarking.

## 3. Research on FHE compiler and system optimization

Several state-of-the-art systems demonstrate that FHE latency can be reduced at different architectural layers. Orion is an automated FHE framework for deep learning that emphasizes graph analysis, ciphertext packing, and the placement of expensive bootstrap operations [11]. Its contribution is primarily a compiler and planning approach for CKKS-style deep-learning workloads. LOHEN applies layer-wise optimization and cost-aware configuration selection, illustrating that a single global cryptographic setting may not be ideal for every part of a neural network [12]. Faster TFHE bootstrapping with block binary keys addresses the native cryptographic backend by changing key representation and bootstrapping-related operations [13]. AEGIS addresses long-sequence encrypted Transformer inference using compiler-runtime co-design, multi-GPU placement, and communication/computation overlap [14].

These studies are valuable because they show where latency originates, but they do not all fit the present project. Orion and LOHEN assume model and cryptographic settings that are not interchangeable with a small Concrete ML experiment. TFHE bootstrapping research requires native backend and security-parameter expertise. AEGIS requires large Transformer workloads and multi-GPU hardware. Consequently, these methods should be cited as architectural motivation and future research context rather than presented as components already implemented by the team. The feasible first contribution is at the model/compiler boundary: select a supported model, compare a default configuration with one candidate calibration or quantization setting, and measure the result under fixed conditions.

## 4. Calibration, quantization, and early candidate screening

Calibration and quantization research is particularly relevant to a student-scale latency experiment because it can be studied without rewriting a cryptographic backend. CoverCal formulates calibration-data selection as a weighted coverage problem over outlier channels and uses a lightweight greedy procedure to select a compact calibration set [15]. SelectQ uses activation statistics, clustering, and distribution-distance measures to select calibration data for post-training quantization [16]. EMQ studies automated mixed-precision search and uses training-free proxies and early rejection to avoid fully evaluating poor candidates [17]. Although these works target broader neural-network quantization settings, their common lesson is applicable to the proposed optimizer: expensive candidates should be screened using inexpensive quality and compatibility checks before they are compiled and measured under FHE.

For the present project, the defensible contribution is a lightweight adaptation rather than a claim of a new calibration theory. The custom optimizer can rank a small set of candidate configurations, select a deterministic representative calibration subset, screen candidates using cleartext prediction agreement or quantization error, and send only feasible candidates to Concrete ML compilation. The final candidate must still be evaluated with actual encrypted inference. A candidate that appears promising in cleartext but fails compilation, changes the storage-policy prediction excessively, or increases measured latency must be rejected. This creates a simple but rigorous connection between the literature and the individual FHE-latency responsibility.

## 5. Backends, compilers, and benchmarking systems

The remaining reviewed systems clarify the boundaries of implementation. The Concrete compiler provides a lower-level path from computation graphs to TFHE circuits and runtime execution [10]. TFHE-rs provides a native Boolean/integer FHE ecosystem and useful microbenchmarking ideas, but it is not automatically a replacement for Concrete ML [18]. HECO and T2 demonstrate intermediate-representation and cross-backend compiler approaches [19] [20], while OpenFHE provides a multi-scheme runtime useful for comparative FHE research [21]. These systems are relevant when studying compiler lowering, backend portability, or cryptographic kernels, but using them all in one B.Tech prototype would make the project unmanageably broad.

Benchmarking literature provides the practical discipline needed to evaluate the proposed system. The FHE Benchmarking Suite separates setup, key generation, preprocessing, encryption, server computation, decryption, communication, correctness, and quality metrics [22]. This stage-wise view is important because an apparent server-side improvement may disappear when key generation, encryption, network transfer, or decryption is included. The project should therefore report at least encryption time, server-side FHE time, decryption time, and total request time. The same input set, hardware, software version, preprocessing, model, and number of trials must be used for both the default baseline and the candidate configuration.

## 6. Literature gap and project position

The literature contains powerful but specialized solutions: compiler-level packing and scheduling, layer-wise configuration search, cryptographic bootstrapping improvements, multi-GPU runtime design, calibration selection, and standardized benchmarking. The project does not attempt to reproduce these systems. Instead, it positions itself as a small, cloud-ready FHE inference prototype that combines a supported Concrete ML model, a synthetic private-record use case, a client/server encrypted-inference workflow, and an initial latency-screening module.

The project-specific research gap should be stated cautiously. The team has not yet demonstrated that its proposed combination is a new state-of-the-art algorithm. The defensible claim is that it applies established ideas—representative calibration, candidate screening, quantization awareness, correctness checking, and stage-wise benchmarking—to a manageable Concrete ML FHE workflow. Any stronger novelty claim would require implementation, comparison with relevant baselines, and a more complete review of current literature.

## 7. Comparative analysis

| Method or source | Main approach | Main advantage | Main limitation for this project | Relevance to the proposed work |
|---|---|---|---|---|
| Gentry FHE foundations [1] [2] | General computation over encrypted data | Establishes the core privacy capability | Original constructions are too expensive for direct student deployment | Explains why encrypted inference is possible |
| BGV/LWE line of work [3] | Lattice-based efficient FHE | Improved practicality and security foundations | Scheme details are not directly interchangeable with Concrete ML | Cryptographic background |
| TFHE [4] | Fast Boolean/integer operations and programmable bootstrapping | Strong fit for exact small-integer computation | Bootstrapping remains costly and backend-specific | Background for Concrete’s TFHE direction |
| CKKS [5] | Approximate arithmetic over packed values | Useful for numerical neural-network workloads | Different scheme assumptions from the first Concrete ML path | Context for Orion and LOHEN |
| CryptoNets [6] | Encrypted neural-network inference | Early proof that ML inference can run over ciphertext | High computational and latency cost | Motivates latency optimization |
| Concrete ML [7–9] | Model API, quantization, compilation, and client/server FHE deployment | Most practical first implementation path | Only supported models/operators compile | Primary framework |
| Concrete compiler [10] | Low-level graph-to-FHE compilation and runtime | Exposes compiler/backend boundary | Native compiler changes are beyond the first milestone | Explains where optimization could eventually occur |
| Orion [11] | Packing, graph analysis, and bootstrap placement | Reduces deep-learning execution cost through planning | CKKS/deep-learning focus; not a drop-in Concrete ML backend | Architecture inspiration |
| LOHEN [12] | Layer-wise cost-aware configuration selection | Makes per-layer performance/quality trade-offs explicit | More complex model and scheme assumptions | Inspiration for cost-aware selection |
| TFHE-BS [13] | Block-binary keys and faster bootstrapping | Targets native cryptographic cost | Requires backend and security-level work | Future research context |
| AEGIS [14] | Multi-GPU compiler-runtime co-design | Addresses large encrypted Transformer workloads | Requires large models and multi-GPU hardware | Future system-level context |
| CoverCal [15] | Weighted coverage-based calibration selection | Reduces calibration-selection effort | Primarily developed for broader PTQ settings | Inspiration for representative sampling |
| SelectQ [16] | Activation statistics and clustering for calibration | Selects calibration samples by distribution information | More complex than required for the first prototype | Calibration-selection reference |
| EMQ [17] | Training-free proxy search and early rejection | Avoids expensive evaluation of poor candidates | Full mixed-precision search is too broad for first milestone | Inspiration for early screening |
| TFHE-rs [18] | Native Boolean/integer runtime and APIs | Useful for kernel-level runtime studies | Not a direct Concrete ML replacement | Optional backend reference |
| HECO and T2 [19] [20] | Intermediate representation and cross-backend compilation | Shows how portability and compiler passes can be organized | Too broad for current implementation | Future compiler context |
| OpenFHE [21] | Multi-scheme FHE runtime | Useful for cross-backend research | Different APIs and assumptions from Concrete ML | Comparative reference only |
| FHE Benchmarking Suite [22] | Stage-wise FHE and ML-inference measurement | Supports fair latency and correctness reporting | Benchmark framework, not an optimizer | Evaluation template |

## 8. Implications for the proposed architecture and experiment

The literature supports a four-part architecture: a frontend/client, a cloud API, a Concrete ML FHE model service, and a black-box latency optimizer connected to the compilation and benchmarking loop. The client should encrypt the selected synthetic-record features before sending them to the cloud. The server should execute the compiled model on encrypted input and return an encrypted storage-policy result. The optimizer should propose or rank a small number of configurations, while the Concrete ML compiler remains responsible for producing the FHE circuit.

The first experiment should use a synthetic record with a small number of numerical or coded fields and a demonstration-only target such as standard, restricted, or high-protection storage. It should not use real Aadhaar numbers, addresses, or personally identifiable records. Large files should be protected using ordinary client-side encryption; FHE should be used for the smaller feature vector required for policy prediction. This keeps the research question technically meaningful and within the available student-level scope.

The expected research sequence is therefore: prepare the synthetic dataset; train and evaluate a small supported cleartext model; compile and execute the default Concrete ML FHE model; measure stage-wise latency and prediction agreement; screen one calibration or quantization candidate; compile the surviving candidate; compare results fairly; and connect the validated local path to a minimal API. Until these steps are completed, the project should claim a literature-grounded design and prototype plan, not a demonstrated cloud speedup.

## References

[1]: [Gentry, “Fully Homomorphic Encryption Using Ideal Lattices”](https://dl.acm.org/doi/10.1145/1536414.1536440)  
[2]: [Gentry, “A Fully Homomorphic Encryption Scheme”](https://crypto.stanford.edu/craig/craig-thesis.pdf)  
[3]: [Brakerski and Vaikuntanathan, “Efficient Fully Homomorphic Encryption from (Standard) LWE”](https://eprint.iacr.org/2011/277)  
[4]: [Chillotti et al., “TFHE: Fast Fully Homomorphic Encryption over the Torus”](https://eprint.iacr.org/2018/421)  
[5]: [Cheon et al., “Homomorphic Encryption for Arithmetic of Approximate Numbers”](https://eprint.iacr.org/2016/421)  
[6]: [Gilad-Bachrach et al., “CryptoNets”](https://proceedings.mlr.press/v48/gilad-bachrach16.html)  
[7]: [Zama, Concrete ML Documentation](https://docs.zama.org/concrete-ml)  
[8]: [Zama, Concrete ML Linear Models](https://docs.zama.org/concrete-ml/built-in-models/linear)  
[9]: [Zama, Concrete ML Client/Server Deployment](https://docs.zama.org/concrete-ml/guides/client_server)  
[10]: [Zama, Concrete Compiler Repository](https://github.com/zama-ai/concrete)  
[11]: [Orion: An Automated FHE Framework for Deep Learning](https://arxiv.org/abs/2311.03470)  
[12]: [LOHEN, USENIX Security 2025](https://www.usenix.org/conference/usenixsecurity25/presentation/nam-lohen)  
[13]: [Faster TFHE Bootstrapping with Block Binary Keys](https://eprint.iacr.org/2023/958)  
[14]: [AEGIS: Scaling Long-Sequence Homomorphic Encrypted Transformer Inference](https://arxiv.org/abs/2604.03425)  
[15]: [CoverCal: Coverage-Based Calibration for Post-Training Quantization](https://arxiv.org/abs/2604.24008)  
[16]: [SelectQ: Calibration Data Selection for Post-Training Quantization](https://www.mi-research.net/en/article/doi/10.1007/s11633-024-1518-0)  
[17]: [EMQ: Evolving Training-Free Proxies for Automated Mixed-Precision Quantization](https://openaccess.thecvf.com/content/ICCV2023/papers/Dong_EMQ_Evolving_Training-free_Proxies_for_Automated_Mixed_Precision_Quantization_ICCV_2023_paper.pdf)  
[18]: [Zama, TFHE-rs Repository](https://github.com/zama-ai/tfhe-rs)  
[19]: [HECO FHE Compiler Repository](https://github.com/MarbleHE/HECO)  
[20]: [T2 FHE Compiler and Benchmarks](https://github.com/TrustworthyComputing/T2-FHE-Compiler-and-Benchmarks)  
[21]: [OpenFHE Project](https://openfhe.org/)  
[22]: [FHE Benchmarking Suite](https://fhe-benchmarking.org/)
