# Use-Case Flow Specification

## UC-06 - Execute Scheduled Health Probe (with Downtime Alert)

| Field | Value |
|---|---|
| Scope | Internal Microservice Catalog & Health Portal |
| Level | User-goal / system-goal (sub-function of continuous monitoring) |
| Primary actor | Health Probe Scheduler (time-triggered system actor) |
| Secondary actors | Registered Microservice, Notification Gateway, DevOps Engineer (alert recipient) |
| Trigger | The probe timer for service S elapses (default every 30 s). |
| Traces to | FR-001, FR-005, NFR-002; includes UC-07, extended by UC-08 |

### Preconditions

1. Service S is registered in the catalog with state ACTIVE and a syntactically valid health-endpoint URL (FR-002).
2. A health-check policy exists for S: interval 30 s, request timeout 5 s, failure threshold 3 consecutive probes (UC-10).
3. The probe worker is running and has network reachability to the segment hosting S.
4. The owning team of S has at least one notification channel configured.

### Postconditions (success guarantee)

1. The outcome of the probe (UP/DOWN, latency, HTTP status, timestamp) is persisted in the probe ledger.
2. The rolling 24-hour availability of S is recomputed and the dashboard tile reflects it within 5 s.
3. The health state of S is exactly one of HEALTHY / DEGRADED / DOWN and is consistent with the last three probe results.
4. If an incident was opened or closed, the corresponding alert or recovery notice has been dispatched and an audit entry written.

**Minimal guarantee:** Even on an internal error the probe attempt is recorded; no probe result is silently lost.

### Main Success Scenario

1. The Health Probe Scheduler triggers the probe cycle for service S at its configured interval.
2. The system loads the health-endpoint URL, request timeout and failure threshold of S from the catalog.
3. The system issues an HTTP GET to the health endpoint of S with a 5 s timeout.
4. Service S responds HTTP 200 with body status = UP inside the timeout.
5. The system records the probe result as UP with its latency and timestamp. [<<include>> UC-07 Record Result & Update Availability Metrics]
6. The system recomputes the rolling 24-hour availability of S and refreshes the dashboard tile.
7. If S had an open incident, the system closes it, sets the state to HEALTHY and sends a recovery notice through the Notification Gateway.
8. The system resets the consecutive-failure counter of S to 0 and schedules the next probe.
9. The use case ends successfully.

### Alternate Flow - 4a. Service unreachable or unhealthy (extension point: failure threshold reached)

- 4a1. The request times out, the connection is refused, or the response is not HTTP 200 with status UP.
- 4a2. The system records the probe as DOWN with its error class (timeout / connection refused / HTTP 5xx) and increments the consecutive-failure counter of S. [<<include>> UC-07]
- 4a3. If the counter is less than 3, the system sets the state of S to DEGRADED, raises no alert, and the flow resumes at main step 8.
- 4a4. If the counter equals 3, the system opens an incident, sets the state of S to DOWN and records the downtime start as the timestamp of the first failed probe in the streak.
- 4a5. [<<extend>> UC-08 Dispatch Downtime Alert] The system composes an alert (service, environment, owning team, downtime start, failure count) and delivers it to every configured channel within 60 s; the incident is marked NOTIFIED (FR-005).
- 4a6. If the counter is greater than 3, duplicate suppression applies and no further alert is raised for the open incident.
- 4a7. The flow resumes at main step 8.

### Alternate Flow - 4a5a. Notification Gateway unavailable

- 4a5a1. The gateway returns an error or times out; the system retries 3 times with exponential backoff (5 s, 15 s, 45 s).
- 4a5a2. If all retries fail, the alert is written to a dead-letter queue, a delivery-failure banner is shown on the dashboard and the ops-tooling channel is notified.
- 4a5a3. The queued alert is redelivered automatically once the gateway recovers; the incident stays OPEN and un-notified until then.

### Exception Flow - 2a. Service decommissioned or disabled during the cycle

- 2a1. The catalog reports the state of S as INACTIVE or DELETED.
- 2a2. The system skips the probe, writes a SKIPPED ledger entry with the reason, raises no alert and ends the cycle.
