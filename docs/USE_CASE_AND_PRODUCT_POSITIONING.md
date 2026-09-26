# Use Case and Product Positioning

## 1. Product Positioning

NEXORA is a **privacy-aware software-in-the-loop research prototype for stress-aware, posture-aware, and context-aware digital interventions.**

It is designed to demonstrate a complete, end-to-end architecture that respects user privacy while delivering intelligent, context-sensitive wellness guidance.

**Key Distinctions:**
*   **It is a Research Prototype:** Built to validate architectural concepts, ML pipelines, and privacy mechanisms.
*   **It is Software-in-the-Loop:** Currently uses synthetic or replayed data to simulate physical sensors.
*   **It is NOT a Medical Device:** It makes no clinical claims and is not intended for diagnosis or treatment.

## 2. Primary Use Case: Desk-Work / Study Wellbeing Assistant

The primary envisioned application for NEXORA is supporting the wellbeing of individuals engaged in prolonged desk work or study.

**The Workflow:**
1.  **Monitoring (Simulated):** The system continuously monitors physiological signals (EDA, Skin Temperature) and physical context (Movement, Posture) while the user works at a desk.
2.  **Local Inference:** An edge-deployed machine learning model infers the user's stress level locally on their device.
3.  **Policy Evaluation:** The intervention engine evaluates the stress score against contextual factors (e.g., "Is the user currently moving too much to safely intervene?" or "Have we already prompted them recently?").
4.  **Intervention:** If appropriate, the system delivers a gentle digital intervention (e.g., a prompt to take a breath or adjust posture) via the Participant App.
5.  **Feedback & Learning:** The user's response to the intervention (or implicit feedback) is used to calculate model updates. These updates are rendered differentially private and sent to a central coordinator via federated learning to improve the system for everyone, without compromising raw data.

## 3. Stakeholders and Interfaces

NEXORA provides distinct interfaces tailored to different stakeholders:

### A. The Participant App (End-User)
*   **Who:** Desk workers, students, prototype participants.
*   **Purpose:** To receive wellness guidance, view session history, and manage personal settings.
*   **Design Philosophy:** Simple, non-technical, human-readable, and calm. It abstracts away the complex ML and privacy mechanisms.

### B. The Research Console (Reviewer/Developer)
*   **Who:** Researchers, patent reviewers, system developers, assessors.
*   **Purpose:** To inspect system internals, monitor live signal processing, evaluate ML model performance (AI Insights), manage federated learning rounds, and export evidence packages.
*   **Design Philosophy:** Information-dense, transparent, structured, and explanatory. It exposes the "engine room" to prove the system works as claimed.

## 4. Why This Prototype Exists

This software prototype was built to de-risk the most complex parts of the NEXORA vision *before* hardware development:

1.  **To prove the edge inference architecture:** Demonstrating that stress models can run efficiently on local clients.
2.  **To validate the intervention policy:** Ensuring the logic for suppressing or triggering alerts works correctly based on multi-modal context.
3.  **To demonstrate privacy-preserving learning:** Proving that the federated learning pipeline with differential privacy (Opacus) functions correctly and can update the edge models.
4.  **To provide a tangible artifact for review:** Offering patent reviewers and researchers a working system that substantiates the architectural claims.
