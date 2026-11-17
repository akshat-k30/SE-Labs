# SE Lab 1 — Requirements Engineering & UML Use-Case Modelling

**SRN: PES2UG24CS046**
**Problem Statement #42 — Developer Tools & IT Operations**
**System: Internal Microservice Catalog & Health Portal**

PES University, Dept. of CSE — Software Engineering Lab

> An enterprise developer portal that maps microservice dependencies, aggregates API
> documentation, and runs automated periodic health-check pingers with downtime alerts.
> **Target stakeholders / actors:** DevOps Engineer, System Architect.

---

## ➡️ Submission file

### [`PES2UG24CS046.pdf`](PES2UG24CS046.pdf) — this single PDF is the deliverable to submit.

Four A3-landscape pages, in the order set by the lab handout:

| Page | Content |
|---|---|
| **1** | Cover — SRN, problem context, contents, the 5 actors, the 10 use cases, and requirement → use-case traceability. |
| **2** | **Deliverable 1 — Requirements Table.** Exactly 5 FRs (FR-001…FR-005) and 2 NFRs (NFR-001, NFR-002), each with Req ID, Type, Description, Priority, measurable Acceptance Criteria, Rationale and peer-critique Comments. Ends with the «include»/«extend» justifications. |
| **3** | **Deliverable 2 — UML Use-Case Diagram.** System boundary, 5 actors, 10 use cases, associations, 2 «include» + 2 «extend» relationships, and a legend. |
| **4** | **Deliverable 3 — Use-Case Flow Specification.** UC-06 on one page: preconditions, postconditions, main success scenario, two alternate flows, one exception flow, plus modelling notes. |

Everything else in this repository is working material, kept for reference — nothing else needs
to be submitted.

![Use-case diagram](source/02_UseCase_Diagram.svg)

---

## 1. Requirements at a glance

| Req ID | Type | Priority | One-line summary |
|---|---|---|---|
| **FR-001** | Functional | High | Probe every service health endpoint every 30 s and compute rolling 24-h availability. |
| **FR-002** | Functional | High | Register / update a microservice with owner, environment, endpoints, spec URL and dependencies. |
| **FR-003** | Functional | High | Render an interactive dependency graph and highlight blast radius up to 5 hops. |
| **FR-004** | Functional | Medium | Fetch, version and render OpenAPI specs every 24 h with a version diff view. |
| **FR-005** | Functional | High | Dispatch a downtime alert after 3 consecutive failed probes; acknowledge / resolve incidents. |
| **NFR-001** | Non-functional (Performance) | High | Dependency graph of 200 services / 600 edges renders in ≤ 2 s and pans at ≥ 30 fps. |
| **NFR-002** | Non-functional (Security) | High | SSO (OIDC) on every request, role-based write access, append-only audit log, TLS 1.2+. |

FR-001 and NFR-001 are the requirements supplied in the problem statement, restated so that
every acceptance criterion has a measurable pass/fail.

## 2. Actors

| Actor | Kind | Responsibility |
|---|---|---|
| **DevOps Engineer** | Human (primary) | Monitors health, tunes probe/alert policy, acknowledges incidents. |
| **System Architect** | Human (primary) | Explores dependencies, analyses blast radius before approving change. |
| **Service Owner / Developer** | Human (primary) | Registers and maintains service records; browses API documentation. |
| **Health Probe Scheduler** | System (time-triggered) | Fires the periodic probe cycle for every active service. |
| **Notification Gateway** | System (external) | Delivers alerts and recovery notices to email, Slack, PagerDuty. |

## 3. Use cases

| UC | Title | Primary actor | Traces to |
|---|---|---|---|
| UC-01 | Register / Update Microservice | Service Owner | FR-002 |
| UC-02 | Validate Metadata & OpenAPI Spec | *(included by UC-01)* | FR-002 |
| UC-03 | Browse Aggregated API Documentation | Service Owner, System Architect | FR-004 |
| UC-04 | View Service Dependency Graph | System Architect, DevOps Engineer | FR-003 |
| UC-05 | Analyse Blast Radius (Impact Analysis) | *(extends UC-04)* | FR-003 |
| UC-06 | Execute Scheduled Health Probe | Health Probe Scheduler | FR-001 |
| UC-07 | Record Result & Update Availability Metrics | *(included by UC-06)* | FR-001 |
| UC-08 | Dispatch Downtime Alert | *(extends UC-06)* → Notification Gateway | FR-005 |
| UC-09 | View Health & Availability Dashboard | DevOps Engineer | FR-001 |
| UC-10 | Configure Health-Check & Alert Policy | DevOps Engineer | FR-005 |

### «include» / «extend» relationships

| Relationship | Why this stereotype |
|---|---|
| `UC-01 ──«include»──▶ UC-02` | Registration **always** validates metadata and the OpenAPI URL — mandatory, reused behaviour. |
| `UC-06 ──«include»──▶ UC-07` | Every probe cycle **always** records its result and recomputes availability. |
| `UC-08 ──«extend»──▶ UC-06` | Alerting is **conditional** — it fires only at the extension point *failure threshold reached* (3 consecutive failures). |
| `UC-05 ──«extend»──▶ UC-04` | Blast-radius analysis is **optional** — added only at the extension point *node selected*. |

*Rule applied: `include` = reuse of mandatory behaviour; `extend` = optional or conditional
behaviour, and the arrow always points from the dependent use case to the base use case.*

## 4. Use-case flow (deliverable 3)

**UC-06 — Execute Scheduled Health Probe (with Downtime Alert)** was chosen because it is the
core automated behaviour of the portal and it exercises both an «include» (UC-07) and an
«extend» (UC-08).

---

## Repository layout

```
SE-Lab1-PS42/
├── PES2UG24CS046.pdf               ← THE SUBMISSION (4 pages)
├── README.md                       this file
├── source/                         individual artefacts kept as working material
│   ├── 01_Requirements_Table.{pdf,docx,csv,md}
│   ├── 02_UseCase_Diagram.{pdf,svg,drawio}   .drawio opens in draw.io
│   └── 03_UseCase_Flow.{pdf,docx,md}
├── problem-statement/              the given lab handout and problem statement
└── tools/                          scripts that generate every artefact
    ├── content.py                  single source of truth for all text
    ├── build_submission.py         → PES2UG24CS046.pdf  (the submission)
    ├── build_docs.py               → source/01_* and source/03_*
    ├── build_diagram.py            → source/02_UseCase_Diagram.svg / .pdf
    └── build_drawio.py             → source/02_UseCase_Diagram.drawio
```

## Reproducing the artefacts

```bash
pip install python-docx reportlab
python tools/build_submission.py   # PES2UG24CS046.pdf — the single file to submit
python tools/build_docs.py         # optional: standalone table + flow documents
python tools/build_diagram.py      # optional: standalone diagram (SVG + PDF)
python tools/build_drawio.py       # optional: editable draw.io source
```

All wording lives in `tools/content.py`, so editing one requirement there regenerates the
submission PDF and every supporting format consistently.
