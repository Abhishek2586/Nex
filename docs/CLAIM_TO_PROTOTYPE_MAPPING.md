# Claim to Prototype Mapping

This document maps the conceptual system architecture (often described in patent applications or system design documents) to the concrete implementation in the current NEXORA software prototype.

It clearly delineates what is actively demonstrated in software versus what represents the future physical embodiment.

| Conceptual System Block | Description | Current Prototype Implementation (Software) | Future Embodiment (Hardware) |
| :--- | :--- | :--- | :--- |
| **Physiological Sensors** | Captures EDA and Skin Temperature. | **Simulated:** Uses synthetic data generators or replays existing datasets (e.g., WESAD) to inject data into the system. | Wrist-worn smart strap with physical EDA and Temperature sensors. |
| **Biomechanical Sensors** | Captures Movement and Posture. | **Simulated:** Uses synthetic data generators (acceleration magnitude, discrete posture states). | Wrist-worn IMU (Movement) and optional upper-back clip/patch (Posture). |
| **Local Feature Extraction** | Processes raw signals into features (e.g., EDA peaks, temperature slopes). | **Implemented:** Python-based extraction pipeline (`src/nexora/features/extract.py`). | Embedded software on wearable or companion mobile app. |
| **Edge Inference Engine** | Runs the machine learning model to infer stress states locally. | **Implemented:** PyTorch model running locally within the client process (`src/nexora/edge/inference.py`). | Inference engine deployed on companion mobile app or edge device. |
| **Contextual Policy Engine** | Determines if/when to intervene based on stress score and context. | **Implemented:** Python rule-based engine suppressing/triggering interventions based on thresholds and state. | Same logic deployed in companion app. |
| **Intervention Interface** | Delivers prompts to the user. | **Implemented:** Web-based "Participant App" UI. | Mobile app notifications, smartwatch haptics/display. |
| **Differential Privacy (DP)** | Adds statistical noise to model updates. | **Implemented:** Uses PyTorch Opacus for DP accounting and noise addition during local training. | DP applied locally before transmission. |
| **Federated Coordinator** | Aggregates model updates from multiple clients. | **Implemented:** Local Python process (`src/nexora/federated/server.py`) managing local client processes. | Cloud-based server. |
| **Secure Aggregation** | Cryptographically secures updates so the coordinator only sees the sum. | **Not Implemented:** Out of scope for current prototype. | Cryptographic protocols (e.g., SecAgg) applied between clients and server. |
| **Reviewer Dashboard** | Interface for researchers to monitor system internals. | **Implemented:** Web-based "Research Console" UI. | Same or similar web dashboard for study administrators. |
