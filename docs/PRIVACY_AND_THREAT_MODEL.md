# Privacy and threat model

Private client updates use Opacus per-example gradient clipping (`max_grad_norm=1.0`), Gaussian noise (`noise_multiplier=1.2`), Poisson sampling and an RDP accountant. The privacy unit is one non-overlapping 30-second synthetic window. Each client currently records twelve optimizer steps, epsilon 5.4077881908 at delta 1e-5. The maximum client epsilon is the summary; disjoint-client values are not summed.

The accountant ledger persists under each client runtime directory and composes across new experiment IDs. A projected-step budget guard prevents a new local epoch if it would exceed epsilon 8. Secure randomness was unavailable, so the executed result is explicitly experimental and non-cryptographic.

Same-laptop process separation is not a security boundary against the host administrator. The implementation has no secure aggregation, patient-level privacy, Byzantine robustness, hardware attestation or public-network hardening.

The `secure-demo` launcher generates a project-local CA and a seven-day server certificate with `localhost` and `127.0.0.1` subject alternative names. Edge-to-coordinator requests verify that CA. The CA is never installed into the operating-system trust store, and an untrusted default-store request was confirmed to fail.
