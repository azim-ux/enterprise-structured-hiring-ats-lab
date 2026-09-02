# Claim-Evidence Matrix

This matrix governs the two public case-study sources and their PDFs. It distinguishes code and evidence that exist now from synthetic outcomes, design specifications, and controls that a production implementation would still require.

| Topic | Earlier implication | Evidence judgment | Governed wording now | Remaining production evidence |
|---|---|---|---|---|
| System status | “Privacy-first enterprise hiring system” | Unsupported: the repository is a static portfolio simulation. | “Synthetic portfolio simulation and enterprise-oriented reference implementation under development.” | Deployed architecture, service ownership, security review, operational acceptance, and monitored reliability. |
| Applicant-data suitability | Enterprise wording could imply real-data use. | Unsupported and unsafe for this static browser delivery. | “Demonstration only,” “not suitable for real applicant data,” and independent review required. | Approved data protection design, threat model, environment controls, DPIA or equivalent review, and operating procedures. |
| Automation | “Blind automated knockout” sounded operational. | The repository documents rules; it does not run a production decision service. | “Design specifies job-related rules”; automation guardrails are documented production requirements. | Validated job-related rules, appeal and accommodation paths, kill switch, replay safety, and monitored service behavior. |
| RBAC | Roles “receive separated permissions.” | No runtime authentication or authorization exists. | “Proposed production RBAC”; “no runtime enforcement exists.” | Identity provider, least-privilege roles, authorization tests, access review, and segregation-of-duties evidence. |
| Encryption and audit logging | Privacy language could imply implemented security controls. | Neither runtime encryption control nor immutable operational log exists here. | Listed as production additions; page 4 states no runtime RBAC, encryption, or audit log. | Key management, encryption configuration, tamper-evident logs, retention, monitoring, and incident procedures. |
| Retention and erasure | “Transfer + purge” and queued 180-day purge sounded executed. | The 180-day period is a design choice only. | Retention and erasure are documented production requirements requiring review. | Jurisdiction-specific schedule, deletion jobs, exceptions, holds, verification, and audited evidence. |
| Backups, recovery, and incidents | Enterprise framing could imply operational resilience. | No backend or production environment exists. | Explicitly listed under “What production teams must add.” | Backup tests, recovery objectives, restoration evidence, incident plan, exercises, and service ownership. |
| Integrations | ATS architecture language could imply live OpenCATS or HRIS connectivity. | No live integration exists. | “OpenCATS-inspired design model · no live integration.” | Authenticated APIs, contracts, error handling, monitoring, reconciliation, and vendor/security review. |
| Legal compliance | Four-fifths and privacy language could be read as compliance claims. | Metrics and design references do not establish legal compliance. | Four-fifths is a screening indicator, not proof of compliance; legal review is required. | Applicable-jurisdiction analysis, counsel review, notices, records, accommodations, and regulatory evidence. |
| Fairness and bias | A 0.87 ratio or demographic separation could imply validated fairness. | The ratio is modeled from engineered synthetic cohorts and cannot prove absence of bias. | “Modeled fairness monitoring”; “not proof of compliance or absence of bias.” | Job-level subgroup analysis, data-quality review, adverse-impact investigation, validity evidence, and ongoing monitoring. |
| Predictive validity | Research-backed design could imply local validation. | No local criterion study or real outcomes exist. | Research is an evidence foundation, not a claim of local predictive validity. | Job analysis, reliability, criterion data, cross-validation, uncertainty estimates, and professional review. |
| Accessibility | Responsive or tagged output could imply conformance. | No assistive-technology or formal conformance audit was performed. | The model explicitly does not claim accessibility conformance. | Keyboard, screen-reader, zoom/reflow, contrast, cognitive, accommodation, and WCAG evaluation evidence. |
| Business outcomes | Conversion, time-to-fill, SLA, and impact ratio could appear operational. | All values are deterministic modeled results from synthetic data. | Every result is labelled modeled or synthetic and keeps its denominator visible. | Production telemetry, measurement definitions, baselines, causality analysis, and audited reporting. |

## Legitimate implemented evidence

- Three deterministic synthetic CSV datasets and value-level parity with both embedded dashboard payloads.
- Executable schema, key, progression, calculation, SLA, KPI, halo-control, slide, and pagination contracts.
- Reproducible 40/40/20 calculation checks across all 500 assessed synthetic candidates.
- Static dashboard and case-study views, local self-hosted Chart.js, governed hashes, privacy scans, and history/provenance controls.
- A contextual claims regression gate and deterministic source-to-PDF build.

These controls support reviewability of the portfolio artifact. They do not convert it into a production ATS, compliance product, validated selection instrument, or approved real-applicant environment.
