# NEXORA — Patent-Reviewer Hardening, Exam Readiness & Complete Change Plan

**Prepared:** 20 September 2026  
**Repository reviewed:** `Abhishek2586/Nex` (`master`, current public GitHub state)  
**Purpose:** turn the current working software-in-the-loop prototype into a **reviewer-defensible, reproducible, understandable and demonstrably closed-loop NEXORA prototype**.

> This document is intentionally strict. It is not a praise report. Anything marked P0 should be treated as a blocker before presenting the project as “complete” to a faculty reviewer, patent-oriented reviewer, or external evaluator.
>
> This is a technical examination-preparation document, not a legal opinion. Claim amendments, prosecution responses and legal positions should be handled with the patent agent/attorney.

---

# 1. Executive verdict

The current build is **not a fake frontend**. It contains real backend state, feature extraction, trained models, local replay, persisted feedback, SHAP/Integrated Gradients, genuine parameter averaging, and genuine Opacus accounting. That is a strong engineering base.

However, I would **not present the project in its current state as “fully complete.”**

The biggest problem is not visual polish. The biggest problem is **evidence consistency**:

- the repository does not reproduce cleanly from GitHub because source files imported as `nexora.data.*` are absent from the tracked tree;
- the current “federated” implementation is three training worker processes, not the three independently running REST client services described in the master specification;
- the federated global model is produced but is not clearly activated back into edge inference;
- the AI stress model is displayed, but the closed-loop intervention path is mainly driven by the deterministic posture rule;
- WESAD support stops at adapter tests; there is no real WESAD model training/evaluation path;
- “Overview” and “Live session” are effectively the same screen;
- “Evidence” and “Settings” are much thinner than their names and documentation imply;
- the only frontend unit test is a placeholder-style test using a mocked shape rather than a real component/API flow;
- project documentation contradicts itself about completion status;
- the public repository contains material explicitly labelled as private patent-agent review notes;
- the current UI is suitable for a technical researcher, but it is **not suitable as the only interface for a normal end user**.

The correct target is:

**A dual-mode NEXORA system**
1. **Participant / User Mode** — simple, understandable, intervention-focused.
2. **Research / Reviewer Mode** — current technical inspection console, significantly expanded.

The technical story should be:

**Acquire / Replay → Validate Quality → Extract Features → Infer Locally → Explain Model → Apply Auditable Context + AI Policy → Deliver Micro-Intervention → Collect User Feedback → Adapt Prompt Policy → Train Local Models → Aggregate Federated Updates → Account Privacy → Validate New Global Model → Activate/Roll Back → Preserve Offline Edge Operation.**

That complete loop should be visible in the software and in the evidence package.

---

# 2. P0 blockers — fix these before the exam

| # | Blocker | Current problem | Required change | Main files |
|---|---|---|---|---|
| P0-01 | **GitHub fresh clone is not reproducible** | `.gitignore` contains `data/`, which also ignores a package directory named `src/nexora/data/`. The tracked GitHub tree has no `src/nexora/data`, while code imports `nexora.data.synthetic` and `nexora.data.wesad`. Your local machine can work because ignored local files exist, but a reviewer cloning the repo can fail immediately. | Change generated-data ignore rule to `/data/`. Add explicit ignores for `/runtime/`, `/models/`, `/artifacts/`. Then force-add the complete `src/nexora/data/` source package. Clone into a brand-new folder and run the documented setup. | `.gitignore`, `src/nexora/data/*` |
| P0-02 | **Public repo contains private prosecution material** | `docs/PATENT_AGENT_REVIEW_NOTES.md` is literally headed “Private patent-agent review notes.” The master build file also records filing discrepancies and patent strategy context. | Make the development repository private, or remove/sanitize private patent strategy files from the public branch. Keep public technical evidence separate from private prosecution notes. | GitHub visibility, `docs/PATENT_AGENT_REVIEW_NOTES.md`, master specification |
| P0-03 | **Completion claims contradict implementation** | `BUILD_STATUS.md` begins with “implementation in progress” but ends with “No further action required.” Evidence UI says acceptance remains in progress. `ACCEPTANCE_REPORT.md` says all mandatory features are complete although several mandatory master-spec items are absent. | Replace binary “complete” language with evidence-based levels: `Core synthetic software loop`, `Reviewer hardening`, `Real-data validation`, `Physical embodiment`, `Patent/legal examination`. Every level gets Passed/Partial/Not tested. | `BUILD_STATUS.md`, `ACCEPTANCE_REPORT.md`, Evidence UI |
| P0-04 | **AI does not meaningfully control the intervention loop** | The live neural stress score is calculated and shown, but the reliable intervention path is posture >20° for 30 s. A reviewer can ask: “What does AI actually change?” | Implement a **model-driven stress-like micro-intervention policy**: quality-approved window → probability threshold chosen on validation → sustained evidence duration → high-motion/data-quality gating → cooldown → breathing/relaxation visual prompt. Record model prediction ID + policy reasons separately. | `edge/policy`, `edge/app.py`, UI Interventions |
| P0-05 | **Federation architecture does not match the claimed/master architecture** | Three workers are separate processes, but they all read partitions from the same repository filesystem and are spawned by the coordinator. This demonstrates FedAvg math, but not realistic client-service separation. | Run `client-a`, `client-b`, `client-c` as actual loopback services on independent ports/stores. Coordinator must distribute a base model and receive safe parameter updates over HTTP. It must not load client windows directly. Add authenticated update protocol, round/base hash checks and deduplication. | federation services, launcher, configs |
| P0-06 | **Federated model is not visibly used by edge inference** | An aggregate model is saved inside a run artifact. Edge inference continues using the cached local neural model. | Add model registry: `candidate → validated → activated → previous/rollback`. After a federated run, allow explicit activation of a validated global model and visibly change the active model hash/version in the dashboard. | ML registry, edge predictor, federation UI |
| P0-07 | **Real-data validation missing** | WESAD converter tests exist, but no real WESAD subject has been imported, trained or evaluated. CLI training only accepts `synthetic`. | Implement `--dataset wesad`, participant-separated train/validation/test, source-specific model registry and metrics. Acquire WESAD only under its original terms. Do not redistribute raw files. | CLI, WESAD adapter, training/evaluation, model registry |
| P0-08 | **Frontend test is a red flag** | `frontend/tests/basic.test.ts` says it is a “Simulated test case to ensure the test suite passes” and does not test the real runtime observation format. | Delete it. Add meaningful component/API tests and Playwright flows covering session start/pause/resume, posture prompt, feedback, missing-data abstention, AI explanation, federation job, evidence export and refresh persistence. | `frontend/tests`, `tests/e2e` |
| P0-09 | **Normal user cannot understand the app** | Terms such as `FedAvg`, epsilon, model hashes, SHAP and raw reason codes dominate the interface. | Add Participant/User Mode and keep Research/Reviewer Mode. Do not expose privacy/accounting jargon on the main user screen. | frontend |
| P0-10 | **Evidence screen is not evidence-grade** | Current Evidence page is a few paragraphs. | Build an actual evidence console: claim matrix, test results, scenario results, data provenance, model versions, experiment manifests, privacy status, architecture, limitations, export button and Git revision. | Evidence page/API/exporter |
| P0-11 | **Offline claim is weakened by external font request** | CSS imports Google Fonts. | Remove network font import. Use system font stack or locally bundled fonts/assets. Normal demo must make zero public network calls. | `frontend/src/style.css` |
| P0-12 | **Bootstrap/handoff mismatch** | `docs/FINAL_HANDOFF.md` tells users to run `scripts/bootstrap.py`; that script is absent from the tracked repository. | Add a real idempotent bootstrap script or change every document to the actual supported setup path. Prefer adding the script because the master contract requires it. | `scripts/bootstrap.py`, README, handoff |
| P0-13 | **Temporary/build artifacts are committed** | `.pytest_temp/...` and `src/nexora.egg-info/` are in Git. | Remove from Git and ignore them. Keep repository evidence intentional and clean. | `.gitignore`, Git history/current tree |
| P0-14 | **Current patent differentiation is too generic** | Wearable stress + FL + DP + explainability are already crowded research/patent areas. | Add a prior-art/differentiation document focusing on NEXORA’s specific **quality-aware, offline-capable, explainable adaptive intervention loop**, not generic “AI + wearable + federation.” Get formal patent-agent prior-art review before making novelty assertions. | `docs/PRIOR_ART_AND_DIFFERENTIATION.md` |

---

# 3. What is already worth preserving

Do **not** throw away the project and restart. Preserve these good parts:

- deterministic labelled synthetic replay;
- participant-separated synthetic dataset;
- shared 30-second feature extractor;
- missing-data abstention;
- random-forest baseline and neural model;
- safe NPZ/safetensors model storage;
- signed SHAP and Integrated Gradients explanations;
- SQLite persistence;
- WebSocket reconnect/catch-up and event IDs;
- intervention feedback state transitions;
- bounded cooldown adaptation after dismissal;
- sample-weighted FedAvg math with tensor validation;
- three isolated training worker processes as an intermediate federation demonstration;
- actual Opacus clipping/noise/accounting;
- persistent privacy ledger;
- loopback coordinator outage demonstration;
- local HTTPS profile;
- evidence ZIP/checksum concept;
- clear synthetic/non-medical disclaimers.

The next phase is about **closing the architecture gaps and making the evidence impossible to misunderstand**.

---

# 4. UI/UX redesign — current UI is reviewer-oriented, not user-oriented

## 4.1 Add a top-level mode switch

At launch show:

**NEXORA**
- `User View`
- `Research View`

Remember the choice locally.

### User View must answer only five questions

1. Is monitoring/replay active?
2. Are the available signals usable?
3. Did NEXORA notice something?
4. What small action is being suggested?
5. Why was that suggestion shown, and can I dismiss it?

Do not show epsilon, FedAvg, model hash, confusion matrix, SHAP values or coordinator internals here.

### Research View

Keep the current console concept and make it much more complete.

---

# 5. User View — required pages

## 5.1 Home

Replace technical metric-first design with:

- **Session state:** “Monitoring simulation active”
- **Source:** “Synthetic demonstration data”
- **Current state card:** Stable / insufficient data / posture reminder / stress-like pattern detected
- **Signal availability:** EDA, temperature, movement, posture; heart rate only if the source genuinely supplies it
- **Current suggestion:** one intervention card
- **Why am I seeing this?** expandable plain-language explanation
- **Data quality:** Good / Missing data / High movement
- **Privacy line:** “This demonstration runs locally on this laptop.”
- large Start / Pause / End buttons.

For raw synthetic values, put “View technical signals” behind an expandable panel.

## 5.2 Guidance

Two software-only interventions are enough:

### Posture
- simple body/posture illustration;
- “Adjust your posture if comfortable”;
- `Done`, `Dismiss`, `Remind me later`.

### Breathing / reset
- user-controlled 45–60 second expanding/contracting circle;
- Start/Stop;
- no compulsory breath holding;
- no therapeutic or medical promises;
- `Helpful`, `Not helpful`, `Dismiss`.

Add the virtual haptic status:
> Physical haptic output not connected in this software prototype.

## 5.3 History

Plain timeline:
- 10:42 — signal quality became sufficient
- 10:43 — posture remained outside demo threshold
- 10:43 — posture reminder offered
- 10:44 — dismissed
- 10:44 — reminder cooldown increased

This makes “adaptation” visible without requiring the user to understand policy code.

## 5.4 About this demo

Explain:
- what is simulated;
- what is real software;
- what is not built physically;
- what data remains local;
- this is not diagnostic/therapeutic software.

---

# 6. Research View — page-by-page changes

## 6.1 Overview

### Problems now
- good visual quality but too much empty card space;
- technical badges are useful but incomplete;
- raw scenario identifiers look unfinished;
- no selected session/model version/replay clock in header;
- only four signal cards and one graph;
- research workflow is not visually explained.

### Change
Add a compact “system pipeline strip”:

`Source → Edge → Quality → Features → Model → Policy → Intervention → Feedback`

Each node can be green/amber/grey and clickable.

Top status must show:
- selected client;
- selected session;
- source;
- replay speed;
- edge status;
- coordinator status;
- **active model version/hash**;
- transport status.

Humanize scenario names:

| Internal ID | Display name |
|---|---|
| `normal` | Normal / stable signals |
| `gradual_stress` | Gradual stress-like change |
| `sustained_posture` | Sustained posture deviation |
| `brief_posture` | Brief posture spike |
| `missing_data` | Missing / low-quality signal |
| `high_motion` | High-motion interference |
| `repeated_dismissal` | Repeated prompt dismissal |

Add one-line “What this tests” under each scenario.

## 6.2 Live Session

### Critical problem
In current code, **Overview and Live session share the same rendering block**. They are not truly separate pages.

### Required Live page
- EDA chart;
- skin-temperature chart;
- acceleration magnitude/motion chart;
- posture chart if that source has posture;
- optional heart rate chart only if genuinely available;
- data-quality timeline;
- 30-second inference-window marker;
- event-time cursor;
- latest prediction card;
- latest policy decision card;
- event table with filters:
  - observation
  - window ready
  - prediction
  - decision
  - intervention
  - feedback
  - policy changed
- provenance label for every channel;
- “repaired samples / coverage / abstention reason.”

This page should prove that the system is not randomly generating frontend values.

## 6.3 Interventions

### Problems now
- all interventions are returned together;
- old prompts can appear repeatedly;
- no clear active prompt;
- no suppression log;
- no visual breathing intervention;
- no visible adaptation state.

### Required design
Top section:
- **Active intervention**
- reason
- triggering prediction/context
- event time
- current cooldown
- source
- physical-output status.

Second:
- “Why selected?”
  - model evidence
  - context rule
  - quality gate
  - suppression checks
  - cooldown.

Third:
- feedback controls.

Fourth:
- history filtered to current session/client.

Fifth:
- policy adaptation:
  - initial cooldown
  - dismissals in rolling window
  - new cooldown
  - reason for change.

Add breathing guidance for a model-driven stress-like policy.

## 6.4 AI Insights

### Problems now
- “100.0%” is visually dominant and can mislead reviewers;
- confusion matrix is raw JSON;
- attributions are a list of numbers;
- no feature values next to contributions;
- model purpose/limitations are easy to miss.

### Required changes
For every model show:
- data source;
- task;
- train/validation/test subject counts;
- class counts;
- balanced accuracy;
- macro-F1;
- per-class precision/recall;
- confusion matrix with labelled axes;
- inference latency median/p95;
- model hash;
- feature schema;
- created date;
- active/not-active state.

For synthetic RF 100%, show an amber note directly beside the number:

> Perfect separation on this artificial generator. This is not a real-world accuracy claim.

For the current weak MLP:
> Held-out synthetic utility is weak. Model retained to demonstrate neural/federated mechanics; do not describe it as validated stress detection.

Attribution visualization:
- horizontal signed bar chart;
- current feature value;
- contribution direction;
- method;
- output class;
- baseline/reference;
- completeness/convergence diagnostic;
- “model explanation, not causal explanation.”

## 6.5 Federated & Privacy Lab

Current page is a good start but it must demonstrate architecture rather than only show jobs.

### Add a live architecture graphic
`Client A` →  
`Client B` → `Coordinator` → `Candidate Global Model` → `Validation` → `Activation`  
`Client C` →

Each client card:
- service port/status;
- assigned participant count;
- local record count;
- base model hash;
- local update hash;
- current round;
- privacy status;
- epsilon/delta;
- steps;
- secure RNG status.

Coordinator:
- current round state;
- number updates accepted;
- duplicates rejected;
- expected base hash;
- aggregate hash;
- evaluation result.

Controls:
- 1/3/5 rounds;
- non-private;
- private;
- cancel;
- **activate validated global model**;
- rollback.

Show:
- “Raw training windows transmitted: No”
- “Secure aggregation: Not implemented”
- “Same laptop: Yes”
- “Cryptographically secure DP RNG: No/Yes”
- “Actual multi-device deployment: No”

Do not hide those limitations.

## 6.6 Evidence

This must become one of the strongest pages.

Sections:
1. **Prototype scope**
2. **Source provenance**
3. **Claim implementation matrix**
4. **Scenario verification**
5. **Model evaluation**
6. **Federated runs**
7. **Privacy accounting**
8. **Test results**
9. **Security verification**
10. **Known limitations**
11. **Hardware/physical mapping**
12. **Export evidence bundle**

Each claim row:
- claim/subclaim;
- status;
- implementation;
- evidence path;
- limitation;
- date verified.

Use only:
- Implemented in software
- Simulated I/O
- Partially demonstrated
- Not implemented
- Not verified

Never “claim validated.”

Add real **Export evidence ZIP** button.

## 6.7 Settings

Current Settings is actually session history. Split it.

Settings should contain:
- source/import status;
- retention policy;
- demo thresholds clearly labelled “experimental demonstration parameters”;
- replay defaults;
- theme;
- reduced-motion option;
- local paths/status;
- privacy-demo budget information;
- synthetic demo reset.

Move session history to a separate “Sessions” panel/page.

---

# 7. Accessibility and presentation polish

Implement before presentation:

- no Google Fonts/CDN dependency;
- system/local font stack;
- `prefers-reduced-motion`;
- keyboard-only operation;
- visible focus;
- meaningful button labels;
- ARIA status for live updates;
- no status shown by colour alone;
- min 44 px touch targets on participant view;
- 1366×768 projector check;
- 1920×1080 check;
- 390×844 narrow check;
- Chrome + Edge automated smoke flow;
- error/empty/loading/disconnected states per page;
- no raw snake_case strings shown to user;
- no unexplained UUIDs as primary labels;
- tooltips/glossary for “balanced accuracy”, “FedAvg”, “epsilon”, “SHAP”, “Integrated Gradients.”

---

# 8. Backend architecture changes

## 8.1 Replace the current single-file edge concentration

`src/nexora/edge/app.py` currently contains persistence, replay, policy, feedback, federation proxy routes and static serving.

Split into:

```text
src/nexora/edge/
  app.py
  schemas.py
  store.py
  replay.py
  inference.py
  policy.py
  feedback.py
  routes/
    health.py
    sessions.py
    events.py
    interventions.py
    explanations.py
    federation.py
    evidence.py
    settings.py
```

This is not just aesthetic. It allows reviewers to follow one subsystem at a time.

## 8.2 Canonical observation schema

Current runtime observation data is much simpler than the master design.

Use typed channel objects:

```json
{
  "value": 2.1,
  "unit": "uS",
  "origin": "synthetic",
  "quality": "good"
}
```

For each observation store:
- event/session/client IDs;
- observed/event time;
- received time;
- source type;
- source ID;
- subject ID where appropriate;
- channel unit;
- channel origin;
- quality;
- nullable missing values.

Do not place heart rate/posture in an ambiguous separate structure.

## 8.3 Prediction records

Persist:
- prediction ID;
- window ID;
- model ID/hash/version;
- task;
- probabilities;
- predicted class;
- abstention;
- inference latency;
- data source;
- feature schema;
- created time.

## 8.4 Decision records

Persist independently from model output:
- policy version;
- prediction ID if used;
- action;
- result;
- reason codes;
- thresholds used;
- cooldown remaining;
- suppression reasons;
- explanation ID;
- event time.

This separation is essential to explain:

**“The model did not directly prescribe an action. The policy evaluated model evidence, context quality and cooldown constraints.”**

## 8.5 Sequence generation

Do not use `MAX(sequence)+1` without a concurrency-safe mechanism.

Use a transaction-protected per-session sequence counter or database-generated monotonic event order.

## 8.6 API errors

Return:
- stable error code;
- human message;
- correlation ID;
- field details.

Do not send raw exception strings into the UI.

---

# 9. The most important algorithmic change: close the AI → intervention loop

Right now the model score is inspectable, but posture is the main reliable trigger.

Implement two independent micro-intervention paths.

## Path A — deterministic posture policy

Inputs:
- valid posture context;
- angle above the demo threshold;
- sustained for the configured duration.

Output:
- posture reminder.

Purpose:
- deterministic, reliable demo of temporal policy and feedback adaptation.

## Path B — model-driven stress-like policy

Inputs:
- complete quality-approved 30-second model window;
- neural/global model;
- model score;
- movement quality;
- sustained evidence.

Suggested technical flow:

```text
prediction available
  ↓
quality valid?
  ├─ no → abstain
  └─ yes
      ↓
high motion?
  ├─ yes → suppress breathing prompt + log reason
  └─ no
      ↓
score above validation-selected threshold?
  ├─ no → no_action
  └─ yes
      ↓
sustained for required event-time duration?
  ├─ no → accumulate evidence
  └─ yes
      ↓
active prompt/cooldown?
  ├─ yes → suppress
  └─ no → offer breathing/reset micro-intervention
```

Important:
- select threshold using validation data only;
- do not tune on the held-out test set;
- if the MLP remains unusable, do **not** force the synthetic generator or threshold to create impressive results;
- document weak utility and use posture as the reliable deterministic demonstration;
- when WESAD is available, establish a real source-specific model before claiming stress-detection performance.

---

# 10. Feedback adaptation — make it visible and correctly scoped

Current adaptation doubles cooldown after two dismissals. Preserve the concept, but make it:

- per intervention type;
- per session/user profile;
- bounded;
- versioned;
- visible in the UI;
- auditable.

Store policy versions such as:

```json
{
  "policy_version": "policy-v3",
  "posture_cooldown_s": 120,
  "breathing_cooldown_s": 240,
  "reason": "two breathing prompts dismissed within 10 min"
}
```

Feedback must **not** silently become a stress label.

Completion must **not** mean the user physiologically improved.

---

# 11. Real WESAD path — this is the highest-value research upgrade

UCI describes WESAD as a 15-subject multimodal wearable stress/affect dataset with wrist EDA and temperature at 4 Hz, wrist acceleration at 32 Hz, and BVP at 64 Hz, in addition to chest channels.

## Required workflow

```bash
python -m nexora.cli data import-wesad --path <official-user-supplied-folder> --trusted-original
python -m nexora.cli train baseline --dataset wesad
python -m nexora.cli train neural --dataset wesad
python -m nexora.cli evaluate --dataset wesad
python -m nexora.cli experiment run --mode federated --dataset wesad --rounds 5
```

Do **not** add WESAD raw files to Git.

## Split

Use subject-level separation.

With 15 valid subjects, a sensible fixed split is:
- 9 train
- 3 validation
- 3 test

or use LOSO as an additional research experiment.

Never randomly split windows from the same person into train and test.

## Labels

Verify label codes from the official README.

For initial binary demonstration:
- baseline → class 0
- stress → class 1
- amusement/transitions/undefined → excluded

Report excluded windows.

## Models

Synthetic and WESAD must have separate registries:

```text
models/
  synthetic/
    baseline/
    neural/
  wesad/
    baseline/
    neural/
```

Do not run a synthetic model on WESAD and call it validated.

## UI

Source selector:
- Synthetic Demo
- Recorded Dataset — WESAD

If WESAD is absent:
> Recorded dataset not imported.

If imported but not trained:
> Dataset imported; matching model unavailable.

If evaluated:
show its own metrics separately from synthetic metrics.

---

# 12. Fix the misleading model story

Current measured synthetic results are approximately:

- Random Forest: balanced accuracy 1.00, macro-F1 1.00
- Local MLP: balanced accuracy 0.50, macro-F1 0.375
- One-round FedAvg: balanced accuracy 0.50, macro-F1 around 0.286

A strict reviewer will immediately ask:

> “If your neural model performs at chance level, why is it the model driving a health system?”

Correct response is **not** to hide the score.

Required engineering response:

1. Keep RF as a sanity baseline.
2. Treat RF 100% as evidence that the synthetic generator is too separable, not as product accuracy.
3. Inspect class distributions and participant-level metrics.
4. Improve neural training using train/validation only:
   - learning rate;
   - local epochs;
   - class balance;
   - seed sensitivity;
   - feature normalization;
   - training length;
   - possibly a smaller linear/logistic baseline.
5. Add multiple-seed summary for synthetic development.
6. Move research-performance discussion to real WESAD.
7. Do not optimize the synthetic test set.
8. Do not claim “AI stress detector works” until real-data evidence supports the statement.

Also add:
- inference latency median/p95;
- per-participant metrics;
- calibration/reliability diagram if you intend to call probabilities “probabilities”;
- otherwise call them **model scores**.

---

# 13. Federation — upgrade from process experiment to defensible distributed architecture

## 13.1 What current code genuinely demonstrates

It demonstrates:
- same initial MLP;
- three distinct worker processes;
- distinct synthetic participant partitions;
- local SGD;
- numerical parameter updates;
- sample-weighted aggregation;
- model hashes;
- held-out aggregate evaluation.

That is useful.

## 13.2 What it does not yet demonstrate

It does not demonstrate:
- independent long-running client services;
- authenticated REST model distribution;
- authenticated update submission;
- no coordinator filesystem access to client training files;
- duplicate-update prevention at coordinator protocol level;
- base-model-hash rejection at protocol boundary;
- client service outage/round timeout;
- model deployment back to edge clients;
- multi-host federation.

## 13.3 Target local architecture

```text
Browser
   |
Edge/User Gateway
   |
   +-------------------------+
   |                         |
Client-A :8111          Coordinator :8100
Client-B :8112  ----->  Round / model registry
Client-C :8113
```

Each client owns:
- its SQLite;
- partition;
- current model;
- update cache;
- privacy ledger;
- service token.

Coordinator owns:
- experiment metadata;
- base/global models;
- accepted update metadata;
- round state;
- public evaluation.

## 13.4 Protocol checks

Update payload metadata:
- run ID;
- round ID;
- client ID;
- base model hash;
- feature schema hash;
- record count;
- update hash;
- parameter shapes/dtypes;
- privacy summary reference.

Reject:
- unknown client;
- wrong round;
- wrong base hash;
- duplicate client update;
- NaN/Inf;
- shape mismatch;
- unexpected tensors;
- size cap violation.

## 13.5 Round states

Expose:
`queued → distributing → training → collecting → aggregating → evaluating → completed`

Terminal:
`failed`, `cancelled`.

This makes the dashboard explain what real federation is doing.

---

# 14. Global model lifecycle — currently missing from the demonstration

Add a model registry with:

- model ID;
- source;
- feature schema;
- parent/base hash;
- training run;
- metrics;
- privacy scope;
- status:
  - candidate
  - validated
  - active
  - retired
  - rejected
- activation time.

Workflow:

```text
Federated aggregate
   ↓
candidate model
   ↓
schema/hash checks
   ↓
held-out evaluation
   ↓
manual “Activate model”
   ↓
edge downloads/verifies
   ↓
atomic activation
   ↓
old model retained for rollback
```

Dashboard must visibly show active model hash before and after activation.

This single improvement makes federated learning part of the product rather than a disconnected laboratory experiment.

---

# 15. Differential privacy — preserve truth, strengthen the demo

Current Opacus implementation is real and is one of the better parts of the project.

Current limitations must remain explicit:
- example-level protection;
- privacy unit = one non-overlapping synthetic 30-second window;
- same-host experiment;
- no patient-level privacy;
- no secure aggregation;
- `secure_mode=False`;
- experimental non-cryptographic randomness.

Opacus documentation explicitly recommends non-secure RNG for experimentation, but cryptographically strong DP requires secure RNG and retraining.

## Required upgrades

### Budget projection
Before a new private run:
- calculate projected epsilon;
- show current epsilon;
- show projected epsilon;
- prevent run if cap would be exceeded.

### UI
Example:

> Current demo privacy budget: ε 5.41 at δ 1e-5  
> Projected after next private round: ε 6.23  
> Configured demo cap: ε 8.00

### Synthetic reset
Because this is disposable synthetic data, an explicit “Reset synthetic DP demo state” may be provided for rehearsal.

The UI must state:
> Resetting the synthetic demo ledger restarts this disposable experiment. Resetting a ledger cannot undo a real-world disclosure.

### Secure RNG
If technically feasible, add a separate secure-DP profile using the supported CSPRNG dependency and measure the cost.

If not feasible:
keep it unavailable and say so.

### Cancellation
Make experiment cancellation cooperative so no child private worker continues training after the coordinator marks the run cancelled.

Persist/over-account if uncertainty exists; never undercount.

---

# 16. Security hardening

Current Origin checks are useful but are **not authentication**.

A request without a browser Origin header can still be made by another local process.

Implement:

- generated local service tokens;
- coordinator/client authentication;
- dashboard local session cookie or equivalent;
- state-changing endpoints protected server-side;
- WebSocket auth;
- exact origin allowlist;
- no secrets in query string;
- no secrets in frontend bundle;
- request size caps;
- safe IDs/path handling;
- export path traversal protection;
- rate limits for expensive explanation/training endpoints;
- content security policy;
- `X-Content-Type-Options`;
- `Referrer-Policy`;
- dependency vulnerability scan;
- no arbitrary pickle upload.

The WESAD pickle path should remain an offline, explicitly trusted original-file conversion operation.

---

# 17. Heart-rate inconsistency — fix documentation immediately

The latest edge code synthesizes a heart-rate stream. Older claim/evidence text says heart rate is unavailable.

Choose one consistent story.

Recommended:

- keep synthetic heart rate if useful for the visual demo;
- label it **Synthetic derived/demo channel**;
- state clearly that it is not a measured PPG/BVP sensor value;
- do not feed it to the current 12-feature model unless the model/schema is intentionally revised and retrained;
- WESAD can later support BVP-derived research features only after a documented method.

Update every claim map/model card/Evidence page accordingly.

Never show a synthetic heart rate card without a provenance label.

---

# 18. Evidence package — rebuild it as if an examiner will audit it

Current evidence ZIP idea is correct, but it needs more.

## Must include

```text
README
BUILD_STATUS
ACCEPTANCE_REPORT
KNOWN_LIMITATIONS
git revision / commit SHA
architecture diagram + Mermaid source
claim map
data/source manifest
dataset licence/source note
feature schema
model metadata
evaluation metrics
participant splits
federated run manifests
privacy ledgers/summaries
scenario traces
test report
browser/e2e report
screenshots
security verification
latency/performance report
environment/runtime versions
demo script
exam Q&A
technical report
export manifest with SHA-256
```

Do not include:
- raw WESAD;
- private participant data;
- `.env`;
- service tokens;
- CA private keys;
- SQLite containing private/raw history unless explicitly selected;
- Python venv;
- node_modules;
- DP RNG state.

## Add generated test artifacts

Run pytest with JUnit XML.

Run Playwright with HTML report.

Save:
- desktop screenshots;
- narrow screenshot;
- one screenshot per main reviewer flow.

## Add code revision

The evidence bundle must say exactly which Git commit produced it.

---

# 19. Documentation inconsistencies to correct

## `BUILD_STATUS.md`
Current contradiction:
- “implementation in progress”
- later “all completion criteria satisfied”

Replace with:

```text
Core synthetic software prototype: PASS
Reviewer hardening: IN PROGRESS
Real WESAD validation: NOT RUN
Physical embodiment: NOT BUILT
Public/cloud deployment: OUT OF SCOPE
Clinical validation: NOT PERFORMED
Patent grant/examination outcome: NOT DETERMINED
```

## `ACCEPTANCE_REPORT.md`

Do not say all master criteria passed until:
- three service clients exist;
- model activation exists;
- Evidence export is functional;
- meaningful browser tests exist;
- P95 latency measured;
- source package is actually tracked/reproducible.

## `FINAL_HANDOFF.md`

Remove nonexistent bootstrap instruction or implement it.

## `API_CONTRACT.md`

Only document routes that exist.

If docs describe an evidence-export endpoint, build it.

## `USER_GUIDE.md`

Do not say Evidence exposes claim map/export until the UI actually does.

## `CLAIM_IMPLEMENTATION_MAP.md`

Update:
- heart-rate provenance;
- true federation status;
- model activation status;
- WESAD status;
- physical actuation status.

---

# 20. Repository cleanup and reproducibility

Use this `.gitignore` direction:

```gitignore
/.venv/
/data/
/runtime/
/models/
/artifacts/
/frontend/dist/
/frontend/node_modules/
/.pytest_cache/
/.pytest_temp/
__pycache__/
*.pyc
src/*.egg-info/
.env
*.pem
*.key
```

Important: **do not use `data/` when you also have `src/nexora/data/`.**

After fixing:

```bash
git rm -r --cached .pytest_temp
git rm -r --cached src/nexora.egg-info
git add -f src/nexora/data
```

Then perform the real test:

1. Clone the repository into a brand-new directory.
2. Run bootstrap.
3. Prepare demo.
4. Run verification.
5. Start the app.
6. Complete demo flow.
7. Export evidence.

If this cannot be done from a fresh clone, the project is not reproducible.

---

# 21. Add CI after fresh-clone reproducibility is fixed

GitHub Actions should run:

- Python install;
- unit/integration tests;
- frontend install/build;
- frontend unit tests;
- lint/typecheck;
- a minimal synthetic generation/model smoke test;
- evidence-export test.

Do not run expensive full DP/federated training on every commit unless cached/appropriately bounded.

Add a manual workflow for the full acceptance suite.

---

# 22. Testing plan — replace “11 passed” with meaningful coverage

A reviewer does not care about test count if the tests are shallow.

## Data / feature tests
- deterministic generation;
- subject split isolation;
- no train/test subject overlap;
- 30 s windows do not cross subject/session;
- finite values;
- short gap repair;
- long gap abstention;
- unit/range validation;
- clipping diagnostics;
- offline/online feature parity.

## Model tests
- save/load prediction equality;
- wrong schema rejected;
- corrupted hash rejected;
- held-out evaluation counts;
- participant metrics;
- inference latency;
- explanation count/finite values;
- IG convergence;
- SHAP completeness.

## Policy tests
- sustained posture triggers;
- brief posture does not;
- missing model data abstains;
- high motion suppresses breathing prompt;
- sustained model score triggers only after required duration;
- cooldown works;
- active prompt suppresses duplicate;
- two same-type dismissals change only that type’s cooldown;
- feedback idempotency.

## Event tests
- duplicate event creates one durable result;
- reconnect does not duplicate intervention;
- late event does not retroactively fire action;
- concurrent event sequence remains unique.

## Federation tests
- three independent services;
- local model parameters actually change;
- coordinator has no raw training loader;
- wrong client rejected;
- wrong base hash rejected;
- duplicate update rejected;
- malformed tensors rejected;
- missing client fails round;
- FedAvg math independently verified;
- global model changes;
- activation changes edge model hash;
- rollback works.

## DP tests
- clipping/noise/accountant exercised;
- accountant persists;
- same protected dataset composes;
- identity mismatch rejected;
- projected epsilon guard works;
- cancellation does not silently lose accounting;
- secure/non-secure mode accurately labelled.

## Browser tests
- user-mode full guidance flow;
- research live session;
- missing-data abstention;
- intervention feedback;
- attribution;
- federation;
- privacy;
- coordinator outage;
- evidence export;
- reload persistence;
- direct URL refresh;
- mobile width;
- keyboard navigation.

---

# 23. Performance measurements you should actually show

Measure rather than claim:

- prepared startup time;
- API health response latency;
- local inference median / p95;
- explanation latency;
- decision-to-WebSocket delivery latency;
- decision-to-render p95;
- one federated round duration;
- private federated round duration;
- evidence-export duration;
- peak memory during full demo.

Use the actual laptop hardware description.

Do not repeat any filed sub-100 ms or other historical percentages unless newly measured by this implementation.

---

# 24. Patent-review perspective — what the software must prove and what it cannot prove

A prototype is not automatically required for every Indian patent application, but Section 10 of the Patents Act requires the complete specification to fully and particularly describe the invention, its operation/use and method of performance, and disclose the best method known to the applicant. A Controller may also require a model/sample in a particular case.

Therefore this prototype is most valuable as:
- technical enablement evidence;
- a coherent implementation record;
- an aid for explaining architecture;
- a source of measured results;
- a way to identify inconsistencies before examination.

It is **not** proof that:
- every claim is novel;
- every claim is inventive;
- the patent will be granted;
- the physical embodiment has been built;
- clinical efficacy exists.

---

# 25. India-specific patent issues your patent agent should explicitly review

## 25.1 Novelty / inventive step

The examiner will look beyond whether the project is impressive.

The questions are:
- What exact claimed combination was new at the relevant priority date?
- Which feature produces a technical advance/economic significance?
- Why would the combination not have been obvious to a skilled person?

A dashboard is not the inventive step.

A generic statement such as:
> “We use AI, federated learning, differential privacy and SHAP”

is weak because those techniques were already known.

## 25.2 Section 3(k) — algorithm/computer-program concerns

The current CRI guidance focuses on the technical problem, technical means and technical effect rather than requiring “novel hardware” in every software-led invention.

Your technical story should therefore remain anchored to:
- acquisition of physical/multimodal sensor signals;
- quality-aware local processing;
- local inference under connectivity loss;
- sensor/context-driven control;
- real intervention interface/actuator mapping;
- controlled model-update architecture;
- latency/privacy/communication effects.

Do not frame the invention as merely:
> “an algorithm that predicts stress.”

## 25.3 Section 3(i) — treatment/process concern

Because the project uses healthcare and “micro-intervention” language, have the agent review whether any method claim can be characterized as a medicinal/therapeutic/treatment method for humans.

Technical system/device architecture and non-therapeutic wellbeing guidance must be described accurately. Do not make legal claim changes yourself from this review.

## 25.4 Section 3(f) — mere aggregation of known devices

An examiner can question a system that appears to be a collection of known sensors, AI, cloud and haptics operating independently.

Your technical evidence should show **cooperative interaction**:
- signal quality changes inference eligibility;
- context suppresses/changes interventions;
- user feedback changes policy timing;
- local failure does not break local inference;
- federation updates a model that is validated and then activated;
- privacy accounting limits whether further training can run.

This is more defensible than a block diagram where every module is simply placed side by side.

---

# 26. Prior-art / crowded-landscape warning

This is not a formal prior-art opinion, but a quick search shows the area is crowded.

Examples include:
- 2023 published work using WESAD and federated learning for wearable stress detection;
- 2024-era patents around wearable/IoT differential-privacy/federated architectures;
- adaptive wearable monitoring and feedback systems;
- 2026 publications combining multimodal wearable stress detection, federated learning, privacy and explainability.

Therefore do **not** position novelty as any one of:
- stress detection;
- wearables;
- edge AI;
- federated learning;
- differential privacy;
- SHAP;
- haptic feedback;
- adaptive feedback.

The strongest technical differentiation to investigate is the **specific integrated control loop and system interaction**, tied to the filed claim language and filing date.

Before an examination response, perform a professional claim-by-claim prior-art search using patents/publications available before the applicable priority date.

---

# 27. Hardware/physical-claim bridge without buying hardware

The software-only build cannot honestly demonstrate the physical sensor/actuator elements of Claim 1.

But the reviewer experience can be improved by adding an explicit **Physical Architecture Mapping** module.

Create:

`configs/hardware_mapping.json`

For every physical element record:
- filed element/reference;
- intended real component/category;
- software signal/event counterpart;
- interface;
- status:
  - simulated
  - virtual circuit only
  - not physically verified.

Example categories:
- electrodermal/GSR input;
- skin temperature;
- posture/motion;
- environmental context;
- edge controller;
- RGB/visual output;
- buzzer;
- haptic/vibration output;
- network/cloud/coordinator role.

Add the circuit image/diagram from the hardware-design work to Evidence.

Label it:
> “Reference physical embodiment mapping — not a physically assembled/validated device.”

This is much better than pretending the software dashboard itself proves physical claims.

---

# 28. Claim-oriented technical review matrix

The exact legal wording must come from the filed specification. For the current software evidence, use a conservative engineering map.

| Claim area | Current technical evidence | Reviewer attack | Required next evidence |
|---|---|---|---|
| Physical sensing | Synthetic replay only | “Where is the actual sensor?” | Hardware mapping + keep `simulated`; optional later bench prototype |
| Edge processing | Local FastAPI/feature/model path | “Is this equivalent to embedded edge?” | Measure local/offline behavior; do not claim embedded equivalence |
| Cloud/AI role | local coordinator | “This is not cloud” | Label local coordinator emulation; cloud deployment remains unverified |
| Automatic intervention | posture browser prompt | “Where does AI cause the action?” | model-driven breathing/reset intervention |
| Multimodal physiological/context input | EDA/temp/acc/posture + synthetic HR | “Which are measured and which are invented?” | per-channel provenance + WESAD |
| Prediction/AI | RF + weak MLP | “Why trust chance-level MLP?” | real WESAD evaluation; honest model-card limitations |
| Explainability | SHAP/IG | “Is explanation causal?” | signed visualization + explicit non-causal label |
| Federated learning | 3 worker processes/FedAvg | “Coordinator owns all data on same filesystem” | independent client services + HTTP update protocol |
| Differential privacy | Opacus ledger | “Is ε patient-level? Is randomness secure?” | precise scope + optional secure profile + budget guard |
| Adaptive feedback | cooldown after dismissals | “What exactly learns/adapts?” | visible per-type versioned policy changes |
| Offline operation | coordinator outage test | “What still works?” | show local inference/intervention while coordinator is stopped |
| Physical actuation | absent | “Where is haptic?” | virtual actuator mapping; physical status remains unverified |
| End-to-end method | synthetic path | “Does global learning return to inference?” | model validation + activation + rollback closes the loop |

---

# 29. Reviewer questions you should be able to answer live

## Architecture
**Q: What is the core novelty you are demonstrating?**  
A: Do not answer “AI healthcare.” Explain the integrated quality-aware local inference, explainable decision policy, micro-intervention feedback adaptation, privacy-preserving distributed update loop and offline continuity. Keep patent novelty conclusions for the agent.

**Q: Which part runs when the coordinator is offline?**  
A: Edge signal processing, quality checks, cached-model inference, context policy, interventions and local event logging.

**Q: Why do you need a coordinator?**  
A: To coordinate distributed model updates/evaluation/versioning, not to perform the local real-time decision.

**Q: Is this cloud deployed?**  
A: No. The coordinator role is emulated locally for the software research prototype.

## Data
**Q: Is the data real?**  
A: The executed current demo uses labelled synthetic data. WESAD adapter support exists, but real-data claims begin only after actual import/evaluation.

**Q: Why synthetic first?**  
A: To validate the deterministic end-to-end software behavior without claiming research validity.

**Q: Why does Random Forest show 100%?**  
A: Because the current synthetic generator is easily separable. It is a generator-fit result and not real-world accuracy.

## AI
**Q: The MLP is around 50%. Why use it?**  
A: It currently demonstrates the neural/federated/private training path; its predictive utility is weak. Real performance must be evaluated on an authorised real dataset.

**Q: What causes an intervention?**  
A after the required fix: model evidence/context + data-quality checks + sustained duration + cooldown/suppression policy. The model score alone does not prescribe an action.

**Q: Is SHAP a clinical explanation?**  
A: No. It explains model output contribution, not causality or medical effect.

## Federation
**Q: Is this really federated?**  
A after upgrade: three separate local services own independent partitions, receive a base model and return parameters; coordinator receives no raw windows. Same-machine deployment is a local federation experiment, not a multi-device production deployment.

**Q: Why not centralized training?**  
A: The architecture demonstrates keeping client training records local while sharing model updates, matching the privacy-oriented distributed design.

**Q: What happens if one client is missing?**  
A: The current configured round requires all three; it fails rather than silently averaging two.

## Privacy
**Q: What does ε=5.4 mean?**  
A: It is the measured example-level privacy budget for the configured synthetic 30-second-window mechanism at the stated delta. It is not patient-level privacy.

**Q: Is it cryptographically secure DP?**  
A: Not in the current experimental `secure_mode=False` run.

**Q: Do you have secure aggregation?**  
A: No. It is an explicit limitation/future security layer.

## Intervention
**Q: Does “Completed” mean the user improved?**  
A: No. It means the user completed the software interaction.

**Q: Does feedback retrain the medical model?**  
A: No. Current feedback changes bounded intervention timing/policy; it is not silently treated as a physiological ground-truth label.

## Patent/physical embodiment
**Q: Where are the physical sensors?**  
A: This software-in-the-loop prototype simulates/plays recorded-compatible inputs. Physical sensing remains outside the demonstrated scope and is mapped separately.

**Q: Then how does this support the patent?**  
A: It provides executable evidence for the software processing, learning, explanation, adaptation and intervention-control architecture, while physical elements remain explicitly unverified.

---

# 30. Things you must NOT say in the viva/demo

Avoid these statements:

| Do not say | Say instead |
|---|---|
| “The patent is validated.” | “This prototype demonstrates selected software aspects of the filed architecture.” |
| “The patent will be granted.” | “Grant/examination is a legal process independent of this prototype.” |
| “Our model has 100% accuracy.” | “The RF separates the current synthetic generator perfectly; this is not real-world accuracy.” |
| “We detect medical stress.” | “The current demo classifies a synthetic baseline-vs-stress-like task; real-data validation is separate.” |
| “Differential privacy makes all data safe.” | “The private training run has a measured example-level `(ε, δ)` scope with stated limitations.” |
| “Federated learning means the server cannot attack anything.” | “Raw training windows remain client-side in the intended protocol; secure aggregation is not yet implemented.” |
| “We implemented the hardware.” | “Physical components are mapped, but not physically assembled/validated in this software-only prototype.” |
| “The cloud is implemented.” | “A local coordinator emulates the cloud/model-coordination role.” |
| “SHAP proves why stress happened.” | “SHAP explains the model’s output contribution, not the cause of a human condition.” |
| “User completed the prompt, so intervention worked.” | “Completion records interaction only.” |

---

# 31. Exact file-level work plan

## Root / repository
- Fix `.gitignore`.
- Remove `.pytest_temp`.
- Remove `src/nexora.egg-info`.
- Add missing tracked `src/nexora/data`.
- Add `scripts/bootstrap.py`.
- Add CI.
- Make repo private or sanitize patent-private docs.
- Add `SECURITY.md` for local prototype scope if repository remains shared.
- Add `THIRD_PARTY_NOTICES.md` / data-source acknowledgement file.

## `src/nexora/data`
Ensure tracked:
- `__init__.py`
- `synthetic.py`
- `wesad.py`
- source manifest helpers
- split validation
- replay abstractions.

## `src/nexora/edge`
Split monolith.
Add:
- canonical schemas;
- quality service;
- model-driven policy;
- per-type cooldown;
- evidence/export routes;
- auth;
- settings;
- session-filtered interventions.

## `src/nexora/ml`
Add:
- source-specific registry;
- evaluate module;
- latency metrics;
- per-subject metrics;
- optional calibration;
- model activation/rollback;
- explanation cache.

## `src/nexora/federation`
Add:
- client FastAPI service;
- protocol schemas;
- update authentication;
- base/update hash verification;
- round registry;
- duplicate protection;
- HTTP aggregation flow;
- global candidate registration;
- cancellation propagation.

## `src/nexora/privacy`
Refactor DP into explicit module:
- ledger;
- budget projection;
- dataset identity;
- secure-mode capability;
- accounting tests.

## Frontend
Refactor `main.tsx` into pages/components.
Add:
- mode switch;
- Participant pages;
- distinct Overview/Live;
- clear intervention page;
- visual attribution;
- labelled confusion matrix;
- federation topology;
- evidence matrix/export;
- real settings;
- glossary/tooltips;
- local fonts/system fonts;
- responsive/reduced motion.

## Tests
Replace placeholder frontend test.
Add Playwright.
Add CI-friendly acceptance smoke.

## Docs
Create/update:
- `PRIOR_ART_AND_DIFFERENTIATION.md`
- `DATA_SOURCES.md`
- `MODEL_REGISTRY.md`
- `REPRODUCIBILITY.md`
- `HARDWARE_MAPPING.md`
- revised claim map;
- revised handoff;
- revised Q&A.

---

# 32. Implementation order — do not randomly beautify the UI first

## Stage 1 — repository integrity
1. Gitignore/source tracking.
2. Remove generated junk.
3. Bootstrap.
4. Fresh clone passes.

## Stage 2 — evidence truthfulness
1. Fix completion documents.
2. Fix heart-rate provenance.
3. Fix API/documentation mismatch.
4. Sanitize/private patent notes.

## Stage 3 — close the product loop
1. Model-driven intervention.
2. breathing guidance.
3. per-type adaptation.
4. explicit decision/prediction linkage.

## Stage 4 — federation
1. independent local client services;
2. actual REST update flow;
3. update validation;
4. candidate model;
5. activation/rollback.

## Stage 5 — real data
1. WESAD import;
2. split;
3. train/evaluate;
4. source-specific model;
5. optional WESAD federation.

## Stage 6 — UI
1. User/Research mode;
2. distinct Live page;
3. Intervention UX;
4. AI visualizations;
5. federation topology;
6. Evidence;
7. Settings.

## Stage 7 — security and DP
1. auth/tokens;
2. privacy projection;
3. cancellation;
4. optional secure RNG.

## Stage 8 — acceptance
1. meaningful unit/integration tests;
2. Playwright;
3. performance;
4. screenshots;
5. final evidence ZIP;
6. clean-start rehearsal.

---

# 33. Final exam acceptance checklist

Do not mark “Exam Ready” until every applicable item is checked.

- [ ] Fresh GitHub clone contains `src/nexora/data`.
- [ ] Fresh clone bootstrap works.
- [ ] No private patent notes in public repo.
- [ ] No `.pytest_temp`/egg-info committed.
- [ ] Normal demo runs with internet disconnected.
- [ ] No Google Fonts/CDN request.
- [ ] User Mode exists.
- [ ] Research Mode exists.
- [ ] Overview and Live are genuinely different.
- [ ] Human-readable scenario names.
- [ ] Every sensor/value has provenance.
- [ ] Heart-rate story is consistent.
- [ ] Missing-data scenario abstains.
- [ ] Brief posture does not trigger.
- [ ] Sustained posture triggers.
- [ ] Model-driven intervention exists.
- [ ] High-motion suppression is visible.
- [ ] Feedback changes per-type policy.
- [ ] Intervention records link to reasons/predictions.
- [ ] SHAP/IG visualization is understandable.
- [ ] Synthetic 100% warning is visible.
- [ ] Real WESAD imported or clearly marked unavailable.
- [ ] If WESAD imported, participant separation is verified.
- [ ] Three real client services run.
- [ ] Coordinator receives no raw client windows.
- [ ] Wrong/duplicate federated update is rejected.
- [ ] Federated model becomes a candidate.
- [ ] Candidate can be activated.
- [ ] Rollback works.
- [ ] Coordinator outage preserves local inference.
- [ ] Privacy budget projection works.
- [ ] Private run cannot silently exceed configured cap.
- [ ] Secure RNG status is truthful.
- [ ] Secure aggregation status is truthful.
- [ ] State-changing APIs are authenticated.
- [ ] Frontend placeholder test removed.
- [ ] Playwright full flow passes.
- [ ] Direct refresh of each route works.
- [ ] Chrome/Edge smoke passes.
- [ ] Keyboard navigation passes.
- [ ] 1366×768 screenshot passes.
- [ ] 390×844 screenshot passes.
- [ ] Inference median/p95 recorded.
- [ ] decision-to-render p95 recorded.
- [ ] Evidence page contains claim map.
- [ ] Evidence export works from UI.
- [ ] Evidence ZIP contains commit SHA.
- [ ] Evidence ZIP contains test reports.
- [ ] Evidence ZIP contains screenshots.
- [ ] Evidence ZIP contains scenario traces.
- [ ] Evidence ZIP excludes secrets/raw WESAD.
- [ ] BUILD_STATUS has no contradictions.
- [ ] ACCEPTANCE_REPORT only marks actually verified criteria.
- [ ] FINAL_HANDOFF commands exist and work.
- [ ] Demo script rehearsed from a clean start.
- [ ] You can answer every question in Section 29 without exaggerating.

---

# 34. Recommended 7–10 minute reviewer demonstration

## Minute 0–1 — scope
Open Evidence/Architecture first.

Say:
> “This is a software-in-the-loop research prototype. I will distinguish simulated sensing, real software decisions and unimplemented physical outputs.”

Show pipeline.

## Minute 1–2 — normal flow
Start Normal at 20×.
Show real streaming EDA/temp/motion.
Show no-action decisions.

## Minute 2–3 — data quality
Run Missing Data.
Show quality failure and model abstention.

## Minute 3–4 — deterministic intervention
Run Sustained Posture.
Show 30-second event-time persistence.
Show posture prompt.
Dismiss twice if rehearsed and show policy cooldown change.

## Minute 4–5 — AI-driven path
Run a scenario that generates a qualified model-driven prompt.
Open “Why this suggestion?”
Show prediction + policy reason + quality/suppression checks.

## Minute 5–6 — explainability
Open AI Insights.
Explain that RF perfect synthetic result is generator-only.
Show signed attribution for one prediction.

## Minute 6–7 — federation
Open Federation.
Show A/B/C client services, local updates, hashes, aggregation.
Run one short round or use a prepared completed run.
Show candidate global model and activation.

## Minute 7–8 — privacy
Show Opacus epsilon/delta, steps, privacy unit, budget projection and limitations.

## Minute 8–9 — outage
Stop coordinator.
Show edge inference remains available.
Restart coordinator.

## Minute 9–10 — evidence
Open claim map.
Show WESAD status.
Export the evidence ZIP.
End with limitations, not marketing.

---

# 35. Technical references used for this hardening review

## Indian patent examination / patentability
- IP India, Patents Act Section 10 — contents/sufficiency of specifications:  
  https://ipindia.gov.in/acts/patent-act-1970/section-10
- IP India, Patents Act Section 3 — exclusions including treatment processes and computer programme/algorithms:  
  https://ipindia.gov.in/acts/patent-act-1970/section-3
- IP India, definition of invention/inventive step:  
  https://ipindia.gov.in/acts/patent-act-1970/section-2-5
- IP India, Guidelines for Examination of Computer Related Inventions (CRIs) — 2025:  
  https://ipindia.gov.in/resource/patents-resources-guidelines
- IP India, Manual of Patent Office Practice and Procedure:  
  https://ipindia.gov.in/resource/patents-resources-manuals

## Dataset
- UCI WESAD dataset:  
  https://archive.ics.uci.edu/dataset/465/wesad+wearable+stress+and+affect+detection

## Differential privacy
- Opacus PrivacyEngine documentation:  
  https://opacus.ai/api/privacy_engine.html
- Opacus secure RNG FAQ:  
  https://opacus.ai/docs/faq

## Examples showing a crowded research area
- Wrist-Based Electrodermal Activity Monitoring for Stress Detection Using Federated Learning (2023):  
  https://pmc.ncbi.nlm.nih.gov/articles/PMC10146352/
- HAFN federated privacy-preserving multimodal stress detection (2026):  
  https://www.nature.com/articles/s41598-026-69876-7
- Privacy-Preserving and Explainable Federated Edge Learning for Multimodal Wearable-Based Self-Tracking and Monitoring (2026):  
  https://journalajrcos.com/index.php/AJRCOS/article/view/845

These references demonstrate why NEXORA should not rely on broad phrases such as “wearable stress detection with FL/DP/XAI” as its entire differentiation.

---

# 36. Codex execution instruction

Place this file in the project root and give Codex this instruction:

> Read `NEXORA_PATENT_REVIEWER_HARDENING_PLAN.md` completely and inspect the current repository before changing anything. Treat all P0 items as blockers. Implement the plan in the stated order, preserving currently working behavior and measured evidence. Do not fabricate metrics, browser verification, WESAD results, hardware outputs, privacy guarantees, patent validity or completion status. After each stage, run the affected tests. At the end, perform a fresh-clone-equivalent clean-start verification, run the complete acceptance suite, update all documentation to match the actual implementation, regenerate the evidence package, and leave any genuinely unverified item explicitly marked as such. Do not mark the project Exam Ready until the checklist in Section 33 is satisfied or each unsatisfied item is recorded as an explicit blocker.

---

# 37. Bottom line

The project is currently a **credible engineering prototype with several real components**, but the current “complete” label is ahead of the evidence.

The highest-value improvements are not cosmetic:

1. make the repository reproducible;
2. close the AI → intervention → feedback loop;
3. make federation a real local service protocol and activate the resulting model;
4. run a genuine WESAD evaluation;
5. provide a normal-user interface alongside the research console;
6. turn Evidence into a real audit surface;
7. replace placeholder tests with browser-level acceptance;
8. align every document with what the code actually does;
9. keep physical/patent limitations explicit;
10. prepare the examiner story around **technical interactions and measurable behavior**, not buzzwords.

When those are done, NEXORA will be much harder for a reviewer to dismiss as “only a dashboard”, “only synthetic”, or “just known AI components put together.”
