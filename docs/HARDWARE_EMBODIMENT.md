# NEXORA Hardware Embodiment

This document clarifies the distinction between the current **software-in-the-loop research prototype** and the **future physical hardware embodiment** of the NEXORA system.

## Important Disclaimer
- **Current State:** NEXORA is currently implemented as a software-in-the-loop simulation. All data used in the current prototype is either synthetic or replayed from existing datasets (e.g., WESAD).
- **Not a Medical Device:** NEXORA is a research tool for stress and context-aware digital interventions. It is not intended for medical diagnosis, treatment, or clinical use.
- **No Current Hardware:** The current demonstration does not include any physical sensors or hardware devices. 
- **Future Vision:** The design presented below outlines the envisioned physical form factor for a future, deployed version of the system.

## Envisioned Hardware Form Factor

The primary future embodiment of NEXORA is designed around non-obtrusive, wearable sensing to continuously monitor physiological and biomechanical signals during desk-work or study.

### 1. Primary Unit: Wrist-Worn Smart Strap
The core of the hardware system is a wrist-worn device (similar to a smartwatch or fitness band).

**Sensors & Signals:**
*   **EDA (Electrodermal Activity):** Measures skin conductance to assess sympathetic nervous system arousal (stress).
*   **Skin Temperature:** Measures peripheral temperature changes often associated with stress responses.
*   **PPG (Photoplethysmography):** (Planned for future iterations, potentially for heart rate/BVP).
*   **IMU (Inertial Measurement Unit - Accelerometer/Gyroscope):** Measures physical activity and movement magnitude to provide context to the physiological signals.

### 2. Optional Accessory: Posture Sensor
To capture biomechanical context (posture), an optional secondary accessory is envisioned.

**Form Factor Options:**
*   Upper-back clip (attaching to clothing)
*   Adhesive patch
*   Chair-integrated accessory

**Sensors & Signals:**
*   **IMU / Tilt Sensor:** Measures spinal alignment and movement to classify posture states (e.g., neutral, slumped, leaning).

## Mapping to the Current Prototype

The current software prototype simulates the data streams that would eventually be provided by this hardware.

| Future Hardware Sensor | Signal | Simulated in Current Prototype? | Source in Prototype |
| :--- | :--- | :--- | :--- |
| Wrist Strap - EDA | Electrodermal Activity | Yes | Synthetic / WESAD Replay |
| Wrist Strap - Temp | Skin Temperature | Yes | Synthetic / WESAD Replay |
| Wrist Strap - IMU | Acceleration Magnitude | Yes | Synthetic / WESAD Replay |
| Posture Accessory | Posture State | Yes | Synthetic Generator |

## The Role of the Software Prototype

The purpose of the current software prototype is to validate the **intelligence and intervention logic** of the system *before* committing to hardware manufacturing. It allows us to test:
*   Machine learning models for stress inference.
*   Differential privacy and federated learning mechanisms.
*   The intervention policy engine (when and how to prompt the user).
*   The user experience of the participant-facing interface.

Once the software loop is fully validated, the hardware abstraction layers will be connected to physical Bluetooth Low Energy (BLE) or similar physical sensor streams.
