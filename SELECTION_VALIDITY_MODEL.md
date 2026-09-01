# Selection Validity Model

## Model purpose

The model turns three job-related assessments into a consistent ranking while preserving the underlying evidence. It does not predict a guaranteed outcome and does not replace professional review of job relevance, accessibility, reliability, or fairness.

## External validity priors

| Method | Corrected validity used in this lab | Use |
|---|---:|---|
| Work sample test | .43 | Highest-fidelity two-hour simulation |
| Structured behavioral interview | .42 | Four-competency BARS assessment |
| Job-knowledge test | .40 | Blueprint-controlled technical knowledge |
| Unstructured interview | .12 | High-bias anti-pattern; zero decision weight |

These supplied values are aligned to the revised-selection-literature framing in Sackett et al. (2022). They are not coefficients estimated from the synthetic APD cohort.

## Composite

All scored components use a common 1.00–5.00 scale after documented standardization.

```text
Composite Score =
    (0.40 × Work Sample Score)
  + (0.40 × Structured Interview Score)
  + (0.20 × Job Knowledge Score)
```

Weights reflect similar external validity for work samples and structured interviews, plus a smaller knowledge contribution to reduce construct overconcentration. A candidate must also pass every required criterion; a high average cannot compensate for a safety, ethics, or critical-knowledge gate.

## Bias-variance diagnostic

```text
Bias Variance Gap = Subjective Impression Score − Composite Score
```

The impression score is collected after evidence ratings and never contributes to the composite. A positive gap of `+0.50` or larger prompts a calibration question: what observable evidence supports the impression, and is it already represented in a governed component?

### Control case: CAND-2026-0013

```text
Work sample                  4.00 × 0.40 = 1.60
Structured interview         3.80 × 0.40 = 1.52
Job knowledge                4.00 × 0.20 = 0.80
Composite                                      3.92
Subjective impression                          4.60
Bias-variance gap                    4.60 − 3.92 = +0.68
```

The candidate was not selected. The gap does not prove assessor bias; it makes an otherwise invisible inconsistency reviewable. The panel found no job-related evidence that justified overriding the composite.

## Threshold and tie protocol

1. Required-criterion gates are evaluated before ranking.
2. The requisition-specific finalist threshold is approved before assessments open.
3. Candidates are ordered by unrounded composite; the dashboard displays two decimals.
4. A tie within 0.05 is resolved by the higher work-sample score, then by a documented additional job-related exercise applied equally to tied candidates.
5. Subjective impression, referral source, demographic cohort, and compensation history cannot break a tie.

## Taylor–Russell utility frame

Taylor–Russell analysis asks how expected employee success changes with three inputs:

- **Base rate (BR):** proportion expected to succeed under the existing method.
- **Selection ratio (SR):** hires divided by qualified applicants.
- **Validity (r):** correlation between the selection composite and a defensible performance criterion.

For a locally validated predictor, the expected success ratio is obtained from a Taylor–Russell table or the equivalent bivariate-normal integration using `(BR, SR, r)`. Expected successful hires are then:

```text
Expected successful hires = hires × expected success ratio
Incremental successful hires =
    hires × (new expected success ratio − baseline expected success ratio)
```

APD must not insert `.42` or `.43` as the validity of the weighted composite. Composite validity depends on component intercorrelations, criterion quality, restriction of range, and local conditions. The lab therefore offers a sensitivity grid rather than a claimed return:

| Scenario | Base rate | Selection ratio | Locally tested validity | Interpretation |
|---|---:|---:|---:|---|
| Conservative | .40 | .20 | .20 | Useful only if benefit survives weak validity |
| Planning | .50 | .15 | .30 | Illustrative operating case |
| Strong evidence | .60 | .10 | .40 | Requires adequate local criterion study |

### High-volume planning application

The enterprise campaign makes **120 hires from 4,000 applicants**, an overall selection ratio of `.03`. For assessed finalists, the ratio is `120/500 = .24`. Taylor–Russell modeling must state which eligible pool defines the ratio; using the full applicant pool can overstate selectivity when 3,014 records failed a minimum-requirement knockout. APD would evaluate each requisition family separately and then volume-weight results, because a G1 trainee base rate and criterion are not interchangeable with G4 engineering.

For each family, analysts enter a defensible baseline success rate, selection ratio, and locally cross-validated composite validity. A Taylor–Russell table or equivalent bivariate-normal calculation yields the expected success proportion. Results are reported as a range of expected successful hires, not as guaranteed headcount value.

## Brogden–Cronbach–Gleser monetary utility extension

After governance approval, a **Brogden–Cronbach–Gleser (BCG)** estimate can supplement Taylor–Russell:

```text
ΔU = N × T × SDy × rxy × Zselected − N × Cost_per_applicant
```

`N` is hires, `T` is average tenure in years, `SDy` is the monetary standard deviation of performance, `rxy` is locally supported validity, and `Zselected` is mean standardized predictor score of selected candidates. Every input must have an evidence owner and low/base/high sensitivity range. The estimate is a decision aid, never an accounting promise.

At 120 hires, small changes in assumed validity or performance-value spread can produce large monetary estimates. The governance view therefore discloses every input, separates the five job families, includes assessment and vacancy costs, discounts benefits over time, and shows a zero-benefit case. Synthetic APD records do not supply a credible `SDy`, tenure, or local `rxy`, so this lab does not claim a monetary return.

## False-positive reduction

An intuitive process can promote a compelling storyteller whose evidence is weaker than the panel impression. Score locking and the +0.68 control case demonstrate the mechanism by which BARS reduces that risk. False-negative risk remains: structure can exclude unconventional but capable candidates if the job analysis, exercises, or accessibility design are poor. Post-hire criterion studies and candidate-reaction reviews must examine both error types.

## Monitoring

Quarterly controls include inter-rater reliability, assessor severity, missing data, score-change history, pass rates, impact ratios, criterion drift, accommodation outcomes, and decision exceptions. Any weight change creates a new model version; historical scores remain reproducible under their original version.
