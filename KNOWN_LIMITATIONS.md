# Known limitations

- This is a local research prototype, not medical software.
- All executed model and federation results use seeded synthetic data. WESAD has not been acquired, imported or evaluated.
- No physical sensors, embedded hardware, haptics, cloud deployment, hospital system or wearable integration is present.
- The first held-out neural and federated runs have balanced accuracy 0.50. The tree's perfect synthetic score reflects an easily separable artificial generator and is not evidence of real-world utility.
- Differential privacy is example-level for non-overlapping 30-second synthetic windows. Opacus ran in experimental non-cryptographic randomness mode. It does not provide patient-level privacy or secure aggregation.
- Browser flows were exercised in the actual app at desktop and narrow widths. Keyboard focus, WebSocket updates, prompt feedback, explanations, federation jobs, restart persistence, and evidence views were inspected. Automated E2E coverage is implemented via Playwright using Chromium, though comprehensive cross-browser matrix testing and a recorded demo video are still absent.
- The WESAD offline adapter is tested with representative arrays, but no real subject file has been imported. No recorded-data metric is claimed.
- Coordinator jobs are local processes on one machine. There is no production database migration strategy, authentication system, secure aggregation, public deployment or multi-host test.
- Secure-demo verifies a project-local CA for loopback service requests and rejects the same certificate under the default trust store. The CA is not installed into the browser or operating-system trust store.
- The frontend production bundle is about 632 kB before gzip and Vite reports a chunk-size advisory. Formal decision-to-render p95 measurement and a real demo recording remain unverified.
