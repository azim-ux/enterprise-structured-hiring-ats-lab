# Current Architecture Map

## Executable topology

```mermaid
flowchart LR
    U[Public evaluator] --> P[GitHub Pages]
    P --> I[index.html]
    P --> D[dashboard.html]
    P --> S[slides.html]
    P --> M[mobile-case-study.html]
    P --> PDF[Two static PDFs]

    I --> C[Vendored Chart.js 4.4.7]
    D --> C
    I --> EJ[Embedded JSON snapshots]
    D --> EJ
    EJ -. generated from .-> CSV[Three synthetic CSV files]

    DOC[Markdown governance specifications] -. describes intended controls .-> FUTURE[Future executable reference implementation]
    TEST[Four Python integrity tests] --> CSV
    TEST --> I
    TEST --> D
    TEST --> S
    TEST --> M
```

`index.html` and `dashboard.html` are identical static applications. They do not fetch the CSV files at runtime; each contains a separate embedded copy of all three datasets.

## Browser data flow

```mermaid
sequenceDiagram
    participant E as Evaluator browser
    participant G as GitHub Pages
    participant J as Embedded JSON
    participant V as Vendored Chart.js

    E->>G: GET index.html
    G-->>E: HTML, CSS, JavaScript, and 3.45M characters of JSON
    E->>G: GET vendor/chart.umd.min.js
    G-->>E: Chart.js 4.4.7
    E->>J: Parse requisitions, candidates, interviews
    E->>E: Compute filters, pagination, scorecards, and charts
    Note over E,J: No API, authentication, server-side pagination, persistence, or audit event is present
```

## Trust boundaries

| Boundary | Current reality | Consequence |
|---|---|---|
| Public Internet → GitHub Pages | Every tracked web/data asset is public | The data must remain synthetic and publishable |
| GitHub Pages → browser | Static files only; GitHub supplies transport | The application cannot enforce user identity or role permissions |
| Browser UI → embedded data | The browser receives the entire dataset | UI filtering is not data-access control |
| Governance documents → executable behavior | Documentation is not connected to runtime policy | RBAC, audit, retention, erasure, and workflow claims remain design intent |
| Source CSV → embedded JSON | Two manually duplicated snapshots | Drift is possible without generation/parity automation |

## Current security model

The current model is publish-only: minimize the repository to synthetic data, avoid secrets and local paths, pin the one client dependency, and keep the application non-transactional. There are no privileged runtime operations to protect, but there is also no basis for claiming authenticated or role-scoped behavior.

## Target direction (not implemented)

A later vertical slice can introduce a relational schema, versioned workflow service, role-scoped API, append-only audit events, and a thin UI consuming field-projected endpoints. That target must preserve the present governed KPIs and synthetic-data boundary without pretending to be a production ATS.
