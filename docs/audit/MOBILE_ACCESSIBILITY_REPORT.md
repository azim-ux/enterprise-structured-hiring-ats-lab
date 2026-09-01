# Mobile and Accessibility Defect Report

**Surfaces tested:** live dashboard, live slide deck, and live phone case-study HTML

**Viewports:** 1440×900 and 375×812

**Method:** browser interaction, accessibility-tree inspection, DOM measurements, console inspection, and screenshots

**Boundary:** baseline review only; this is not a WCAG conformance audit

## Findings

### MOB-001 — Dashboard creates document-level horizontal scrolling

- **Severity:** High
- **Evidence:** At a 375 px viewport, `document.documentElement.scrollWidth` was 707 px. At 1440 px, scroll width matched the 1440 px viewport.
- **Observed contributors:** the 1,020 px pipeline table and closed scorecard-layer geometry overflow their containers.
- **User impact:** a phone user can accidentally pan the entire page, lose the content edge, and have difficulty understanding the candidate table.
- **Reproduction:** open the live dashboard at 375×812 and compare `document.documentElement.scrollWidth` with `window.innerWidth`.

### MOB-002 — Fixed slide controls obscure phone content

- **Severity:** Medium
- **Evidence:** After activating “Next slide” at phone width, the previous/next controls overlay the lower “Safe batch automation” card and its text.
- **User impact:** content is partially hidden and the reading order is visually interrupted.
- **Reproduction:** open the live slide deck at 375×812, activate “Next slide,” and inspect the lower control card.

### A11Y-001 — No repeatable accessibility gate exists

- **Severity:** High process gap
- **Evidence:** No accessibility test dependency, browser test, CI workflow, or stored conformance result exists.
- **User impact:** semantic, keyboard, focus, contrast, zoom, and responsive regressions can ship unnoticed.

### A11Y-002 — Complex chart meaning depends on a visual canvas

- **Severity:** Medium
- **Evidence:** Canvases have roles, names, and short fallback text, but the full plotted values and relationships are not available as adjacent data tables.
- **User impact:** non-visual users receive a summary rather than equivalent access to the detailed plotted evidence.

### PERF-001 — Duplicate embedded datasets increase phone transfer and parse cost

- **Severity:** Medium
- **Evidence:** Each dashboard is 3,480,689 bytes and embeds 3,448,439 characters of JSON. `index.html` and `dashboard.html` are exact duplicates.
- **User impact:** avoidable bandwidth, parsing, memory, and maintenance cost, especially on lower-end phones or constrained networks.

## Positive observations

- The dashboard declares `lang="en"`, one `main`, one `nav`, one `header`, and one `footer`.
- The sampled page has a single H1 followed by logical H2/H3 sections.
- Search, filters, pagination, scorecard buttons, and close controls expose accessible names.
- The scorecard uses `role="dialog"`, `aria-modal="true"`, and a labelled title; the tested open/close path worked.
- No console errors occurred in the tested dashboard and slide flows.
- The phone case-study page matched its 375 px viewport exactly and remained legible in the sampled view.
- Dashboard search returned the expected single synthetic candidate, and the phone scorecard was readable.

## Evidence handling

Five screenshots were captured and visually inspected during the audit. They remain local QA artifacts rather than new public repository assets because this Stage 0 pull request makes no visible implementation change. The numerical measurements and reproduction paths above are sufficient to repeat the findings, and any Stage 1 visual fix must include before/after evidence in its own reviewed pull request.

## Untested in this baseline

Screen-reader output, 200%/400% zoom, forced colors, color-contrast ratios, reduced motion, switch input, voice input, multiple mobile browsers, PDF reading order, and a complete keyboard-only journey were not tested. No compliance claim should be inferred.
