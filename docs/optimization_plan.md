# Optimization Plan

## Current stage

The current stage is a planning and practice stage. The repository contains a simple method selector with illustrative latency values. It is intended to demonstrate the optimization workflow while the Concrete ML-compatible model and runtime environment are being finalized.

## First experiment

The first real experiment will compare a default supported Concrete ML model with one candidate method. The same model, calibration data, test samples, hardware, and repetition count will be used for both configurations.

The comparison will record baseline latency, candidate latency, accuracy, prediction agreement, and the exact model/compiler configuration. If the runtime exposes them, input/output ciphertext sizes and key artifact sizes will also be recorded.

## Candidate selection rule

A candidate is suitable only when it is supported by the chosen runtime, meets the minimum accuracy or agreement requirement, and is realistic for the available hardware and project schedule. A method is not selected only because it has a large theoretical speedup.

## Future experiment sequence

1. Obtain a supported model and preprocessing handoff.
2. Compile and run the default configuration.
3. Record the baseline result.
4. Apply one candidate method.
5. Run the same correctness and latency measurements.
6. Keep or reject the candidate based on the measured result.
7. Document the result and limitations.

## Expected contribution

The expected contribution at this stage is a transparent and reusable process for selecting and testing latency-reduction methods. The project will report a real optimization only after a candidate has been compiled, executed, and compared with the baseline.
