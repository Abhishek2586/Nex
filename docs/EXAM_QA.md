# Examination Q&A

**Where do inputs come from?** The executed demo uses a seeded, generated Synthetic dataset and Synthetic live replay. Manual feedback comes from browser actions. WESAD is a supported Recorded dataset adapter, but no WESAD files were supplied or evaluated.

**Why is there no hardware?** This build is software-in-the-loop and no physical device was available. It demonstrates interfaces and processing behavior, not physical sensors or actuation.

**What is trained?** A random forest baseline and an MLP classify a narrow synthetic baseline-versus-stress task using 12 window features. The tree scored 1.0 balanced accuracy and macro-F1 on 120 artificial held-out windows; the MLP scored 0.5 and 0.375. These are generator-specific results.

**How does aggregation work?** Three separate local processes train from one model state on 100 windows each. The coordinator validates updates and computes sample-count-weighted FedAvg. It receives parameters and metadata, not raw windows.

**What is the privacy unit?** One non-overlapping 30-second Synthetic window. Opacus RDP accounting reached epsilon 5.407788 at delta 1e-5 after 12 steps per client. This is example-level, uses experimental non-cryptographic randomness and is not a patient-level guarantee.

**What happens offline?** The cached dashboard, edge API, model and coordinator run on loopback with no public network dependency. Coordinator loss does not stop cached edge inference.

**What do explanations mean?** SHAP or Integrated Gradients assigns signed contributions to the 12 features for a particular model output. They describe the model calculation and are neither causal nor clinical explanations.

**What remains untested?** Real WESAD performance, physical hardware, embedded equivalence, multi-host federation, secure aggregation, public cloud deployment, clinical safety/efficacy, patient-level privacy, formal cross-browser automation and formal render-latency p95.

**Why can replay not establish efficacy?** Replay verifies software behavior against known generated inputs. It provides no prospective users, clinical outcomes, device measurements or controlled comparison.

**What do the metrics represent?** Balanced accuracy averages recall across the two synthetic classes; macro-F1 averages class F1 scores; epsilon/delta bound the configured example-level DP mechanism; completeness delta checks attribution arithmetic. None measures diagnosis, treatment benefit or real-world safety.
