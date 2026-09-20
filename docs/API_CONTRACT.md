# API contract

The edge service is available at `http://127.0.0.1:8080/api/v1` in demo mode. It exposes health, sessions, observations, decisions, interventions, feedback, explanations, experiments and evidence export. The coordinator runs at `http://127.0.0.1:8100` and owns experiment jobs and model aggregation. The browser receives durable observations over the edge WebSocket stream with monotonically increasing sequence values and catch-up after reconnect.

All replay signals are labelled **Synthetic**. User actions are labelled **Manual feedback**. Missing values remain null; a primary-channel coverage failure returns an abstention reason. Local HTTP is identified in the UI. Secure-demo uses HTTPS with a project-local CA, and inter-service requests verify that CA.

State-changing routes validate request models. The WebSocket accepts the configured loopback origin, rejects mismatched origins, and the client deduplicates event IDs. The coordinator accepts parameter updates, record counts and metadata; it does not receive raw training windows.
