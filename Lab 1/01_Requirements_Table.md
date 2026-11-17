# Requirements Table - Internal Microservice Catalog & Health Portal

**PES University, Dept. of CSE - Software Engineering**  
**Lab 1: Requirements Engineering & UML Use-Case Modelling**  
**Problem Statement #42 - Developer Tools & IT Operations**

> An enterprise developer portal that maps microservice dependencies, aggregates API documentation, and runs automated periodic health-check pingers with downtime alerts.

Exactly **5 functional requirements** (FR-001 - FR-005) and **2 non-functional requirements** (NFR-001, NFR-002). The `Comments` column records the peer-critique round (Lab step 3) and how each requirement was revised in response.

| Req ID | Type | Description | Priority | Acceptance Criteria (measurable pass/fail) | Rationale | Comments (peer critique -> revision) |
|---|---|---|---|---|---|---|
| **FR-001** | Functional | The system shall probe the health endpoint of every registered microservice at a configurable interval (default 30 s, with a 5 s request timeout) and shall compute, per service, a rolling 24-hour availability percentage from the recorded probe results. | High | PASS: probes for a registered service are recorded every 30 s +/- 2 s; a probe returning HTTP 200 within 5 s is stored as UP and any other response or timeout as DOWN; after 3 consecutive DOWN probes the downtime interval is persisted and an alert is dispatched (FR-005); the displayed rolling 24-h availability equals (UP probes / total probes in the last 24 h) x 100, rounded to 2 decimals, and matches an independent recount of the probe ledger within +/- 0.1 %.<br>FAIL: an unreachable service is displayed as HEALTHY, the probe interval drifts beyond +/- 2 s, or availability deviates from the ledger by more than 0.1 %. | Core monitoring capability of the portal: automated detection replaces manual checking and produces an objective, auditable availability figure per service. | Peer: interval, timeout and rounding are not stated, so the requirement is not testable. Revised: default 30 s interval, 5 s timeout, +/- 2 s tolerance and 2-decimal rounding added to the acceptance criteria. |
| **FR-002** | Functional | The system shall allow a Service Owner to register a new microservice, or update an existing one, by supplying service name, owning team, environment, repository URL, health-endpoint URL, OpenAPI specification URL and its declared upstream dependencies. | High | PASS: on submitting a form in which every mandatory field is present and well formed, the service is persisted, is returned by catalog search within 5 s, its record version is incremented by 1, and an audit entry (actor, timestamp, changed fields) is written.<br>FAIL: a record is saved with a mandatory field missing, with a malformed health-endpoint or OpenAPI URL, or with a name that duplicates an existing service in the same environment. | The catalog is the single source of truth; probing, documentation aggregation and the dependency graph all consume this registration data, so an incomplete record breaks every downstream feature. | Peer: what exactly counts as a duplicate service? Revised: uniqueness defined explicitly as the pair (service name, environment). |
| **FR-003** | Functional | The system shall generate an interactive directed dependency graph from the declared dependencies of all registered services, and shall allow a System Architect to select any node to highlight its upstream callers and downstream dependencies (blast radius) up to a chosen depth of 1 to 5 hops. | High | PASS: the graph renders exactly one node per registered service and one directed edge per declared dependency; selecting a node highlights exactly the transitive upstream and downstream sets for the selected depth and dims all other nodes; a dependency cycle is flagged with a warning badge naming the services in the cycle.<br>FAIL: a declared dependency has no corresponding edge, an unrelated node is highlighted, or a cycle is rendered without a warning. | Architects must understand coupling and the true impact of an outage or a planned deprecation before approving a change; manually maintained wiki diagrams go stale immediately. | Peer: showing impact is vague - impact of what, and how far does it propagate? Revised: impact defined as the transitive upstream/downstream sets with a selectable depth of 1 to 5 hops. |
| **FR-004** | Functional | The system shall fetch the OpenAPI/Swagger specification of every registered service at least once every 24 hours, store each retrieved version, and render it as browsable API documentation including a difference view between any two stored versions. | Medium | PASS: a specification changed in a service repository is reflected in the portal within 24 h; at least the last 5 versions of each specification are retained and selectable; the diff view lists added, removed and modified endpoints between the two selected versions; a failed fetch marks the document STALE and shows the last successful fetch timestamp.<br>FAIL: a failed fetch silently leaves outdated documentation presented as current, or the diff omits an endpoint that changed. | Consumers of an internal API need a current, discoverable contract in one place; version diffs surface breaking changes before they reach dependent teams. | Peer: what is shown when the specification URL is unreachable? Revised: added the STALE badge and the last-successful-fetch timestamp as explicit failure behaviour. |
| **FR-005** | Functional | The system shall dispatch a downtime alert to every notification channel configured for the owning team (email, Slack, PagerDuty) when a service records 3 consecutive failed health probes, and shall allow a DevOps Engineer to acknowledge and resolve the resulting incident. | High | PASS: an alert carrying service name, environment, owning team, downtime start time and consecutive-failure count is delivered to every configured channel within 60 s of the third failed probe; at most one alert is raised per open incident (duplicate suppression); acknowledging sets the incident to ACKNOWLEDGED with actor and timestamp; a recovery notice is sent on the first successful probe after recovery.<br>FAIL: no alert within 60 s, a repeat alert for an already-open incident, or a resolved incident with no recovery notice. | Detection has no operational value unless the on-call owner is notified quickly; suppression and explicit acknowledgement prevent alert fatigue during an incident. | Peer: a flapping service would spam the on-call channel. Revised: one alert per open incident (duplicate suppression), plus an explicit recovery notice. |
| **NFR-001** | Non-functional<br>(Performance / Usability) | The service catalog dependency-graph viewer shall render a catalog of up to 200 services and 600 dependency edges within 2 seconds and shall sustain interactive pan, zoom and node selection at 30 frames per second or better. | High | PASS: with a seeded catalog of 200 services and 600 edges on the reference client (Chrome, 8 GB RAM, 1920x1080) and a background load of 50 concurrent portal users, the p95 time from opening the graph view to the first fully rendered frame is <= 2.0 s and the p95 frame time during a scripted pan/zoom sequence is <= 33 ms, measured over 20 runs.<br>FAIL: p95 initial render > 2.0 s, or any frame time > 100 ms (visible stutter) during the scripted pan/zoom. | The graph is the most-used analysis view in the portal; a viewer that stalls at enterprise scale would push architects back to stale, hand-drawn diagrams. | Peer: renders smoothly cannot be tested. Revised: quantified as <= 2.0 s p95 initial render and >= 30 fps, with reference hardware, data volume and concurrent load all stated. |
| **NFR-002** | Non-functional<br>(Security) | The system shall authenticate every user through the corporate SSO (OIDC) provider and shall authorise catalog-modifying operations by role, so that only a member of the owning team of a service or a DevOps Engineer may create, update or delete that service record; every modification shall be written to an append-only audit log. | High | PASS: an unauthenticated request to any portal API returns HTTP 401; a request from an authenticated user who is neither an owning-team member nor a DevOps Engineer returns HTTP 403; every successful mutation writes an audit record (actor, role, service, action, timestamp, before/after values) within 1 s; the audit store rejects update and delete operations; all traffic is served over TLS 1.2 or higher.<br>FAIL: any mutation succeeds without a matching audit record, or a non-owner modifies another team record. | The catalog exposes the internal architecture, endpoints and ownership of the entire estate; unrestricted edits would corrupt the source of truth and leak the internal topology to anyone on the network. | Peer: who is allowed to delete a service, and can we prove who changed what? Revised: explicit RBAC rule (owning team or DevOps Engineer) plus an append-only audit log holding before/after values. |

## Actors

| Actor | Kind | Responsibility in this system |
|---|---|---|
| **DevOps Engineer** | Human (primary) | Monitors service health, tunes probe and alert policy, acknowledges and resolves incidents. |
| **System Architect** | Human (primary) | Explores the dependency graph and analyses blast radius before approving architectural change. |
| **Service Owner / Developer** | Human (primary) | Registers and maintains the service records of the team and browses aggregated API docs. |
| **Health Probe Scheduler** | System (time-triggered, secondary) | Fires the periodic probe cycle for every active service at its configured interval. |
| **Notification Gateway** | System (external, secondary) | Delivers dispatched alerts and recovery notices to email, Slack and PagerDuty. |

## Use Cases

| UC ID | Use Case | Actor(s) / Relationship | Traces to |
|---|---|---|---|
| **UC-01** | Register / Update Microservice | Service Owner | FR-002 |
| **UC-02** | Validate Metadata & OpenAPI Spec | (included by UC-01) | FR-002 |
| **UC-03** | Browse Aggregated API Documentation | Service Owner, System Architect | FR-004 |
| **UC-04** | View Service Dependency Graph | System Architect, DevOps Engineer | FR-003 |
| **UC-05** | Analyse Blast Radius (Impact Analysis) | (extends UC-04) System Architect | FR-003 |
| **UC-06** | Execute Scheduled Health Probe | Health Probe Scheduler | FR-001 |
| **UC-07** | Record Result & Update Availability Metrics | (included by UC-06) | FR-001 |
| **UC-08** | Dispatch Downtime Alert | (extends UC-06) Notification Gateway | FR-005 |
| **UC-09** | View Health & Availability Dashboard | DevOps Engineer | FR-001 |
| **UC-10** | Configure Health-Check & Alert Policy | DevOps Engineer | FR-005 |

## Requirement -> Use-Case Traceability

| Requirement | Realised by |
|---|---|
| FR-001 | UC-06 Execute Scheduled Health Probe; UC-07 Record Result & Update Availability Metrics; UC-09 View Health & Availability Dashboard |
| FR-002 | UC-01 Register / Update Microservice; UC-02 Validate Metadata & OpenAPI Spec |
| FR-003 | UC-04 View Service Dependency Graph; UC-05 Analyse Blast Radius (Impact Analysis) |
| FR-004 | UC-03 Browse Aggregated API Documentation |
| FR-005 | UC-08 Dispatch Downtime Alert; UC-10 Configure Health-Check & Alert Policy |
| NFR-001 | Quality constraint on UC-04 / UC-05 (graph rendering) |
| NFR-002 | Quality constraint on all use cases (SSO, RBAC, audit log) |

## <<include>> and <<extend>> Relationships

- **`UC-01 --<<include>>--> UC-02`** - Registering or updating a service ALWAYS validates the submitted metadata and the reachability of the OpenAPI specification URL, so that mandatory behaviour is factored out and reused.
- **`UC-06 --<<include>>--> UC-07`** - Every probe cycle ALWAYS persists its outcome to the probe ledger and recomputes the rolling 24-hour availability: unconditional, mandatory sub-behaviour.
- **`UC-08 --<<extend>>--> UC-06`** - Alert dispatch is CONDITIONAL: it adds behaviour to the probe cycle only at the extension point failure threshold reached, i.e. when 3 consecutive probes have failed.
- **`UC-05 --<<extend>>--> UC-04`** - Blast-radius analysis is OPTIONAL: the architect may simply view the graph; impact highlighting is added only at the extension point node selected.
