# Claim-versus-Evidence Matrix

| Claim | Evidence at baseline | Assessment | Required wording/action |
|---|---|---|---|
| 4,000 candidates, 5 requisitions, 2,000 interview rows | CSV row counts and automated test | Verified synthetic scale | Keep “synthetic” adjacent to the scale claim |
| 120 modeled hires and 3.0% conversion | CSV stage counts and test | Verified simulation result | Do not present as an employer outcome |
| 28.5-day average time to fill | Five requisition values and test | Verified synthetic KPI | Use “modeled” or “simulated” |
| 91.8% 48-hour feedback SLA | 1,836 of 2,000 rows and test | Verified synthetic KPI | Do not imply an operational service commitment |
| 0.87 adverse-impact ratio | Cohort progression counts and test | Verified descriptive result | Keep non-causal/legal caveat; not proof of fairness |
| 40/40/20 composite | 500 populated composites independently recomputed with zero differences | Verified arithmetic | Not evidence of predictive validity or job relatedness |
| Demographics are inaccessible to decision-makers | RBAC documentation; UI does not display cohort fields | Design intent only | Public browser still receives every synthetic cohort value; avoid enforcement language |
| Role-based access, score locking, immutable audit, purge, idempotent workers | RACI, RBAC, methodology, and UAT documents | Specified, not executable | Use “proposed,” “modeled,” or “control design” |
| “Audit-ready” / “auditable operating model” | Traceable documentation and deterministic synthetic data | Partially supported | Prefer “audit-oriented reference design”; no immutable runtime audit trail exists |
| “Enterprise edition/project/system” | High-volume dataset and governance documentation | Positioning risk | Replace with “enterprise-oriented reference implementation” as work progresses; never “enterprise-ready” |
| Independently deployable | Static files run locally and on GitHub Pages | Verified for demonstration | Clarify that deployment is static demonstration hosting |
| Acceptance suite covers schemas, references, formulas, pagination, embedded parity, and slide contract | Current four tests | Unsupported | Correct README now or add the missing tests in Stage 1 |
| Tailwind CSS and Chart.js use CDNs | Current source and methodology statement | False/stale | Chart.js is vendored; no Tailwind runtime is present |
| Privacy by design | Synthetic-only publish boundary, privacy docs, exact-index scan | Partially supported for a public demo | Not evidence of production privacy engineering or legal compliance |
| DPDP/GDPR controls | Legal references and proposed workflows | Educational design only | Require jurisdiction-specific professional review before real use |
| OpenCATS architecture | Workflow is described as OpenCATS-inspired/platform-neutral | Conceptual mapping | No OpenCATS instance, plugin, migration, or integration is included |

## Approved project description

> An open-source, enterprise-oriented structured-hiring reference implementation in development. The current release is a static portfolio simulation using fully synthetic data to demonstrate evidence models, governance specifications, reconciled analytics, and decision-support UX. It is not a production ATS or validated employment-selection instrument.
