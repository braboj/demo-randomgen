# 1. Introduction and Goals

RandomGen is a small web service (a Flask REST API) that produces random
numbers. Each possible number has a set chance of being chosen, so some
numbers appear more often than others. With every response the service also
reports how closely the numbers it produced match the chances that were
requested. This check uses a standard statistical method, the Chi-Square
goodness-of-fit test, from the scipy library. A caller asks for a number of
draws and receives both the result and a clear fairness verdict.

## 1.1 Requirements overview

A functional requirement states what the service does. Qualities such as speed
and reliability — sometimes called non-functional requirements — are covered
separately by the quality goals.

| ID | Requirement |
|------|-------------|
| FR01 | The service shall generate random numbers that follow a given distribution. |
| FR02 | The service shall provide a default distribution that callers can override. |
| FR03 | The service shall report how well each sample matches the distribution. |
| FR04 | The service shall reject invalid input with a clear error. |
| FR05 | The service shall expose a health check. |
| FR06 | The service shall publish its API documentation. |
| FR07 | The service shall provide a web page to try the API. |

## 1.2 Quality goals

Quality goals describe how well the service works, rather than what it does.
They are also known as quality attributes or non-functional requirements.

| ID | Quality goal | Motivation |
|------|--------------|------------|
| QG01 | Correctness | Generated samples closely match the requested distribution; the Chi-Square report on every response makes this measurable. |
| QG02 | Reliability | Bad input fails predictably with an HTTP 400 and a JSON error, and never crashes a worker. |
| QG03 | Maintainability | Clean, readable, well-tested code: a clear layout, type checks, linting, and a coverage gate. |
| QG04 | Portability | One pinned, non-root image runs the same locally, on Docker Hub, and on Render. |
| QG05 | Compatibility | Existing callers keep working: the versioned paths (`/api/v1`, `/api/v2`) are a public contract whose behavior does not change. |
| QG06 | Usability | An interviewer or client can run and explore the service quickly: a live demo, a browser UI, interactive API docs, and a one-command container. |

## 1.3 Stakeholders

Stakeholders are the people with an interest in the system, and this section
lists their expectations from it.

| Role | Concern |
|------|---------|
| Interviewer / prospective client | Quickly assess engineering quality: clean code, sound decisions, and a running demo. |
| Maintainer | Exemplary, testable, low-maintenance code that passes its quality gates and deploys cleanly as the demo. |
