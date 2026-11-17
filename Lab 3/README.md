# SE Lab 3 — Component Modelling & Architectural Pattern Selection

**SRN: PES2UG24CS046**
**Problem Statement #42 — Developer Tools & IT Operations**
**System: Internal Microservice Catalog & Health Portal**

PES University, Dept. of CSE — Software Engineering Lab

> The same system carried through **Lab 1** (requirements table, use-case diagram, use-case flow)
> and **Lab 2** (Jira epics, user stories, sprint simulation). Lab 3 turns those requirements into
> an architecture. The Self-Service Coffee Kiosk in the handout is the worked **example**, not the
> assigned scenario.

---

## ➡️ Submission file

### [`PES2UG24CS046_SE_Lab3.pdf`](PES2UG24CS046_SE_Lab3.pdf) — this single PDF is the deliverable to submit.

| Page | Size | Content |
|---|---|---|
| **1** | A3 landscape | **Deliverable 1 — UML Component Diagram.** 12 components, 15 interfaces, ball-and-socket notation, tier grouping, legend. |
| **2** | A4 portrait | **Deliverable 2 — Architecture Justification.** Exactly one page: choice, two reasons, security advantage, performance benefit. |
| **3–4** | A4 portrait | Appendix A — Step 1 scenario review and Step 2 architectural style analysis. |
| **5–6** | A4 portrait | Appendix B — component and interface catalogues (Steps 3–4). |

The diagram alone is also available as **PNG** and **PDF**, and the justification alone as
**`.docx`** (the Word document the handout asks for) and **PDF** — see `source/`.

![Component diagram](source/01_Component_Diagram.png)

---

## Architecture selection

> **We chose the Microservices Architecture for the Internal Microservice Catalog & Health Portal.**

| Style | Verdict | Deciding factor for *this* system |
|---|---|---|
| Layered | Rejected | One deployable means the probe engine and the graph API share a thread pool and a heap. A fleet-wide outage parks hundreds of probe threads on 5 s timeouts and breaks NFR-001. |
| Client-Server | Rejected | A single server is a single point of failure — a monitoring system that dies under the load it observes is worse than none — and a hard ceiling at 200+ probed services plus 50 concurrent users. |
| **Microservices** | **Selected** | Independent scaling of two opposite workloads, fault isolation of two hang-prone outbound calls, storage picked per workload, and one gateway to enforce SSO/RBAC/audit. |

**Two reasons.** (1) The portal carries two workloads with opposite scaling profiles — continuous
IO-bound probing (FR-001: 200 services every 30 s, 5 s timeout) versus bursty CPU-bound graph
rendering (NFR-001: 600 edges in ≤ 2.0 s p95) — which cannot be tuned or scaled as one unit.
(2) The portal must survive the very failures it exists to report: the OpenAPI fetch (FR-004) and
the alert dispatch (FR-005) are outbound calls that can hang, and isolating them keeps
registration, the dependency graph and health probing serving.

**Security advantage.** A single enforcement point — every request passes the API Gateway & Auth
component, which validates the OIDC token, enforces the NFR-002 RBAC rule before any service is
reached, and journals every mutation to an append-only (WORM) store that exposes no update or
delete. Internal services are unroutable from outside and take only mTLS calls.

**Performance benefit.** Targeted horizontal scaling: the Dependency Graph Service is replicated
on its own and keeps a warm blast-radius cache, so NFR-001 is met from memory without competing
with the probe loop, while the probe ledger lives in a time-series store tuned for high-rate
appends and the catalog stays relational.

---

## Components (9 internal + 3 external)

| # | Component | Tier | Traces to |
|---|---|---|---|
| **C1** | Portal Web UI | Presentation | UC-01, UC-03, UC-04, UC-05, UC-09, UC-10 |
| **C2** | API Gateway & Auth | Edge & Security | NFR-002 (all use cases) |
| **C3** | Catalog Service | Service | UC-01, UC-02 / FR-002 |
| **C4** | Dependency Graph Service | Service | UC-04, UC-05 / FR-003, NFR-001 |
| **C5** | Alerting Service | Service | UC-08, UC-10 / FR-005 |
| **C6** | API Doc Aggregator Service | Service | UC-03 / FR-004 |
| **C7** | Health Probe Service | Service | UC-06, UC-07, UC-09 / FR-001 |
| **C8** | Catalog Store | Data | FR-002, FR-003, FR-004 |
| **C9** | Probe Ledger & Audit Store | Data | FR-001, FR-005, NFR-002 |
| **E1** | Corporate SSO (OIDC) Provider | External | — |
| **E2** | Registered Microservice Fleet | External | — |
| **E3** | Notification Gateway | External | — |

*The handout asks for at least 5 components and at least 4 interfaces; this design shows 12
components and 15 interfaces. The full interface catalogue — provider, consumer, protocol and
purpose for each of I1…I15 — is Appendix B of the submission PDF.*

---

## Repository layout

```
SE-Lab3/
├── PES2UG24CS046_SE_Lab3.pdf            ← THE SUBMISSION (6 pages)
├── README.md                            this file
├── source/                              individual artefacts, kept as working material
│   ├── 01_Component_Diagram.{pdf,png,svg}
│   ├── 01_Component_Diagram.drawio          opens in draw.io / app.diagrams.net
│   ├── 02_Architecture_Justification.{docx,pdf}
│   └── 03_Architecture_Analysis.pdf
├── problem-statement/                   the supplied lab handout
└── tools/                               scripts that generate every artefact
    ├── content.py                       single source of truth for all text
    ├── build_submission.py              → PES2UG24CS046_SE_Lab3.pdf  (runs the other three)
    ├── build_diagram.py                 → source/01_Component_Diagram.{pdf,png,svg}
    ├── build_docs.py                    → source/02_* and source/03_*
    └── build_drawio.py                  → source/01_Component_Diagram.drawio
```

## Reproducing the artefacts

```bash
pip install reportlab python-docx pymupdf
python tools/build_submission.py   # builds everything, then merges the submission PDF
```

All wording lives in `tools/content.py`, so editing one requirement or one interface there
regenerates the diagram, the justification and the appendix consistently. `build_docs.py` fails
the build if the justification ever spills past one page, which the handout caps it at.
