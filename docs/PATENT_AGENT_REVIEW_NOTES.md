# Patent Agent Review Notes

**File purpose:** Internal technical discrepancy notes for agent review. Not for automatic distribution.  
**Date recorded:** 2026-09-18 (initial inspection). Updated 2026-09-22.  
**Classification:** Internal record only; does not modify any legal filing.

---

## 1. Source narrative versus prototype status discrepancy

The filed application (IN202521117940 A1, filed 27 November 2025, published 16 January 2026) contains narrative text reporting completed development with specific performance percentages including figures such as "92% accuracy", "87% precision" and "94% explainability score."

The applicant's own statement to the building agent was: **"no prototype has been built."**

These two facts are inconsistent. Possible explanations (none verified by this agent):
- The narrative was aspirational or forward-looking rather than reporting measured results.
- Results were obtained from a prior experimental version that was not provided to this build.
- Numbers may have been drawn from related prior work or literature and attributed to this system.

This prototype measured (on synthetic data only): random forest balanced accuracy 1.000, MLP balanced accuracy 0.500. These numbers do not match the filed narrative figures and were produced on an artificial seeded generator, not real physiological data.

**Action:** Do not reuse or reproduce the filed narrative percentages as evidence for this prototype. All performance claims in BUILD_STATUS.md, ACCEPTANCE_REPORT.md and NEXORA_TECHNICAL_REPORT.md are based on actual measured prototype runs only, clearly labelled as Synthetic.

---

## 2. Applicant list discrepancy on publication cover

The publication cover (IN202521117940 A1) appears to contain a duplicated entry in the applicant field (the name "Abhishek" appears twice in the applicant listing) and "Sanskar" appears to be absent or in a different position from what might be expected based on related context.

**This agent does not have access to the official patent office records, the complete prosecution history, or authority to determine which applicant entry is authoritative.**

**Action:** Preserved as a private note. This discrepancy has not been surfaced as a public warning in the application UI, README, or any user-facing document. No legal filing has been modified. If correction is needed, this must be handled through the official patent office procedure by the applicant or their legal representative.

---

## 3. Missing examination documents

No prosecution history, examiner reports, office actions, claim amendments or search reports were provided to this build. The current patent status (granted, pending, lapsed, etc.) has not been verified against any official patent office database as of this writing.

**Action:** Patent legal status determination is outside the scope of this software prototype build.

---

## 4. Physical claim elements not demonstrated

Claim 1 of IN202521117940 A1 expressly references physical sensors (multi-modal biometric input layer). This software prototype does not demonstrate, substitute for, or establish equivalence to those physical elements. The prototype uses synthetic data and labelled replay inputs only.

This limitation is disclosed in:
- `KNOWN_LIMITATIONS.md`
- `ACCEPTANCE_REPORT.md`
- `artifacts/reports/NEXORA_TECHNICAL_REPORT.md`
- `configs/claim_map.json`

---

*This file is a technical record by the implementing agent. It does not constitute legal advice, a freedom-to-operate opinion, a claim construction, or a grant conclusion.*
