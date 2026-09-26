# NEXORA Reviewer Q&A

This document provides concise answers to common questions about the NEXORA prototype. It is designed to assist reviewers, patent assessors, and researchers in understanding the scope, purpose, and architecture of the system.

### Q: What is NEXORA?
A: NEXORA is a privacy-aware, software-in-the-loop research prototype designed for stress-aware, posture-aware, and context-aware digital interventions. It processes physiological and biomechanical signals to provide timely, context-appropriate feedback to the user.

### Q: Who uses it?
A: NEXORA has two distinct user modes:
1.  **Participants (End-Users):** Desk workers or students who receive the digital interventions and wellness guidance.
2.  **Researchers / Reviewers:** Technical personnel who monitor the system, evaluate model performance, and inspect the federated learning and privacy mechanisms.

### Q: What problem does it solve?
A: Continuous monitoring of stress and posture often raises significant privacy concerns, and centralizing raw physiological data is a risk. NEXORA demonstrates how to run intelligent, context-aware interventions locally on the edge, while using federated learning and differential privacy to improve the global model without sharing raw user data.

### Q: Why is it not just a smartwatch dashboard?
A: Unlike a standard smartwatch dashboard that just shows raw metrics (e.g., "Your heart rate is 80"), NEXORA incorporates a multi-modal policy engine. It combines stress predictions (from EDA/Temp), physical context (Movement), and biomechanical state (Posture) to decide *if* and *when* an intervention is appropriate, minimizing alert fatigue. Furthermore, its core architecture is built around federated learning and differential privacy, which are not standard in consumer dashboards.

### Q: Why federated learning?
A: Federated learning allows the global stress-inference model to improve by learning from many users without ever transferring their raw physiological data (EDA, Temp, etc.) off their local devices. Only model weight updates are sent to the central coordinator.

### Q: Why differential privacy?
A: Differential privacy (implemented via Opacus) adds statistical noise to the model updates before they are sent to the coordinator. This ensures that the global model cannot inadvertently memorize and leak specific characteristics of any individual participant's data.

### Q: What is simulated in this prototype?
A: The current build is a **software-in-the-loop simulation**. The physical sensors are simulated using synthetic data generators or replay of existing datasets (like WESAD). The client processes for federated learning are currently running as isolated local processes on the same host machine for demonstration purposes.

### Q: What is not implemented?
A: 
*   **Physical Hardware:** No physical sensors are connected.
*   **Secure Aggregation:** Cryptographic secure aggregation (e.g., SecAgg) of federated updates is not implemented.
*   **Network Distribution:** Clients run locally; a true distributed network environment is simulated locally.
*   **Clinical Validation:** The system is not clinically validated and is not a medical device.

### Q: How would hardware be built later?
A: The envisioned hardware embodiment consists of a wrist-worn smart strap (for EDA, Temp, IMU) and an optional posture accessory (e.g., an upper-back clip). The current software prototype defines the data interfaces that these physical devices would eventually connect to (see `HARDWARE_EMBODIMENT.md`).
