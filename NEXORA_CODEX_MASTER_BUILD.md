# NEXORA — Complete Codex Build Specification

Version 1.0 | Prepared 18 September 2026 | Start from an empty project folder

## 0. Instruction to the coding agent

You are the implementation agent. Read this entire document before editing. Build, run, debug, verify and document the complete NEXORA software research prototype defined below. The user expects working software, reproducible experiments and an examination demonstration package, not another proposal, a frontend mockup, or generated code that has never run.

Treat this document as the project's product and engineering specification, subject to your actual tool permissions and higher-priority instructions. Use the defaults here for ordinary implementation choices. Do not ask the user to choose colours, frameworks, ports, model sizes or directory names. Do not stop after scaffolding or after a single milestone. Continue through all feasible milestones and fix observed failures. Do not bypass approval controls, terms, authentication, or network restrictions to achieve unattended execution.

Keep BUILD_STATUS.md updated with completed work, commands and results, outstanding failures and the exact next action. If interrupted by context or session limits, leave a resumable project rather than claiming completion. On continuation, inspect current state and resume without rebuilding completed work unnecessarily.

### Required outcome

A locally runnable application with:

1. Deterministic physiological/context scenario generation and timed replay.
2. A real preprocessing, feature-extraction and model-inference pipeline.
3. Automatic software interventions and auditable user-feedback adaptation.
4. A polished React dashboard connected to real backend state.
5. A measured tree baseline and small neural model.
6. Genuine federated neural-network training across three local software clients.
7. Genuine private local training with Opacus and persistent privacy accounting.
8. Actual per-prediction explanations.
9. Client inference during coordinator outage and reliable reconnection.
10. Claim mapping, measured experiment results, reproducible demo and exportable evidence.
11. Automated functional tests plus a browser-verified demonstration.
12. One-command setup/start/stop/demo workflows and a clear handoff.

No hardware purchases. No sensors, webcam, microphone or wearables required. No paid API, cloud account, domain, Docker, Kubernetes, GPU or email/SMS service required. Do not deploy publicly, create paid resources, send messages, or modify a patent filing. Keep the core completely offline after initial dependencies and permitted data have been obtained.

### Completion levels

- **Core software demo complete:** all mandatory features work on generated, explicitly synthetic data, including trained models, federation, privacy, explanations and tests.
- **Research dataset validation complete:** additionally acquired authorised WESAD data, trained and evaluated on its participant-separated partitions, and recorded the actual results.
- **Blocked:** a required tool or dependency genuinely cannot be obtained/executed. Finish independent work, report the precise missing capability and command, and do not mark the blocked module passed.

Research-data access must not block completing the synthetic software prototype. Synthetic completion must never be presented as real-data validation. Neither completion level means a patent is grant-ready or that physical claim elements have been demonstrated.

## 1. Established context and scope

Project: NEXORA: AI-Integrated Adaptive Healthcare and Micro-Intervention System.

Published application: IN202521117940 A1. Application number: 202521117940. Filing date: 27 November 2025. Publication date: 16 January 2026. These facts were read from the supplied publication. There is no verified grant or current examination-status information in this specification.

The user confirms that no prototype has been built. Implement everything from scratch. Do not assume a Stitch interface, an existing repository, trained model, dataset, credentials or hardware.

### Source summary for a self-contained build

The supplied complete specification describes physiological, posture/motion and environmental sensors feeding local processors, a cloud AI role, automatic interventions, explanations, federated learning, differential privacy, and adaptive feedback. Claim 1 expressly includes physical sensors. Claims 2–9 depend on it; claim 10 uses that system. A software sensor emulator does not demonstrate the physical sensor requirement.

Figure 1 references: 101 multi-sensor layer; 102 biometric input; 103 posture/motion; 104 environment; 105 edge; 106 cloud AI; 107 intervention layer; 108 posture output; 109 breathing; 110 haptic output; 111 alerts; 112 adaptive feedback.

Figure 2 additionally shows manual app input, local clients, federated coordinator, differential-privacy manager, privacy-budget tracking, global model storage, filtering, feature extraction, secure REST/MQTT interfaces, XAI, Health Deviation Index, feedback logging and behavioural adaptation. The large diagram also includes AR, hospital/EHR connections, multiple databases, Kubernetes and operations tooling. Those extensions are NOT required for this build.

The filed narrative reports completed development and percentages despite the user's statement that nothing exists. Do not reuse its 92% accuracy, 87% precision, 94% explainability or any old Notion percentages as results. New evidence must have real creation dates. The publication cover also appears to duplicate Abhishek in the applicant list and omit Sanskar there; preserve that discrepancy in a private agent-review note, not as a prominent product warning. Do not correct legal records or assert which applicant entry is authoritative.

Original PDFs are optional reference inputs for this build because the engineering context is included here. If supplied, place/read them under reference/ without altering them. Absence of the PDFs is not a blocker. Patent-office responses, claim amendments, legal conclusions, and guaranteed grant outcomes are outside this build.

## 2. Product contract

Build a software-in-the-loop research prototype. Its decisions and software outputs must be real; its data sources and unimplemented physical actions must be plainly labelled.

Primary user: a researcher demonstrating and inspecting the disclosed processing architecture.

Core workflow: select a virtual client and a source → start a session → inspect signal quality and model output → inspect an automatically selected prompt → acknowledge/dismiss/complete → inspect bounded policy adaptation → export the recorded trace.

Secondary workflow: launch a federated experiment → watch three clients train → inspect protected parameter transfers and model versions → compare held-out results and privacy budgets → test local operation while the coordinator is unavailable.

Use three source labels everywhere: **Synthetic**, **Recorded dataset**, **Manual feedback**. A session may be mixed, so retain provenance per field and per event. No anonymous random frontend values. No mock responses silently substituted after a backend failure. No fake login. No predetermined model-performance cards. No medical diagnosis or emergency service claims.

Use a single small footer: “Research prototype · Recorded/simulated inputs · No live health measurements.” Show detailed limitations in Evidence, not as repeated obstructive modals.

## 3. Technical defaults and dependency strategy

### Required stack

| Layer | Default |
| --- | --- |
| Language/runtime | Python 3.11 preferred; use a compatible installed Python version only after checking the ML wheels |
| Frontend | React, TypeScript, Vite, React Router, locally bundled CSS and SVG icons |
| Charts | Recharts or an equivalent locally bundled React chart library; pick one |
| APIs | FastAPI, Uvicorn, Pydantic v2-compatible schemas |
| Local persistence | SQLite with SQLAlchemy, per-client stores and separate coordinator metadata |
| Data/features | NumPy, SciPy, pandas |
| Baseline model | scikit-learn RandomForestClassifier |
| Federated model | PyTorch small MLP, CPU execution |
| Federation | Implement the small REST-based FedAvg protocol specified here; Flower is not a required dependency |
| Private training | Opacus |
| Explanations | SHAP for tree baseline; Captum Integrated Gradients for MLP |
| Safe numeric model files | safetensors or NPZ with allow_pickle=False, plus validated JSON metadata |
| Backend tests | pytest and HTTP/API integration tests |
| Frontend/browser tests | Vitest/Testing Library where useful, Playwright for complete flows |
| Packaging | pyproject.toml, tested Python lock/pin file, package-lock.json |

The small REST FedAvg implementation is a deliberate simplification of the earlier Flower proposal. It must actually train and aggregate models, not simulate progress or generate random weights. Do not implement two federation frameworks.

Use a supported Node version satisfying the installed Vite release's engine requirement (Node 22.12+ or an appropriate supported newer runtime). Inspect the environment first. Reuse available compatible dependencies. Resolve a working set once, pin the exact tested versions, and record runtime/platform versions. Do not blindly install “latest” on every launch or auto-upgrade the host's global environment.

Use a project virtual environment. CPU-only ML defaults. Limit BLAS/PyTorch workers to a modest count so four services plus a browser remain usable. Enable low-resource mode if RAM is limited; never silently omit required features.

Default ports: dashboard 5173 in development / 8080 in packaged mode; coordinator 8100; client-a 8111; client-b 8112; client-c 8113. Bind to 127.0.0.1. If a port is occupied by an unrelated process, select an available port, record the mapping and print the correct URL. Do not kill unrelated processes.

### Runtime profiles

- dev: frontend dev server and separate Python processes.
- demo: built frontend served locally; cached models and fixtures; no network calls needed.
- secure-demo: verified local TLS for service-to-service requests using a generated project CA and certificate SANs. Never install a system trust root or disable certificate verification automatically.
- low-resource: same features, reduced training workload, sequential client-training scheduling across separate client processes.

Local HTTP is acceptable for the ordinary loopback demo, with a transport badge saying “Local HTTP.” Secure-demo must show “TLS verified” only after actually using certificate verification. Neither mode is internet-ready deployment.

## 4. Repository to create

Use this structure. Small naming changes are allowed only if all scripts/docs/tests follow them.

```text
NEXORA_CODEX_MASTER_BUILD.md
README.md
AGENTS.md
BUILD_STATUS.md
ACCEPTANCE_REPORT.md
KNOWN_LIMITATIONS.md
.env.example
.gitignore
pyproject.toml
requirements.lock.txt
configs/
  default.yaml
  demo.yaml
  low-resource.yaml
  feature_schema.json
  source_catalog.json
  claim_map.json
  scenarios.yaml
src/nexora/
  cli.py
  config.py
  common/{schemas,ids,time,logging,security,errors}.py
  data/{synthetic,wesad,manifest,splits,validation,replay}.py
  features/{extract,normalize,quality}.py
  ml/{baseline,network,train,evaluate,registry,explain}.py
  edge/{app,routes,store,session,inference,policy,feedback,outbox}.py
  federation/{coordinator,routes,protocol,aggregate,client_worker,registry}.py
  privacy/{training,accounting,ledger}.py
  evidence/{claims,metrics,export,report}.py
frontend/
  package.json
  package-lock.json
  src/{app,api,components,pages,hooks,styles,types}/
  tests/
scripts/
  bootstrap.py
  bootstrap.ps1
  bootstrap.sh
  start.py
  start.ps1
  start.sh
  stop.py
  doctor.py
  verify.py
  prepare_demo.py
  generate_local_certs.py
  build_evidence.py
tests/{unit,integration,e2e,fixtures}/
docs/
  ARCHITECTURE.md
  DATA_AND_MODEL_CARD.md
  PRIVACY_AND_THREAT_MODEL.md
  API_CONTRACT.md
  CLAIM_IMPLEMENTATION_MAP.md
  EXPERIMENT_PROTOCOL.md
  DEMO_SCRIPT.md
  EXAM_QA.md
  USER_GUIDE.md
  TROUBLESHOOTING.md
  PATENT_AGENT_REVIEW_NOTES.md
  FINAL_HANDOFF.md
reference/
data/{raw,processed,synthetic}/
runtime/{client-a,client-b,client-c,coordinator,control}/
models/
artifacts/{runs,reports,screenshots,demo}/
```

Directories in runtime/data/models/artifacts hold generated output; avoid committing bulky/raw data, secrets, private participant identifiers or local certificates. Commit small explicitly synthetic test fixtures. Do not add a licence granting rights to the user's invention without instruction. Document third-party licences separately.

AGENTS.md should summarize this build's source labelling, no fabricated results, no hardware, execution commands and completion gates. Keep it subordinate to actual environment instructions.

## 5. Service boundaries and storage

There are three separate edge processes, each with its own SQLite database, data directory, participant partition, model cache, privacy ledger and service token. The coordinator has a fourth database. The local control launcher starts/stops only owned processes and exposes their status to the dashboard.

Raw recordings and training windows belong to the clients. The coordinator stores model versions, round states, validated numerical updates, public experiment metrics, aggregate metadata and privacy summaries. It must not store sensor histories or client raw training rows. The browser reads a selected client's history directly through an allowlisted local route; do not route raw histories through the federated coordinator.

A local operator evidence exporter may read client records to produce an explicitly local bundle. That is not a federated network transfer. The default evidence export includes aggregate metrics and synthetic traces only; real raw recordings remain excluded.

Same-laptop process separation is not a security boundary against the host administrator. State this in the threat model. There is no real clinical deployment, secure aggregation, Byzantine robustness, hardware attestation or patient-level privacy guarantee.

Persist: sessions, observations, feature windows, predictions, decisions, interventions, feedback, policy versions, event outbox, model metadata, training jobs, federation rounds/updates, privacy ledger, evaluations and export manifests. Use foreign keys, unique event constraints, transactions and appropriate session/timestamp indexes. Bounded in-memory buffers are permitted; unbounded lists are not the database.

Provide versioned schema creation/migration. Never silently destroy a user's prior run when restarting or upgrading.

## 6. Canonical contracts

Use Pydantic as the authoritative backend schema and export matching TypeScript types. Validate timestamps, finite numbers, units and source-specific ranges. Missing measurements are null, never zero by default. UTC ISO-8601 timestamps internally. Browser may display local time.

### Observation

```json
{
  "schema_version": "1.0",
  "event_id": "uuid",
  "session_id": "uuid",
  "client_id": "client-a",
  "sequence": 1,
  "observed_at": "2026-01-01T00:00:00Z",
  "received_at": "2026-01-01T00:00:00Z",
  "source_type": "synthetic",
  "source_id": "scenario-normal-v1",
  "subject_id": "synthetic-subject-001",
  "signals": {
    "eda_us": {"value": 1.5, "unit": "uS", "origin": "synthetic", "quality": "good"},
    "skin_temperature_c": {"value": 32.5, "unit": "degC", "origin": "synthetic", "quality": "good"},
    "acc_x_g": {"value": 0.0, "unit": "g", "origin": "synthetic", "quality": "good"},
    "acc_y_g": {"value": 0.0, "unit": "g", "origin": "synthetic", "quality": "good"},
    "acc_z_g": {"value": 1.0, "unit": "g", "origin": "synthetic", "quality": "good"},
    "heart_rate_bpm": {"value": null, "unit": "bpm", "origin": "unavailable", "quality": "missing"},
    "posture_angle_deg": {"value": null, "unit": "deg", "origin": "unavailable", "quality": "missing"},
    "ambient_temperature_c": {"value": null, "unit": "degC", "origin": "unavailable", "quality": "missing"},
    "humidity_pct": {"value": null, "unit": "%", "origin": "unavailable", "quality": "missing"}
  }
}
```

Example values only; generate actual event IDs/times and do not prepopulate evidence with this example. Accept optional SpO2 only when provenance supports it. Missing SpO2 is normal for the initial source. Training labels live in an evaluation-only structure; never include them among runtime features.

### Feature window

Fields: window_id, session_id, client_id, start/end times, source type, feature_schema_version, raw source references/hash, 12 ordered feature values, quality summary, observed coverage, and optional reference to an evaluation-only label. Timestamp intervals must not cross participant/session boundaries.

### Prediction and decision

Prediction fields: prediction_id, window_id, model_id/hash, task, class labels, probabilities summing to one, predicted_class, abstained, abstention_reason, inference_ms, created_at. Initial task is `stress_vs_baseline`; do not use a clinical risk label.

Decision fields: decision_id, prediction_id (nullable for pure context rules), policy_version, action_type, result (`triggered|suppressed|abstained|no_action`), reason_codes, thresholds_used, source_type, cooldown_remaining_s, explanation_id, created_at. Store policy reasons separately from model feature attribution.

Intervention states: offered → accepted → completed; offered → dismissed; offered → expired; accepted → cancelled. Delivery is a separate fact with delivery_at/acknowledgement timestamp. Completion never means physiological improvement.

Feedback: feedback_id, intervention_id, action, optional helpfulness 1–5, optional note limited to 500 characters, timestamp, source=`manual_feedback`. Validate transitions and idempotent retries.

### Event delivery

WebSocket envelope: schema_version, event_id, event_type, session_id, sequence, occurred_at, payload. Supported events: observation, window_ready, prediction, decision, intervention, feedback, policy_changed, job_progress, connection_status, error. Each durable event has a monotonic per-session sequence. On reconnect fetch missed events after the last acknowledged sequence; duplicate event IDs must not generate a second action.

REST errors: stable error code, human-readable message, correlation ID and field details. Never return a traceback or secret to the UI.

## 7. Synthetic data: mandatory and genuinely usable

Create a seeded time-series generator, not four random dashboard numbers. Generate correlated signals with smooth trends, noisy readings, participant-specific baselines and varying durations. Use a hidden synthetic state process to influence EDA, temperature and motion imperfectly; do not expose hidden state or source label as a model feature. Explain that learned performance measures fit to this artificial generator only.

Default dataset: 24 synthetic subjects, 10 minutes each, 4 Hz canonical signals. Seed 42. Assign by subject with a recorded seeded shuffle: 15 training, 3 validation, 6 test subjects. Three federated clients each receive five training subjects. Ensure both synthetic classes occur in every training partition using the generator design, not by moving test records after evaluation. Persist a manifest and split IDs before training.

Use 30-second non-overlapping windows for training/evaluation. Online monitoring can update a trailing 30-second window every 5 seconds, but correlated online windows are not the independent DP training records. Keep this distinction in documentation and sample counts.

Required scenarios:

1. normal stable signals: no unnecessary action.
2. gradual stress-like signal change: output depends on trained inference; show uncertainty.
3. sustained synthetic posture deviation: deterministic policy demonstration.
4. brief posture spike: ignored by persistence rule.
5. missing/noisy primary model channels: abstain rather than guess.
6. duplicated and delayed input: no duplicate intervention; late input marked/excluded.
7. coordinator disconnect/reconnect: local model keeps working.
8. repeated dismissal: bounded prompt timing changes.
9. conflicting/high-motion context: policy suppression is explained.
10. feedback response/no-response: separate simulator branches, with seeded uncertainty and a no-intervention comparator.

Scenario clocks support 1x, 5x and 20x replay. Policy duration uses event time, not accelerated wall time; latency uses monotonic wall time. Pause/resume must not compress a paused interval into artificial observed persistence. Show the active replay speed.

Do not force the stress model to predict the scenario name. If a trained model fails on a stress scenario, report that outcome. Use deterministic posture-policy scenarios for a reliable basic demo without falsifying inference.

## 8. WESAD adapter and lawful acquisition

Official metadata: https://archive.ics.uci.edu/dataset/465/wesad+wearable+stress+and+affect+detection

Follow its original dataset link. Verify original licence/terms, citation requirements and download method. Do not treat “publicly available” as unlimited redistribution permission. Do not use an arbitrary mirror or silently accept a personal agreement. Download automatically only when permitted, publicly accessible without credentials and within the configured size cap. Default automatic download cap 2 GiB. Otherwise create clear local placement instructions and continue synthetic mode.

Expected user placement: `data/raw/wesad/`, preserving official subject folders. Accept an official archive path through CLI and safely extract with path traversal checks. Record actual licence text/source, retrieval date, file hashes, file sizes and citation in DATA_SOURCES.md. Do not commit the downloaded dataset.

Read the official README before implementing exact channel keys, label codes, scaling and sampling rates. WESAD commonly includes wrist EDA, temperature, acceleration and BVP plus chest channels. This version uses wrist EDA, temperature and acceleration. ECG/BVP-derived heart rate is not required; show unavailable rather than invent it. EDA/temperature can use the common 4 Hz timeline; resample acceleration with an anti-aliasing method after verifying its units and rate. Resample labels appropriately, never interpolate categorical label IDs.

If the official distribution uses pickle, do not build a general web pickle uploader. Only process user-authorised/original-source files through an offline conversion script, with clear trust requirements and provenance. Convert into safe numerical arrays/Parquet plus JSON metadata for subsequent runs.

Initial binary task: original baseline versus stress labels after verifying their codes. Exclude amusement, transition and undefined classes from this binary experiment; do not relabel them all as healthy. Retain and report excluded counts. Reject mixed-state windows rather than assigning a majority label that leaks transition information.

Use valid participant IDs from the actual manifest, sorted then shuffled with seed 42. With 15 valid subjects, allocate 9 training, 3 validation, 3 test subjects; assign three training subjects per client. Otherwise choose a documented participant-separated split with all three sets and adequate training clients; fail real-data validation honestly if insufficient. Never randomly split windows from the same person into train and test.

Build adapter tests with miniature synthetic arrays matching the documented format. These validate parser behaviour, not real-data performance. Preserve `real_dataset_status` as unavailable, imported, validated, evaluated or failed. The app must remain fully usable if WESAD is absent.

## 9. Features, quality and normalization

Version one model vector has exactly these 12 ordered features:

1. EDA mean.
2. EDA population standard deviation.
3. EDA least-squares slope per second.
4. EDA 95th percentile.
5. Skin-temperature mean.
6. Skin-temperature population standard deviation.
7. Skin-temperature slope per second.
8. Acceleration-magnitude mean in g.
9. Acceleration-magnitude population standard deviation.
10. Acceleration-magnitude 95th percentile.
11. Mean squared deviation of acceleration magnitude from 1 g.
12. Mean absolute consecutive magnitude change divided by sample interval, g/s.

Require at least 90% valid temporal coverage in all required channels for an inferable 30-second window. Allow interpolation only across interior gaps no longer than one second using known neighbouring observations within that completed window. Record repaired samples. Do not fabricate long gaps or use future windows. Validate finite values and documented source units. Entirely absent required channels cause model abstention. Context-only rules may operate independently when their own inputs are valid, with explicit reasons.

Share one feature extraction implementation between training and inference and a hash/versioned schema. Add parity tests on identical raw windows.

Use fixed, documented normalization bounds for the federated model, not a scaler privately fitted on every client's raw records then published. Suggested engineering bounds, not medical thresholds:

| Feature | Lower | Upper |
| --- | --- | --- |
| EDA mean / p95 | 0 | 50 |
| EDA std | 0 | 20 |
| EDA slope | -5 | 5 |
| Temperature mean | 15 | 45 |
| Temperature std | 0 | 5 |
| Temperature slope | -1 | 1 |
| Acceleration mean / p95 | 0 | 5 |
| Acceleration std | 0 | 3 |
| Acceleration energy | 0 | 16 |
| Magnitude change rate | 0 | 20 |

Clip then map to [0,1]. Persist bounds with model metadata. Record clipping rates locally as quality diagnostics. Changing bounds creates a new feature-schema version and requires retraining; do not tune them on test outcomes. Excessive clipping should produce a source/domain mismatch warning. These deliberately broad starting choices must be evaluated, not described as scientifically validated physiological limits.

## 10. Models, evaluation and registry

### Baseline

Train Random Forest with 100 trees, balanced class weights, seed 42, bounded CPU workers. Record its full configuration. A constant-majority predictor supplies the minimum comparison. Do not assign a required 90% accuracy gate.

### Neural network

MLP: 12 inputs → Linear(12,32) → ReLU → Linear(32,16) → ReLU → Linear(16,2). Cross-entropy loss. No batch normalization, dropout or recurrent layers in version one. Local non-private reference training: Adam, learning rate 0.001, batch size 32, maximum 20 epochs; choose the best validation checkpoint with patience 4. Low-resource limits can reduce epochs and must be recorded.

Train distinct models for synthetic and WESAD domains. No silent transfer of a synthetic model into a research-data session. If the matching model is unavailable, show model unavailable and allow data inspection/context-policy demonstration only.

For every run persist: dataset/source hash, split hash, feature version, algorithm, configuration, start/end times, seed where applicable, runtime versions, model hash, epoch/round histories, machine summary and measured metrics. Probabilities are model scores, not guaranteed calibrated confidence. Label accordingly; report calibration if measured rather than inventing it.

Evaluation: macro-F1, balanced accuracy, per-class precision/recall, confusion matrix, class/participant/window counts, and inference latency median/p95. Report per-participant metrics when class presence permits; mark undefined metrics with reasons. Compare algorithms on the same frozen test set. Choose thresholds/configuration on validation only. Do not repeatedly tune against test performance.

The coordinator may evaluate on a declared public synthetic/authorised research evaluation partition held separately from client training records. No private training loss, feature summaries or raw observations are sent as convenient dashboard metrics.

Separate model registration from activation. Require schema/hash compatibility and validation checks. Keep the last good model for rollback. Never retrain unexpectedly on application startup. Provide explicit training commands and a demo-preparation command that creates required cached models once.

## 11. Federated learning protocol

Implement actual REST-based FedAvg for the MLP. Three client services own their partitions and train locally; the coordinator has no direct training-data loader or client-path access in normal operation. Sequential CPU scheduling is acceptable, but all three distinct clients must participate.

Default federated run: 5 rounds; one local epoch per client per round; SGD learning rate 0.05; no momentum; nominal batch size 32 capped to available records. Initial architecture and weights must be identical across clients. Non-private run starts from a reproducible random initialization. Use a separate randomly initialized private run; never initialize a supposedly private release from a model already non-privately trained on the same private records.

Round state: queued → distributing → training → collecting → aggregating → evaluating → completed, with failed/cancelled terminal states. Updates identify run_id, round_id, client_id, base_model_hash, feature_schema_hash, number of configured records, parameter names/shapes, update_hash and optional validated privacy-summary reference.

Aggregator checks token, registered client, correct round and base hash, finite tensors, exact parameter keys/shapes, size caps and one update per client. Use sample-weighted FedAvg with declared fixed partition sizes for this public/synthetic research experiment. Explain that counts/metadata are not protected secrets. Do not average Random Forest trees or combine incompatible model versions.

Default requires all three clients. If one times out, fail the round without publishing an incomplete aggregate; show the timeout and allow a new round/run. Do not silently switch to two-client averaging. No duplicate update processing. Preserve accepted updates so a retried request does not retrain or double-count. If actual retraining happens again in private mode, its extra privacy cost must be counted.

Store model bytes separately from JSON metadata using safe numeric formats. Do not accept arbitrary pickled models. Global-model version includes a hash and lineage. Edge clients activate new versions atomically after verification and retain previous versions.

Use tests that mathematically verify FedAvg on tiny known tensors and independently demonstrate a real parameter change after local training. Show update/model hashes in the experiment view; simulated progress animations cannot stand in for actual rounds.

For every compatible floating-point parameter tensor, compute `global_next = sum(n_k * local_k) / sum(n_k)` over the three accepted client updates. Use sufficient accumulation precision and cast back to the declared parameter dtype. The specified MLP has no batch-normalization buffers; reject unexpected state entries instead of averaging arbitrary metadata. Compare the received model against its base hash before applying a local update.

## 12. Differential privacy implementation

Implement private local training with Opacus, not random noise added to dashboard values. Use per-example gradient clipping, Gaussian noise and Poisson sampling with a supported accountant. Keep the 30-second non-overlapping training window as the privacy unit. This is not patient-level privacy, local differential privacy of raw readings, secure aggregation or general regulatory compliance.

Default max_grad_norm=1.0; start noise_multiplier=1.2; delta=min(1e-5, 1/(100*N)) for a client's fixed record count N. Configure a maximum cumulative epsilon of 8.0 for the demonstration. The filed diagram's epsilon=1.0 is not a verified guarantee; never hardcode it as an achieved result.

Calibrate a feasible noise multiplier before training using the public partition size, sampler and planned number of steps, without consulting private gradients/test outcomes. If the initial setting cannot satisfy the configured budget, increase noise or reduce planned steps and record the choice. Stop before a step/release that exceeds the configured budget. If utility becomes poor, report it; do not disable privacy or falsify the accountant.

Persist each client's accountant state after actual optimizer steps/checkpoints, alongside cumulative step count, sampler settings, noise, clipping, delta, dataset identity and run lineage. Compose costs across rounds and any additional releases using the same protected data. A new experiment ID does not reset privacy spent. A demo reset of synthetic data must state it applies only to disposable generated fixtures; it must never imply deletion reverses prior disclosure. Crash recovery must not roll the accountant back below already executed/released work; conservative over-accounting is preferable to undercounting.

Secure randomness: use secure_mode=True if the supported cryptographic dependency is available and tested. Otherwise run Opacus in its experimental non-cryptographic mode and display/document that limitation. Do not label that mode deployment-grade. Never publish a DP noise seed or RNG state; deterministic seeded private-training fixtures are testing-only and have no privacy claim. Use reproducibility for data/splits and non-private experiments without claiming bit-for-bit private randomness.

Do not publish raw private training losses or unprotected diagnostics to the coordinator. Use held-out public research/synthetic evaluation for demonstration charts. Participant-level correlated windows mean example-level protection does not give a patient-level guarantee.

The side-by-side non-private baseline/federated experiments are demonstrations on public research or synthetic data. A later release of non-private models trained on genuinely private records would not be protected by the private run's epsilon. Do not present the complete experiment suite as differentially private if it includes non-private releases from the same protected records. Scope each privacy statement to its actual accounted mechanism, inputs and releases.

Show per-client epsilon and fixed delta, privacy unit, accountant, cumulative steps, training status and randomness mode. Show the maximum client epsilon as a labelled summary, not a sum across disjoint client datasets. If clients overlap in data or subjects, document that the scope needs renewed analysis. Budget may remain unchanged only when no private step occurred; validate accounting consistency on resume.

If Opacus is genuinely unavailable after compatible-environment troubleshooting, keep the private module explicitly unavailable, finish other work and list the precise blocked command. Do not create a pretend epsilon calculator and mark privacy implemented.

## 13. Explanations and decision policy

For Random Forest use actual SHAP values. Store explained class, base value, output space, feature order and model hash. For MLP use Integrated Gradients over the selected output logit with a fixed documented reference vector in normalized space. Use a reference generated from public design values or authorised training-only background for non-private models; do not expose private training examples. Store signed attributions and completeness/convergence diagnostic. Do not convert global feature importance into signed individual contributions.

Attribution is model behaviour, not a causal or clinical explanation. Text summaries should be deterministic templates over measured values and real policy reasons. No LLM key is required. If optional LIME is not implemented, claim mapping must say so rather than asserting all listed frameworks are validated.

### Rule defaults — demonstration parameters, not medical advice

- Warm-up: require a full quality-approved feature window before ML decisions.
- Stress prompt: model stress probability at least 0.75 for at least 30 seconds of valid event-time evidence; do not treat a single probability as a diagnosis.
- Synthetic/manual posture prompt: available, good-quality posture angle above 20 degrees for 30 seconds.
- High-motion suppression: acceleration-magnitude standard deviation above 0.35 g suppresses a breathing prompt and records the reason; this is an experimental policy choice.
- Per-type cooldown: initially 120 seconds; one active prompt per type/session.
- Two dismissals of a type within a rolling 10-minute session window double its cooldown, capped at 600 seconds. Persist a policy-change event. Completed prompts do not automatically reduce medical risk or update model labels.
- Prioritize data-quality abstention, then valid context evaluation; never infer a missing signal from an unrelated one.
- Record no_action and suppressed outcomes so the demo can explain why nothing happened.

Offer visual breathing guidance with user-controlled Start/Stop and a comfortable animation; avoid compulsory breath holding or therapeutic prescriptions. Posture output is an onscreen reminder. A virtual haptic icon displays a command only and says “Physical output not connected.” Do not auto-contact emergency services or prescribe treatment.

Do not implement a mysterious “Health Deviation Index” from arbitrary weighted numbers. Either omit it from the main UI and document it as unimplemented, or provide a clearly named experimental normalized signal-deviation score with a documented formula and validation. It must not be called a clinical risk index. Default: omit until a justified specification exists.

Recorded replay does not respond physiologically to interventions. A later change in a recording cannot be credited to the software. Keep synthetic response/no-response branches in a separate simulation analysis, with an untreated comparator and stated assumptions. User clicks prove interaction, not health improvement.

## 14. API surface

Prefix API routes with /api/v1. Generate OpenAPI docs. Paginate histories with limit/cursor, cap payloads and query sizes, and validate all IDs. Dates are filters, not approximated by “last 500 readings.”

### Each client service

| Method | Path | Behaviour |
| --- | --- | --- |
| GET | /health | client status, model and source availability; no raw data |
| GET | /sources | available scenarios/datasets with provenance |
| POST | /sessions | create source/session configuration |
| GET | /sessions | paginated session list |
| GET | /sessions/{id} | state, replay clock and summary |
| POST | /sessions/{id}/start | begin or resume through validated transition |
| POST | /sessions/{id}/pause | freeze replay clock |
| POST | /sessions/{id}/stop | finish without deleting history |
| POST | /observations | validated ingestion, idempotent by event_id |
| GET | /sessions/{id}/observations | source-labelled history |
| GET | /sessions/{id}/events | catch-up after sequence |
| GET | /sessions/{id}/predictions | actual saved predictions |
| GET | /sessions/{id}/decisions | actions, suppressed and abstained decisions |
| GET | /interventions | filtered intervention list |
| POST | /interventions/{id}/feedback | validated idempotent transition |
| GET | /explanations/{prediction_id} | actual explanation, cached per model/input |
| GET/PATCH | /settings | validated non-secret settings and policy versions |
| POST | /exports | local export job with source/real-data inclusion controls |
| WS | /sessions/{id}/stream | typed events and reconnect support |

### Coordinator

| Method | Path | Behaviour |
| --- | --- | --- |
| GET | /health | coordinator availability and version |
| GET | /clients | registered virtual client status and last contact |
| POST | /experiments | queue a baseline/federated/private experiment |
| GET | /experiments/{id} | real job state and measured progress |
| POST | /experiments/{id}/cancel | cooperative cancellation with accountant persistence |
| GET | /rounds/{id} | round status and participant summary |
| GET | /assignments/{client_id} | authenticated task polling |
| POST | /rounds/{id}/updates | authenticated, deduplicated safe model update |
| GET | /models/{id} | metadata and separately downloadable numerical weights |
| GET | /metrics | persisted public evaluation results |
| GET | /privacy | accountant summaries, limitations and lineage |
| GET | /claims | source-grounded implementation/evidence mapping |
| POST | /evidence/exports | aggregate/synthetic evidence bundle job |

Long-running jobs return HTTP 202 plus job ID; never block the request thread on training. Limit to one heavy experiment at a time by default. Report real progress from checkpoints, not a timer reaching 100%. Avoid CPU-heavy explanation work inside event-loop handlers.

## 15. Local security and dependable execution

No account registration is required for the default single-user loopback app. Generate strong per-service tokens and a local dashboard session at first boot; store secrets outside version control. Use exact origin allowlists, server-side authorization for control/data routes, and websocket origin/auth validation. Do not let an arbitrary website issue commands to localhost. Do not send long-lived tokens in query strings or write them to frontend source. A loopback control gateway with HttpOnly SameSite session cookies is an acceptable design; it routes to edge services, not through the federation server.

Accept only configured local service destinations; no user-controlled open proxy/SSRF. Cap ZIP/file sizes, prohibit path traversal, parameterize queries and escape export fields where appropriate. No arbitrary user model/pickle execution. Log correlation IDs, not secrets. Tokens, certificates, raw data and privacy random states are excluded from archives.

Session-level outbox and observation IDs provide retry/deduplication. Inputs too old or out of order cannot retroactively trigger a duplicate prompt. Keep an explicit reorder policy: default mark late observations for history only once the relevant window was processed. Server restart recovers session history and safely pauses replay; it does not silently replay all prior interventions.

Health indicators distinguish process reachability, model readiness, source availability, training status and secure transport. Missing coordinator does not stop local inference from a cached model. Never swap to frontend mock data during downtime.

## 16. Frontend design specification

Build a professional research dashboard that looks coherent on a projector and a laptop. Avoid decorative “AI” hero sections. Use light background #EAEDF0, white surfaces, dark navy text and restrained teal/blue accents. Amber for insufficient data and source warnings; red for failures, not sensational clinical danger. Bundle fonts/assets locally or use system fonts. No external CDN dependency in demo mode.

Desktop layout: left navigation about 230 px, compact top bar with selected client/session, source badge, replay speed, model version and connection state. Main area uses clear cards and charts with readable labels, units, legends and timestamps. Support 1366x768 and 1440x900 without clipped controls; usable narrow layout around 390 px. Keyboard operation, labelled forms, focus visibility, contrast, reduced motion and text alternatives to colour are required.

### Pages

1. **Overview:** source selector, client selector, start/pause/stop, model readiness, current available signals, model state, recent decisions. Missing heart rate says “Unavailable,” not 0. First visit offers a clearly synthetic guided demo.
2. **Live session:** EDA, skin-temperature and motion charts, optional valid context channels, window-quality timeline, source provenance, replay controls and event table. Charts receive actual backend events; bounded live window prevents browser memory growth.
3. **Interventions:** active prompt, accept/dismiss/complete, optional breathing animation, searchable history, suppression reasons, current cooldown and feedback adaptation log. Completion rate is labelled user interaction, not treatment success.
4. **AI insights:** tree/neural model switch for available domain-matched models, signed feature attributions, explanation method, real evaluation cards, confusion matrix, participant split and model card. Avoid comparing incomparable synthetic and research runs as one score.
5. **Federated & privacy lab:** three client cards, coordinator status, round table, actual training progress, model hashes, per-client budgets, public test metrics, private/non-private comparison and transport indicator. Actions start/cancel real jobs. Label same-laptop clients.
6. **Evidence:** claim matrix, scenario results, run manifests, source/licence status, tests actually run, export controls, disclosed limitations, research-demo description. Export builds a real artifact.
7. **Settings:** local source paths via supported controlled import flow, retention/configuration, theme and demonstration thresholds. Persist valid changes. Do not include dummy integrations or nonfunctional switches.

Every screen has meaningful loading, empty, error and disconnected states. Synthetic fixtures shown during design must be removed from runtime paths unless explicitly selected as a synthetic session. Do not count a page as complete because it renders.

## 17. CLI, bootstrap and launcher contract

Expose a `python -m nexora.cli` entrypoint; a short `nexora` command is optional after installation. Implement these commands with useful --help:

```bash
python scripts/bootstrap.py
python scripts/doctor.py
python -m nexora.cli data generate --profile demo --seed 42
python -m nexora.cli data import-wesad --path data/raw/wesad
python -m nexora.cli train baseline --dataset synthetic
python -m nexora.cli train neural --dataset synthetic
python -m nexora.cli experiment run --mode federated --dataset synthetic --rounds 5
python -m nexora.cli experiment run --mode private-federated --dataset synthetic --rounds 5
python scripts/prepare_demo.py
python scripts/start.py --profile demo
python scripts/verify.py
python scripts/build_evidence.py
python scripts/stop.py
```

Commands run in the project environment. Bootstrap must create/use the venv and print the exact Windows/Linux invocation needed; PowerShell and shell wrappers should avoid requiring users to know activation syntax. Provide Windows `py -3.11 scripts/bootstrap.py` guidance and a fallback to the compatible installed Python command.

Bootstrap checks Python, Node/npm, disk space and available memory; installs only project dependencies; runs a small import/runtime compatibility smoke check; generates local secrets if absent; and builds frontend assets. It is idempotent and preserves existing evidence. If no internet/package cache exists, identify the actual missing downloads rather than writing fake modules.

prepare_demo performs one-time synthetic generation, baseline and neural training, genuine non-private/private federation, evaluation and evidence preparation. It must detect already matching completed artifacts by input/config hashes. Never restart expensive work solely because a file's modification time changed. Fresh random DP training is a new accounted execution, not a reproducible cache miss to hide.

start.py starts owned services with subprocess argument arrays, waits for readiness, opens/prints the actual dashboard URL, captures per-service logs and writes a process manifest. Handle spaces in Windows paths. No Bash-only assumptions, embedded shell quoting or global execution-policy changes. Ctrl+C and stop.py terminate owned children gracefully. Detect stale PIDs without terminating unrelated processes.

The normal exam-day command must use cached model artifacts and bundled frontend assets. It must not install packages, download data or run a full training job on startup. A restart recovers last completed records. Provide a clean new synthetic session without wiping experiment history.

## 18. Testing and measurable acceptance

Use meaningful tests of behaviours and failure modes. Do not mirror implementation line-for-line or inflate a test count as quality evidence. Fix actual failures, rerun affected tests, then run the final required suite once the build is stable.

### Mandatory backend/model checks

- Invalid units, NaN/Inf, malformed timestamps and oversized payloads fail cleanly.
- Missing values remain null and primary-channel gaps cause abstention.
- Replaying an event twice produces one durable observation and at most one action.
- Participant/session split isolation, non-overlapping training windows and excluded labels are verified.
- Features are identical for offline and online processing of an identical window.
- Model save/load preserves predictions within numerical tolerance; wrong schema/hash is rejected.
- Baseline/MLP evaluation reads held-out records and writes actual counts and metrics.
- Sustained posture scenario triggers; brief spike does not; cooldown suppresses repeats.
- Feedback transitions are enforced; two dismissals change cooldown within caps.
- Three client processes perform real local training; coordinator gets parameter updates only.
- FedAvg matches an independent tiny tensor calculation; wrong round/shape/duplicate client updates fail.
- Private training exercises gradient clipping/noise/accounting; resume composes rather than resets budget; budget guard is enforced.
- Explanations have correct feature count, class/output reference and finite signed values; IG completeness is checked within documented tolerance.
- Coordinator outage preserves local inference; reconnect does not duplicate actions.
- Local TLS profile rejects an untrusted certificate instead of silently disabling verification.
- Export excludes secrets and real raw data by default and includes checksums for included files.

### Mandatory browser flows

1. Start synthetic normal session and see real live updates.
2. Pause and resume; displayed replay speed and event timestamps remain coherent.
3. Run sustained posture scenario, interact with its prompt, and inspect persisted feedback.
4. Inspect actual prediction explanation and a source-labelled evaluation report.
5. Launch a small federated run and see real round completion/model version changes.
6. Inspect private run and accountant values; no hardcoded privacy/accuracy cards.
7. Disconnect coordinator, observe honest status while edge continues, then reconnect.
8. Export and open the evidence bundle.
9. Refresh the browser; session/history recover.
10. Check keyboard navigation and screenshot desktop/narrow layouts for clipping.

Collect browser console/network failures; no unexplained failed required requests. Use screenshots/video only of the actual app. If the environment cannot run a browser, record that exact verification gap and produce a runnable Playwright command; do not assert browser QA passed.

### Performance reporting

Measure startup time with prepared artifacts, inference median/p95 and decision-to-render latency. Include machine details and replay workload. Signal-window accumulation is separate latency. Set an initial usability target of a local decision-to-render p95 under 2 seconds on the test machine, but report actual outcomes and investigate failures instead of inventing success. This is not the filed sub-100ms claim.

Do not require high synthetic accuracy to pass engineering tests. Report weak model utility honestly. Software acceptance and research validity are different gates.

## 19. Execution sequence — complete in this order

### Phase 1: Inspect and scaffold
Inspect the blank folder/runtime and any existing instructions. Create structure, status file, dependency locks, source contracts and gitignore. Do not clone an unrelated complete project. Gate: Python imports, frontend build and test runner execute.

### Phase 2: First complete flow
Implement simulator, SQLite stores, session controls, event stream, deterministic posture policy and first dashboard page. Gate: a scenario causes a traceable backend decision, browser prompt and stored feedback.

### Phase 3: Real model path
Generate the synthetic participant dataset; implement feature extraction, split checks, fixed normalization, baseline and MLP training/evaluation/registry. Connect actual inference and attributions. Gate: versioned models and measured held-out results appear in the UI.

### Phase 4: Remaining functional interface
Implement all listed pages, persistence, filtering/export, source labels and error states. Gate: user flows work through the API; no fake cards or stub buttons.

### Phase 5: Distributed roles
Run three separate clients, implement genuine REST FedAvg, model distribution and outage/reconnect behaviour. Gate: parameter math and integration tests pass and a recorded round succeeds.

### Phase 6: Private training
Add Opacus and durable ledger/accounting; run a private experiment from an appropriate initialization and compare actual held-out results. Gate: meaningful DP tests pass and UI accurately displays scope/budget/randomness limitations.

### Phase 7: Research-data support
Implement and test WESAD converter/adapter. Attempt permitted acquisition once with bounded retries; if available run participant-separated evaluation. Otherwise preserve a fully functional importer with exact placement instructions and clear unavailable status. Gate: adapter tests pass; real-data run status is truthful.

### Phase 8: Security and packaging
Finish local tokens, origin checks, safe file/model handling, TLS profile, start/stop/doctor wrappers and cached offline demo. Gate: no public calls needed for demo and restart works.

### Phase 9: Evidence and browser verification
Run required suite, inspect real browser screens, fix failures and export evidence. Generate documentation from actual implementation and measured runs. Gate: artifacts open and agree with saved metrics.

### Phase 10: Final clean-start rehearsal
Stop owned processes, launch from documented command, run normal/posture/missing-data/outage scenarios and export once. Preserve results. Finish with the final handoff described below, listing any genuine verification gap.

Do not insert approval checkpoints between these phases. The user's authorization covers building and reversible local verification. Actual external permission/access restrictions must still be respected. If an optional service/dataset is unavailable, continue independent work. If a mandatory feature fails, debug it rather than quietly removing it from scope.

## 20. Claim and evidence package

Create a machine-readable claim map and a human-readable table. Use statuses: `implemented_software`, `simulated_input_or_output`, `partially_demonstrated`, `not_implemented`, `not_verified`. Never use “patent claim validated” or “grant guaranteed.” Include links/paths to actual evidence files; an empty test placeholder is not evidence.

| Claim | Required mapping |
| --- | --- |
| 1(a) | Physical sensors absent; recorded/synthetic inputs only |
| 1(b) | Local processing implemented; embedded execution/equivalence not established |
| 1(c) | Coordinator/model role implemented locally; actual cloud hosting absent |
| 1(d) | Browser interventions implemented; physical actuation absent |
| 2 | Supported signals and provenance; missing sensor varieties explicit |
| 3 | Actual narrow classification/anomaly capability; no presymptomatic disease forecasting assertion |
| 4 | Implemented browser actions and adaptation; haptics simulated |
| 5 | Actual SHAP/IG outputs; LIME status and clinical-validation gap explicit |
| 6 | Genuine three-client local federation; same-host limitation |
| 7 | Measured private training/accounting; example-level scope and implementation limitations |
| 8 | Actual local transport/reconnect/TLS profile; physical IoT links absent |
| 9 | Adapter contracts tested; no actual hospital/wearable integration |
| 10 | End-to-end software workflow; inherited sensor/physical limitations |

Evidence ZIP generated by the implementation must include README, architecture diagrams, claim map, model/data cards, source/licence manifest, configurations without secrets, model/evaluation hashes, test report, measured experiments, synthetic scenario traces, screenshots and demonstration instructions. Include code revision if git exists and file hashes regardless. Use checksums in an export manifest. Exclude dependency folders, venv, real raw data, tokens, certificates/private keys and DP RNG states.

Create `artifacts/reports/NEXORA_TECHNICAL_REPORT.md` and a readable standalone HTML report with embedded/bundled visuals and no remote assets. A PDF export via browser printing is desirable if available; do not block the core on a missing PDF renderer. Generate `artifacts/demo/DEMO_SCRIPT.md`, a short real demo recording if browser recording is supported, and the original editable Mermaid architecture source. Never create a fake demonstration video.

EXAM_QA.md must give honest answers to: where inputs come from; why no hardware; what is actually trained; how aggregation works; what the privacy unit is; what happens offline; what explanations mean; what remains untested; why replay cannot establish efficacy; and what each measured metric represents. Do not script claims of novelty, clinical benefit or historical results that have not been established.

PATENT_AGENT_REVIEW_NOTES.md records the source narrative/results discrepancy, cover applicant discrepancy and missing examination documents. Do not send it automatically. Preserve dated technical records; no legal filing modifications.

## 21. Configuration and secrets

No external API keys are required. `.env.example` documents only supported settings, including local bind host, port profile, generated service-token file location, source directories, runtime directory, worker limits, replay defaults and logging level. Do not put real secrets in the example.

Do not add OpenAI/FastRouter/Fastcoder integration by default. Existing coding-assistant access can help development without changing the app. If the user later specifically requests an optional language-model layer, keep it outside inference and privacy-sensitive raw data flows, disabled by default and documented separately. Do not ask for unused keys.

A research dataset needing sign-in/terms or a missing system runtime can require user action. Do not claim a Markdown file can bypass those constraints. The final handoff must distinguish optional dataset inputs from actual blockers.

## 22. Final handoff requirements

At completion provide:

1. Exact project path and working launch command for the detected OS.
2. Actual dashboard URL and stop command.
3. What was implemented and what was executed, with evidence paths.
4. Synthetic versus WESAD validation status.
5. Tests run and pass/fail/skip status with reasons.
6. Measured model metrics and experiment scope, not target numbers.
7. Exact evidence/report/demo paths.
8. Remaining limitations and blockers, including hardware/cloud/clinical gaps.
9. A three-step exam-day launch checklist and how to recover from a restart.
10. BUILD_STATUS.md with an accurate final state or explicit next action.

Do not tell the user to finish major implementation themselves while claiming the build is complete. Do not conceal an unavailable required module behind a simulated screen. Do not claim the application is production medical software or that a demonstration guarantees grant.

## 23. Official technical references

Use the installed compatible versions' documentation when implementing APIs. Re-check signatures rather than copying stale examples.

- FastAPI: https://fastapi.tiangolo.com/
- Vite runtime/setup: https://vite.dev/guide/
- PyTorch: https://pytorch.org/docs/stable/
- scikit-learn: https://scikit-learn.org/stable/
- Opacus: https://opacus.ai/ and https://opacus.ai/api/privacy_engine.html
- Captum Integrated Gradients: https://captum.ai/api/integrated_gradients.html
- SHAP: https://shap.readthedocs.io/
- WESAD metadata and original-source link: https://archive.ics.uci.edu/dataset/465/wesad+wearable+stress+and+affect+detection
- Playwright: https://playwright.dev/docs/intro

These are technical sources, not a completed prior-art search. Public metadata was reviewed when this specification was prepared; exact installed versions, data access, licences, system capacity and measured results must be established by the implementing agent.

## Final instruction

Begin with environment inspection and Phase 1, then execute the complete sequence. Keep the real system and evidence consistent. Continue through implementation, tests, fixes, packaging and the final rehearsal. Use this document's defaults without routine clarification, and report any unavoidable access/runtime limits truthfully.
