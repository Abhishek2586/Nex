# NEXORA Demo Script

This script provides a structured walkthrough of the NEXORA prototype, ideal for reviewers or assessors.

## Setup
1.  Ensure the development server is running (`npm run dev` in the `frontend` directory).
2.  Open the application in a web browser (usually `http://localhost:3000`).

## Part 1: Product Positioning & The Participant Experience
*Goal: Establish what the product is and how the end-user interacts with it.*

1.  **Start at the Mode Selection Screen.**
    *   Explain: "NEXORA is a research prototype for context-aware digital interventions. It has two modes: one for the end-user (Participant App) and one for researchers/reviewers (Research Console)."
2.  **Select 'Participant App'.**
    *   **Home Tab:** Show the simple, non-technical dashboard. Explain that this is what a desk worker would see. Point out the current system status (e.g., "Monitoring active").
    *   **About Tab:** Emphasize the limitations. Read the disclaimer: "This is a software-in-the-loop simulation, not a medical device. Hardware sensors are simulated."
    *   **Guidance Tab:** Show where interventions appear.
3.  **Switch Modes:** Use the toggle/button to return to Mode Selection or switch directly to the Research Console.

## Part 2: The Research Console & System Internals
*Goal: Demonstrate the technical architecture, live processing, and privacy mechanisms.*

1.  **Overview Page:**
    *   Point out the **Prototype Summary**.
    *   Walk through the **Architecture Pipeline** visualization (Input -> Extraction -> Model -> Policy -> Intervention -> Learning).
    *   Start a session using the **Session Control** card (e.g., select 'Synthetic Normal').
2.  **Live Session Page:**
    *   Show the live streaming charts (EDA, Temp, Posture, Movement). Reiterate that these are currently synthetic/replayed signals simulating future hardware.
    *   Highlight the **Model State** card. Show how the stress score reacts to the inputs.
    *   Look at the **Recent Decisions** log. Explain the policy engine: "Notice how an intervention might be suppressed if the user is moving too much, even if stress is high."
3.  **Interventions Page:**
    *   Show the detailed event log of triggered and suppressed interventions. This proves the contextual policy engine is working.
4.  **AI Insights Page:**
    *   Explain that this shows the performance of the local edge model.
    *   Show the comparison between the baseline and the neural model.
    *   Point out the **Feature Importance** (Explanation) to show transparency in model behavior.
5.  **Federated & Privacy Lab:**
    *   This is the core privacy demonstration.
    *   Explain the Topology: "We have multiple client processes simulating different users, and one central coordinator."
    *   Highlight the **Differential Privacy** section. "We use Opacus to ensure updates don't leak individual data."
    *   *(Optional)* If the system supports it, trigger a federated learning round and watch the run status update.
6.  **Evidence Page:**
    *   Show where reviewers can export a comprehensive ZIP package containing logs, models, and reports for reproducibility and verification.

## Conclusion
*   Summarize: "NEXORA successfully demonstrates an edge-based, privacy-preserving pipeline for digital interventions in software. The next step in the product roadmap would be integrating physical hardware sensors."
